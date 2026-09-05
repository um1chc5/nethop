"""Named nmap scan profiles (common learner-friendly sets)."""

from __future__ import annotations

from .models import ScanProfile

PROFILES: list[ScanProfile] = [
    ScanProfile(
        id="fast",
        title="Fast ports (-F)",
        nmap_args=["-F"],
        description="Top 100 TCP ports — quick overview.",
    ),
    ScanProfile(
        id="common",
        title="Common ports",
        nmap_args=["-p", "21,22,23,25,53,80,110,139,443,445,3306,3389,8080,8443"],
        description="Frequent admin / web / file-share ports.",
    ),
    ScanProfile(
        id="version",
        title="Service versions (-sV)",
        nmap_args=["-sV", "-F"],
        description="Detect service/version on top ports.",
    ),
    ScanProfile(
        id="scripts",
        title="Default scripts (-sC)",
        nmap_args=["-sC", "-sV", "-F"],
        description="Safe default NSE scripts + versions.",
    ),
    ScanProfile(
        id="os",
        title="OS detect (-O)",
        nmap_args=["-O", "-F"],
        description="OS fingerprint (often needs admin/root).",
        needs_admin=True,
    ),
    ScanProfile(
        id="aggressive",
        title="Aggressive (-A)",
        nmap_args=["-A"],
        description="OS + versions + scripts + traceroute. Slow.",
        needs_admin=True,
    ),
]


def get_profile(profile_id: str) -> ScanProfile:
    for p in PROFILES:
        if p.id == profile_id:
            return p
    raise KeyError(profile_id)
