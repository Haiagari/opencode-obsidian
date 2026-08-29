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

# 2. Notificar al Agente (Triggering logic)
echo "🤖 Solicitando análisis agéntico..."

"${VAULT_DIR}/bin/bunker-alert.sh" "Bunker-Ingest" "INFO" "📥 NUEVA FUENTE DETECTADA: Se ha iniciado la ingestión de $SOURCE. Procesando entidades y conceptos..."

echo "✅ Proceso de ingestión iniciado. Esperando síntesis..."
