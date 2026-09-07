"""Tetris lock and line clear (no TUI)."""

from __future__ import annotations

import random

from aner_games.games.tetris.engine import Piece, TetrisGame
from aner_games.games.tetris.models import HEIGHT, WIDTH


def test_piece_falls_then_locks() -> None:
    g = TetrisGame(rng=random.Random(0))
    g.grid = [[0] * WIDTH for _ in range(HEIGHT)]
    g.piece = Piece(kind="O", rot=0, x=0, y=HEIGHT - 3)
    g.alive = True
    g.tick()
    assert g.piece is not None
    assert g.piece.y == HEIGHT - 2
    g.tick()
    assert any(g.grid[HEIGHT - 1]) or any(g.grid[HEIGHT - 2])


def test_clear_full_line() -> None:
    g = TetrisGame(rng=random.Random(1))
    g.piece = Piece(kind="O", rot=0, x=3, y=0)
    g.grid = [[0] * WIDTH for _ in range(HEIGHT)]
    g.grid[-1] = [1] * WIDTH
    n = g.clear_lines()
    assert n == 1
    assert g.lines == 1
    assert g.score == 100
    assert g.grid[-1] == [0] * WIDTH


def test_rotate_stays_in_bounds() -> None:
    g = TetrisGame(rng=random.Random(2))
    g.grid = [[0] * WIDTH for _ in range(HEIGHT)]
    g.piece = Piece(kind="I", rot=0, x=0, y=0)
    g.rotate()
    assert g.piece is not None
    assert g.valid(g.piece)


if __name__ == "__main__":
    test_piece_falls_then_locks()
    test_clear_full_line()
    test_rotate_stays_in_bounds()
    print("ok")
