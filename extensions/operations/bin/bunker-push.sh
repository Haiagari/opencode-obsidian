#!/bin/bash
set -euo pipefail

# bunker-push.sh — Sincroniza el Bunker y notifica vía n8n
# Uso: ./bin/bunker-push.sh "mensaje del commit"

MESSAGE="${1:-}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

if [ -z "$MESSAGE" ]; then
    echo "❌ Error: Debes proporcionar un mensaje para el commit."
    echo "Uso: $0 \"mensaje del commit\""
    exit 1
fi

echo "📦 Iniciando sincronización del Bunker..."

# 1. Git Add y Commit
git add -A
git commit -m "$MESSAGE"

# 2. Git Push
if git push; then
    echo "✅ Sincronización exitosa en GitHub."

    # 3. Optional n8n notification; never affect the Git push result.
    if [ "${BUNKER_N8N_ALERTS:-0}" = "1" ]; then
        LAST_COMMIT_HASH=$(git rev-parse --short HEAD)
        if ! "$REPO_ROOT/bin/bunker-alert.sh" "Bunker-Git" "SUCCESS" "📦 PUSH EXITOSO: El Bunker ha sido sincronizado.\n\nHash: $LAST_COMMIT_HASH\nMessage: $MESSAGE\n\n_System status: Protected_"; then
            echo "⚠️ Advertencia: falló la notificación opcional de n8n." >&2
        fi
    fi
else
    echo "❌ Error al sincronizar con el remote."
    if [ "${BUNKER_N8N_ALERTS:-0}" = "1" ]; then
        if ! "$REPO_ROOT/bin/bunker-alert.sh" "Bunker-Git" "ERROR" "⚠️ FALLO DE SINCRONIZACIÓN: Error al intentar hacer push al repositorio."; then
            echo "⚠️ Advertencia: falló la notificación opcional de n8n." >&2
        fi
    fi
    exit 1
fi
