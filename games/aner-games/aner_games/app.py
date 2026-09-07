"""aner-games launcher — pick a title, play, return to the list."""

from __future__ import annotations

import time
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Static

from . import __version__
from .catalog import GameEntry, all_games
from .logo import render_logo
from .state import load_theme, save_theme
from .themes import Theme, get_theme, next_theme_id

CSS_PATH = Path(__file__).with_name("app.tcss")


class AnerGamesApp(App[None]):
    TITLE = "aner-games"
    CSS_PATH = CSS_PATH
    BINDINGS = [
        Binding("enter", "play", "Play", show=True),
        Binding("t", "cycle_theme", "Skin", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._games: list[GameEntry] = all_games()
        self.skin_id = load_theme()
        self._last_theme_swap = 0.0

    @property
    def skin(self) -> Theme:
        return get_theme(self.skin_id)

    def compose(self) -> ComposeResult:
        yield Static("", id="title-bar")
        yield Static("", id="chrome")
        yield Static("", id="scan")
        with Horizontal(id="body"):
            with Vertical(id="menu-pane"):
                yield Static("", id="pane-title", classes="pane-title")
                yield DataTable(id="games")
            with Vertical(id="logo-pane"):
                yield Static("", id="logo")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#games", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("Game", "Controls", "About")
        for g in self._games:
            table.add_row(g.title, g.keys, g.blurb, key=g.id)
        if self._games:
            table.move_cursor(row=0)
        table.focus()
        self.apply_theme()

    def apply_theme(self) -> None:
        for cls in ("-cassette", "-phosphor", "-cyberpunk", "-tactical"):
            self.remove_class(cls)
        self.add_class(self.skin.class_name)
        t = self.skin
        self.query_one("#title-bar", Static).update(t.title.format(ver=__version__))
        self.query_one("#chrome", Static).update(t.chrome)
        self.query_one("#scan", Static).update(t.scan)
        self.query_one("#pane-title", Static).update(t.pane)
        self.query_one("#logo", Static).update(render_logo(t))
        for screen in self.screen_stack:
            on_theme = getattr(screen, "on_theme", None)
            if callable(on_theme):
                on_theme()

    def action_cycle_theme(self) -> None:
        now = time.monotonic()
        if now - self._last_theme_swap < 0.15:
            return
        self._last_theme_swap = now
        self.skin_id = next_theme_id(self.skin_id)
        save_theme(self.skin_id)
        self.apply_theme()

    def _selected(self) -> GameEntry | None:
        table = self.query_one("#games", DataTable)
        if table.cursor_row is None or table.cursor_row < 0:
            return None
        if table.cursor_row >= len(self._games):
            return None
        return self._games[table.cursor_row]

    def action_play(self) -> None:
        if len(self.screen_stack) > 1:
            return
        game = self._selected()
        if not game:
            return
        self.push_screen(game.screen())

    def on_data_table_row_selected(self, _event: DataTable.RowSelected) -> None:
        self.action_play()


def run() -> None:
    AnerGamesApp().run()
