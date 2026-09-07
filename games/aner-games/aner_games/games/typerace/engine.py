"""Typing race rules — no TUI."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .quotes import QUOTES


@dataclass
class TypeRaceGame:
    prompt: str = ""
    typed: str = ""
    started: float | None = None
    done: bool = False
    errors: int = 0
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        if not self.prompt:
            self.prompt = self.rng.choice(QUOTES)

    def feed(self, ch: str, now: float) -> None:
        if self.done or not ch:
            return
        if self.started is None:
            self.started = now
        i = len(self.typed)
        if i >= len(self.prompt):
            self.done = True
            return
        if ch == self.prompt[i]:
            self.typed += ch
            if len(self.typed) == len(self.prompt):
                self.done = True
        else:
            self.errors += 1

    def wpm(self, now: float) -> float:
        if self.started is None:
            return 0.0
        mins = (now - self.started) / 60.0
        if mins <= 0:
            return 0.0
        return (len(self.typed) / 5.0) / mins
