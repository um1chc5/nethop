"""Tetris types and shapes."""

from __future__ import annotations

WIDTH = 10
HEIGHT = 20
Pos = tuple[int, int]
KINDS = ("I", "O", "T", "S", "Z", "J", "L")


def _rot(cells: tuple[Pos, ...]) -> tuple[Pos, ...]:
    return tuple(sorted((y, 3 - x) for x, y in cells))


def _rots(base: tuple[Pos, ...]) -> tuple[tuple[Pos, ...], ...]:
    cur = tuple(sorted(base))
    out = [cur]
    for _ in range(3):
        cur = _rot(cur)
        out.append(cur)
    return tuple(out)


O_CELLS: tuple[Pos, ...] = ((1, 0), (2, 0), (1, 1), (2, 1))

SHAPES: dict[str, tuple[tuple[Pos, ...], ...]] = {
    "I": _rots(((0, 1), (1, 1), (2, 1), (3, 1))),
    "O": (O_CELLS,) * 4,
    "T": _rots(((1, 0), (0, 1), (1, 1), (2, 1))),
    "S": _rots(((1, 0), (2, 0), (0, 1), (1, 1))),
    "Z": _rots(((0, 0), (1, 0), (1, 1), (2, 1))),
    "J": _rots(((0, 0), (0, 1), (1, 1), (2, 1))),
    "L": _rots(((2, 0), (0, 1), (1, 1), (2, 1))),
}

COLORS = {k: i + 1 for i, k in enumerate(KINDS)}
