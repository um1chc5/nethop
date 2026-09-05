# nethop

Interactive LAN explorer — an **htop/btop-style terminal UI** over [`nmap`](https://nmap.org/).

Discover devices on your Wi‑Fi/LAN, run common scans, open HTTP ports in a browser.

**Use only on networks you own or are authorized to test.**

## Requirements

| | |
|---|---|
| Python | 3.10+ |
| nmap | on your `PATH` |
| OS | Windows, Linux (Ubuntu and others), macOS |

### Install nmap

**Ubuntu / Debian**

```bash
sudo apt update
sudo apt install -y nmap
```

**Fedora**

```bash
sudo dnf install nmap
```

**Arch**

```bash
sudo pacman -S nmap
```

**Windows** — install from [nmap.org/download.html](https://nmap.org/download.html) (include Npcap when prompted).

**macOS**

```bash
brew install nmap
```

## Install (so `nethop` works as a command)

These installers put `nethop` on your PATH so you only type:

```bash
nethop
```

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
| ↑↓ / click | Select host, action, or port |
| `Enter` | Run selected scan on selected host |
| `o` / double-click port | Open port URL in browser |
| `Tab` | Cycle focus |
| `q` | Quit |

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
  network.py       # detect local CIDR
  nmap_client.py   # nmap subprocess + XML
  scans.py         # named scan profiles
  browser.py       # open URLs
  widgets/         # HostTable, PortTable, ActionList
```

## License

MIT — see [LICENSE](LICENSE).
