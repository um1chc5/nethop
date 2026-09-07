"""Host list table widget."""

from __future__ import annotations

from textual.widgets import DataTable

from ..models import Host


class HostTable(DataTable):
    """Selectable list of LAN hosts."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns("IP", "Name", "Role", "Vendor / MAC", "Ports")
        self._ips: list[str] = []

    def set_hosts(self, hosts: list[Host], selected_ip: str | None = None) -> None:
        self.clear()
        self._ips = []
        target_row = 0
        for i, host in enumerate(hosts):
            open_n = sum(1 for p in host.ports if p.state == "open")
            vendor = host.vendor or host.mac or "—"
            ip_col = f"*{host.ip}" if host.is_new else host.ip
            self.add_row(
                ip_col,
                host.label_name,
                host.role or "—",
                vendor,
                str(open_n) if open_n else "—",
                key=host.ip,
            )
            self._ips.append(host.ip)
            if selected_ip and host.ip == selected_ip:
                target_row = i
        if hosts:
            self.move_cursor(row=target_row)

    def selected_ip(self) -> str | None:
        if not self._ips:
            return None
        if self.cursor_row is None or self.cursor_row < 0:
            return None
        if self.cursor_row >= len(self._ips):
            return None
        return self._ips[self.cursor_row]
