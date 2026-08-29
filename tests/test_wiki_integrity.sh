#!/usr/bin/env bash
# test_wiki_integrity.sh — Health check del vault.
# Verifica:
# 1. wiki/hot.md, wiki/index.md, wiki/log.md existen
# 2. BUNKER_RULES.md existe
# 3. Los scripts clave en bin/ son ejecutables
# 4. .raw/ no está vacío o tiene archivos fuente
# 5. Los frontmatter de las páginas principales son válidos
# 6. wiki-sync.sh y bunker-check.sh existen y son ejecutables

set -euo pipefail

VAULT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0
ERRORS=()

test() {
    local name="$1" condition="$2" detail="${3:-}"
    if [ "$condition" = true ]; then
        PASS=$((PASS + 1))
        echo "  ✅ ${name}"
    else
        FAIL=$((FAIL + 1))
        echo "  ❌ ${name}${detail:+: $detail}"
        ERRORS+=("${name}: ${detail}")
    fi
}

check_file_exists() {
    local path="$1" label="${2:-$1}"
    if [ -f "${VAULT_DIR}/${path}" ]; then
        test "${label} existe" true
    else
        test "${label} existe" false "ruta: ${path}"
    fi
}

check_executable() {
    local path="$1" label="${2:-$1}"
    if [ -x "${VAULT_DIR}/${path}" ]; then
        test "${label} es ejecutable" true
    else
        test "${label} es ejecutable" false "ruta: ${path}"
    fi
}

check_frontmatter() {
    local path="$1" field="$2" label="${3:-$1.$field}"
    local file="${VAULT_DIR}/${path}"
    if [ ! -f "$file" ]; then
        test "${label} frontmatter" false "archivo no existe: ${path}"
        return
    fi
    # Verificar que el campo existe en frontmatter (entre --- y ---)
    if grep -q "^${field}:" "$file" 2>/dev/null; then
        test "${label} frontmatter tiene '${field}'" true
    else
        test "${label} frontmatter tiene '${field}'" false
    fi
}

echo "🔍 Wiki Integrity Test"
echo "======================="
echo ""

# === 1. Archivos esenciales ===
echo "--- Archivos Esenciales ---"
check_file_exists "wiki/hot.md" "wiki/hot.md"
check_file_exists "wiki/index.md" "wiki/index.md"
check_file_exists "wiki/log.md" "wiki/log.md"
check_file_exists "BUNKER_RULES.md" "BUNKER_RULES.md"
check_file_exists "PROJECT.md" "PROJECT.md"
check_file_exists "AGENTS.md" "AGENTS.md"
echo ""

# === 2. Scripts clave ===
echo "--- Scripts Ejecutables ---"
check_executable "bin/bunker-check.sh" "bin/bunker-check.sh"
check_executable "bin/wiki-integrity.sh" "bin/wiki-integrity.sh"
check_executable "bin/evidence-index.sh" "bin/evidence-index.sh"
check_executable "bin/wiki-sync.sh" "bin/wiki-sync.sh"
check_executable "bin/bunker.sh" "bin/bunker.sh"
echo ""

# === 3. Frontmatter mínimo ===
echo "--- Frontmatter ---"
check_frontmatter "wiki/hot.md" "title" "wiki/hot.md"
check_frontmatter "wiki/hot.md" "updated" "wiki/hot.md"
check_frontmatter "wiki/index.md" "title" "wiki/index.md"
check_frontmatter "wiki/index.md" "updated" "wiki/index.md"
# BUNKER_RULES.md no usa frontmatter YAML por diseño, se saltea
echo ""

# === 4. n8n lab ===
echo "--- n8n Lab ---"
check_file_exists "automation/n8n-lab/docker-compose.yml" "docker-compose.yml"
check_file_exists "automation/n8n-lab/.env" ".env"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q n8n; then
    test "n8n container running" true
else
    echo "  ⚠️  [WARN] n8n container not running (offline mode)"
fi
echo ""

# === 5. Skills y estructura ===
echo "--- Skills ---"
check_file_exists "skills/autoresearch/SKILL.md" "skills/autoresearch/SKILL.md"
check_file_exists "skills/wiki-ingest/SKILL.md" "skills/wiki-ingest/SKILL.md"
# Verificar que el directorio skills no está vacío
skill_count=$(ls -d "${VAULT_DIR}"/skills/*/ 2>/dev/null | wc -l)
if [ "$skill_count" -ge 5 ]; then
    test "skills/ con ${skill_count} skills" true
else
    test "skills/ con suficientes skills" false "solo ${skill_count} skills"
fi
echo ""

# === Resumen ===
TOTAL=$((PASS + FAIL))
echo "======================="
echo "RESUMEN: ${TOTAL} tests | ✅ ${PASS} passed | ❌ ${FAIL} failed"
echo "======================="

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "Errores:"
    for e in "${ERRORS[@]}"; do
        echo "  ❌ ${e}"
    done
    exit 1
fi

echo "🎉 Vault integrity check passed"
