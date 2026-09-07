"""Mini ASCII LAN map grouped by role."""

from __future__ import annotations

from collections import defaultdict

from textual.widgets import Static

from ..models import Host


class LanMap(Static):
    """Read-only topology-ish view of discovered hosts."""

    DEFAULT_CSS = """
    LanMap {
        height: 1fr;
        padding: 0 1;
        background: #0d1218;
        color: #c8d0d8;
        overflow-y: auto;
    }
    """

    def set_map(
        self,
        hosts: list[Host],
        *,
        you_ip: str = "",
        gateway: str | None = None,
        iface: str = "",
        cidr: str = "",
    ) -> None:
        lines: list[str] = []
        header = "LAN map"
        if iface or cidr:
            header += f"  ·  {iface + ' ' if iface else ''}{cidr}".rstrip()
        lines.append(f"[b cyan]{header}[/]")
        you = you_ip or "you"
        if gateway:
            lines.append(f"  [green]you[/] ({you})")
            lines.append("       │")
            lines.append(f"       └─ [yellow]gateway[/] {gateway}")
            lines.append("              │")
            stem = "              ├─ "
            stem_last = "              └─ "
        else:
            lines.append(f"  [green]you[/] ({you})")
            lines.append("       │")
            stem = "       ├─ "
            stem_last = "       └─ "

        by_role: dict[str, list[Host]] = defaultdict(list)
        for h in hosts:
            by_role[h.role or "unknown"].append(h)

        roles = sorted(by_role.keys(), key=lambda r: (r == "unknown", r))
        if not roles:
            lines.append(f"{stem_last}[dim](no hosts — press d to discover)[/dim]")
            self.update("\n".join(lines))
            return

        for ri, role in enumerate(roles):
            group = sorted(
                by_role[role],
                key=lambda h: tuple(int(x) for x in h.ip.split(".")),
            )
            is_last_role = ri == len(roles) - 1
            role_branch = stem_last if is_last_role else stem
            lines.append(f"{role_branch}[b]{role}[/b] ({len(group)})")
            if gateway:
                child_pad = "                 " if is_last_role else "              │  "
            else:
                child_pad = "          " if is_last_role else "       │  "
            for hi, h in enumerate(group):
                last = hi == len(group) - 1
                branch = "└─ " if last else "├─ "
                label = h.nickname or h.hostname or "—"
                mark = "*" if h.is_new else " "
                lines.append(
                    f"{child_pad}{branch}{mark}[cyan]{h.ip}[/]  {label}"
                )

        self.update("\n".join(lines))
