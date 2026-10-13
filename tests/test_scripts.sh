#!/usr/bin/env bash
# test_scripts.sh — Verifica que los scripts del Bunker sean coherentes.
# 1. Todos los scripts en bin/ son ejecutables
# 2. No contienen errores de sintaxis bash
# 3. Tienen shebang correcto
# 4. No tienen secretos hardcodeados

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
        echo "  ❌ ${name}${detail:+: ${detail}}"
        ERRORS+=("${name}: ${detail}")
    fi
}

echo "🔍 Scripts Test"
echo "================"
echo ""

# === 1. Sintaxis bash ===
echo "--- Sintaxis Bash ---"
readarray -d '' -t shell_scripts < <(find "${VAULT_DIR}/bin" "${VAULT_DIR}/extensions" -type f -name '*.sh' -print0)
for script in "${shell_scripts[@]}"; do
    name=$(basename "$script")
    if [ ! -f "$script" ]; then
        test "${name}" false "no es archivo"
        continue
    fi
    if bash -n "$script" 2>/dev/null; then
        test "${name} sintaxis" true
    else
        test "${name} sintaxis" false "error de sintaxis bash"
    fi
done
echo ""

# === 2. Shebang correcto ===
echo "--- Shebang ---"
for script in "${shell_scripts[@]}"; do
    name=$(basename "$script")
    first_line=$(head -1 "$script" 2>/dev/null || echo "")
    if [[ "$first_line" == "#!/usr/bin/env bash" ]] || [[ "$first_line" == "#!/bin/bash" ]] || [[ "$first_line" == "#!/usr/bin/bash" ]]; then
        test "${name} shebang" true
    else
        test "${name} shebang" false "tiene: ${first_line}"
    fi
done
echo ""

# === 3. Ejecutable ===
echo "--- Ejecutable ---"
for script in "${shell_scripts[@]}"; do
    name=$(basename "$script")
    if [ -x "$script" ]; then
        test "${name} ejecutable" true
    else
        test "${name} ejecutable" false
    fi
done
echo ""

# === 4. Sin secretos hardcodeados ===
echo "--- Secrets Scan ---"
SECRET_PATTERNS=(
    'sk-[a-zA-Z0-9]{20,}'      # OpenAI keys
    'ghp_[a-zA-Z0-9]{20,}'     # GitHub PAT
    'gho_[a-zA-Z0-9]{20,}'     # GitHub OAuth
    'AKIA[0-9A-Z]{16}'         # AWS keys
    'AIza[0-9A-Za-z_-]{20,}'   # Google API
    'xox[baprs]-[0-9A-Za-z-]{10,}' # Slack tokens
)

for script in "${shell_scripts[@]}"; do
    name=$(basename "$script")
    found=false
    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -Pq "${pattern}" "$script" 2>/dev/null; then
            test "${name}: secreto detectado" false "match: ${pattern}"
            found=true
            break
        fi
    done
    if [ "$found" = false ]; then
        test "${name}: sin secretos" true
    fi
done
echo ""

# === 5. Go source check ===
echo "--- Go Source ---"
go_count=$(ls "${VAULT_DIR}"/bin/*.go 2>/dev/null | wc -l)
if [ "$go_count" -gt 0 ]; then
    readarray -t go_files < <(ls "${VAULT_DIR}"/bin/*.go 2>/dev/null)
    for f in "${go_files[@]}"; do
        name=$(basename "$f")
        if command -v go &>/dev/null; then
            if go vet "$f" 2>/dev/null; then
                test "${name} go vet" true
            else
                test "${name} go vet" false
            fi
        else
            test "${name} go vet" false "go no instalado"
        fi
    done
else
    echo "  (no hay archivos Go para testear)"
fi
echo ""

# === Resumen ===
TOTAL=$((PASS + FAIL))
echo "================"
echo "RESUMEN: ${TOTAL} tests | ✅ ${PASS} passed | ❌ ${FAIL} failed"
echo "================"

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "Errores:"
    for e in "${ERRORS[@]}"; do
        echo "  ❌ ${e}"
    done
    exit 1
fi

echo "🎉 Scripts check passed"
