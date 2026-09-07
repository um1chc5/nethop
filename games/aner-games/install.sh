#!/usr/bin/env bash
# Install aner-games so `aner-games` is on PATH.
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/um1chc5/aner-toolkits/main/games/aner-games/install.sh | bash
# Or from a clone:
#   chmod +x install.sh && ./install.sh
#
# Prompts read from the terminal even when piped. Default is Yes.
# Non-interactive: ANER_GAMES_YES=1 ./install.sh

set -euo pipefail

GIT_SRC="git+https://github.com/um1chc5/aner-toolkits.git#subdirectory=games/aner-games"

confirm() {
  local prompt="$1"
  local ans=""
  if [[ "${ANER_GAMES_YES:-}" == "1" ]]; then
    echo "$prompt [Y/n] Y"
    return 0
  fi
  if [[ -e /dev/tty ]]; then
    read -r -p "$prompt [Y/n] " ans </dev/tty || true
  elif [[ -t 0 ]]; then
    read -r -p "$prompt [Y/n] " ans || true
  else
    echo "$prompt — no TTY, skipping (set ANER_GAMES_YES=1 to auto-accept)."
    return 1
  fi
  case "${ans:-Y}" in
    y|Y|yes|YES|"") return 0 ;;
    *) return 1 ;;
  esac
}

have() { command -v "$1" >/dev/null 2>&1; }

run_pkg() {
  if have apt-get; then
    sudo apt-get update
    sudo apt-get install -y "$@"
  elif have dnf; then
    sudo dnf install -y "$@"
  elif have yum; then
    sudo yum install -y "$@"
  elif have pacman; then
    sudo pacman -Sy --noconfirm "$@"
  elif have zypper; then
    sudo zypper --non-interactive install "$@"
  elif have brew; then
    brew install "$@"
  else
    return 1
  fi
}

ensure_python() {
  if have python3; then
    local ver major minor
    ver="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || true)"
    major="${ver%%.*}"
    minor="${ver#*.}"
    echo "Python $ver found."
    if [[ -n "$major" && -n "$minor" ]] && { [[ "$major" -gt 3 ]] || { [[ "$major" -eq 3 && "$minor" -ge 10 ]]; }; }; then
      return 0
    fi
    echo "Python 3.10+ is required (found $ver)."
  else
    echo "Python 3 is required (3.10+)."
  fi
  if ! confirm "Install Python 3 now?"; then
    echo "Install Python 3.10+, then re-run this script."
    exit 1
  fi
  if have brew; then
    brew install python
  elif ! run_pkg python3 python3-pip python3-venv; then
    echo "Could not detect a package manager. Install Python 3.10+ and retry."
    exit 1
  fi
  if ! have python3; then
    echo "Python 3 still not on PATH after install."
    exit 1
  fi
}

ensure_pip() {
  if python3 -m pip --version >/dev/null 2>&1; then
    return 0
  fi
  echo "pip is missing for python3."
  if ! confirm "Install pip now?"; then
    echo "Install pip (e.g. python3-pip), then re-run this script."
    exit 1
  fi
  if python3 -m ensurepip --user >/dev/null 2>&1; then
    return 0
  fi
  if have brew; then
    echo "Try: brew reinstall python"
    exit 1
  fi
  if ! run_pkg python3-pip; then
    echo "Could not install pip. See https://pip.pypa.io/en/stable/installation/"
    exit 1
  fi
}

spec() {
  local here=""
  if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -f "$here/pyproject.toml" ]]; then
      echo "$here"
      return 0
    fi
  fi
  echo "$GIT_SRC"
}

install_pipx() {
  local src="$1"
  if [[ "$src" == git+* ]]; then
    pipx install --force "$src"
  else
    pipx install --force --editable "$src"
  fi
}

echo "Installing aner-games..."

ensure_python
ensure_pip
SRC="$(spec)"

if have pipx; then
  install_pipx "$SRC"
  echo
  echo "OK — run:  aner-games"
  exit 0
fi

if confirm "pipx is not installed (recommended). Install pipx and use it?"; then
  python3 -m pip install --user --upgrade pipx
  python3 -m pipx ensurepath || true
  export PATH="$(python3 -m site --user-base)/bin:$PATH"
  if have pipx; then
    install_pipx "$SRC"
    echo
    echo "OK — run:  aner-games"
    echo "(New terminals pick up pipx via PATH.)"
    exit 0
  fi
  echo "pipx not on PATH yet; falling back to pip --user."
fi

if [[ "$SRC" == git+* ]]; then
  python3 -m pip install --user --upgrade "$SRC"
else
  python3 -m pip install --user --upgrade --editable "$SRC"
fi

SCRIPTS="$(python3 -c 'import sysconfig; print(sysconfig.get_path("scripts", "posix_user") or "")')"
if [[ -z "$SCRIPTS" || ! -x "$SCRIPTS/aner-games" ]]; then
  SCRIPTS="$(python3 -m site --user-base)/bin"
fi

SHELL_NAME="$(basename "${SHELL:-bash}")"
RC=""
case "$SHELL_NAME" in
  zsh) RC="$HOME/.zshrc" ;;
  bash) RC="$HOME/.bashrc" ;;
  *) RC="$HOME/.profile" ;;
esac

LINE="export PATH=\"$SCRIPTS:\$PATH\""
if [[ -f "$RC" ]] && grep -Fq "$SCRIPTS" "$RC" 2>/dev/null; then
  echo "PATH already mentions $SCRIPTS in $RC"
else
  echo "" >> "$RC"
  echo "# aner-games" >> "$RC"
  echo "$LINE" >> "$RC"
  echo "Added to $RC: $SCRIPTS"
fi

export PATH="$SCRIPTS:$PATH"

if have aner-games; then
  echo
  echo "OK — run:  aner-games"
  echo "(New terminals will pick this up via $RC.)"
else
  echo
  echo "Installed. Open a new terminal, then run:  aner-games"
fi
