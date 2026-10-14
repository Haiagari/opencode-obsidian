#!/usr/bin/env bash
set -euo pipefail

# Stage and sanitize a local source file. URL ingestion is handled by wiki-ingest.
# Usage: ./bin/bunker-ingest.sh <local-file>

VAULT_DIR="${BUNKER_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SOURCE="${1:-}"

if [[ -z "$SOURCE" ]]; then
    echo "Error: provide a local source file." >&2
    echo "Usage: $0 <local-file>" >&2
    exit 2
fi

case "$SOURCE" in
    http://*|https://*)
        echo "URL ingestion is not supported by this CLI. Use the wiki-ingest skill in OpenCode." >&2
        exit 2
        ;;
esac

if [[ ! -f "$SOURCE" ]]; then
    echo "Error: source file not found: $SOURCE" >&2
    exit 2
fi

FILENAME="$(basename -- "$SOURCE")"
mkdir -p "${VAULT_DIR}/.raw"
RAW_DEST="${VAULT_DIR}/.raw/$FILENAME"

if [[ -e "$RAW_DEST" ]]; then
    echo "Error: refusing to overwrite existing staged source: .raw/$FILENAME" >&2
    exit 1
fi

RAW_TEMP="$(mktemp "${RAW_DEST}.tmp.XXXXXX")"
trap 'rm -f -- "$RAW_TEMP"' EXIT

python3 "${VAULT_DIR}/scripts/sanitize_ingest.py" "$SOURCE" --output "$RAW_TEMP"

# Link creation is atomic and fails if another process created the destination.
if ! ln -- "$RAW_TEMP" "$RAW_DEST"; then
    echo "Error: could not stage source without overwriting .raw/$FILENAME" >&2
    exit 1
fi
rm -f -- "$RAW_TEMP"
RAW_TEMP=""

echo "Sanitized source staged at .raw/$FILENAME"
echo "This command only stages the file. Run the wiki-ingest skill in OpenCode to create wiki notes."

# Optional notification. Its failure never removes or invalidates the staged file.
if [[ "${BUNKER_N8N_ALERTS:-0}" == "1" ]]; then
    if "${VAULT_DIR}/bin/bunker-alert.sh" "Bunker-Ingest" "INFO" "Sanitized source staged: $FILENAME"; then
        echo "Optional n8n notification sent."
    else
        echo "Warning: source is staged, but the optional n8n alert failed." >&2
    fi
else
    echo "n8n notification skipped (set BUNKER_N8N_ALERTS=1 to opt in)."
fi
