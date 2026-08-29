#!/bin/bash
set -euo pipefail

# bunker-alert.sh — Dispara una alerta de seguridad firmada con HMAC al orquestador n8n
# Uso: ./bunker-alert.sh <target> <level> <message>

TARGET="${1:-}"
LEVEL="${2:-}"
MESSAGE="${3:-}"

VAULT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N8N_ENV_FILE="${VAULT_DIR}/automation/n8n-lab/.env"

# Cargar variables de entorno si existen
if [ -f "$N8N_ENV_FILE" ]; then
    # Leer AOC_WEBHOOK_SECRET si existe
    SECRET_FROM_ENV=$(grep -E '^AOC_WEBHOOK_SECRET=' "$N8N_ENV_FILE" | cut -d '=' -f2- || true)
    AOC_WEBHOOK_SECRET="${AOC_WEBHOOK_SECRET:-$SECRET_FROM_ENV}"
fi

AOC_WEBHOOK_SECRET="${AOC_WEBHOOK_SECRET:-bunker_default_webhook_secret}"
N8N_WEBHOOK_URL="${N8N_WEBHOOK_URL:-http://localhost:5678/webhook/bunker-security-alert}"

if [ -z "$TARGET" ] || [ -z "$LEVEL" ] || [ -z "$MESSAGE" ]; then
    echo "Uso: $0 <target> <level> <message>"
    exit 1
fi

echo "📡 Enviando alerta de seguridad a n8n..."

JSON_PAYLOAD=$(python3 -c 'import json, sys; print(json.dumps({"target": sys.argv[1], "level": sys.argv[2], "message": sys.argv[3]}, separators=(",", ":")))' "$TARGET" "$LEVEL" "$MESSAGE")

# Generar firma HMAC-SHA256
SIGNATURE=$(python3 -c 'import hmac, hashlib, sys; key = sys.argv[1].encode("utf-8"); msg = sys.argv[2].encode("utf-8"); print(hmac.new(key, msg, hashlib.sha256).hexdigest())' "$AOC_WEBHOOK_SECRET" "$JSON_PAYLOAD")

HTTP_RESPONSE=$(mktemp)
HTTP_CODE=$(curl -sS -o "$HTTP_RESPONSE" -w "%{http_code}" -X POST "$N8N_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "X-Bunker-Signature: sha256=${SIGNATURE}" \
  -H "X-Webhook-Secret: ${AOC_WEBHOOK_SECRET}" \
  -d "$JSON_PAYLOAD" || echo "000")

if [ "$HTTP_CODE" -lt 200 ] || [ "$HTTP_CODE" -ge 300 ]; then
    echo "❌ Error al enviar la alerta. HTTP $HTTP_CODE"
    if [ -s "$HTTP_RESPONSE" ]; then
        cat "$HTTP_RESPONSE"
    fi
    rm -f "$HTTP_RESPONSE"
    exit 1
fi

rm -f "$HTTP_RESPONSE"

echo -e "\n✅ Alerta enviada exitosamente con firma HMAC-SHA256."
