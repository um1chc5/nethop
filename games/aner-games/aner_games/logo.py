"""Center-piece ASCII mark for the launcher (terminals render this fine)."""

from __future__ import annotations

from .themes import Theme

# Block letters stay inside ~46 columns so they fit a split pane.
_MARK = [
    r"  █████╗ ███╗   ██╗███████╗██████╗  ",
    r" ██╔══██╗████╗  ██║██╔════╝██╔══██╗ ",
    r" ███████║██╔██╗ ██║█████╗  ██████╔╝ ",
    r" ██╔══██║██║╚██╗██║██╔══╝  ██╔══██╗ ",
    r" ██║  ██║██║ ╚████║███████╗██║  ██║ ",
    r" ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ",
]

_SUB = {
    "cassette": "G A M E S   ·   TAPE DECK 01",
    "phosphor": "GAMES // SELECT   ·   CRT P1",
    "cyberpunk": "GAMES   ·   BLOOM LINK LIVE",
    "tactical": "GAMES // BROADCAST   ·   HUD",
}


def render_logo(theme: Theme) -> str:
    ink = theme.snake.head[1]
    dim = theme.snake.body[1]
    lines = [f"[{ink}]{row}[/{ink}]" for row in _MARK]
    sub = _SUB.get(theme.id, "G A M E S")
    lines.append("")
    lines.append(f"[{dim}]          {sub}[/{dim}]")
    lines.append(f"[{dim}]          t skin   enter play[/{dim}]")
    return "\n".join(lines)
