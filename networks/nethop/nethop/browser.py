"""Open likely web services in the default browser."""

from __future__ import annotations

import webbrowser

from .models import Port


def url_for(ip: str, port: Port) -> str:
    """Build a browser URL for a host:port (HTTP/HTTPS heuristics)."""
    name = port.service.lower()
    https_hints = ("https", "ssl", "tls", "http-proxy")
    if port.number == 443 or any(h in name for h in https_hints):
        if port.number == 443:
            return f"https://{ip}"
        return f"https://{ip}:{port.number}"
    if port.number == 80:
        return f"http://{ip}"
    return f"http://{ip}:{port.number}"


def open_in_browser(ip: str, port: Port) -> str:
    url = url_for(ip, port)
    webbrowser.open(url, new=2)
    return url
