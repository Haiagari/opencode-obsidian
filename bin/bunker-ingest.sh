#!/bin/bash
set -euo pipefail

# bunker-ingest.sh — Procesa una fuente y la integra al Bunker con sanitización defensiva
# Uso: ./bin/bunker-ingest.sh <ruta_al_archivo_o_url>

VAULT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="${1:-}"

if [ -z "$SOURCE" ]; then
    echo "❌ Error: Debes proporcionar una fuente (archivo o URL)."
    echo "Uso: $0 <archivo_o_url>"
    exit 1
fi

echo "🧠 Iniciando ingestión de: $SOURCE"

# 1. Mover a .raw y sanitizar si es un archivo local
if [ -f "$SOURCE" ]; then
    mkdir -p "${VAULT_DIR}/.raw"
    FILENAME=$(basename "$SOURCE")
    RAW_DEST="${VAULT_DIR}/.raw/${FILENAME}"
    
    # Sanitizar contenido defensivamente contra prompt injections
    python3 "${VAULT_DIR}/scripts/sanitize_ingest.py" "$SOURCE" --output "$RAW_DEST"
    echo "📥 Archivo sanitizado y copiado a .raw/$FILENAME"
fi

# 2. Optional n8n notification. Ingestion never depends on the extension.
if [[ "${BUNKER_N8N_ALERTS:-0}" == "1" ]]; then
    if "${VAULT_DIR}/bin/bunker-alert.sh" "Bunker-Ingest" "INFO" "📥 NUEVA FUENTE DETECTADA: Se ha iniciado la ingestión de $SOURCE. Procesando entidades y conceptos..."; then
        echo "📡 Optional n8n alert sent."
    else
        echo "⚠️ Ingestion completed; optional n8n alert failed." >&2
    fi
else
    echo "ℹ️ n8n notification skipped (set BUNKER_N8N_ALERTS=1 to opt in)."
fi

echo "✅ Proceso de ingestión iniciado. Esperando síntesis..."
