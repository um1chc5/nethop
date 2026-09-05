"""Local interface / subnet detection (stdlib + Windows-friendly fallbacks)."""

from __future__ import annotations

import ipaddress
import platform
import re
import socket
import subprocess
from typing import Optional

from .models import NetInfo


def _primary_ipv4() -> Optional[str]:
    """Best-effort local IPv4 used for outbound traffic."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if not ip.startswith("127."):
                return ip
    except OSError:
        pass

    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."):
                return ip
    except OSError:
        pass
    return None


def _mask_from_ipconfig(ip: str) -> Optional[str]:
    """Parse IPv4 subnet mask next to `ip` from `ipconfig` (Windows)."""
    try:
        out = subprocess.check_output(
            ["ipconfig"],
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    blocks = re.split(r"\r?\n\r?\n", out)
    for block in blocks:
        if ip not in block:
            continue
        m = re.search(
            r"Subnet Mask[^:]*:\s*(\d+\.\d+\.\d+\.\d+)",
            block,
            re.IGNORECASE,
        )
        if m:
            return m.group(1)
    return None


def _mask_from_ip(ip: str) -> Optional[str]:
    system = platform.system()
    if system == "Windows":
        return _mask_from_ipconfig(ip)

    # Linux / macOS: `ip -o -f inet addr` or ifconfig
    try:
        out = subprocess.check_output(
            ["ip", "-o", "-f", "inet", "addr"],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for line in out.splitlines():
            if ip in line:
                m = re.search(rf"{re.escape(ip)}/(\d+)", line)
                if m:
                    prefix = int(m.group(1))
                    net = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
                    return str(net.netmask)
    except (OSError, subprocess.CalledProcessError, ValueError):
        pass
    return None


def detect_lan(default_prefix: int = 24) -> NetInfo:
    """
    Detect the likely LAN CIDR for the primary interface.

    Falls back to /24 when the mask cannot be resolved (common home Wi‑Fi).
    """
    ip = _primary_ipv4()
    if not ip:
        raise RuntimeError("Could not detect a local IPv4 address")

    mask = _mask_from_ip(ip)
    if mask:
        network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
    else:
        network = ipaddress.IPv4Network(f"{ip}/{default_prefix}", strict=False)

    return NetInfo(
        ip=ip,
        cidr=str(network),
        netmask=str(network.netmask),
    )
