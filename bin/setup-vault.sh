#!/usr/bin/env bash
# opencode-obsidian vault setup script
# Run this ONCE before opening Obsidian for the first time.
# Usage: bash bin/setup-vault.sh [optional: /path/to/vault]
# Default: uses the directory where this script lives (the vault root)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT="${1:-$(dirname "$SCRIPT_DIR")}"
OBSIDIAN="$VAULT/.obsidian"

echo "Setting up opencode-obsidian vault at: $VAULT"

# ── 1. Create directories ─────────────────────────────────────────────────────
mkdir -p "$OBSIDIAN/snippets"
mkdir -p "$VAULT/.raw"
mkdir -p "$VAULT/wiki/concepts" "$VAULT/wiki/entities" "$VAULT/wiki/sources" "$VAULT/wiki/meta"
mkdir -p "$VAULT/_templates"

# ── 2. Write graph.json ───────────────────────────────────────────────────────
cat > "$OBSIDIAN/graph.json" << 'EOF'
{
  "collapse-filter": false,
  "search": "path:wiki",
  "showTags": false,
  "showAttachments": false,
  "hideUnresolved": true,
  "showOrphans": false,
  "collapse-color-groups": false,
  "colorGroups": [
    { "query": "path:wiki/entities",    "color": { "a": 1, "rgb": 12945088 } },
    { "query": "path:wiki/concepts",    "color": { "a": 1, "rgb": 5227007  } },
    { "query": "path:wiki/sources",     "color": { "a": 1, "rgb": 6986069  } },
    { "query": "path:wiki/meta",        "color": { "a": 1, "rgb": 5676246  } },
    { "query": "path:wiki",             "color": { "a": 1, "rgb": 5676246  } }
  ],
  "showArrow": true,
  "textFadeMultiplier": -1,
  "nodeSizeMultiplier": 1.8,
  "lineSizeMultiplier": 1.2,
  "centerStrength": 0.5,
  "repelStrength": 30,
  "linkStrength": 1.5,
  "linkDistance": 120,
  "scale": 1.0
}
EOF

# ── 3. Write app.json (excluded files) ───────────────────────────────────────
cat > "$OBSIDIAN/app.json" << 'EOF'
{
  "userIgnoreFilters": [
    "agents/",
    "commands/",
    "hooks/",
    "skills/",
    "_templates/",
    "README.md",
    "CLAUDE.md",
    "WIKI.md",
    "Welcome.md"
  ]
}
EOF

# ── 4. Write appearance.json (enable CSS snippets) ───────────────────────────
cat > "$OBSIDIAN/appearance.json" << 'EOF'
{
  "enabledCssSnippets": [
    "vault-colors",
    "ITS-Dataview-Cards",
    "ITS-Image-Adjustments"
  ]
}
EOF

# ── 5. Download Excalidraw main.js (8MB, not in git) ─────────────────────────
EXCALIDRAW="$OBSIDIAN/plugins/obsidian-excalidraw-plugin"
if [ -f "$EXCALIDRAW/manifest.json" ] && [ ! -f "$EXCALIDRAW/main.js" ]; then
  EXCALIDRAW_VERSION="2.22.0"
  EXCALIDRAW_SHA256="8f7d5dc538228020805a255db9615ba2fdb82a9c0e6081f1b37ee7c2750ab37e"
  MANIFEST_VERSION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$EXCALIDRAW/manifest.json")"
  if [ "$MANIFEST_VERSION" != "$EXCALIDRAW_VERSION" ]; then
    echo "Error: Excalidraw manifest is $MANIFEST_VERSION but setup pins $EXCALIDRAW_VERSION. Update the release pin and checksum before downloading." >&2
    exit 1
  fi
  echo "Downloading pinned Excalidraw $EXCALIDRAW_VERSION main.js (~8MB)..."
  EXCALIDRAW_TEMP="$(mktemp "$EXCALIDRAW/main.js.tmp.XXXXXX")"
  trap 'rm -f -- "$EXCALIDRAW_TEMP"' EXIT
  curl --fail --show-error --silent --location \
    "https://github.com/zsviczian/obsidian-excalidraw-plugin/releases/download/$EXCALIDRAW_VERSION/main.js" \
    -o "$EXCALIDRAW_TEMP"
  ACTUAL_SHA256="$(python3 - "$EXCALIDRAW_TEMP" <<'PYTHON'
import hashlib, sys
h = hashlib.sha256()
with open(sys.argv[1], 'rb') as artifact:
    for chunk in iter(lambda: artifact.read(1024 * 1024), b''):
        h.update(chunk)
print(h.hexdigest())
PYTHON
)"
  if [ "$ACTUAL_SHA256" != "$EXCALIDRAW_SHA256" ]; then
    echo "Error: Excalidraw checksum mismatch; the downloaded file was discarded." >&2
    exit 1
  fi
  mv -- "$EXCALIDRAW_TEMP" "$EXCALIDRAW/main.js"
  trap - EXIT
  echo "✓ Excalidraw main.js downloaded"
elif [ -f "$EXCALIDRAW/main.js" ]; then
  echo "✓ Excalidraw main.js already present"
fi

echo ""
echo "✓ Setup complete."
echo ""
echo "Next steps:"
echo "  1. Open Obsidian"
echo "  2. Manage Vaults → Open folder as vault → select: $VAULT"
echo "  3. Enable community plugins when prompted (Calendar, Thino, Excalidraw, Banners are pre-installed)"
echo "  4. Install: Dataview, Templater, Obsidian Git  (Settings → Community Plugins)"
echo "  5. Type /wiki in Claude Code to scaffold your knowledge base"
echo ""
echo "Pre-installed plugins:"
echo "  - Calendar (sidebar calendar with word count + task dots)"
echo "  - Thino (quick memo capture)"
echo "  - Excalidraw (freehand drawing + image annotation)"
echo "  - Banners (add banner: to any note frontmatter for header images)"
echo ""
echo "CSS snippets enabled:"
echo "  - vault-colors: color-codes wiki/ folders in file explorer"
echo "  - ITS-Dataview-Cards: use \`\`\`dataviewjs with .cards for card grids"
echo "  - ITS-Image-Adjustments: append |100 to image embeds for sizing"
echo ""
echo "Views available:"
echo "  - Wiki Map canvas (wiki/Wiki Map.canvas) — knowledge graph"
echo "  - Design Ideas canvas (projects/visual-vault/design-ideas.canvas) — visual reference board"
echo "  - Graph view filtered to wiki/ only, color-coded by type"
echo ""
echo "To switch to the visual layout (Canvas + Calendar + Thino sidebar):"
echo "  Quit Obsidian, then run:"
echo "    cp $OBSIDIAN/workspace-visual.json $OBSIDIAN/workspace.json"
echo "  Then reopen Obsidian."
echo ""
echo "Graph colors: if they reset after closing Obsidian, open Graph settings"
echo "→ Color groups and re-add them once. They persist permanently after that."
