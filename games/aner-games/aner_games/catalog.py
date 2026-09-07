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
    from .games.mines.screen import MinesScreen
    from .games.packet.screen import PacketScreen
    from .games.snake.screen import SnakeScreen
    from .games.sokoban.screen import SokobanScreen
    from .games.tetris.screen import TetrisScreen
    from .games.twenty48.screen import Twenty48Screen
    from .games.typerace.screen import TypeRaceScreen
    from .games.wordle.screen import WordleScreen

    return [
        GameEntry("snake", "Snake", "Eat food, grow, stay on the board.", "↑↓←→ / WASD", SnakeScreen),
        GameEntry("twenty48", "2048", "Slide and merge tiles to 2048.", "↑↓←→ / WASD", Twenty48Screen),
        GameEntry("tetris", "Tetris", "Stack pieces, clear lines.", "←→  ↓  ↑ rot  space drop", TetrisScreen),
        GameEntry("mines", "Minesweeper", "Open cells, flag mines.", "↑↓←→  enter dig  f flag", MinesScreen),
        GameEntry("sokoban", "Sokoban", "Push crates onto the marks.", "↑↓←→  u undo  n next", SokobanScreen),
        GameEntry("wordle", "Wordle", "Guess the five-letter word.", "type  enter  esc menu", WordleScreen),
        GameEntry("typerace", "Typing race", "Type the quote, watch WPM.", "type  esc menu", TypeRaceScreen),
        GameEntry("packet", "Packet chase", "Catch packets on a fake LAN.", "↑↓←→ / WASD", PacketScreen),
    ]
