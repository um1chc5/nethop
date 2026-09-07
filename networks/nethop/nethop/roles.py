"""Heuristics to guess host roles on tech-company LANs."""

from __future__ import annotations

import re
from typing import Iterable

from .models import Host, Port

# (role, port numbers) — first match in this ordered list wins for ports
_PORT_RULES: list[tuple[str, frozenset[int]]] = [
    ("k8s", frozenset({6443, 10250, 10255, 10256, 2379, 2380})),
    ("docker", frozenset({2375, 2376, 2377})),
    ("elasticsearch", frozenset({9200, 9300})),
    ("mongo", frozenset({27017})),
    ("redis", frozenset({6379})),
    ("postgres", frozenset({5432})),
    ("mysql", frozenset({3306})),
    ("observability", frozenset({3000, 9090, 5601, 16686})),
    ("rdp", frozenset({3389})),
    ("windows-file", frozenset({445, 139})),
    ("printer", frozenset({9100, 631})),
    ("snmp-device", frozenset({161})),
]

_HOST_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("k8s", re.compile(r"k8s|kube|kubernetes", re.I)),
    ("bastion", re.compile(r"bastion|jump|jumphost", re.I)),
    ("esxi", re.compile(r"esxi|vmware", re.I)),
    ("proxmox", re.compile(r"proxmox|pve", re.I)),
    ("nas", re.compile(r"\bnas\b|synology|true?nas|qnap", re.I)),
    ("pihole", re.compile(r"pi[-_]?hole", re.I)),
    ("docker", re.compile(r"docker|portainer", re.I)),
    ("ci", re.compile(r"jenkins|gitlab|github-runner|buildkite|drone", re.I)),
]


def _open_ports(ports: Iterable[Port]) -> set[int]:
    return {p.number for p in ports if p.state == "open"}


def guess_role(host: Host) -> str:
    """Return a short role label, or empty string if unknown."""
    text = " ".join(
        x for x in (host.hostname, host.nickname, host.vendor, host.os_guess) if x
    )
    for role, pat in _HOST_PATTERNS:
        if text and pat.search(text):
            return role

    open_n = _open_ports(host.ports)
    if not open_n:
        return host.role or ""

    for role, ports in _PORT_RULES:
        if open_n & ports:
            return role

    # SSH-only box
    if open_n == {22} or (22 in open_n and len(open_n) <= 2):
        return "ssh"

    # Generic web
    if open_n & {80, 443, 8080, 8443}:
        return "web"

    return host.role or ""


def apply_role(host: Host) -> Host:
    role = guess_role(host)
    if role:
        host.role = role
    return host
