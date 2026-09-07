#!/usr/bin/env bash
# Install nethop + nmap (and Python/pip if needed) so `nethop` is on PATH.
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/um1chc5/nethop/main/install.sh | bash
# Or from a clone:
#   chmod +x install.sh && ./install.sh
#
# One script: installs nmap via your package manager when missing (asks Y/n first).
# Prompts read from the terminal even when piped. Default is Yes.
# Non-interactive: NETHOP_YES=1 ./install.sh   (auto-accept all prompts)

set -euo pipefail

confirm() {
  local prompt="$1"
  local ans=""
  if [[ "${NETHOP_YES:-}" == "1" ]]; then
    echo "$prompt [Y/n] Y"
    return 0
  fi
  if [[ -e /dev/tty ]]; then
    read -r -p "$prompt [Y/n] " ans </dev/tty || true
  elif [[ -t 0 ]]; then
    read -r -p "$prompt [Y/n] " ans || true
  else
    echo "$prompt — no TTY, skipping (set NETHOP_YES=1 to auto-accept)."
    return 1
  fi
  case "${ans:-Y}" in
    y|Y|yes|YES|"") return 0 ;;
    *) return 1 ;;
  esac
}

have() { command -v "$1" >/dev/null 2>&1; }

run_pkg() {
  # Distro package install; may ask for sudo password.
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
    local ver
    ver="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || true)"
    echo "Python $ver found."
    return 0
  fi
  echo "Python 3 is required (3.10+)."
  if ! confirm "Install Python 3 now?"; then
    echo "Install Python 3, then re-run this script."
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

ensure_nmap() {
  if have nmap; then
    echo "nmap found: $(command -v nmap)"
    return 0
  fi
  echo "nmap is required (system package — this script installs it for you)."
  if ! confirm "Install nmap now (may ask for sudo)?"; then
    echo "nmap is required. Re-run and answer Y, or install nmap then re-run."
    exit 1
  fi
  if have brew; then
    brew install nmap
  elif ! run_pkg nmap; then
    echo "No supported package manager found."
    echo "Install nmap from https://nmap.org/download.html then re-run this script."
    exit 1
  fi
  if have nmap; then
    echo "nmap installed: $(command -v nmap)"
  else
    echo "nmap was installed but is not on PATH yet. Open a new terminal and re-run if needed."
    exit 1
  fi
}

echo "Installing nethop..."

ensure_python
ensure_nmap
ensure_pip

if have pipx; then
  pipx install --force git+https://github.com/um1chc5/nethop.git
  echo
  echo "OK — run:  nethop"
  exit 0
fi

if confirm "pipx is not installed (recommended). Install pipx and use it?"; then
  python3 -m pip install --user --upgrade pipx
  python3 -m pipx ensurepath || true
  export PATH="$(python3 -m site --user-base)/bin:$PATH"
  if have pipx; then
    pipx install --force git+https://github.com/um1chc5/nethop.git
    echo
    echo "OK — run:  nethop"
    echo "(New terminals pick up pipx via PATH.)"
    exit 0
  fi
  echo "pipx not on PATH yet; falling back to pip --user."
fi

python3 -m pip install --user --upgrade "git+https://github.com/um1chc5/nethop.git"

# User scripts dir (PEP 370)
SCRIPTS="$(python3 -c 'import sysconfig; print(sysconfig.get_path("scripts", "posix_user") or "")')"
if [[ -z "$SCRIPTS" || ! -x "$SCRIPTS/nethop" ]]; then
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
  echo "# nethop" >> "$RC"
  echo "$LINE" >> "$RC"
  echo "Added to $RC: $SCRIPTS"
fi

export PATH="$SCRIPTS:$PATH"

if have nethop; then
  echo
  echo "OK — run:  nethop"
  echo "(New terminals will pick this up via $RC.)"
else
  echo
  echo "Installed. Open a new terminal, then run:  nethop"
fi
