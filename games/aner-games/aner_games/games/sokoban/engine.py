"""Sokoban rules — no TUI."""

from __future__ import annotations

from dataclasses import dataclass, field

from .levels import LEVELS
from .models import Pos


def parse_level(text: str) -> tuple[int, int, set[Pos], set[Pos], set[Pos], Pos]:
    rows = [ln.rstrip() for ln in text.strip("\n").splitlines()]
    height = len(rows)
    width = max(len(r) for r in rows)
    walls: set[Pos] = set()
    crates: set[Pos] = set()
    targets: set[Pos] = set()
    player = (1, 1)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                walls.add((x, y))
            elif ch == "@":
                player = (x, y)
            elif ch == "+":
                player = (x, y)
                targets.add((x, y))
            elif ch == "$":
                crates.add((x, y))
            elif ch == "*":
                crates.add((x, y))
                targets.add((x, y))
            elif ch == ".":
                targets.add((x, y))
    return width, height, walls, crates, targets, player


@dataclass
class SokobanGame:
    level: int = 0
    width: int = 0
    height: int = 0
    walls: set[Pos] = field(default_factory=set)
    crates: set[Pos] = field(default_factory=set)
    targets: set[Pos] = field(default_factory=set)
    player: Pos = (1, 1)
    undo: list[tuple[Pos, frozenset[Pos]]] = field(default_factory=list)
    won: bool = False

    def __post_init__(self) -> None:
        if not self.walls:
            self.load(self.level)

    def load(self, index: int) -> None:
        self.level = index % len(LEVELS)
        w, h, walls, crates, targets, player = parse_level(LEVELS[self.level])
        self.width, self.height = w, h
        self.walls, self.crates, self.targets = walls, crates, targets
        self.player = player
        self.undo = []
        self.won = crates == targets

    def _snapshot(self) -> None:
        self.undo.append((self.player, frozenset(self.crates)))

    def revert(self) -> None:
        if not self.undo:
            return
        self.player, crates = self.undo.pop()
        self.crates = set(crates)
        self.won = self.crates == self.targets

    def move(self, dx: int, dy: int) -> bool:
        if self.won:
            return False
        px, py = self.player
        nxt = (px + dx, py + dy)
        if nxt in self.walls:
            return False
        if nxt in self.crates:
            beyond = (nxt[0] + dx, nxt[1] + dy)
            if beyond in self.walls or beyond in self.crates:
                return False
            self._snapshot()
            self.crates.remove(nxt)
            self.crates.add(beyond)
            self.player = nxt
        else:
            self._snapshot()
            self.player = nxt
        self.won = self.crates == self.targets
        return True
