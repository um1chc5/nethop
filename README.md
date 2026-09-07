# nethop

Interactive LAN explorer — an **htop/btop-style terminal UI** over [`nmap`](https://nmap.org/).

Discover devices on your Wi‑Fi / office LAN (including tech gear like k8s nodes, DBs, bastions), run common scans, open HTTP ports in a browser.

**Use only on networks you own or are authorized to test.**

## Requirements

| | |
|---|---|
| Python | 3.10+ |
| nmap | on your `PATH` (installed by the scripts below if missing) |
| OS | Windows, Linux (Ubuntu and others), macOS |

## Install (so `nethop` works as a command)

These installers install **nethop + nmap** and put `nethop` on your PATH so you only type:

```bash
nethop
```

They ask `Y/n` before installing missing system packages (default Yes). Unattended: set `NETHOP_YES=1` (bash) or `$env:NETHOP_YES = "1"` (PowerShell).

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/um1chc5/nethop/main/install.ps1 | iex
```

Then open a **new** PowerShell window if this one still cannot find `nethop`.

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/um1chc5/nethop/main/install.sh | bash
```

### Alternative: pipx (any OS)

```bash
pipx install git+https://github.com/um1chc5/nethop.git
nethop
```

`pipx` installs only the Python app — use `install.sh` / `install.ps1` if you also need nmap.

### From a local clone

```bash
git clone https://github.com/um1chc5/nethop.git
cd nethop

# Windows
.\install.ps1

# Linux / macOS
chmod +x install.sh && ./install.sh
```

## Keys / mouse

| Input | Action |
|-------|--------|
| `d` / `r` | Discover hosts on LAN (`nmap -sn`) |
| `i` | Pick network interface / CIDR (skips VPN `/32` tunnels when possible) |
| `n` | Set / clear nickname for selected host (saved under `~/.config/nethop/`) |
| `w` | Toggle watch mode (auto rediscover; bell on new hosts) |
| `m` | Toggle LAN map (hosts grouped by role) vs ports |
| `c` / `C` | Copy markdown host card / all-hosts summary to clipboard |
| ↑↓ / click | Select host, action, or port |
| `Enter` | Run selected scan on selected host |
| `o` / double-click port | Open port URL in browser |
| `Tab` | Cycle focus |
| `q` | Quit |

After a port scan, nethop guesses a **role** from ports/hostname (e.g. `k8s`, `postgres`, `docker`, `bastion`, `ssh`).

## Scan actions

- Fast ports (`-F`)
- Common ports
- Service versions (`-sV`)
- Default scripts (`-sC`)
- OS detect (`-O`) — often needs admin/root
- Aggressive (`-A`) — slow; often needs admin/root

## Project layout

```
nethop/
  app.py           # Textual UI
  app.tcss         # theme
  models.py        # Host / Port / profiles
  network.py       # VPN-aware LAN / iface detect
  roles.py         # tech-LAN role heuristics
  state.py         # nicknames + watch prefs
  export.py        # markdown cards + clipboard
  nmap_client.py   # nmap subprocess + XML
  scans.py         # named scan profiles
  browser.py       # open URLs
  widgets/         # HostTable, PortTable, ActionList, LanMap, modals
```

## License

MIT — see [LICENSE](LICENSE).
