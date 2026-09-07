"""Persistent nethop state (nicknames, iface preference, presence snapshot)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def state_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "nethop" / "state.json"


@dataclass
class AppState:
    nicknames: dict[str, str] = field(default_factory=dict)
    last_iface: str = ""
    last_cidr: str = ""
    watch_interval_s: int = 120
    last_hosts: list[str] = field(default_factory=list)

    def nickname_for(self, ip: str) -> str:
        return self.nicknames.get(ip, "")

    def set_nickname(self, ip: str, name: str) -> None:
        name = name.strip()
        if name:
            self.nicknames[ip] = name
        else:
            self.nicknames.pop(ip, None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nicknames": dict(self.nicknames),
            "last_iface": self.last_iface,
            "last_cidr": self.last_cidr,
            "watch_interval_s": self.watch_interval_s,
            "last_hosts": list(self.last_hosts),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppState:
        interval = data.get("watch_interval_s", 120)
        try:
            interval_i = int(interval)
        except (TypeError, ValueError):
            interval_i = 120
        nicknames = data.get("nicknames") or {}
        if not isinstance(nicknames, dict):
            nicknames = {}
        last_hosts = data.get("last_hosts") or []
        if not isinstance(last_hosts, list):
            last_hosts = []
        return cls(
            nicknames={str(k): str(v) for k, v in nicknames.items()},
            last_iface=str(data.get("last_iface") or ""),
            last_cidr=str(data.get("last_cidr") or ""),
            watch_interval_s=max(30, interval_i),
            last_hosts=[str(x) for x in last_hosts],
        )


def load_state() -> AppState:
    path = state_path()
    if not path.is_file():
        return AppState()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return AppState()
        return AppState.from_dict(data)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return AppState()


def save_state(state: AppState) -> None:
    path = state_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(state.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass
