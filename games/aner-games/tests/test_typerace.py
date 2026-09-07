"""Typing race feed (no TUI)."""

from __future__ import annotations

from aner_games.games.typerace.engine import TypeRaceGame


def test_correct_advances() -> None:
    g = TypeRaceGame(prompt="ab")
    g.feed("a", 1.0)
    g.feed("b", 2.0)
    assert g.typed == "ab"
    assert g.done
    assert g.errors == 0
    assert g.wpm(2.0) > 0


def test_wrong_does_not_advance() -> None:
    g = TypeRaceGame(prompt="ab")
    g.feed("x", 1.0)
    assert g.typed == ""
    assert g.errors == 1
    assert not g.done


if __name__ == "__main__":
    test_correct_advances()
    test_wrong_does_not_advance()
    print("ok")
