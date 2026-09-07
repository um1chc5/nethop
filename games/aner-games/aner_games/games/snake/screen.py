"""Snake Textual screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import Footer, Static

from ...themes import Theme
from .engine import SnakeGame


def _cell(ch: str, style: str) -> str:
    return f"[{style}]{ch}[/{style}]"


class SnakeScreen(Screen[None]):
    DEFAULT_CSS = """
    SnakeScreen {
        layout: vertical;
        overflow: hidden;
    }
    """
    BINDINGS = [
        Binding("q", "back", "Menu", show=True),
        Binding("escape", "back", "Menu", show=False),
        Binding("t", "cycle_theme", "Skin", show=True),
        Binding("up", "north", "Up", show=False),
        Binding("w", "north", show=False),
        Binding("down", "south", "Down", show=False),
        Binding("s", "south", show=False),
        Binding("left", "west", "Left", show=False),
        Binding("a", "west", show=False),
        Binding("right", "east", "Right", show=False),
        Binding("d", "east", show=False),
        Binding("space", "restart", "Restart", show=True),
        Binding("r", "restart", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.game = SnakeGame()
        self._timer: Timer | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="snake-wrap"):
            yield Static("", id="snake-hud")
            yield Static("", id="snake-board")
        yield Footer()

    def on_mount(self) -> None:
        self._paint()
        self._arm_timer()

    def on_unmount(self) -> None:
        if self._timer is not None:
            self._timer.stop()
            self._timer = None

    def on_theme(self) -> None:
        self._paint()

    def action_cycle_theme(self) -> None:
        cycle = getattr(self.app, "action_cycle_theme", None)
        if callable(cycle):
            cycle()

    def _theme(self) -> Theme:
        theme = getattr(self.app, "skin", None)
        if isinstance(theme, Theme):
            return theme
        from ...themes import CASSETTE

        return CASSETTE

    def _arm_timer(self) -> None:
        if self._timer is not None:
            self._timer.stop()
        self._timer = self.set_interval(self.game.speed_s(), self._tick)

    def _tick(self) -> None:
        if not self.game.alive:
            return
        self.game.tick()
        self._paint()
        if self.game.alive:
            self._arm_timer()

    def _paint(self) -> None:
        g = self.game
        t = self._theme()
        look = t.snake
        hud = self.query_one("#snake-hud", Static)
        board = self.query_one("#snake-board", Static)
        if g.won:
            hud.update(t.snake_win.format(score=g.score))
        elif not g.alive:
            hud.update(t.snake_over.format(score=g.score))
        else:
            hud.update(t.snake_play.format(score=g.score))

        occ = {p: i for i, p in enumerate(g.body)}
        lines: list[str] = []
        for y in range(g.height):
            row: list[str] = []
            for x in range(g.width):
                pos = (x, y)
                if g.food is not None and pos == g.food and g.alive:
                    row.append(_cell(*look.food))
                elif pos in occ:
                    row.append(_cell(*(look.head if occ[pos] == 0 else look.body)))
                else:
                    row.append(_cell(*look.empty))
            lines.append("".join(row))
        board.update("\n".join(lines))

    def action_north(self) -> None:
        self.game.set_direction(0, -1)

    def action_south(self) -> None:
        self.game.set_direction(0, 1)

    def action_west(self) -> None:
        self.game.set_direction(-1, 0)

    def action_east(self) -> None:
        self.game.set_direction(1, 0)

    def action_restart(self) -> None:
        self.game = SnakeGame()
        self._paint()
        self._arm_timer()

    def action_back(self) -> None:
        self.app.pop_screen()
