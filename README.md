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

## Install nethop (CLI)

Recommended: **[pipx](https://pipx.pypa.io/)** so the `nethop` command is isolated and on your PATH.

### From GitHub (all platforms)

```bash
pipx install git+https://github.com/um1chc5/nethop.git
```

Or with pip (user install):

```bash
python3 -m pip install --user git+https://github.com/um1chc5/nethop.git
```

On Windows (PowerShell / cmd), if `python3` is not found:

```bash
py -m pip install --user git+https://github.com/um1chc5/nethop.git
```

### From a local clone

```bash
git clone https://github.com/um1chc5/nethop.git
cd nethop
pipx install .
# or: python3 -m pip install -e .
```

### Run

```bash
nethop
```

If Windows says `nethop` is not recognized, either:

```powershell
py -m nethop
```

or add your user Scripts folder to PATH (then open a **new** terminal):

```text
%APPDATA%\Python\Python314\Scripts
```

(Adjust `Python314` to match your Python version.)

Or without the script entrypoint:

```bash
python3 -m nethop
# Windows:
py -m nethop
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
