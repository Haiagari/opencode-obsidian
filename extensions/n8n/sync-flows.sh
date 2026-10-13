#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/bin" && pwd)"
exec "$SCRIPT_DIR/sync-flows.sh" "$@"
