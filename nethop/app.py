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
from . import nmap_client
from .models import Host, NetInfo
from .network import detect_lan
from .widgets import ActionList, HostTable, PortTable

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
        Binding("tab", "focus_next", "Focus", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.net: NetInfo | None = None
        self.hosts: dict[str, Host] = {}
        self._busy = False
        self._job_label = ""
        self._spin_i = 0
        self._spin_timer: Timer | None = None
        self._last_nmap_status = ""

    def compose(self) -> ComposeResult:
        yield Static("nethop", id="title-bar")
        with Horizontal(id="body"):
            with Vertical(id="left-pane"):
                yield Static("HOSTS  ·  click / ↑↓  ·  d discover", classes="pane-title")
                yield HostTable(id="hosts")
            with Vertical(id="right-pane"):
                yield Static("ACTIONS  ·  enter to run on selected host", classes="pane-title")
                yield ActionList(id="actions")
        with Vertical(id="lower"):
            with Vertical(id="bottom-pane"):
                yield Static("PORTS  ·  o open in browser (HTTP-ish)", classes="pane-title")
                yield PortTable(id="ports")
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
            self.net = detect_lan()
        except RuntimeError as exc:
            self.log_line(str(exc), "err")
            self._set_title("no LAN")
            return

        self._set_title(f"LAN {self.net.cidr}  ·  you {self.net.ip}")
        self.log_line(f"Local address {self.net.ip}  subnet {self.net.cidr}", "ok")
        self.log_line(
            "Press [b]d[/b] to discover hosts on your network (authorized use only).",
            "info",
        )
        self.action_discover()

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
            # total=None → pulsing bar until nmap reports a %
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
        """Called from worker thread — marshal to UI."""

        def apply() -> None:
            # Prefer short timing lines in the status strip
            short = text
            if len(short) > 90:
                short = short[:87] + "…"
            self._last_nmap_status = short
            self._render_job_status()
            bar = self.query_one("#job-progress", ProgressBar)
            if fraction is not None:
                bar.update(total=100, progress=max(0, min(100, fraction * 100)))
            # Mirror meaningful stats into the terminal
            if "about" in text.lower() and "%" in text:
                self.log_line(text, "cmd")

        self.call_from_thread(apply)

    def _on_nmap_log(self, msg: str, level: str = "info") -> None:
        self.call_from_thread(self.log_line, msg, level)

    def _host_list(self) -> list[Host]:
        return sorted(
            self.hosts.values(),
            key=lambda h: tuple(int(x) for x in h.ip.split(".")),
        )

    def _refresh_hosts(self, keep_ip: str | None = None) -> None:
        table = self.query_one("#hosts", HostTable)
        table.set_hosts(self._host_list(), selected_ip=keep_ip)
        self._sync_ports_from_selection()

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
        self._set_title(f"discovering {self.net.cidr}…")
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
                self._set_title(f"LAN {cidr}  ·  discover failed")
                return
            merged: dict[str, Host] = {}
            for host in found:
                prev = self.hosts.get(host.ip)
                if prev and prev.ports and not host.ports:
                    host.ports = prev.ports
                    host.os_guess = host.os_guess or prev.os_guess
                    host.last_scan = prev.last_scan
                merged[host.ip] = host
            self.hosts = merged
            self._refresh_hosts()
            self.log_line(f"Found {len(found)} host(s)", "ok")
            detail = f"LAN {cidr}  ·  {len(found)} hosts"
            if self.net:
                detail += f"  ·  you {self.net.ip}"
            self._set_title(detail)

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
        self._set_title(f"scanning {host.ip} · {profile.id}…")
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
                if self.net:
                    self._set_title(f"LAN {self.net.cidr}  ·  scan failed")
                return
            prev = self.hosts.get(ip)
            if prev:
                result.hostname = result.hostname or prev.hostname
                result.mac = result.mac or prev.mac
                result.vendor = result.vendor or prev.vendor
                if not result.os_guess:
                    result.os_guess = prev.os_guess
            self.hosts[ip] = result
            self._refresh_hosts(keep_ip=ip)
            open_n = len(result.ports)
            self.log_line(f"{title} done — {open_n} open port(s) on {ip}", "ok")
            if result.os_guess:
                self.log_line(f"OS guess: {result.os_guess}", "info")
            if self.net:
                self._set_title(
                    f"LAN {self.net.cidr}  ·  {len(self.hosts)} hosts  ·  last {ip}"
                )

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


def run() -> None:
    NethopApp().run()
