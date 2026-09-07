"""Local interface / subnet detection (stdlib + Windows-friendly fallbacks)."""

from __future__ import annotations

import ipaddress
import platform
import re
import socket
import subprocess
from dataclasses import dataclass
from typing import Optional

from .models import NetInfo

_TUNNEL_RE = re.compile(
    r"warp|tun|tap|vpn|utun|wg|docker|veth|br-|cni|flannel|calico|virbr|vmnet|tailscale|zt",
    re.IGNORECASE,
)


@dataclass
class IfaceCandidate:
    name: str
    ip: str
    prefix: int
    cidr: str
    score: int = 0


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


def _score_candidate(c: IfaceCandidate, preferred_ip: str | None) -> int:
    score = 0
    if c.ip.startswith("127."):
        return -1000
    if c.prefix >= 31:
        score -= 80
    elif 16 <= c.prefix <= 24:
        score += 40
    elif c.prefix < 16:
        score += 10
    else:
        score += 5

    try:
        addr = ipaddress.IPv4Address(c.ip)
        if addr.is_private:
            score += 30
        if addr.is_link_local:
            score -= 50
    except ValueError:
        score -= 100

    if _TUNNEL_RE.search(c.name):
        score -= 60

    if preferred_ip and c.ip == preferred_ip:
        # Prefer outbound iface only when it looks like a real LAN.
        if c.prefix < 31 and not _TUNNEL_RE.search(c.name):
            score += 25
        else:
            score -= 20

    c.score = score
    return score


def list_ipv4_ifaces() -> list[IfaceCandidate]:
    """Enumerate IPv4 interfaces with CIDR."""
    system = platform.system()
    found: list[IfaceCandidate] = []

    if system == "Windows":
        found.extend(_list_windows_ifaces())
    else:
        found.extend(_list_posix_ifaces())

    preferred = _primary_ipv4()
    for c in found:
        _score_candidate(c, preferred)
    found.sort(key=lambda x: (-x.score, x.name, x.ip))
    return found


