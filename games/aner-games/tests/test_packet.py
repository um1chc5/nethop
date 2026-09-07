"""Packet chase catch / leak (no TUI)."""

from __future__ import annotations

import random

from aner_games.games.packet.engine import PacketGame
from aner_games.games.packet.models import HEIGHT, Packet


def test_catch_scores() -> None:
    g = PacketGame(rng=random.Random(0), player=(4, 3))
    g.packets = [Packet(x=4, y=3, dx=1)]
    g._catch()
    assert g.score == 10
    assert not g.packets


def test_leak_costs_life() -> None:
    g = PacketGame(rng=random.Random(1), player=(0, 0), lives=1)
    g.packets = [Packet(x=0, y=1, dx=-1)]
    g.tick()
    assert not g.alive
    assert g.lives == 0


def test_player_clamped() -> None:
    g = PacketGame(rng=random.Random(2), player=(0, 0))
    g.move_player(-1, -1)
    assert g.player == (0, 0)
    g.move_player(1, 1)
    assert g.player == (1, 1)
    assert HEIGHT >= 2


if __name__ == "__main__":
    test_catch_scores()
    test_leak_costs_life()
    test_player_clamped()
    print("ok")
