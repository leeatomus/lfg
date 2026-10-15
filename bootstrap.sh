#!/usr/bin/env bash
# Older name for install.sh, kept so existing instructions keep working.
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install.sh" "$@"
