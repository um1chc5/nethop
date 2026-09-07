"""Wordle scoring (no TUI)."""

from __future__ import annotations

from aner_games.games.wordle.engine import WordleGame, score_guess
from aner_games.games.wordle.words import WORDS


def test_score_duplicate_letters() -> None:
    marks = score_guess("crane", "trace")
    assert [m for _, m in marks] == ["miss", "hit", "hit", "close", "hit"]


def test_submit_win() -> None:
    g = WordleGame(secret="crane")
    for ch in "crane":
        g.type_char(ch)
    g.submit()
    assert g.won
    assert g.over


def test_rejects_unknown() -> None:
    g = WordleGame(secret="crane")
    for ch in "zzzzz":
        g.type_char(ch)
    g.submit()
    assert g.message == "not in word list"
    assert not g.guesses


def test_word_bank() -> None:
    assert "crane" in WORDS
    assert all(len(w) == 5 for w in WORDS)


if __name__ == "__main__":
    test_score_duplicate_letters()
    test_submit_win()
    test_rejects_unknown()
    test_word_bank()
    print("ok")
