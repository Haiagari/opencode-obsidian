#!/bin/bash
set -euo pipefail

BUNKER_HOME="${BUNKER_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$BUNKER_HOME"

FAIL=0

section() { printf '\n== %s ==\n' "$1"; }

section "Bash syntax"
if find bin extensions -type f -name '*.sh' -print0 | xargs -0 -r -n1 bash -n; then
  echo "OK: shell scripts parse."
else
  echo "FAIL: shell syntax issue."
  FAIL=1
fi

section "Go ingest server build"
if command -v go >/dev/null 2>&1; then
  if go build -o /tmp/bunker-ingest-check ./bin/ingest_server.go; then
    echo "OK: ingest server builds."
  else
    echo "FAIL: ingest server does not build."
    FAIL=1
  fi
else
  echo "SKIP: go not installed."
fi

section "Forbidden local secret file"
if git ls-files --error-unmatch .obsidian/plugins/obsidian-local-rest-api/data.json >/dev/null 2>&1; then
  echo "FAIL: .obsidian/plugins/obsidian-local-rest-api/data.json is tracked in git! Must be removed from git cache."
  FAIL=1
else
  echo "OK: Local REST API data.json is not tracked in git repository."
fi

section "Hard-coded vault path check"
NEEDLE="/home/""sam/opencode-obsidian"
if grep -RIn "$NEEDLE" bin README.md PROJECT.md AGENTS.md WIKI.md BUNKER_RULES.md docs wiki 2>/dev/null | grep -v 'wiki/meta/INTEGRITY-REPORT.json' | grep -v 'wiki/meta/INTEGRITY-REPORT.md'; then
  echo "FAIL: hard-coded legacy vault path remains."
  FAIL=1
else
  echo "OK: no hard-coded legacy vault path found in active docs/scripts."
fi

section "Evidence index"
if ./bin/evidence-index.sh; then
  echo "OK: evidence index and manifest generated."
else
  echo "FAIL: evidence index generation failed."
  FAIL=1
fi

section "Tracked Obsidian plugin state"
if git ls-files -- '.obsidian/plugins/*/data.json' | grep -q .; then
  echo "FAIL: plugin data.json files are tracked; remove local plugin state from the index."
  FAIL=1
else
  echo "OK: no Obsidian plugin data.json files are tracked."
fi

section "Wiki integrity"
if ./bin/wiki-integrity.sh; then
  echo "OK: integrity report generated."
else
  echo "FAIL: integrity scan failed."
  FAIL=1
fi

section "Summary"
if [[ "$FAIL" -eq 0 ]]; then
  echo "Bunker check passed."
else
  echo "Bunker check completed with failures."
fi
exit "$FAIL"
