#!/usr/bin/env bash
set -euo pipefail
echo "📤 Exportando flujos desde el contenedor n8n..."
docker exec -u node n8n_meco_lab n8n export:workflow --all --output=/data/workflows/
echo "✅ Exportación completada dentro del contenedor n8n."
