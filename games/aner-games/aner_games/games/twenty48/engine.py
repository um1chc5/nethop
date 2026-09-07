"""2048 rules — no TUI."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .models import SIZE, WIN_TILE, Grid


def _empty_grid() -> Grid:
    return [[0] * SIZE for _ in range(SIZE)]


def _slide_left(row: list[int]) -> tuple[list[int], int]:
    tiles = [v for v in row if v]
    merged: list[int] = []
    score = 0
    i = 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            val = tiles[i] * 2
            merged.append(val)
            score += val
            i += 2
        else:
            merged.append(tiles[i])
            i += 1
    merged.extend([0] * (SIZE - len(merged)))
    return merged, score


def _rotate_cw(grid: Grid) -> Grid:
    return [[grid[SIZE - 1 - x][y] for x in range(SIZE)] for y in range(SIZE)]


def _rotate_ccw(grid: Grid) -> Grid:
    return [[grid[x][SIZE - 1 - y] for x in range(SIZE)] for y in range(SIZE)]


def _copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


@dataclass
class Twenty48Game:
    grid: Grid = field(default_factory=_empty_grid)
    score: int = 0
    won: bool = False
    alive: bool = True
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        if all(v == 0 for row in self.grid for v in row):
            self._spawn()
            self._spawn()

    def _empties(self) -> list[tuple[int, int]]:
        return [
            (x, y)
            for y in range(SIZE)
            for x in range(SIZE)
            if self.grid[y][x] == 0
        ]

    def _spawn(self) -> None:
        spots = self._empties()
        if not spots:
            return
        x, y = self.rng.choice(spots)
        self.grid[y][x] = 4 if self.rng.random() < 0.1 else 2

    def _has_moves(self) -> bool:
        if self._empties():
            return True
        for y in range(SIZE):
            for x in range(SIZE):
                v = self.grid[y][x]
                if x + 1 < SIZE and self.grid[y][x + 1] == v:
                    return True
                if y + 1 < SIZE and self.grid[y + 1][x] == v:
                    return True
        return False

    def move(self, dx: int, dy: int) -> bool:
        if not self.alive or (dx, dy) not in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            return False
        work = _copy(self.grid)
        if dx == 1:
            work = [list(reversed(row)) for row in work]
        elif dy == -1:
            work = _rotate_ccw(work)
        elif dy == 1:
            work = _rotate_cw(work)
        gained = 0
        slid: Grid = []
        for row in work:
            nxt, add = _slide_left(row)
            slid.append(nxt)
            gained += add
        if dx == 1:
            slid = [list(reversed(row)) for row in slid]
        elif dy == -1:
            slid = _rotate_cw(slid)
        elif dy == 1:
            slid = _rotate_ccw(slid)
        if slid == self.grid:
            return False
        self.grid = slid
        self.score += gained
        if any(v >= WIN_TILE for row in self.grid for v in row):
            self.won = True
        self._spawn()
        if not self._has_moves():
            self.alive = False
        return True
