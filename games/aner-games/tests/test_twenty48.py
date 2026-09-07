"""2048 movement rules (no TUI)."""

from __future__ import annotations

import random

from aner_games.games.twenty48.engine import Twenty48Game


def test_merges_up() -> None:
    g = Twenty48Game(rng=random.Random(0))
    g.grid = [[2, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    g.won = False
    g.alive = True
    assert g.move(0, -1)
    assert g.grid[0][0] == 4
    assert g.score == 4


def test_no_move_when_blocked() -> None:
    g = Twenty48Game(rng=random.Random(1))
    g.grid = [[2, 4, 8, 16], [32, 64, 128, 256], [2, 4, 8, 16], [32, 64, 128, 256]]
    g.alive = True
    before = [row[:] for row in g.grid]
    assert not g.move(-1, 0)
    assert g.grid == before


def test_win_at_2048() -> None:
    g = Twenty48Game(rng=random.Random(2))
    g.grid = [[1024, 1024, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    g.alive = True
    g.move(-1, 0)
    assert g.won
    assert any(v == 2048 for row in g.grid for v in row)


def test_dead_when_full() -> None:
    g = Twenty48Game(rng=random.Random(3))
    g.grid = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    g.alive = True
    assert not g._has_moves()
    g.grid[0][0] = 4
    assert g._has_moves()


if __name__ == "__main__":
    test_merges_up()
    test_no_move_when_blocked()
    test_win_at_2048()
    test_dead_when_full()
    print("ok")
