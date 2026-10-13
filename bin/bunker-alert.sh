#!/usr/bin/env bash
set -euo pipefail
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")/../extensions/n8n/bin" && pwd)/bunker-alert.sh" "$@"
