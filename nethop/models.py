"""Domain models for discovered hosts and ports."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Port:
    number: int
    protocol: str = "tcp"
    state: str = "open"
    service: str = ""
    product: str = ""
    version: str = ""

    @property
    def label(self) -> str:
        bits = [f"{self.number}/{self.protocol}"]
        if self.service:
            bits.append(self.service)
        detail = " ".join(x for x in (self.product, self.version) if x).strip()
        if detail:
            bits.append(detail)
        return "  ".join(bits)

    @property
    def is_webby(self) -> bool:
        name = self.service.lower()
        if any(k in name for k in ("http", "https", "ssl/http", "http-proxy")):
            return True
        return self.number in {80, 443, 8000, 8008, 8080, 8443, 8888, 3000, 5000, 5173}


@dataclass
class Host:
    ip: str
    hostname: str = ""
    status: str = "up"
    mac: str = ""
    vendor: str = ""
    os_guess: str = ""
    ports: list[Port] = field(default_factory=list)
    last_scan: str = ""
    nickname: str = ""
    role: str = ""
    is_new: bool = False

    @property
    def display_name(self) -> str:
        if self.nickname:
            return f"{self.ip}  ({self.nickname})"
        if self.hostname:
            return f"{self.ip}  ({self.hostname})"
        return self.ip

    @property
    def label_name(self) -> str:
        return self.nickname or self.hostname or "—"

    @property
    def summary(self) -> str:
        parts: list[str] = []
        if self.role:
            parts.append(self.role)
        if self.vendor:
            parts.append(self.vendor)
        if self.mac:
            parts.append(self.mac)
        if self.os_guess:
            parts.append(self.os_guess)
        open_n = sum(1 for p in self.ports if p.state == "open")
        if open_n:
            parts.append(f"{open_n} open port{'s' if open_n != 1 else ''}")
        return " · ".join(parts) if parts else "—"


@dataclass
class ScanProfile:
    id: str
    title: str
    nmap_args: list[str]
    description: str
    needs_admin: bool = False


@dataclass
class NetInfo:
    ip: str
    cidr: str
    interface: str = ""
    netmask: str = ""


@dataclass
class LogLine:
    text: str
    level: str = "info"  # info | ok | warn | err | cmd
