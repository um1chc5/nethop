"""Named nmap scan profiles (common learner-friendly sets)."""

from __future__ import annotations

from .models import ScanProfile

# Dev / app ranges often used on tech LANs (Vite, Next, Spring, Tomcat, …)
_DEV_WEB_PORTS = (
    "3000,3001,3002,4000,4173,4200,4321,5000,5001,5173,5174,"
    "8000,8008,8080,8081,8443,8888,9000,9090"
)

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
        id="dev-web",
        title="Dev web ports",
        nmap_args=["-p", _DEV_WEB_PORTS],
        description="Vite 5173, Next/React 3000, Flask 5000, 8xxx proxies, …",
    ),
    ScanProfile(
        id="range-3xxx",
        title="Range 3xxx (3000–3999)",
        nmap_args=["-p", "3000-3999"],
        description="Wide scan: Node/React/Next and other 3xxx app ports.",
    ),
    ScanProfile(
        id="range-5xxx",
        title="Range 5xxx (5000–5999)",
        nmap_args=["-p", "5000-5999"],
        description="Wide scan: Flask/Vite (5173) and other 5xxx app ports.",
    ),
    ScanProfile(
        id="range-8xxx",
        title="Range 8xxx (8000–8999)",
        nmap_args=["-p", "8000-8999"],
        description="Wide scan: proxies, Tomcat, alt-HTTP on 8xxx.",
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
