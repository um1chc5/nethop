"""Wordle rules — no TUI."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .models import MAX_GUESSES, WORD_LEN, Mark
from .words import WORDS


def score_guess(secret: str, guess: str) -> list[tuple[str, Mark]]:
    secret = secret.lower()
    guess = guess.lower()
    leftover: list[str] = []
    marks: list[Mark | None] = [None] * WORD_LEN
    for i, ch in enumerate(guess):
        if ch == secret[i]:
            marks[i] = "hit"
        else:
            leftover.append(secret[i])
    for i, ch in enumerate(guess):
        if marks[i] is not None:
            continue
        if ch in leftover:
            leftover.remove(ch)
            marks[i] = "close"
        else:
            marks[i] = "miss"
    return [(guess[i], marks[i] or "miss") for i in range(WORD_LEN)]


@dataclass
class WordleGame:
    secret: str = ""
    guesses: list[str] = field(default_factory=list)
    row: str = ""
    won: bool = False
    over: bool = False
    message: str = ""
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        if not self.secret:
            self.secret = self.rng.choice(sorted(WORDS))

    def type_char(self, ch: str) -> None:
        if self.over or len(self.row) >= WORD_LEN:
            return
        if ch.isalpha():
            self.row += ch.lower()
            self.message = ""

    def backspace(self) -> None:
        if self.over:
            return
        self.row = self.row[:-1]
        self.message = ""

    def submit(self) -> None:
        if self.over:
            return
        if len(self.row) != WORD_LEN:
            self.message = "need 5 letters"
            return
        if self.row not in WORDS:
            self.message = "not in word list"
            return
        self.guesses.append(self.row)
        if self.row == self.secret:
            self.won = True
            self.over = True
        elif len(self.guesses) >= MAX_GUESSES:
            self.over = True
        self.row = ""
        self.message = ""
