#!/usr/bin/env bash
# LFG installer. Checks the basics, then runs `lfg setup`, which looks at your machine, shows exactly what it
# would change and changes nothing until you agree. Options are passed through:
#
#   ./install.sh                     install Core (asks first)
#   ./install.sh --dry-run           only show the plan
#   ./install.sh --here              also turn LFG on in the repo you're in
#   ./install.sh --packs security    also install optional packs (security,shipcheck,pentest,knowledge,linear,headroom)
#   ./install.sh --yes               don't ask
#
# Undo everything with `lfg uninstall`.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$(uname -s)" != Darwin ]; then
  echo "LFG supports macOS only for now (Linux is on the roadmap)." >&2
  exit 2
fi

PY=""
for c in python3 /usr/bin/python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 9))' 2>/dev/null; then
    PY="$(command -v "$c")"
    break
  fi
done
if [ -z "$PY" ]; then
  echo "LFG needs Python 3.9 or newer. \`xcode-select --install\` provides one." >&2
  exit 2
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code isn't on your PATH. Install it first: https://claude.com/claude-code" >&2
  echo "(Continuing: LFG's files and tools can be set up now; re-run this to register the plugin.)" >&2
fi

exec "$PY" "$SRC/plugin/bin/lfg" setup "$@"
