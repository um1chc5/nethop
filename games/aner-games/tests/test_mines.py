"""Minesweeper reveal rules (no TUI)."""

from __future__ import annotations

import random

from aner_games.games.mines.engine import MinesGame
from aner_games.games.mines.models import HEIGHT, MINE_COUNT, WIDTH


def test_first_click_is_safe() -> None:
    g = MinesGame(rng=random.Random(0), cursor=(0, 0))
    g.reveal()
    assert not g.dead
    assert g.mines is not None
    assert (0, 0) not in g.mines
    assert (0, 0) in g.revealed
    assert len(g.mines) == MINE_COUNT


def test_flag_blocks_reveal() -> None:
    g = MinesGame(rng=random.Random(1), cursor=(1, 1))
    g.toggle_flag()
    g.reveal()
    assert not g.revealed
    assert (1, 1) in g.flags


def test_mine_kills() -> None:
    g = MinesGame(rng=random.Random(2), cursor=(0, 0))
    g.mines = {(0, 0)}
    g.reveal()
    assert g.dead
    assert not g.won


def test_win_when_all_clear() -> None:
    g = MinesGame(rng=random.Random(3), cursor=(0, 0))
    g.mines = {(WIDTH - 1, HEIGHT - 1)}
    g.reveal()
    if not g.won:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (x, y) not in g.mines and (x, y) not in g.revealed:
                    g.cursor = (x, y)
                    g.reveal()
    assert g.won
    assert not g.dead


if __name__ == "__main__":
    test_first_click_is_safe()
    test_flag_blocks_reveal()
    test_mine_kills()
    test_win_when_all_clear()
    print("ok")
