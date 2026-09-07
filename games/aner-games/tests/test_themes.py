"""Theme cycle helpers."""

from aner_games.themes import fullwidth, next_theme_id, get_theme, THEMES


def test_theme_cycle() -> None:
    assert THEMES == ("cassette", "phosphor", "cyberpunk", "tactical")
    assert next_theme_id("cassette") == "phosphor"
    assert next_theme_id("phosphor") == "cyberpunk"
    assert next_theme_id("cyberpunk") == "tactical"
    assert next_theme_id("tactical") == "cassette"


def test_palettes() -> None:
    assert "FFF8C8" in get_theme("cassette").snake.head[1]
    assert get_theme("phosphor").snake.head[1] == "bold #00FF41"
    assert get_theme("cyberpunk").snake.head[1] == "bold #FFFFFF"
    assert get_theme("cyberpunk").snake.empty[0].startswith("░")
    assert get_theme("tactical").snake.body[1] == "#FF2020"
    assert get_theme("tactical").snake.head[1] == "bold #FFFFFF"


def test_lettering() -> None:
    assert "Ｄ" in fullwidth("DECK")


def test_logo() -> None:
    from aner_games.logo import render_logo
    from aner_games.themes import get_theme

    art = render_logo(get_theme("phosphor"))
    assert "██" in art or "█" in art
    assert "GAMES" in art


if __name__ == "__main__":
    test_theme_cycle()
    test_palettes()
    test_lettering()
    test_logo()
    print("ok")
