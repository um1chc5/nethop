"""Playable games registered for the launcher."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from textual.screen import Screen


@dataclass(frozen=True)
class GameEntry:
    id: str
    title: str
    blurb: str
    keys: str
    screen: Callable[[], Screen]


def all_games() -> list[GameEntry]:
    from .games.snake.screen import SnakeScreen

    return [
        GameEntry(
            id="snake",
            title="Snake",
            blurb="Eat food, grow, stay on the board.",
            keys="↑↓←→ / WASD",
            screen=SnakeScreen,
        ),
    ]
