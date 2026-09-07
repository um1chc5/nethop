"""Tetris rules — no TUI."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .models import COLORS, HEIGHT, KINDS, SHAPES, WIDTH, Pos


def _empty() -> list[list[int]]:
    return [[0] * WIDTH for _ in range(HEIGHT)]


@dataclass
class Piece:
    kind: str
    rot: int = 0
    x: int = 3
    y: int = 0


@dataclass
class TetrisGame:
    grid: list[list[int]] = field(default_factory=_empty)
    piece: Piece | None = None
    next_kind: str = "T"
    score: int = 0
    lines: int = 0
    alive: bool = True
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        if self.piece is None and self.alive:
            self.next_kind = self.rng.choice(KINDS)
            self._spawn()

    def cells(self, piece: Piece | None = None) -> list[Pos]:
        p = piece if piece is not None else self.piece
        if p is None:
            return []
        return [(p.x + dx, p.y + dy) for dx, dy in SHAPES[p.kind][p.rot % 4]]

    def valid(self, piece: Piece) -> bool:
        for x, y in self.cells(piece):
            if x < 0 or x >= WIDTH or y >= HEIGHT:
                return False
            if y >= 0 and self.grid[y][x]:
                return False
        return True

    def _spawn(self) -> None:
        kind = self.next_kind
        self.next_kind = self.rng.choice(KINDS)
        spawned = Piece(kind=kind, rot=0, x=3, y=0)
        if not self.valid(spawned):
            self.piece = spawned
            self.alive = False
            return
        self.piece = spawned

    def clear_lines(self) -> int:
        kept = [row for row in self.grid if any(c == 0 for c in row)]
        n = HEIGHT - len(kept)
        if n:
            self.grid = [[0] * WIDTH for _ in range(n)] + kept
            self.lines += n
            self.score += (0, 100, 300, 500, 800)[n]
        return n

    def _lock(self) -> None:
        if self.piece is None:
            return
        color = COLORS[self.piece.kind]
        for x, y in self.cells():
            if 0 <= y < HEIGHT:
                self.grid[y][x] = color
        self.piece = None
        self.clear_lines()
        if self.alive:
            self._spawn()

    def tick(self) -> None:
        if not self.alive or self.piece is None:
            return
        nxt = Piece(self.piece.kind, self.piece.rot, self.piece.x, self.piece.y + 1)
        if self.valid(nxt):
            self.piece = nxt
        else:
            self._lock()

    def shift(self, dx: int) -> None:
        if not self.alive or self.piece is None:
            return
        nxt = Piece(self.piece.kind, self.piece.rot, self.piece.x + dx, self.piece.y)
        if self.valid(nxt):
            self.piece = nxt

    def rotate(self) -> None:
        if not self.alive or self.piece is None:
            return
        rot = (self.piece.rot + 1) % 4
        for kick in (0, -1, 1, -2, 2):
            nxt = Piece(self.piece.kind, rot, self.piece.x + kick, self.piece.y)
            if self.valid(nxt):
                self.piece = nxt
                return

    def soft_drop(self) -> None:
        if not self.alive or self.piece is None:
            return
        nxt = Piece(self.piece.kind, self.piece.rot, self.piece.x, self.piece.y + 1)
        if self.valid(nxt):
            self.piece = nxt
            self.score += 1
        else:
            self._lock()

    def hard_drop(self) -> None:
        if not self.alive or self.piece is None:
            return
        while self.piece is not None and self.alive:
            nxt = Piece(self.piece.kind, self.piece.rot, self.piece.x, self.piece.y + 1)
            if self.valid(nxt):
                self.piece = nxt
                self.score += 2
            else:
                self._lock()
                return

    def speed_s(self) -> float:
        return max(0.12, 0.55 - self.lines * 0.02)
