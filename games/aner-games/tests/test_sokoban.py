"""Sokoban push rules (no TUI)."""

from __future__ import annotations

from aner_games.games.sokoban.engine import SokobanGame, parse_level


def test_push_crate_and_undo() -> None:
    text = "#####\n#@$ #\n#####\n"
    w, h, walls, crates, targets, player = parse_level(text)
    g = SokobanGame(
        width=w,
        height=h,
        walls=walls,
        crates=crates,
        targets=targets,
        player=player,
    )
    assert g.move(1, 0)
    assert g.player == (2, 1)
    assert (3, 1) in g.crates
    g.revert()
    assert g.player == (1, 1)
    assert (2, 1) in g.crates


def test_cannot_push_two_crates() -> None:
    text = "######\n#@$$ #\n######\n"
    w, h, walls, crates, targets, player = parse_level(text)
    g = SokobanGame(width=w, height=h, walls=walls, crates=crates, targets=targets, player=player)
    assert not g.move(1, 0)
    assert g.player == player


def test_level_one_loads() -> None:
    g = SokobanGame()
    assert g.walls
    assert g.crates
    assert g.targets
    assert not g.won


if __name__ == "__main__":
    test_push_crate_and_undo()
    test_cannot_push_two_crates()
    test_level_one_loads()
    print("ok")
