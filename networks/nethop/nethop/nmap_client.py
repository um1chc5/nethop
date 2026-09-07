"""Thin nmap subprocess wrapper with XML parsing."""

from __future__ import annotations

import platform
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from typing import Callable, Optional

from .models import Host, Port

LogFn = Callable[[str, str], None]
# Optional progress callback: fraction 0..1 or None if unknown, plus status text
ProgressFn = Callable[[Optional[float], str], None]

_PCT_RE = re.compile(r"About\s+([\d.]+)%\s+done", re.IGNORECASE)


class NmapError(RuntimeError):
    pass


def find_nmap() -> str:
    path = shutil.which("nmap")
    if path:
        return path
    # Common Windows install path when PATH is incomplete in some shells
    fallback = r"C:\Program Files (x86)\Nmap\nmap.exe"
    if platform.system() == "Windows":
        import os

        if os.path.isfile(fallback):
            return fallback
    raise NmapError(
        "nmap not found on PATH. Install from https://nmap.org/download.html"
    )


def _run(
    args: list[str],
    log: Optional[LogFn] = None,
    progress: Optional[ProgressFn] = None,
    stats_every: str = "1s",
) -> str:
    nmap = find_nmap()
    cmd = [nmap, "--stats-every", stats_every, *args, "-oX", "-"]
    if log:
        log(" ".join(cmd), "cmd")

    creationflags = 0
    if platform.system() == "Windows":
        creationflags = subprocess.CREATE_NO_WINDOW

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creationflags,
        )
    except OSError as exc:
        raise NmapError(f"Failed to run nmap: {exc}") from exc

    assert proc.stderr is not None
    assert proc.stdout is not None

    # Stream stderr for live stats while nmap runs; stdout is the full XML at end.
    err_lines: list[str] = []
    for line in proc.stderr:
        text = line.rstrip()
        if not text:
            continue
        err_lines.append(text)
        pct_match = _PCT_RE.search(text)
        if pct_match and progress:
            try:
                frac = float(pct_match.group(1)) / 100.0
            except ValueError:
                frac = None
            progress(frac, text)
        elif progress:
            progress(None, text)
        elif log and not text.lower().startswith("stats:"):
            # Non-stats noise only if no live progress UI
            log(text, "warn")

    stdout = proc.stdout.read()
    code = proc.wait()

    if code not in (0, 1):  # 1 = host down / no ports in some cases
        err = "\n".join(err_lines).strip() or stdout.strip()
        raise NmapError(err or f"nmap exited with code {code}")

    if progress:
        progress(1.0, "nmap finished")

    return stdout


def _parse_host(host_el: ET.Element) -> Optional[Host]:
    status_el = host_el.find("status")
    status = status_el.get("state", "unknown") if status_el is not None else "unknown"
    if status not in ("up", "unknown"):
        return None

    ip = ""
    mac = ""
    vendor = ""
    for addr in host_el.findall("address"):
        addrtype = addr.get("addrtype", "")
        if addrtype == "ipv4":
            ip = addr.get("addr", "")
        elif addrtype == "mac":
            mac = addr.get("addr", "")
            vendor = addr.get("vendor", "") or ""

    if not ip:
        return None

    hostname = ""
    hostnames = host_el.find("hostnames")
    if hostnames is not None:
        hn = hostnames.find("hostname")
        if hn is not None:
            hostname = hn.get("name", "") or ""

    os_guess = ""
    os_el = host_el.find("os")
    if os_el is not None:
        match = os_el.find("osmatch")
        if match is not None:
            os_guess = match.get("name", "") or ""

    ports: list[Port] = []
    ports_el = host_el.find("ports")
    if ports_el is not None:
        for port_el in ports_el.findall("port"):
            state_el = port_el.find("state")
            state = state_el.get("state", "") if state_el is not None else ""
            if state != "open":
                continue
            svc = port_el.find("service")
            ports.append(
                Port(
                    number=int(port_el.get("portid", "0")),
                    protocol=port_el.get("protocol", "tcp"),
                    state=state,
                    service=(svc.get("name", "") if svc is not None else "") or "",
                    product=(svc.get("product", "") if svc is not None else "") or "",
                    version=(svc.get("version", "") if svc is not None else "") or "",
                )
            )

    ports.sort(key=lambda p: (p.protocol, p.number))
    return Host(
        ip=ip,
        hostname=hostname,
        status=status,
        mac=mac,
        vendor=vendor,
        os_guess=os_guess,
        ports=ports,
    )


def parse_xml(xml_text: str) -> list[Host]:
    if not xml_text.strip():
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise NmapError(f"Invalid nmap XML: {exc}") from exc

    hosts: list[Host] = []
    for host_el in root.findall("host"):
        host = _parse_host(host_el)
        if host:
            hosts.append(host)
    hosts.sort(key=lambda h: tuple(int(x) for x in h.ip.split(".")))
    return hosts


def discover_hosts(
    cidr: str,
    log: Optional[LogFn] = None,
    progress: Optional[ProgressFn] = None,
) -> list[Host]:
    """Ping-style discovery (`nmap -sn`)."""
    xml = _run(["-sn", cidr], log=log, progress=progress)
    return parse_xml(xml)


def scan_host(
    ip: str,
    extra_args: list[str],
    log: Optional[LogFn] = None,
    progress: Optional[ProgressFn] = None,
) -> Host:
    """Run a port/OS/service scan against one host; merge into a Host model."""
    xml = _run([*extra_args, ip], log=log, progress=progress)
    hosts = parse_xml(xml)
    if not hosts:
        return Host(ip=ip, status="up", last_scan=" ".join(extra_args))
    host = hosts[0]
    host.last_scan = " ".join(extra_args)
    return host
