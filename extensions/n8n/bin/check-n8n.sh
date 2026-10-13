#!/usr/bin/env bash
set -euo pipefail
EXTENSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$EXTENSION_DIR"
[[ -f .env ]] || { echo "FAIL: extensions/n8n/.env is not configured." >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "FAIL: Docker is not installed." >&2; exit 1; }
docker compose config --quiet
docker ps --format '{{.Names}}' | grep -qx n8n_meco_lab
echo "Optional n8n extension configuration and container are available."
