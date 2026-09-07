"""Snake types and board constants — no rules, no TUI."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

WIDTH = 28
HEIGHT = 16

Pos = tuple[int, int]

OPPOSITE: dict[Pos, Pos] = {
    (1, 0): (-1, 0),
    (-1, 0): (1, 0),
    (0, 1): (0, -1),
    (0, -1): (0, 1),
}


@dataclass
class SnakeState:
    width: int = WIDTH
    height: int = HEIGHT
    body: list[Pos] = field(default_factory=list)
    direction: Pos = (1, 0)
    pending: Pos | None = None
    food: Pos | None = None
    alive: bool = True
    won: bool = False
    score: int = 0
    rng: random.Random = field(default_factory=random.Random)
