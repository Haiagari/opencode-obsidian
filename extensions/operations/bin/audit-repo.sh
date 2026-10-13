#!/bin/bash
set -euo pipefail
# bin/audit-repo.sh
# Estandariza el uso de Trivy para auditorías de seguridad en el Bunker.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

echo "🛡️ Iniciando auditoría de seguridad con Trivy..."
trivy fs --severity HIGH,CRITICAL --format json . > security-audit-report.json
echo "✅ Reporte generado en security-audit-report.json"
