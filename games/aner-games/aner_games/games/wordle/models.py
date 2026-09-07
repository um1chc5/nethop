"""Wordle types."""

from __future__ import annotations

from typing import Literal

WORD_LEN = 5
MAX_GUESSES = 6
Mark = Literal["hit", "close", "miss"]
