#!/bin/bash
set -euo pipefail
# opencode-obsidian setup.
# Installs the vault skills and registers the MCP vault path for OpenCode.

VAULT_DIR="${VAULT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
SKILLS_DIR="${SKILLS_DIR:-$HOME/.config/opencode/skills}"
OPENCODE_CONFIG="${OPENCODE_CONFIG:-$HOME/.config/opencode/opencode.json}"

cat <<MSG
========================================
  opencode-obsidian Setup
========================================
Vault:  $VAULT_DIR
Skills: $SKILLS_DIR
Config: $OPENCODE_CONFIG
MSG

if [[ ! -d "$VAULT_DIR/wiki" || ! -d "$VAULT_DIR/skills" ]]; then
  echo "❌ VAULT_DIR does not look like an opencode-obsidian vault: $VAULT_DIR" >&2
  exit 1
fi

# 1. Install skills.
echo "[1/4] Installing skills..."
mkdir -p "$SKILLS_DIR"
for skill in wiki wiki-ingest wiki-query save wiki-lint canvas autoresearch obsidian-markdown obsidian-bases defuddle; do
  if [[ -d "$VAULT_DIR/skills/$skill" ]]; then
    rm -rf "$SKILLS_DIR/$skill"
    cp -r "$VAULT_DIR/skills/$skill" "$SKILLS_DIR/"
    echo "  → installed $skill"
  fi
done

# 2. Configure MCP in opencode.json.
echo "[2/4] Configuring MCP..."
mkdir -p "$(dirname "$OPENCODE_CONFIG")"
if [[ ! -f "$OPENCODE_CONFIG" ]]; then
  printf '{\n  "mcp": {}\n}\n' > "$OPENCODE_CONFIG"
fi
cp "$OPENCODE_CONFIG" "$OPENCODE_CONFIG.backup.$(date +%Y%m%d%H%M%S)"

python3 - "$OPENCODE_CONFIG" "$VAULT_DIR" <<'PYTHON'
import json
import sys
from pathlib import Path

config_file = Path(sys.argv[1])
vault_dir = sys.argv[2]
try:
    config = json.loads(config_file.read_text())
except json.JSONDecodeError as exc:
    raise SystemExit(f"Invalid JSON in {config_file}: {exc}")

config.setdefault("mcp", {})
config["mcp"]["obsidian-vault"] = {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@bitbonsai/mcpvault@latest", vault_dir]
}
config_file.write_text(json.dumps(config, indent=2) + "\n")
PYTHON

echo "  → MCP configured for $VAULT_DIR"

# 3. Obsidian note.
echo "[3/4] Checking Obsidian..."
if command -v obsidian >/dev/null 2>&1; then
  echo "  → Obsidian installed. Open vault: obsidian \"$VAULT_DIR\""
else
  echo "  ⚠ Obsidian command not found. Open the vault manually in the Obsidian app."
fi

# 4. Final instructions.
echo "[4/4] Done."
echo "Next: restart OpenCode, open Obsidian, then read wiki/hot.md and wiki/meta/dashboard.md."
