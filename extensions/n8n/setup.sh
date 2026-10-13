#!/usr/bin/env bash
set -Eeuo pipefail

echo "🛡️ Levantando el orquestador n8n de Bunker OS..."

if ! docker info >/dev/null 2>&1; then
  echo "❌ No se pudo conectar con Docker. Iniciá el daemon (por ejemplo: sudo systemctl start docker) y volvé a ejecutar este script." >&2
  exit 1
fi

# Iniciar el contenedor en segundo plano.
if ! docker compose up -d; then
  echo "❌ No se pudo desplegar n8n. Revisá el error anterior y volvé a intentar." >&2
  exit 1
fi

echo "✅ Contenedor desplegado exitosamente."
echo "🌐 Abre tu navegador y accede a: http://localhost:5678"
