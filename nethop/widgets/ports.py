"""Open-ports table widget."""

from __future__ import annotations

from textual.widgets import DataTable

from ..models import Port


class PortTable(DataTable):
    """Open ports for the selected host."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns("Port", "Service", "Product", "Open?")
        self._ports: list[Port] = []

    def set_ports(self, ports: list[Port]) -> None:
        self.clear()
        self._ports = []
        for port in ports:
            web = "browser" if port.is_webby else ""
            self.add_row(
                f"{port.number}/{port.protocol}",
                port.service or "—",
                " ".join(x for x in (port.product, port.version) if x) or "—",
                web or "—",
                key=f"{port.protocol}:{port.number}",
            )
            self._ports.append(port)
        if ports:
            self.move_cursor(row=0)

    def selected_port(self) -> Port | None:
        if not self._ports or self.cursor_row is None or self.cursor_row < 0:
            return None
        if self.cursor_row >= len(self._ports):
            return None
        return self._ports[self.cursor_row]
