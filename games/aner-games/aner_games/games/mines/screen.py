"""Minesweeper Textual screen."""

from __future__ import annotations

from textual.binding import Binding

from ...play import ESC_MENU, Q_MENU, SKIN, PlayScreen, styled
from .engine import MinesGame
from .models import HEIGHT, WIDTH


class MinesScreen(PlayScreen):
    BINDINGS = [
        Q_MENU,
        ESC_MENU,
        SKIN,
        Binding("up", "north", show=False),
        Binding("w", "north", show=False),
        Binding("down", "south", show=False),
        Binding("s", "south", show=False),
        Binding("left", "west", show=False),
        Binding("a", "west", show=False),
        Binding("right", "east", show=False),
        Binding("d", "east", show=False),
        Binding("enter", "dig", "Dig", show=True),
        Binding("space", "dig", show=False),
        Binding("f", "flag", "Flag", show=True),
        Binding("r", "restart", "Restart", show=True),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.game = MinesGame()

    def on_mount(self) -> None:
        self._paint()

    def _paint(self) -> None:
        g = self.game
        t = self._skin()
        look = t.snake
        flags = len(g.flags)
        if g.won:
            self._hud().update(t.lock.format(msg="CLEAR"))
        elif g.dead:
            self._hud().update(t.fault.format(msg="MINE"))
        else:
            self._hud().update(t.run.format(msg=f"FLAGS {flags}  ·  ENTER DIG  F FLAG"))
        lines: list[str] = []
        for y in range(HEIGHT):
            row: list[str] = []
            for x in range(WIDTH):
                pos = (x, y)
                cursor = pos == g.cursor
                if g.dead and g.mines and pos in g.mines:
                    ch, st = "* ", look.head[1]
                elif pos in g.flags:
                    ch, st = "▶ ", look.food[1]
                elif pos not in g.revealed:
                    ch, st = look.empty
                else:
                    n = g.adjacent(x, y)
                    ch = "  " if n == 0 else f"{n} "
                    st = look.body[1] if n else look.empty[1]
                cell = styled(ch, "reverse " + st if cursor else st)
                row.append(cell)
            lines.append("".join(row))
        self._board().update("\n".join(lines))

    def action_north(self) -> None:
        self.game.move_cursor(0, -1)
        self._paint()

    def action_south(self) -> None:
        self.game.move_cursor(0, 1)
        self._paint()

    def action_west(self) -> None:
        self.game.move_cursor(-1, 0)
        self._paint()

    def action_east(self) -> None:
        self.game.move_cursor(1, 0)
        self._paint()

    def action_dig(self) -> None:
        self.game.reveal()
        self._paint()

    def action_flag(self) -> None:
        self.game.toggle_flag()
        self._paint()

    def action_restart(self) -> None:
        self.game = MinesGame()
        self._paint()
