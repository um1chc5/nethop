"""nethop Textual application."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import Footer, ProgressBar, RichLog, Static

from . import __version__
from . import browser as browser_mod
from . import export as export_mod
from . import nmap_client
from . import network as network_mod
from . import roles
from .models import Host, NetInfo
from .state import AppState, load_state, save_state
from .widgets import ActionList, HostTable, InterfaceModal, LanMap, NicknameModal, PortTable

CSS_PATH = Path(__file__).with_name("app.tcss")

_SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


class NethopApp(App[None]):
    """Interactive LAN host explorer backed by nmap."""

    TITLE = "nethop"
    CSS_PATH = CSS_PATH
    BINDINGS = [
        Binding("d", "discover", "Discover", show=True),
        Binding("r", "discover", "Refresh", show=False),
        Binding("enter", "run_scan", "Scan", show=True),
        Binding("o", "open_port", "Open URL", show=True),
        Binding("i", "pick_iface", "Iface", show=True),
        Binding("n", "nickname", "Nick", show=True),
        Binding("w", "toggle_watch", "Watch", show=True),
        Binding("m", "toggle_map", "Map", show=True),
        Binding("c", "copy_host", "Copy", show=True),
        Binding("C", "copy_all", "Copy all", show=False),
        Binding("tab", "focus_next", "Focus", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.net: NetInfo | None = None
        self.hosts: dict[str, Host] = {}
        self.state: AppState = load_state()
        self._busy = False
        self._job_label = ""
        self._spin_i = 0
        self._spin_timer: Timer | None = None
        self._last_nmap_status = ""
        self._watching = False
        self._watch_timer: Timer | None = None
        self._watch_left = 0
        self._show_map = False
        self._gateway: str | None = None
        self._title_flash_timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Static("nethop", id="title-bar")
        with Horizontal(id="body"):
            with Vertical(id="left-pane"):
                yield Static("HOSTS  ·  d discover  ·  n nick  ·  i iface", classes="pane-title")
                yield HostTable(id="hosts")
            with Vertical(id="right-pane"):
                yield Static("ACTIONS  ·  enter to run on selected host", classes="pane-title")
                yield ActionList(id="actions")
        with Vertical(id="lower"):
            with Vertical(id="bottom-pane"):
                yield Static(
                    "PORTS  ·  o open  ·  m map  ·  c copy",
                    id="bottom-title",
                    classes="pane-title",
                )
                yield PortTable(id="ports")
                yield LanMap(id="lan-map", classes="-hidden")
            yield Static("idle", id="job-status", classes="-idle")
            yield ProgressBar(id="job-progress", total=100, show_eta=False)
            yield RichLog(id="log-pane", markup=True, highlight=True, max_lines=500)
        yield Footer()

    def on_mount(self) -> None:
        self._set_title("detecting LAN…")
        self.query_one("#hosts", HostTable).focus()
        self.call_after_refresh(self._bootstrap)

    def _bootstrap(self) -> None:
        try:
            nmap_client.find_nmap()
            self.log_line("nmap found", "ok")
        except nmap_client.NmapError as exc:
            self.log_line(str(exc), "err")
            self._set_title("nmap missing")
            return

        try:
            self.net = network_mod.detect_lan(
                preferred_iface=self.state.last_iface,
                preferred_cidr=self.state.last_cidr,
            )
        except RuntimeError as exc:
            self.log_line(str(exc), "err")
            self._set_title("no LAN")
            return

        self._gateway = network_mod.default_gateway()
        self._persist_net()
        self._set_title(self._lan_title())
        iface = self.net.interface or "?"
        self.log_line(
            f"Local {self.net.ip} on {iface}  subnet {self.net.cidr}",
            "ok",
        )
        if self.net.cidr.endswith("/32") or "/31" in self.net.cidr:
            self.log_line(
                "CIDR looks like a tunnel — press [b]i[/b] to pick Wi‑Fi/Ethernet.",
                "warn",
            )
        self.log_line(
            "Press [b]d[/b] to discover (authorized use only). "
            "[b]w[/b] watch · [b]m[/b] map · [b]n[/b] nickname.",
            "info",
        )
        self.action_discover()

    def _persist_net(self) -> None:
        if not self.net:
            return
        self.state.last_iface = self.net.interface
        self.state.last_cidr = self.net.cidr
        save_state(self.state)

    def _lan_title(self, extra: str = "") -> str:
        if not self.net:
            return extra or "no LAN"
        iface = self.net.interface or "iface?"
        parts = [f"{iface} {self.net.cidr}", f"you {self.net.ip}"]
        if self._watching:
            parts.append(f"watch {self._watch_left}s")
        if extra:
            parts.append(extra)
        return "  ·  ".join(parts)

    def _set_title(self, detail: str) -> None:
        bar = self.query_one("#title-bar", Static)
        bar.update(f" nethop v{__version__}  ·  {detail}")

    def log_line(self, text: str, level: str = "info") -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        style = {
            "ok": "ok",
            "warn": "warn",
            "err": "err",
            "cmd": "cmd",
        }.get(level, "")
        prefix = f"[{style}]{stamp}[/{style}]" if style else stamp
        self.query_one("#log-pane", RichLog).write(f"{prefix}  {text}")

    def _set_job_ui(
        self,
        *,
        busy: bool,
        label: str = "",
        profile_id: str | None = None,
    ) -> None:
        self._busy = busy
        self._job_label = label
        self._last_nmap_status = ""
        status = self.query_one("#job-status", Static)
        bar = self.query_one("#job-progress", ProgressBar)
        actions = self.query_one("#actions", ActionList)

        if busy:
            status.remove_class("-idle")
            bar.add_class("-active")
            bar.update(total=None)
            actions.set_running(profile_id)
            self._spin_i = 0
            self._render_job_status()
            if self._spin_timer is not None:
                self._spin_timer.stop()
            self._spin_timer = self.set_interval(0.1, self._tick_job)
            self.log_line(f"Started: {label}", "info")
        else:
            if self._spin_timer is not None:
                self._spin_timer.stop()
                self._spin_timer = None
            bar.update(total=100, progress=100)
            bar.remove_class("-active")
            status.add_class("-idle")
            status.update("idle")
            actions.set_running(None)

    def _tick_job(self) -> None:
        if not self._busy:
            return
        self._spin_i = (self._spin_i + 1) % len(_SPIN)
        self._render_job_status()
        self.query_one("#actions", ActionList).tick_spinner()

    def _render_job_status(self) -> None:
        spin = _SPIN[self._spin_i]
        extra = f"  ·  {self._last_nmap_status}" if self._last_nmap_status else ""
        self.query_one("#job-status", Static).update(
            f"{spin}  {self._job_label}{extra}"
        )

    def _on_nmap_progress(self, fraction: Optional[float], text: str) -> None:
        def apply() -> None:
            short = text
            if len(short) > 90:
                short = short[:87] + "…"
            self._last_nmap_status = short
            self._render_job_status()
            bar = self.query_one("#job-progress", ProgressBar)
            if fraction is not None:
                bar.update(total=100, progress=max(0, min(100, fraction * 100)))
            if "about" in text.lower() and "%" in text:
                self.log_line(text, "cmd")

        self.call_from_thread(apply)

    def _on_nmap_log(self, msg: str, level: str = "info") -> None:
        self.call_from_thread(self.log_line, msg, level)

    def _decorate_host(self, host: Host) -> Host:
        host.nickname = self.state.nickname_for(host.ip) or host.nickname
        roles.apply_role(host)
        return host

    def _host_list(self) -> list[Host]:
        return sorted(
            self.hosts.values(),
            key=lambda h: tuple(int(x) for x in h.ip.split(".")),
        )

    def _refresh_hosts(self, keep_ip: str | None = None) -> None:
        table = self.query_one("#hosts", HostTable)
        table.set_hosts(self._host_list(), selected_ip=keep_ip)
        self._sync_ports_from_selection()
        self._refresh_map()

    def _refresh_map(self) -> None:
        lan_map = self.query_one("#lan-map", LanMap)
        you = self.net.ip if self.net else ""
        iface = self.net.interface if self.net else ""
        cidr = self.net.cidr if self.net else ""
        lan_map.set_map(
            self._host_list(),
            you_ip=you,
            gateway=self._gateway,
            iface=iface,
            cidr=cidr,
        )

    def _sync_ports_from_selection(self) -> None:
        table = self.query_one("#hosts", HostTable)
        ip = table.selected_ip()
        ports = self.query_one("#ports", PortTable)
        if not ip or ip not in self.hosts:
            ports.set_ports([])
            return
        ports.set_ports(self.hosts[ip].ports)

    def _selected_host(self) -> Host | None:
        ip = self.query_one("#hosts", HostTable).selected_ip()
        if not ip:
            return None
        return self.hosts.get(ip)

    def _flash_title(self) -> None:
        bar = self.query_one("#title-bar", Static)
        bar.add_class("-flash")
        if self._title_flash_timer is not None:
            self._title_flash_timer.stop()

        def clear() -> None:
            bar.remove_class("-flash")
            self._title_flash_timer = None

        self._title_flash_timer = self.set_timer(0.6, clear)

    @on(HostTable.RowHighlighted)
    def _on_host_highlight(self, _event: HostTable.RowHighlighted) -> None:
        self._sync_ports_from_selection()

    @on(HostTable.RowSelected)
    def _on_host_selected(self, _event: HostTable.RowSelected) -> None:
        self._sync_ports_from_selection()
        self.query_one("#actions", ActionList).focus()

    @on(ActionList.Selected)
    def _on_action_selected(self, _event: ActionList.Selected) -> None:
        self.action_run_scan()

    @on(PortTable.RowSelected)
    def _on_port_selected(self, _event: PortTable.RowSelected) -> None:
        self.action_open_port()

    def action_discover(self) -> None:
        if self._busy:
            self.log_line("Busy — wait for the current scan.", "warn")
            return
        if not self.net:
            self.log_line("LAN not detected.", "err")
            return
        label = f"Discover {self.net.cidr}"
        self._set_job_ui(busy=True, label=label, profile_id=None)
        self._set_title(self._lan_title("discovering…"))
        self._discover_worker(self.net.cidr)

    @work(thread=True, exclusive=True)
    def _discover_worker(self, cidr: str) -> None:
        try:
            found = nmap_client.discover_hosts(
                cidr,
                log=self._on_nmap_log,
                progress=self._on_nmap_progress,
            )
            error: str | None = None
        except nmap_client.NmapError as exc:
            found = []
            error = str(exc)

        def apply() -> None:
            self._set_job_ui(busy=False)
            if error:
                self.log_line(error, "err")
                self._set_title(self._lan_title("discover failed"))
                return

            prev_ips = set(self.hosts.keys()) or set(self.state.last_hosts)
            new_ips = {h.ip for h in found}
            added = sorted(new_ips - prev_ips, key=lambda ip: tuple(int(x) for x in ip.split(".")))
            gone = sorted(prev_ips - new_ips, key=lambda ip: tuple(int(x) for x in ip.split(".")))

            merged: dict[str, Host] = {}
            for host in found:
                prev = self.hosts.get(host.ip)
                if prev and prev.ports and not host.ports:
                    host.ports = prev.ports
                    host.os_guess = host.os_guess or prev.os_guess
                    host.last_scan = prev.last_scan
                    host.role = prev.role
                host.is_new = host.ip in added and bool(prev_ips)
                self._decorate_host(host)
                merged[host.ip] = host
            self.hosts = merged
            self.state.last_hosts = sorted(merged.keys())
            save_state(self.state)
            self._refresh_hosts()

            self.log_line(f"Found {len(found)} host(s)", "ok")
            if prev_ips:
                self.log_line(
                    f"Presence  +{len(added)} new  −{len(gone)} gone",
                    "info",
                )
                if added:
                    self.log_line("New: " + ", ".join(added[:12]) + ("…" if len(added) > 12 else ""), "ok")
                if gone:
                    self.log_line("Gone: " + ", ".join(gone[:12]) + ("…" if len(gone) > 12 else ""), "warn")
                if added and self._watching:
                    self.bell()
                    self._flash_title()

            self._set_title(self._lan_title(f"{len(found)} hosts"))

        self.call_from_thread(apply)

    def action_run_scan(self) -> None:
        if self._busy:
            self.log_line("Busy — wait for the current scan.", "warn")
            return
        host = self._selected_host()
        if not host:
            self.log_line("Select a host first.", "warn")
            return
        profile = self.query_one("#actions", ActionList).selected_profile()
        if not profile:
            self.log_line("Select an action.", "warn")
            return
        if profile.needs_admin:
            self.log_line(
                f"{profile.title} often needs Administrator / root privileges.",
                "warn",
            )
        label = f"{profile.title} → {host.ip}"
        self._set_job_ui(busy=True, label=label, profile_id=profile.id)
        self._set_title(self._lan_title(f"scan {host.ip}"))
        self._scan_worker(host.ip, list(profile.nmap_args), profile.title)

    @work(thread=True, exclusive=True)
    def _scan_worker(self, ip: str, args: list[str], title: str) -> None:
        try:
            result = nmap_client.scan_host(
                ip,
                args,
                log=self._on_nmap_log,
                progress=self._on_nmap_progress,
            )
            error: str | None = None
        except nmap_client.NmapError as exc:
            result = None
            error = str(exc)

        def apply() -> None:
            self._set_job_ui(busy=False)
            if error or result is None:
                self.log_line(error or "Scan failed", "err")
                self._set_title(self._lan_title("scan failed"))
                return
            prev = self.hosts.get(ip)
            if prev:
                result.hostname = result.hostname or prev.hostname
                result.mac = result.mac or prev.mac
                result.vendor = result.vendor or prev.vendor
                result.nickname = prev.nickname
                result.is_new = prev.is_new
                if not result.os_guess:
                    result.os_guess = prev.os_guess
                if not result.ports and prev.role:
                    result.role = prev.role
            self._decorate_host(result)
            self.hosts[ip] = result
            self._refresh_hosts(keep_ip=ip)
            open_n = len(result.ports)
            self.log_line(f"{title} done — {open_n} open port(s) on {ip}", "ok")
            if result.role:
                self.log_line(f"Role guess: {result.role}", "info")
            if result.os_guess:
                self.log_line(f"OS guess: {result.os_guess}", "info")
            self._set_title(self._lan_title(f"last {ip}"))

        self.call_from_thread(apply)

    def action_open_port(self) -> None:
        host = self._selected_host()
        if not host:
            self.log_line("Select a host first.", "warn")
            return
        port = self.query_one("#ports", PortTable).selected_port()
        if not port:
            self.log_line("Select a port (run a scan first).", "warn")
            return
        url = browser_mod.open_in_browser(host.ip, port)
        self.log_line(f"Opened {url}", "ok")

    def action_pick_iface(self) -> None:
        candidates = network_mod.list_ipv4_ifaces()
        if not candidates:
            self.log_line("No IPv4 interfaces found.", "err")
            return
        current = self.net.cidr if self.net else ""

        def on_close(choice: network_mod.IfaceCandidate | None) -> None:
            if choice is None:
                return
            import ipaddress

            try:
                netmask = str(ipaddress.IPv4Network(choice.cidr).netmask)
            except ValueError:
                netmask = ""
            self.net = NetInfo(
                ip=choice.ip,
                cidr=choice.cidr,
                interface=choice.name,
                netmask=netmask,
            )
            self._persist_net()
            self._gateway = network_mod.default_gateway()
            self.log_line(
                f"Using {choice.name}  {choice.ip}  →  {choice.cidr}",
                "ok",
            )
            self._set_title(self._lan_title())
            self._refresh_map()
            self.action_discover()

        self.push_screen(InterfaceModal(candidates, current_cidr=current), on_close)

    def action_nickname(self) -> None:
        host = self._selected_host()
        if not host:
            self.log_line("Select a host first.", "warn")
            return

        def on_close(value: str | None) -> None:
            if value is None:
                return
            self.state.set_nickname(host.ip, value)
            save_state(self.state)
            host.nickname = self.state.nickname_for(host.ip)
            roles.apply_role(host)
            self._refresh_hosts(keep_ip=host.ip)
            if host.nickname:
                self.log_line(f"Nickname {host.ip} → {host.nickname}", "ok")
            else:
                self.log_line(f"Cleared nickname for {host.ip}", "info")

        self.push_screen(NicknameModal(host.ip, host.nickname), on_close)

    def action_toggle_watch(self) -> None:
        if self._watching:
            self._watching = False
            if self._watch_timer is not None:
                self._watch_timer.stop()
                self._watch_timer = None
            self.log_line("Watch off.", "info")
            self._set_title(self._lan_title())
            return

        self._watching = True
        self._watch_left = self.state.watch_interval_s
        if self._watch_timer is not None:
            self._watch_timer.stop()
        self._watch_timer = self.set_interval(1.0, self._tick_watch)
        self.log_line(
            f"Watch on — rediscover every {self.state.watch_interval_s}s when idle.",
            "ok",
        )
        self._set_title(self._lan_title())

    def _tick_watch(self) -> None:
        if not self._watching:
            return
        self._watch_left -= 1
        if self._watch_left <= 0:
            self._watch_left = self.state.watch_interval_s
            if not self._busy:
                self.action_discover()
        self._set_title(self._lan_title())

    def action_toggle_map(self) -> None:
        self._show_map = not self._show_map
        ports = self.query_one("#ports", PortTable)
        lan_map = self.query_one("#lan-map", LanMap)
        title = self.query_one("#bottom-title", Static)
        if self._show_map:
            ports.add_class("-hidden")
            lan_map.remove_class("-hidden")
            title.update("LAN MAP  ·  m ports  ·  grouped by role")
            self._refresh_map()
            self.log_line("Showing LAN map.", "info")
        else:
            lan_map.add_class("-hidden")
            ports.remove_class("-hidden")
            title.update("PORTS  ·  o open  ·  m map  ·  c copy")
            self.log_line("Showing ports.", "info")

    def action_copy_host(self) -> None:
        host = self._selected_host()
        if not host:
            self.log_line("Select a host first.", "warn")
            return
        text = export_mod.host_card(host)
        if export_mod.copy_to_clipboard(text):
            self.log_line(f"Copied host card for {host.ip}", "ok")
        else:
            self.log_line("Clipboard unavailable — card follows:", "warn")
            for line in text.strip().splitlines():
                self.log_line(line, "cmd")

    def action_copy_all(self) -> None:
        hosts = self._host_list()
        if not hosts:
            self.log_line("No hosts to copy.", "warn")
            return
        text = export_mod.hosts_summary(hosts)
        if export_mod.copy_to_clipboard(text):
            self.log_line(f"Copied summary for {len(hosts)} host(s)", "ok")
        else:
            self.log_line("Clipboard unavailable — summary follows:", "warn")
            for line in text.strip().splitlines()[:40]:
                self.log_line(line, "cmd")


def run() -> None:
    NethopApp().run()
