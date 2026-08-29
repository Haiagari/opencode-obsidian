#!/usr/bin/env bash
# bin/vault-lock.sh — CLI utility for safe concurrent agent writes/appends in Bunker OS.
#
# Uso:
#   ./bin/vault-lock.sh append <file> "text to append"
#   ./bin/vault-lock.sh write <file> "text to write"
#   ./bin/vault-lock.sh prepend-log <file> "log entry"
#   echo "stream data" | ./bin/vault-lock.sh append <file>

set -euo pipefail

VAULT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_PY="${VAULT_DIR}/scripts/vault_lock.py"

if [ "$#" -lt 2 ]; then
    echo "Uso: $0 <append|write|prepend-log> <target_file> [text]"
    exit 1
fi

ACTION="$1"
TARGET_FILE="$2"
shift 2

if [ "$#" -ge 1 ]; then
    python3 "$LOCK_PY" "$ACTION" "$TARGET_FILE" "$*"
else
    # Read from stdin
    python3 "$LOCK_PY" "$ACTION" "$TARGET_FILE"
fi
