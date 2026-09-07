"""Persisted launcher prefs."""

from __future__ import annotations

import json
import os
from pathlib import Path


def state_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "aner-games" / "state.json"


def load_theme() -> str:
    path = state_path()
    if not path.is_file():
        return "cassette"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        theme = str(data.get("theme") or "cassette")
        if theme in {"cassette", "phosphor", "cyberpunk", "tactical"}:
            return theme
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        pass
    return "cassette"


def save_theme(theme: str) -> None:
    path = state_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"theme": theme}, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
