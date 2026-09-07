"""Typing race Textual screen. Escape returns to the menu; letters type the quote."""

from __future__ import annotations

import time

from textual import events

from ...play import ESC_MENU, PlayScreen, styled
from .engine import TypeRaceGame


class TypeRaceScreen(PlayScreen):
    BINDINGS = [ESC_MENU]

    def __init__(self) -> None:
        super().__init__()
        self.game = TypeRaceGame()

    def on_mount(self) -> None:
        self._paint()

    def on_key(self, event: events.Key) -> None:
        g = self.game
        if g.done:
            if event.key == "t":
                self.action_cycle_theme()
                event.stop()
            elif event.key in ("space", "r"):
                self.action_restart()
                event.stop()
            return
        ch = event.character
        if not ch:
            return
        g.feed(ch, time.monotonic())
        event.stop()
        self._paint()

    def _paint(self) -> None:
        g = self.game
        t = self._skin()
        look = t.snake
        now = time.monotonic()
        wpm = g.wpm(now)
        if g.done:
            self._hud().update(t.lock.format(msg=f"{wpm:.0f} WPM  ·  {g.errors} ERR  ·  SPACE"))
        else:
            self._hud().update(t.run.format(msg=f"{wpm:.0f} WPM  ·  {g.errors} ERR  ·  ESC MENU"))
        parts: list[str] = []
        for i, ch in enumerate(g.prompt):
            if i < len(g.typed):
                parts.append(styled(ch, look.head[1]))
            elif i == len(g.typed):
                parts.append(styled(ch, "reverse " + look.body[1]))
            else:
                parts.append(styled(ch, look.empty[1]))
        self._board().update("".join(parts))

    def action_restart(self) -> None:
        self.game = TypeRaceGame()
        self._paint()
