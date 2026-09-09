# Ideas

Backlog for **aner-toolkits**: small, keyboard-first TUIs (and a few kits) that fit the nethop / aner-games vibe — useful, a bit geeky, one job each.

Status: **shipped** already exists · **idea** not started. Names are working titles. Layout would follow the monorepo (`networks/`, `games/`, then new top-level buckets).

---

## Shipped

| Path | Tool | Notes |
|---|---|---|
| `networks/nethop` | **nethop** | LAN explorer (nmap, roles, nicknames, watch, map, export) |
| `games/aner-games` | **aner-games** | Launcher + Snake, 2048, Tetris, Minesweeper, Sokoban, Wordle, typing race, packet chase |

---

## Networks

| Tool | Idea |
|---|---|
| **porthop** | Live local ports + owning process (`ss` / `lsof` as a table) |
| **pingmap** | Who’s home + RTT sparkline (watch mode, visual) |
| **sshmenu** | Fuzzy jump from `~/.ssh/config` with latency probe |
| **certwatch** | TLS expiry table for a saved host list |
| **dnspeek** | Live DNS query log (resolver / Pi-hole-ish view) |
| **bandhop** | Per-process / per-iface bandwidth bars (light nethogs) |
| **tracehop** | Traceroute / mtr as a hop table with loss sparkline |
| **wifihop** | Nearby SSIDs, signal, channel (read-only scan) |
| **routehop** | Routing table + default-path explainer (“why this iface”) |
| **nics** | Interface picker: IPs, MTU, flags, “is this a tunnel?” |
| **wakehop** | Saved MAC list, send WOL, ping until up |
| **fakeLAN kit** | Docs + scripts: VPS WireGuard/SoftEther hub so friends share a virtual LAN (broadcast caveats called out) |
| **nethop+** | Deeper nethop: traceroute from a host, service probes you already have, better VPN/WARP handling, subnet history |

Stay on the authorized / own-LAN side. No exploit kits, no “hello” to boxes you don’t run.

---

## Containers / k8s / VMs

| Tool | Idea |
|---|---|
| **dockhop** | Containers, ports, logs, one-key exec |
| **kubehop** | Pods/services by namespace, port-forward from the TUI |
| **imagehop** | Local images: size, dangling, quick prune |
| **composehop** | Pick a compose project, up/down/logs/ps |
| **podmanhop** | Same as dockhop for Podman |
| **lxchop** | LXC/LXD list, start/stop, attach |
| **qemuhop** | Local VMs: state, console, snapshot names |

---

## Git / code

| Tool | Idea |
|---|---|
| **githop** | Dirty repos under a tree, ahead/behind, one-key status/diff/log |
| **stashhop** | Browse / apply / drop stashes visually |
| **prhop** | `gh` PR list: checks, checkout, open in browser |
| **bisecthop** | Guided `git bisect` with test command |
| **hookhop** | List repo + global hooks, enable/disable |
| **ghoph** | GitHub notifications / review queue in the terminal |

---

## System / host

| Tool | Idea |
|---|---|
| **proc hop / syshop** | Processes, CPU/RSS, kill/nice without full `btop` |
| **diskhop** | Disks, mounts, SMART snippet, “what’s eating `/`” |
| **svc hop** | systemd/user units: status, logs, restart |
| **cronhop** | crontab + systemd timers in one table |
| **envhop** | Diff current env vs a profile; highlight secrets-looking keys (don’t print values) |
| **pkghop** | What owns this binary / reverse-depends (apt/pacman/brew) |
| **userhop** | Logged-in sessions, last, ssh keys present |
| **cliphop** | Clipboard history (opt-in, local only) |
| **notihop** | Desktop notification log / send test ping |

---

## Files / text

| Tool | Idea |
|---|---|
| **treehop** | Fuzzy file tree with size + git status badges |
| **duphop** | Duplicate-file finder (hash) with keep/trash |
| **jsonhop** | Pipe JSON/YAML, tree-navigate, copy jq path |
| **loghop** | Tail + filter + bookmark (journalctl / files) |
| **diffhop** | Two files/dirs, side-by-side, copy hunks |
| **renamehop** | Batch rename preview (regex) before apply |
| **ziphop** | Peek archives without full extract |

---

## Time / notes / life

| Tool | Idea |
|---|---|
| **calhop** | Week view from `cal` / ICS files |
| **timerhop** | Pomodoro + labels, bell in the terminal |
| **habit hop** | Tiny daily checks stored in `~/.config` |
| **noteshop** | Scratch pad / daily log, grep across files |
| **taskhop** | Local todo (markdown or json), keyboard triage |
| **passhop** | Wrapper around `pass` / age: list, copy, never dump |
| **billhop** | Recurring reminders (rent, domains, certs — dates only) |

---

## Media / radio / fun hardware

| Tool | Idea |
|---|---|
| **mpvhop** | Playlist + now playing for mpv/cmus |
| **cast hop** | Local DLNA/Chromecast discover (LAN, your gear) |
| **camhop** | List V4L devices, snapshot to file |
| **serialhop** | Pick `/dev/ttyUSB*`, baud, send/receive log (Arduino / radio) |
| **rtlhop** | SDR waterfalls are heavy — start with station presets + record |
| **print hop** | CUPS queues, cancel job, default printer |

---

## Home lab / self-host

| Tool | Idea |
|---|---|
| **dashhop** | One screen: which homelab boxes answer ping + HTTP |
| **backuphop** | Last restic/borg/rsync run, next due, dry-run button |
| **ddnshop** | Show public IP vs last update (your updater only) |
| **piholehop** | Query stats if you already run a blocker (API, local) |
| **ups hop** | NUT / battery minutes if a UPS is attached |

---

## Games (beyond what’s shipped)

Same `models` / `engine` / `screen` folders as aner-games.

| Title | Notes |
|---|---|
| Pong / Breakout | Two more “arcade tick” games |
| Connect Four / Reversi | Perfect for keyboard + small board |
| Sudoku / Nonogram | Pencil marks, check |
| Hangman / Anagram | Reuse word lists |
| Conway’s Life | Skin-friendly glyphs |
| Solitaire / FreeCell | Classic TUI |
| Chess / Checkers | UCI engine optional later |
| Mini roguelike | One dungeon, ASCII, skins |
| Battleship | Two-player hotseat or vs CPU |
| Trivia / quiz | Local JSON packs |
| Snake netplay | Only on a LAN/VPN you control (ties to fakeLAN) |
| High-score file | Shared `~/.local/share/aner-games/` |

---

## Cross-cutting (any tool)

- Shared **skins** (cassette / phosphor / blue / red-white) as a tiny library
- Shared **install.sh** pattern (pipx, `*_YES=1`, curl one-liner)
- Shared **state.json** under `~/.config/<tool>/`
- Windows **install.ps1** where a tool is useful on Win
- One **aner** meta-launcher: list installed toolkit commands

---

## Maybe later / park

- Mobile / web ports (this repo stays terminal-first)
- Cloud SaaS dashboards (too account-heavy)
- Anything that needs sending traffic to machines you don’t own

Add a row when an idea shows up in chat. Promote to a folder when you start it.
