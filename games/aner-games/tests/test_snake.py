"""Snake movement rules (no TUI)."""

from __future__ import annotations

import random

from aner_games.games.snake.engine import SnakeGame


def test_eats_food_and_grows() -> None:
    g = SnakeGame(rng=random.Random(0))
    g.body = [(5, 5), (4, 5), (3, 5)]
    g.direction = (1, 0)
    g.food = (6, 5)
    length = len(g.body)
    g.tick()
    assert g.alive
    assert g.score == 1
    assert len(g.body) == length + 1
    assert g.body[0] == (6, 5)


def test_hits_wall() -> None:
    g = SnakeGame(rng=random.Random(1))
    g.body = [(0, 5), (1, 5)]
    g.direction = (-1, 0)
    g.food = (10, 10)
    g.tick()
    assert not g.alive


def test_no_instant_reverse() -> None:
    g = SnakeGame(rng=random.Random(2))
    g.body = [(5, 5), (4, 5), (3, 5)]
    g.direction = (1, 0)
    g.set_direction(-1, 0)
    assert g.pending is None
    g.set_direction(0, -1)
    assert g.pending == (0, -1)


if __name__ == "__main__":
    test_eats_food_and_grows()
    test_hits_wall()
    test_no_instant_reverse()
    print("ok")
