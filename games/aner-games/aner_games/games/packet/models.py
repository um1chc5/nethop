"""Packet chase types."""

from __future__ import annotations

from dataclasses import dataclass

WIDTH = 22
HEIGHT = 10
LIVES = 3
Pos = tuple[int, int]


@dataclass
class Packet:
    x: int
    y: int
    dx: int
