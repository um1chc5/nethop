"""Wordle Textual screen. Letters are typed; escape returns to the menu."""

from __future__ import annotations

from textual import events

from ...play import ESC_MENU, PlayScreen, styled
from .engine import WordleGame, score_guess
from .models import MAX_GUESSES, WORD_LEN


class WordleScreen(PlayScreen):
    BINDINGS = [ESC_MENU]

    def __init__(self) -> None:
        super().__init__()
        self.game = WordleGame()

    def on_mount(self) -> None:
        self._paint()

    def on_key(self, event: events.Key) -> None:
        g = self.game
        if g.over:
            if event.key == "t":
                self.action_cycle_theme()
                event.stop()
            elif event.key in ("space", "r"):
                self.action_restart()
                event.stop()
            return
        if event.key == "enter":
            g.submit()
            event.stop()
            self._paint()
            return
        if event.key == "backspace":
            g.backspace()
            event.stop()
            self._paint()
            return
        ch = event.character
        if ch and ch.isalpha():
            g.type_char(ch)
            event.stop()
            self._paint()

    def _paint(self) -> None:
        g = self.game
        t = self._skin()
        look = t.snake
        styles = {"hit": look.head[1], "close": look.food[1], "miss": look.empty[1]}
        if g.won:
            self._hud().update(t.lock.format(msg=g.secret.upper()))
        elif g.over:
            self._hud().update(t.fault.format(msg=g.secret.upper()))
        elif g.message:
            self._hud().update(t.fault.format(msg=g.message.upper()))
        else:
            self._hud().update(t.run.format(msg="TYPE  ·  ENTER SUBMIT  ·  ESC MENU"))
        rows: list[str] = []
        for i in range(MAX_GUESSES):
            if i < len(g.guesses):
                cells = score_guess(g.secret, g.guesses[i])
                rows.append("".join(styled(f" {ch.upper()} ", styles[mark]) for ch, mark in cells))
            elif i == len(g.guesses) and not g.over:
                cur = (g.row + " " * WORD_LEN)[:WORD_LEN]
                rows.append("".join(styled(f" {ch.upper()} ", look.body[1]) for ch in cur))
            else:
                rows.append("".join(styled(" · ", look.empty[1]) for _ in range(WORD_LEN)))
        self._board().update("\n".join(rows))

    def action_restart(self) -> None:
        self.game = WordleGame()
        self._paint()
