"""2048 Textual screen."""

from __future__ import annotations

from textual.binding import Binding

from ...play import ESC_MENU, Q_MENU, RESTART, SKIN, PlayScreen, styled
from .engine import Twenty48Game
from .models import SIZE


class Twenty48Screen(PlayScreen):
    BINDINGS = [
        Q_MENU,
        ESC_MENU,
        SKIN,
        RESTART,
        Binding("up", "north", "Up", show=False),
        Binding("w", "north", show=False),
        Binding("down", "south", "Down", show=False),
        Binding("s", "south", show=False),
        Binding("left", "west", "Left", show=False),
        Binding("a", "west", show=False),
        Binding("right", "east", "Right", show=False),
        Binding("d", "east", show=False),
        Binding("r", "restart", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.game = Twenty48Game()

    def on_mount(self) -> None:
        self._paint()

    def _paint(self) -> None:
        g = self.game
        t = self._skin()
        look = t.snake
        if g.won:
            self._hud().update(t.lock.format(msg=f"TILE {g.score}"))
        elif not g.alive:
            self._hud().update(t.fault.format(msg=f"SCORE {g.score}"))
        else:
            self._hud().update(t.run.format(msg=f"SCORE {g.score}"))
        lines: list[str] = []
        for y in range(SIZE):
            row: list[str] = []
            for x in range(SIZE):
                v = g.grid[y][x]
                if v == 0:
                    row.append(styled(" ·  ", look.empty[1]))
                else:
                    style = look.head[1] if v >= 64 else look.body[1] if v >= 8 else look.food[1]
                    row.append(styled(f"{v:^4}", style))
            lines.append("".join(row))
        self._board().update("\n".join(lines))

    def action_north(self) -> None:
        self.game.move(0, -1)
        self._paint()

    def action_south(self) -> None:
        self.game.move(0, 1)
        self._paint()

    def action_west(self) -> None:
        self.game.move(-1, 0)
        self._paint()

    def action_east(self) -> None:
        self.game.move(1, 0)
        self._paint()

    def action_restart(self) -> None:
        self.game = Twenty48Game()
        self._paint()
