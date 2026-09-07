# aner-games

Terminal game launcher: **list → select → play**. `q` in a game returns to the menu.

```bash
aner-games
```

Press **`t`** to cycle skins (saved under `~/.config/aner-games/`). Terminals can’t load real typefaces, so each skin uses a different **lettering + glyph set**.

| Skin | Palette | Lettering |
|---|---|---|
| **Cassette Futurism** | Black CRT + high-contrast amber | Fullwidth caps, inverted cursor |
| **Cassette Phosphor** | Black CRT + `#00FF41`, inverted green cursor | All-caps `SECTION // LABEL` |
| **Sci-Fi Blue** | White core, bright cyan `░` bloom field | Italic HUD readout |
| **Sci-Fi Red/White** | White data, red banners (mission HUD) | All-caps `BROADCAST //` |

## Games

Each title lives in `aner_games/games/<id>/` with the same split:

| File | Role |
|---|---|
| `models.py` | Types, constants, state dataclasses |
| `engine.py` | Rules (`tick`, input, win/lose) — no Textual |
| `screen.py` | Textual `Screen` only |
| `__init__.py` | Keep light (tests import engine without Textual) |

Extra files are fine (`levels.py`, `words.py`, …) when a game needs them.

| Game | Folder | Status | Notes |
|---|---|---|---|
| **Snake** | `games/snake/` | **Playable** | arrows / WASD · space restart · t skin · q menu |
| 2048 | `games/twenty48/` | Planned | Merge tiles, arrow keys |
| Tetris | `games/tetris/` | Planned | Stack pieces, line clears |
| Minesweeper | `games/mines/` | Planned | Grid + flags |
| Sokoban | `games/sokoban/` | Planned | Push crates, text levels |
| Wordle | `games/wordle/` | Planned | Five-letter guess |
| Typing race | `games/typerace/` | Planned | WPM on a quote |
| Packet chase | `games/packet/` | Planned | Catch packets on a fake LAN map |

The launcher menu only lists **Playable** titles.

## Install

From this monorepo:

```bash
pipx install --editable games/aner-games
# or from repo root:
pipx install --editable ./games/aner-games
```

From GitHub:

```bash
pipx install git+https://github.com/um1chc5/aner-toolkits.git#subdirectory=games/aner-games
```

## Add a game later

1. Create `aner_games/games/<id>/` with `models.py`, `engine.py`, and `screen.py`. Keep `__init__.py` light so tests can import the engine without Textual.
2. Register it in `aner_games/catalog.py` (`from .games.<id>.screen import …` in `all_games()`).
3. Mark it **Playable** in this README. The menu only lists Playable titles.
