# aner-toolkits

Terminal tools monorepo.

## Tools

| Path | Tool | What it does |
|---|---|---|
| [`networks/nethop`](networks/nethop/) | **nethop** | LAN explorer TUI (nmap-backed) |
| [`games/aner-games`](games/aner-games/) | **aner-games** | Terminal game launcher — Snake, 2048, Tetris, Minesweeper, Sokoban, Wordle, typing race, packet chase |

## Quick install — nethop

```bash
curl -fsSL https://raw.githubusercontent.com/um1chc5/aner-toolkits/main/networks/nethop/install.sh | bash
```

```powershell
irm https://raw.githubusercontent.com/um1chc5/aner-toolkits/main/networks/nethop/install.ps1 | iex
```

Or from a clone:

```bash
git clone https://github.com/um1chc5/aner-toolkits.git
cd aner-toolkits/networks/nethop
./install.sh   # or .\install.ps1 on Windows
```

## Layout

```
aner-toolkits/
  networks/
    nethop/        # LAN / nmap TUI
  games/
    aner-games/    # list → select → play
```

## Quick install — aner-games

```bash
curl -fsSL https://raw.githubusercontent.com/um1chc5/aner-toolkits/main/games/aner-games/install.sh | bash
```

Or from a clone:

```bash
git clone https://github.com/um1chc5/aner-toolkits.git
cd aner-toolkits/games/aner-games
./install.sh
```

## License

MIT — see [LICENSE](LICENSE).
