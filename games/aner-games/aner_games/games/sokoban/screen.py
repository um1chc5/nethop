"""Sokoban Textual screen."""

from __future__ import annotations

from textual.binding import Binding

from ...play import ESC_MENU, Q_MENU, RESTART, SKIN, PlayScreen, styled
from .engine import SokobanGame
from .levels import LEVELS


class SokobanScreen(PlayScreen):
    BINDINGS = [
        Q_MENU,
        ESC_MENU,
        SKIN,
        RESTART,
        Binding("up", "north", show=False),
        Binding("w", "north", show=False),
        Binding("down", "south", show=False),
        Binding("s", "south", show=False),
        Binding("left", "west", show=False),
        Binding("a", "west", show=False),
        Binding("right", "east", show=False),
        Binding("d", "east", show=False),
        Binding("u", "undo", "Undo", show=True),
        Binding("n", "next", "Next", show=True),
        Binding("r", "restart", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.game = SokobanGame()

    def on_mount(self) -> None:
        self._paint()

    def _paint(self) -> None:
        g = self.game
        t = self._skin()
        look = t.snake
        lvl = f"ROOM {g.level + 1}/{len(LEVELS)}"
        if g.won:
            self._hud().update(t.lock.format(msg=f"{lvl}  ·  N NEXT"))
        else:
            self._hud().update(t.run.format(msg=f"{lvl}  ·  U UNDO"))
        lines: list[str] = []
        for y in range(g.height):
            row: list[str] = []
            for x in range(g.width):
                pos = (x, y)
                if pos in g.walls:
                    row.append(styled("██", look.body[1]))
                elif pos == g.player:
                    row.append(styled("@ ", look.head[1]))
                elif pos in g.crates and pos in g.targets:
                    row.append(styled("* ", look.food[1]))
                elif pos in g.crates:
                    row.append(styled("$ ", look.food[1]))
                elif pos in g.targets:
                    row.append(styled(". ", look.head[1]))
                else:
                    row.append(styled("  ", look.empty[1]))
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

    def action_undo(self) -> None:
        self.game.revert()
        self._paint()

    def action_next(self) -> None:
        if self.game.won:
            self.game.load(self.game.level + 1)
            self._paint()

    def action_restart(self) -> None:
        self.game.load(self.game.level)
        self._paint()
