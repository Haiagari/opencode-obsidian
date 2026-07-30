#!/bin/bash
# bunker-github-setup.sh — Aplica la configuración de GitHub (About, Tags, Branch Protection)

REPO="Haiagari/opencode-obsidian"

echo "🚀 Configurando la identidad del repositorio en GitHub..."
gh repo edit "$REPO" \
  --description "Bunker OS (v3.0): Local-first Knowledge Operating System and Agentic Command Center." \
  --homepage "https://opencode.ai" \
  --add-topic "knowledge-graph,agentic-workflows,obsidian,n8n,bunker-os,local-first,cybersecurity"

echo "🔒 Aplicando reglas de protección a la rama 'main'..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/$REPO/branches/main/protection" \
  -f enforce_admins=false \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"required_approving_review_count":1}' \
  -f required_status_checks='{"strict":true,"contexts":[]}' \
  -f restrictions=null

echo "✅ ¡Configuración de GitHub aplicada con éxito!"
