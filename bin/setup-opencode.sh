#!/usr/bin/env bash
set -euo pipefail
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")/../extensions/operations/bin" && pwd)/setup-opencode.sh" "$@"
