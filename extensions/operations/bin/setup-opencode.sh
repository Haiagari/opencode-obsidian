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
    destination="$SKILLS_DIR/$skill"
    staging="$(mktemp -d "$SKILLS_DIR/.${skill}.install.XXXXXX")"
    backup=""
    if ! cp -a "$VAULT_DIR/skills/$skill" "$staging/$skill"; then
      rmdir "$staging"
      echo "❌ Could not stage skill $skill; existing installation was left intact." >&2
      exit 1
    fi
    if [[ -e "$destination" || -L "$destination" ]]; then
      backup_dir="$(mktemp -d "$SKILLS_DIR/.${skill}.backup.XXXXXX")"
      backup="$backup_dir/$skill"
      if ! mv "$destination" "$backup"; then
        rmdir "$backup_dir"
        rm -rf -- "$staging"
        echo "❌ Could not back up existing skill $skill; existing installation was left intact." >&2
        exit 1
      fi
    fi
    if ! mv "$staging/$skill" "$destination"; then
      if [[ -n "$backup" ]]; then mv "$backup" "$destination"; fi
      rm -rf -- "$staging"
      echo "❌ Could not install skill $skill; previous installation was restored." >&2
      exit 1
    fi
    rmdir "$staging"
    echo "  → installed $skill"
  fi
done

# 2. Configure MCP in opencode.json.
echo "[2/4] Configuring MCP..."
mkdir -p "$(dirname "$OPENCODE_CONFIG")"
if [[ ! -f "$OPENCODE_CONFIG" ]]; then
  printf '{\n  "mcp": {}\n}\n' > "$OPENCODE_CONFIG"
fi
CONFIG_BACKUP="$(mktemp "${OPENCODE_CONFIG}.backup.XXXXXX")"
cp -p "$OPENCODE_CONFIG" "$CONFIG_BACKUP"
echo "Config backup: $CONFIG_BACKUP"

python3 - "$OPENCODE_CONFIG" "$VAULT_DIR" <<'PYTHON'
import json
import os
import sys
import tempfile
from pathlib import Path

config_file = Path(sys.argv[1])
vault_dir = sys.argv[2]
try:
    config = json.loads(config_file.read_text())
except json.JSONDecodeError as exc:
    raise SystemExit(f"Invalid JSON in {config_file}: {exc}")

config.setdefault("mcp", {})
entry = config["mcp"].setdefault("obsidian-vault", {})
if not isinstance(entry, dict):
    raise SystemExit("mcp.obsidian-vault must be an object; existing config was not changed")
entry.update({
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@bitbonsai/mcpvault@0.16.0", vault_dir],
})
fd, temp_name = tempfile.mkstemp(prefix=f".{config_file.name}.", suffix=".tmp", dir=config_file.parent)
os.close(fd)
temp_file = Path(temp_name)
try:
    temp_file.write_text(json.dumps(config, indent=2) + "\n")
    temp_file.replace(config_file)
finally:
    temp_file.unlink(missing_ok=True)
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