def _list_posix_ifaces() -> list[IfaceCandidate]:
    out_lines: list[str] = []
    try:
        out_lines = subprocess.check_output(
            ["ip", "-o", "-f", "inet", "addr"],
            text=True,
            encoding="utf-8",
            errors="replace",
        ).splitlines()
    except (OSError, subprocess.CalledProcessError):
        try:
            raw = subprocess.check_output(
                ["ifconfig"],
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            return _parse_ifconfig(raw)
        except (OSError, subprocess.CalledProcessError):
            return []

    results: list[IfaceCandidate] = []
    for line in out_lines:
        # 2: eth0    inet 192.168.1.10/24 brd ...
        m = re.match(
            r"\d+:\s+(\S+)\s+inet\s+(\d+\.\d+\.\d+\.\d+)/(\d+)",
            line,
        )
        if not m:
            continue
        name, ip, prefix_s = m.group(1), m.group(2), m.group(3)
        name = name.split("@", 1)[0]
        if ip.startswith("127."):
            continue
        prefix = int(prefix_s)
        try:
            net = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
        except ValueError:
            continue
        results.append(
            IfaceCandidate(name=name, ip=ip, prefix=prefix, cidr=str(net))
        )
    return results


def _parse_ifconfig(raw: str) -> list[IfaceCandidate]:
    results: list[IfaceCandidate] = []
    blocks = re.split(r"\n(?=\S)", raw)
    for block in blocks:
        name_m = re.match(r"^(\S+):", block)
        if not name_m:
            continue
        name = name_m.group(1)
        inet = re.search(
            r"inet (?:addr:)?(\d+\.\d+\.\d+\.\d+).*?(?:netmask|Mask[:\s]+)(\S+)",
            block,
            re.IGNORECASE | re.DOTALL,
        )
        cidr_m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/(\d+)", block)
        if cidr_m:
            ip = cidr_m.group(1)
            prefix = int(cidr_m.group(2))
        elif inet:
            ip = inet.group(1)
            mask = inet.group(2)
            if mask.startswith("0x"):
                try:
                    mask_int = int(mask, 16)
                    mask = str(ipaddress.IPv4Address(mask_int))
                except ValueError:
                    continue
            try:
                net = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
                prefix = net.prefixlen
            except ValueError:
                continue
        else:
            continue
        if ip.startswith("127."):
            continue
        try:
            net = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
        except ValueError:
            continue
        results.append(
            IfaceCandidate(name=name, ip=ip, prefix=prefix, cidr=str(net))
        )
    return results


def _list_windows_ifaces() -> list[IfaceCandidate]:
    try:
        out = subprocess.check_output(
            ["ipconfig"],
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    results: list[IfaceCandidate] = []
    blocks = re.split(r"\r?\n\r?\n", out)
    for block in blocks:
        name_m = re.search(
            r"^(?:Ethernet|Wireless|Wi-?Fi|PPP|Tunnel|VPN|Unknown)[^\r\n]*adapter\s+(.+):",
            block,
            re.IGNORECASE | re.MULTILINE,
        )
        if not name_m:
            # Fallback: "adapter Foo:"
            name_m = re.search(r"adapter\s+(.+):", block, re.IGNORECASE)
        if not name_m:
            continue
        name = name_m.group(1).strip()
        ip_m = re.search(
            r"IPv4 Address[^:]*:\s*(\d+\.\d+\.\d+\.\d+)",
            block,
            re.IGNORECASE,
        )
        mask_m = re.search(
            r"Subnet Mask[^:]*:\s*(\d+\.\d+\.\d+\.\d+)",
            block,
            re.IGNORECASE,
        )
        if not ip_m or not mask_m:
            continue
        ip = ip_m.group(1)
        if ip.startswith("127."):
            continue
        try:
            net = ipaddress.IPv4Network(f"{ip}/{mask_m.group(1)}", strict=False)
        except ValueError:
            continue
        results.append(
            IfaceCandidate(
                name=name,
                ip=ip,
                prefix=net.prefixlen,
                cidr=str(net),
            )
        )
    return results


def default_gateway() -> Optional[str]:
    """Best-effort IPv4 default gateway."""
    system = platform.system()
    try:
        if system == "Windows":
            out = subprocess.check_output(
                ["route", "print", "0.0.0.0"],
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            for line in out.splitlines():
                m = re.search(
                    r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)",
                    line,
                )
                if m:
                    return m.group(1)
        else:
            out = subprocess.check_output(
                ["ip", "route", "show", "default"],
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            m = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", out)
            if m:
                return m.group(1)
            out = subprocess.check_output(
                ["route", "-n", "get", "default"],
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            m = re.search(r"gateway:\s*(\d+\.\d+\.\d+\.\d+)", out, re.IGNORECASE)
            if m:
                return m.group(1)
    except (OSError, subprocess.CalledProcessError):
        pass
    return None


def detect_lan(
    default_prefix: int = 24,
    preferred_iface: str = "",
    preferred_cidr: str = "",
) -> NetInfo:
    """
    Detect the likely LAN CIDR, skipping /32 tunnels when a real LAN exists.
    """
    candidates = list_ipv4_ifaces()

    if preferred_cidr:
        for c in candidates:
            if c.cidr == preferred_cidr or (
                preferred_iface and c.name == preferred_iface and c.cidr == preferred_cidr
            ):
                return NetInfo(
                    ip=c.ip,
                    cidr=c.cidr,
                    interface=c.name,
                    netmask=str(ipaddress.IPv4Network(c.cidr).netmask),
                )
        # User preference may still be valid even if iface rename
        try:
            net = ipaddress.IPv4Network(preferred_cidr, strict=False)
            # Find an IP on that network
            for c in candidates:
                if ipaddress.IPv4Address(c.ip) in net:
                    return NetInfo(
                        ip=c.ip,
                        cidr=str(net),
                        interface=c.name or preferred_iface,
                        netmask=str(net.netmask),
                    )
        except ValueError:
            pass

    if preferred_iface:
        matches = [c for c in candidates if c.name == preferred_iface]
        if matches:
            best = max(matches, key=lambda x: x.score)
            return NetInfo(
                ip=best.ip,
                cidr=best.cidr,
                interface=best.name,
                netmask=str(ipaddress.IPv4Network(best.cidr).netmask),
            )

    # Prefer non-tunnel, non-/32 candidates
    usable = [c for c in candidates if c.score > -40 and c.prefix < 31]
    if usable:
        best = usable[0]
        return NetInfo(
            ip=best.ip,
            cidr=best.cidr,
            interface=best.name,
            netmask=str(ipaddress.IPv4Network(best.cidr).netmask),
        )

    if candidates:
        best = candidates[0]
        return NetInfo(
            ip=best.ip,
            cidr=best.cidr,
            interface=best.name,
            netmask=str(ipaddress.IPv4Network(best.cidr).netmask),
        )

    # Last resort: outbound IP + resolved mask / default /24
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
        interface="",
        netmask=str(network.netmask),
    )
