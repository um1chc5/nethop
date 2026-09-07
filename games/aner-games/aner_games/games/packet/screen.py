"""Packet chase Textual screen."""

from __future__ import annotations

from textual.binding import Binding
from textual.timer import Timer

from ...play import ESC_MENU, Q_MENU, RESTART, SKIN, PlayScreen, styled
from .engine import PacketGame
from .models import HEIGHT, WIDTH


class PacketScreen(PlayScreen):
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
        Binding("r", "restart", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.game = PacketGame()
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
        if not g.alive:
            self._hud().update(t.fault.format(msg=f"SCORE {g.score}"))
        else:
            self._hud().update(t.run.format(msg=f"SCORE {g.score}  ·  LIVES {g.lives}"))
        pkts = {(p.x, p.y) for p in g.packets}
        lines: list[str] = []
        for y in range(HEIGHT):
            row: list[str] = []
            for x in range(WIDTH):
                pos = (x, y)
                if pos == g.player:
                    row.append(styled(*look.head))
                elif pos in pkts:
                    row.append(styled(*look.food))
                else:
                    row.append(styled(*look.empty))
            lines.append("".join(row))
        self._board().update("\n".join(lines))

    def action_north(self) -> None:
        self.game.move_player(0, -1)
        self._paint()

    def action_south(self) -> None:
        self.game.move_player(0, 1)
        self._paint()

    def action_west(self) -> None:
        self.game.move_player(-1, 0)
        self._paint()

    def action_east(self) -> None:
        self.game.move_player(1, 0)
        self._paint()

    def action_restart(self) -> None:
        self.game = PacketGame()
        self._paint()
        self._arm()
