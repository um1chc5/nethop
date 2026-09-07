"""Scan-action list widget."""

from __future__ import annotations

from textual.widgets import ListItem, ListView, Static

from ..models import ScanProfile
from ..scans import PROFILES

_SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


class ActionList(ListView):
    """Scan profile picker with optional running indicator."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._running_id: str | None = None
        self._spin_i = 0
        self._labels: dict[str, Static] = {}
        self._items: dict[str, ListItem] = {}

    def on_mount(self) -> None:
        for profile in PROFILES:
            label = Static(self._format(profile), classes="action-item")
            item = ListItem(label, id=f"action-{profile.id}")
            self._labels[profile.id] = label
            self._items[profile.id] = item
            self.append(item)

    def selected_profile(self) -> ScanProfile | None:
        if self.index is None or self.index < 0 or self.index >= len(PROFILES):
            return None
        return PROFILES[self.index]

    def set_running(self, profile_id: str | None) -> None:
        self._running_id = profile_id
        self._spin_i = 0
        self._render_all()

    def tick_spinner(self) -> None:
        if not self._running_id:
            return
        self._spin_i = (self._spin_i + 1) % len(_SPIN)
        self._render_all()

    def _format(self, profile: ScanProfile) -> str:
        admin = " ⚠ admin" if profile.needs_admin else ""
        if profile.id == self._running_id:
            spin = _SPIN[self._spin_i]
            return (
                f"[b cyan]{spin} {profile.title}[/] [b yellow]RUNNING[/]{admin}\n"
                f"[dim]{profile.description}[/dim]"
            )
        return f"[b]{profile.title}[/b]{admin}\n[dim]{profile.description}[/dim]"

    def _render_all(self) -> None:
        for profile in PROFILES:
            label = self._labels.get(profile.id)
            item = self._items.get(profile.id)
            if label is None or item is None:
                continue
            label.update(self._format(profile))
            if profile.id == self._running_id:
                item.add_class("-running")
            else:
                item.remove_class("-running")
