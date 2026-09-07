"""Markdown host cards + best-effort clipboard copy (no extra deps)."""

from __future__ import annotations

import platform
import shutil
import subprocess
from typing import Iterable

from .models import Host


def host_card(host: Host) -> str:
    name = host.nickname or host.hostname or host.ip
    lines = [
        f"### {name}",
        f"- **IP:** `{host.ip}`",
    ]
    if host.nickname:
        lines.append(f"- **Nickname:** {host.nickname}")
    if host.hostname:
        lines.append(f"- **Hostname:** {host.hostname}")
    if host.role:
        lines.append(f"- **Role:** `{host.role}`")
    if host.vendor:
        lines.append(f"- **Vendor:** {host.vendor}")
    if host.mac:
        lines.append(f"- **MAC:** `{host.mac}`")
    if host.os_guess:
        lines.append(f"- **OS guess:** {host.os_guess}")
    open_ports = [p for p in host.ports if p.state == "open"]
    if open_ports:
        lines.append("- **Open ports:**")
        for p in sorted(open_ports, key=lambda x: (x.protocol, x.number)):
            detail = p.service or p.product or ""
            extra = f" — {detail}" if detail else ""
            lines.append(f"  - `{p.number}/{p.protocol}`{extra}")
    else:
        lines.append("- **Open ports:** _(none scanned yet)_")
    return "\n".join(lines) + "\n"


def hosts_summary(hosts: Iterable[Host]) -> str:
    items = list(hosts)
    chunks = [f"# nethop LAN summary ({len(items)} hosts)\n"]
    for h in items:
        chunks.append(host_card(h))
    return "\n".join(chunks)


def copy_to_clipboard(text: str) -> bool:
    """Copy text using OS tools. Returns True on success."""
    system = platform.system()
    try:
        if system == "Darwin" and shutil.which("pbcopy"):
            subprocess.run(
                ["pbcopy"],
                input=text.encode("utf-8"),
                check=True,
            )
            return True
        if system == "Windows":
            # clip.exe expects UTF-16LE on many Windows builds
            subprocess.run(
                ["clip"],
                input=text.encode("utf-16-le"),
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return True
        if shutil.which("wl-copy"):
            subprocess.run(
                ["wl-copy"],
                input=text.encode("utf-8"),
                check=True,
            )
            return True
        if shutil.which("xclip"):
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text.encode("utf-8"),
                check=True,
            )
            return True
        if shutil.which("xsel"):
            subprocess.run(
                ["xsel", "--clipboard", "--input"],
                input=text.encode("utf-8"),
                check=True,
            )
            return True
    except (OSError, subprocess.CalledProcessError):
        return False
    return False
