#!/bin/bash
echo "📤 Exportando flujos individuales desde el contenedor n8n..."
docker exec -u node n8n_meco_lab n8n export:workflow --all --output=/data/workflows/
echo "✅ Exportación completada en la carpeta automation/n8n-lab/workflows/"
