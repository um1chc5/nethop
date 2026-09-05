#!/usr/bin/env bash
# Install nethop and ensure `nethop` is on PATH (Linux / macOS).
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/um1chc5/nethop/main/install.sh | bash
# Or from a clone:
#   chmod +x install.sh && ./install.sh

set -euo pipefail

echo "Installing nethop..."

if command -v pipx >/dev/null 2>&1; then
  pipx install --force git+https://github.com/um1chc5/nethop.git
  echo
  echo "OK — run:  nethop"
  exit 0
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

if command -v nethop >/dev/null 2>&1; then
  echo
  echo "OK — run:  nethop"
  echo "(New terminals will pick this up via $RC.)"
else
  echo
  echo "Installed. Open a new terminal, then run:  nethop"
fi
