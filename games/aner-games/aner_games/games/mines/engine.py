"""Minesweeper rules — no TUI."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .models import HEIGHT, MINE_COUNT, WIDTH, Pos

_DELTAS = tuple((dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)


def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < WIDTH and 0 <= y < HEIGHT


def neighbors(x: int, y: int) -> list[Pos]:
    return [(x + dx, y + dy) for dx, dy in _DELTAS if in_bounds(x + dx, y + dy)]


@dataclass
class MinesGame:
    mines: set[Pos] | None = None
    revealed: set[Pos] = field(default_factory=set)
    flags: set[Pos] = field(default_factory=set)
    cursor: Pos = (WIDTH // 2, HEIGHT // 2)
    dead: bool = False
    won: bool = False
    rng: random.Random = field(default_factory=random.Random)

    @property
    def over(self) -> bool:
        return self.dead or self.won

    def adjacent(self, x: int, y: int) -> int:
        if self.mines is None:
            return 0
        return sum(1 for n in neighbors(x, y) if n in self.mines)

    def _plant(self, safe: Pos) -> None:
        cells = [
            (x, y)
            for y in range(HEIGHT)
            for x in range(WIDTH)
            if (x, y) != safe
        ]
        self.mines = set(self.rng.sample(cells, MINE_COUNT))

    def _check_win(self) -> None:
        if self.dead or self.mines is None:
            return
        if len(self.revealed) == WIDTH * HEIGHT - len(self.mines):
            self.won = True

    def move_cursor(self, dx: int, dy: int) -> None:
        if self.over:
            return
        x, y = self.cursor
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny):
            self.cursor = (nx, ny)

    def toggle_flag(self) -> None:
        if self.over:
            return
        pos = self.cursor
        if pos in self.revealed:
            return
        if pos in self.flags:
            self.flags.remove(pos)
        else:
            self.flags.add(pos)

    def reveal(self) -> None:
        if self.over:
            return
        pos = self.cursor
        if pos in self.flags:
            return
        if self.mines is None:
            self._plant(pos)
        assert self.mines is not None
        if pos in self.mines:
            self.dead = True
            self.revealed.add(pos)
            return
        stack = [pos]
        while stack:
            cx, cy = stack.pop()
            cur = (cx, cy)
            if cur in self.revealed or cur in self.flags:
                continue
            if not in_bounds(cx, cy):
                continue
            self.revealed.add(cur)
            if self.adjacent(cx, cy) == 0:
                stack.extend(neighbors(cx, cy))
        self._check_win()
