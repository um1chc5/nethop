"""Shared TUI helpers for game screens (no game rules)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from .themes import CASSETTE, Theme


def styled(ch: str, style: str) -> str:
    return f"[{style}]{ch}[/{style}]"


Q_MENU = Binding("q", "back", "Menu", show=True)
ESC_MENU = Binding("escape", "back", "Menu", show=True)
SKIN = Binding("t", "cycle_theme", "Skin", show=True)
RESTART = Binding("space", "restart", "Restart", show=True)


class PlayScreen(Screen[None]):
    DEFAULT_CSS = """
    PlayScreen {
        layout: vertical;
        overflow: hidden;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="game-wrap"):
            yield Static("", id="game-hud")
            yield Static("", id="game-board")
        yield Footer()

    def on_theme(self) -> None:
        self._paint()

    def action_cycle_theme(self) -> None:
        cycle = getattr(self.app, "action_cycle_theme", None)
        if callable(cycle):
            cycle()

    def action_back(self) -> None:
        self.app.pop_screen()

    def _skin(self) -> Theme:
        theme = getattr(self.app, "skin", None)
        if isinstance(theme, Theme):
            return theme
        return CASSETTE

    def _hud(self) -> Static:
        return self.query_one("#game-hud", Static)

    def _board(self) -> Static:
        return self.query_one("#game-board", Static)

    def _paint(self) -> None:
        raise NotImplementedError
