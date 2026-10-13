#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/extensions/n8n/bin" && pwd)"
exec "$SCRIPT_DIR/sync-flows.sh" "$@"
