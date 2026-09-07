"""Tetris Textual screen."""

from __future__ import annotations

from textual.binding import Binding
from textual.timer import Timer

from ...play import ESC_MENU, Q_MENU, SKIN, PlayScreen, styled
from .engine import TetrisGame
from .models import HEIGHT, WIDTH


class TetrisScreen(PlayScreen):
    BINDINGS = [
        Q_MENU,
        ESC_MENU,
        SKIN,
        Binding("left", "west", "Left", show=False),
        Binding("a", "west", show=False),
        Binding("right", "east", "Right", show=False),
        Binding("d", "east", show=False),
        Binding("down", "drop", "Drop", show=False),
        Binding("s", "drop", show=False),
        Binding("up", "turn", "Rot", show=False),
        Binding("w", "turn", show=False),
        Binding("x", "turn", show=False),
        Binding("space", "slam", "Drop", show=True),
        Binding("r", "restart", "Restart", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.game = TetrisGame()
        self._timer: Timer | None = None

    def on_mount(self) -> None:
        self._paint()
        self._arm()

    def on_unmount(self) -> None:
        if self._timer is not None:
            self._timer.stop()
            self._timer = None

    def _arm(self) -> None:
        if self._timer is not None:
            self._timer.stop()
        self._timer = self.set_interval(self.game.speed_s(), self._tick)

    def _tick(self) -> None:
        if not self.game.alive:
            return
        self.game.tick()
        self._paint()
        if self.game.alive:
            self._arm()

    def _paint(self) -> None:
        g = self.game
        t = self._skin()
        look = t.snake
        styles = (look.empty[1], look.head[1], look.body[1], look.food[1], look.head[1], look.body[1], look.food[1], look.head[1])
        if not g.alive:
            self._hud().update(t.fault.format(msg=f"LINES {g.lines}  SCORE {g.score}"))
        else:
            nxt = g.next_kind
            self._hud().update(t.run.format(msg=f"NEXT {nxt}  LINES {g.lines}  SCORE {g.score}"))
        occ = {p: True for p in g.cells()}
        lines: list[str] = []
        for y in range(HEIGHT):
            row: list[str] = []
            for x in range(WIDTH):
                if (x, y) in occ:
                    row.append(styled("██", look.head[1]))
                elif g.grid[y][x]:
                    row.append(styled("▓▓", styles[g.grid[y][x] % len(styles)]))
                else:
                    row.append(styled("· ", look.empty[1]))
            lines.append("".join(row))
        self._board().update("\n".join(lines))

    def action_west(self) -> None:
        self.game.shift(-1)
        self._paint()

    def action_east(self) -> None:
        self.game.shift(1)
        self._paint()

    def action_drop(self) -> None:
        self.game.soft_drop()
        self._paint()

    def action_turn(self) -> None:
        self.game.rotate()
        self._paint()

    def action_slam(self) -> None:
        self.game.hard_drop()
        self._paint()

    def action_restart(self) -> None:
        self.game = TetrisGame()
        self._paint()
        self._arm()
