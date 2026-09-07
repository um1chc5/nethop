"""Switchable visual languages for aner-games."""

from __future__ import annotations

from dataclasses import dataclass

THEMES = ("cassette", "phosphor", "cyberpunk", "tactical")


@dataclass(frozen=True)
class SnakeLook:
    food: tuple[str, str]
    head: tuple[str, str]
    body: tuple[str, str]
    empty: tuple[str, str]


@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    class_name: str
    title: str
    pane: str
    chrome: str
    scan: str
    snake_play: str
    snake_over: str
    snake_win: str
    snake: SnakeLook


def fullwidth(text: str) -> str:
    """Display-face: fullwidth Latin (terminal stand-in for a chunky CRT font)."""
    out: list[str] = []
    for ch in text:
        code = ord(ch)
        if ch == " ":
            out.append("\u3000")
        elif 33 <= code <= 126:
            out.append(chr(code + 0xFEE0))
        else:
            out.append(ch)
    return "".join(out)


def spaced(text: str) -> str:
    """Display-face: tracking, IBM-terminal style."""
    return " ".join(text)


CASSETTE = Theme(
    id="cassette",
    name="Cassette Futurism",
    class_name="-cassette",
    title=f" {fullwidth('DECK')}  v{{ver}}  ·  {fullwidth('TRACK')}  ·  t skin",
    pane="TAPE LIBRARY  ·  LATCH CARTRIDGE  ·  ENTER PLAY",
    chrome="● REC   CRT AMBER   ANALOG LATCH   WOW/FLUTTER 0.0",
    scan="░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒",
    snake_play="REEL  ·  SCORE {score}  ·  RUNNING",
    snake_over="TAPE EJECT  ·  SCORE {score}  ·  SPACE RECUE",
    snake_win="SPLICED  ·  SCORE {score}  ·  FULL REEL",
    snake=SnakeLook(
        food=("◎ ", "bold #FF9A40"),
        head=("██", "bold #FFF8C8"),
        body=("▓▓", "#FFD000"),
        empty=("░ ", "#2A1800"),
    ),
)

PHOSPHOR = Theme(
    id="phosphor",
    name="Cassette Phosphor",
    class_name="-phosphor",
    # Nostromo-style CRT: black field, bright terminal green, all-caps industrial.
    title=" DECK // GAMES   v{ver}   ·   t SKIN",
    pane="LIBRARY // SELECT TITLE   ·   ENTER PLAY",
    chrome="CRT P1   ·   SCANLINE 60   ·   CHROMA OFF   ·   REC .",
    scan="░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
    snake_play="STATUS // RUN   ·   SCORE {score}   ·   NORMAL █",
    snake_over="STATUS // FAULT   ·   SCORE {score}   ·   SPACE RECUE",
    snake_win="STATUS // LOCK   ·   SCORE {score}   ·   CLEAR",
    snake=SnakeLook(
        food=("+ ", "bold #CCFFCC"),
        head=("██", "bold #00FF41"),
        body=("▓▓", "#00EE44"),
        empty=("░ ", "#007A22"),
    ),
)

CYBERPUNK = Theme(
    id="cyberpunk",
    name="Sci-Fi Blue",
    class_name="-cyberpunk",
    # Black CRT + ice-blue bloom (bright core, dim halo field).
    title=" NAV / GAMES  v{ver}  ·  t SKIN",
    pane="DIRECTORY // GAMES   ·   ENTER RUN",
    chrome="LINK ▸ LIVE   BLOOM ▸ ON   CORE ▸ WHITE   FIELD ▸ CYAN",
    scan="▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░",
    snake_play="NAV  ·  SCORE {score}  ·  LIVE",
    snake_over="LOST  ·  SCORE {score}  ·  SPACE REBOOT",
    snake_win="LOCK  ·  SCORE {score}  ·  CLEAR",
    snake=SnakeLook(
        food=("* ", "bold #FFFFFF"),
        head=("██", "bold #FFFFFF"),
        body=("▒▒", "#88E0FF"),
        empty=("░ ", "#1A68B0"),
    ),
)

TACTICAL = Theme(
    id="tactical",
    name="Sci-Fi Red/White",
    class_name="-tactical",
    # Mission HUD: white data, glowing red banners, black field.
    title=" BROADCAST // GAMES   v{ver}   ·   t SKIN",
    pane="DIRECTORY // SELECT   ·   ENTER RUN",
    chrome="LINK ▸ LIVE   GRID ▸ ON   CHROMA ▸ RED   TARGET ▸ —",
    scan="░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
    snake_play="STATUS // LIVE   ·   SCORE {score}   ·   TRACKING",
    snake_over="STATUS // FAULT   ·   SCORE {score}   ·   SPACE REBOOT",
    snake_win="STATUS // LOCK   ·   SCORE {score}   ·   CLEAR",
    snake=SnakeLook(
        food=("+ ", "bold #FF6A6A"),
        head=("██", "bold #FFFFFF"),
        body=("▓▓", "#FF2020"),
        empty=("░ ", "#3A0000"),
    ),
)

_BY_ID = {t.id: t for t in (CASSETTE, PHOSPHOR, CYBERPUNK, TACTICAL)}


def get_theme(theme_id: str) -> Theme:
    return _BY_ID.get(theme_id, CASSETTE)


def next_theme_id(theme_id: str) -> str:
    idx = THEMES.index(theme_id) if theme_id in THEMES else 0
    return THEMES[(idx + 1) % len(THEMES)]
