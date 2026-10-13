#!/bin/bash
set -euo pipefail
# wiki-integrity.sh — Bunker OS vault integrity scanner.
# Produces Markdown and JSON reports without modifying wiki content besides reports.

BUNKER_HOME="${BUNKER_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
VAULT_DIR="${BUNKER_VAULT_DIR:-$BUNKER_HOME/wiki}"
REPORT_FILE="${BUNKER_INTEGRITY_REPORT:-$VAULT_DIR/meta/INTEGRITY-REPORT.md}"
JSON_FILE="${BUNKER_INTEGRITY_JSON:-$VAULT_DIR/meta/INTEGRITY-REPORT.json}"
SHORT_NOTE_LIMIT="${BUNKER_SHORT_NOTE_LIMIT:-30}"

mkdir -p "$(dirname "$REPORT_FILE")"

python3 - "$BUNKER_HOME" "$VAULT_DIR" "$REPORT_FILE" "$JSON_FILE" "$SHORT_NOTE_LIMIT" <<'PY'
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1]).resolve()
vault = Path(sys.argv[2]).resolve()
report_path = Path(sys.argv[3]).resolve()
json_path = Path(sys.argv[4]).resolve()
short_limit = int(sys.argv[5])

wiki_link_re = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
frontmatter_re = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)
type_re = re.compile(r"^type:\s*([A-Za-z0-9_-]+)\s*$", re.M)

md_files = sorted(f for f in vault.rglob("*.md") if f.name not in {"INTEGRITY-REPORT.md"})
all_files = sorted(vault.rglob("*"))
relative = lambda p: str(p.relative_to(root))

lookup = {}
for f in all_files:
    if not f.is_file():
        continue
    suffix = f.suffix.lower()
    if suffix not in {".md", ".canvas", ".base", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".txt", ".json"}:
        continue
    stem_key = f.stem.lower()
    rel_no_suffix = str(f.relative_to(vault).with_suffix("")).replace(os.sep, "/").lower()
    rel_with_suffix = str(f.relative_to(vault)).replace(os.sep, "/").lower()
    for key in {stem_key, rel_no_suffix, rel_with_suffix}:
        lookup.setdefault(key, []).append(f)

def resolves(target: str) -> bool:
    t = target.strip().replace("\\", "/")
    if not t or t.startswith("http://") or t.startswith("https://"):
        return True
    key = t.lower()
    if key in lookup:
        return True
    if key.endswith(".md") and key[:-3] in lookup:
        return True
    return False

incoming = {f: 0 for f in md_files}
broken_links = []
wikilink_refs = []
file_types = {}

for f in md_files:
    rel_f = relative(f)
    text = f.read_text(errors="ignore")
    fm = frontmatter_re.match(text)
    file_type = None
    if fm:
        m = type_re.search(fm.group(0))
        if m:
            file_type = m.group(1).strip().lower()
    file_types[f] = file_type
    for match in wiki_link_re.finditer(text):
        target = match.group(1).strip()
        wikilink_refs.append({"from": relative(f), "target": target})
        if not resolves(target):
            if "/archive/" not in rel_f:
                broken_links.append({"from": relative(f), "target": target})
        else:
            for dest in lookup.get(target.lower(), []):
                if dest in incoming and dest != f:
                    incoming[dest] += 1

ignored_orphan_names = {"index.md", "hot.md", "log.md", "overview.md", "getting-started.md"}
orphans = []
for f, count in incoming.items():
    rel = relative(f)
    if count == 0 and "/meta/" not in rel and "/archive/" not in rel and f.name not in ignored_orphan_names and file_types[f] != "alias":
        orphans.append(rel)

short_notes = []
missing_frontmatter = []
for f in md_files:
    rel = relative(f)
    if "/archive/" not in rel and "/inbox/" not in rel and file_types[f] != "alias":
        lines = f.read_text(errors="ignore").splitlines()
        if len(lines) < short_limit:
            short_notes.append({"path": rel, "lines": len(lines)})
    if "/archive/" not in rel and not frontmatter_re.search(f.read_text(errors="ignore")):
        missing_frontmatter.append(rel)

raw_files = [relative(p) for p in sorted((root / ".raw").glob("*")) if p.is_file() and p.name != ".gitkeep"] if (root / ".raw").exists() else []
ingestion_log = root / "wiki" / "meta" / "ingestion-log.md"
ingestion_text = ingestion_log.read_text(errors="ignore") if ingestion_log.exists() else ""
unprocessed_raw = [p for p in raw_files if Path(p).name not in ingestion_text]

plugins_declared = []
plugins_missing = []
plugins_extra = []
community = root / ".obsidian" / "community-plugins.json"
plugins_dir = root / ".obsidian" / "plugins"
if community.exists():
    try:
        plugins_declared = json.loads(community.read_text())
    except json.JSONDecodeError:
        plugins_declared = []
    installed = sorted([p.name for p in plugins_dir.iterdir() if p.is_dir()]) if plugins_dir.exists() else []
    plugins_missing = sorted([p for p in plugins_declared if p not in installed])
    plugins_extra = sorted([p for p in installed if p not in plugins_declared])

sensitive_files = []
for p in root.rglob("*"):
    if not p.is_file():
        continue
    rel = relative(p)
    if rel.endswith("data.json") and ".obsidian/plugins/" in rel:
        sensitive_files.append(rel)
    if p.name in {".env", ".env.local"}:
        sensitive_files.append(rel)

absolute_paths = []
for base in [root / "bin", root / "docs", root / "wiki", root / "README.md", root / "PROJECT.md", root / "AGENTS.md", root / "WIKI.md", root / "BUNKER_RULES.md"]:
    paths = [base] if base.is_file() else sorted(base.rglob("*")) if base.exists() else []
    for p in paths:
        if not p.is_file() or p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ""} and p.name == "ingest_server":
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        needle = "/home/" + "sam/opencode-obsidian"
        if needle in text and p.name not in {"INTEGRITY-REPORT.md", "INTEGRITY-REPORT.json"}:
            absolute_paths.append(relative(p))

report = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "root": str(root),
    "vault": str(vault),
    "counts": {
        "markdown_files": len(md_files),
        "wikilinks": len(wikilink_refs),
        "broken_links": len(broken_links),
        "orphans": len(orphans),
        "short_notes": len(short_notes),
        "missing_frontmatter": len(missing_frontmatter),
        "unprocessed_raw": len(unprocessed_raw),
        "plugins_missing": len(plugins_missing),
        "local_config_files": len(sensitive_files),
        "absolute_path_files": len(set(absolute_paths)),
    },
    "broken_links": broken_links,
    "orphans": orphans,
    "short_notes": short_notes,
    "missing_frontmatter": missing_frontmatter,
    "raw_files": raw_files,
    "unprocessed_raw": unprocessed_raw,
    "plugins_declared": plugins_declared,
    "plugins_missing": plugins_missing,
    "plugins_extra": plugins_extra,
    "local_config_files": sorted(set(sensitive_files)),
    "absolute_path_files": sorted(set(absolute_paths)),
}

json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

lines = []
lines.append("# Bunker OS Integrity Report")
lines.append("")
lines.append(f"Generated: {report['generated_at']}")
lines.append("")
lines.append("## Summary")
lines.append("")
for k, v in report["counts"].items():
    lines.append(f"- {k}: {v}")
lines.append("")

lines.append("## Broken Links")
if broken_links:
    for item in broken_links[:200]:
        lines.append(f"- `{item['target']}` from `{item['from']}`")
    if len(broken_links) > 200:
        lines.append(f"- ... {len(broken_links)-200} more in JSON report")
else:
    lines.append("- None detected.")
lines.append("")

lines.append("## Orphan Notes")
if orphans:
    for item in orphans[:200]:
        lines.append(f"- `{item}`")
    if len(orphans) > 200:
        lines.append(f"- ... {len(orphans)-200} more in JSON report")
else:
    lines.append("- None detected.")
lines.append("")

lines.append(f"## Short Notes (< {short_limit} lines)")
if short_notes:
    for item in short_notes[:200]:
        lines.append(f"- `{item['path']}` ({item['lines']} lines)")
    if len(short_notes) > 200:
        lines.append(f"- ... {len(short_notes)-200} more in JSON report")
else:
    lines.append("- None detected.")
lines.append("")

lines.append("## Missing Frontmatter")
if missing_frontmatter:
    for item in missing_frontmatter[:200]:
        lines.append(f"- `{item}`")
    if len(missing_frontmatter) > 200:
        lines.append(f"- ... {len(missing_frontmatter)-200} more in JSON report")
else:
    lines.append("- None detected.")
lines.append("")

lines.append("## Raw Files Not Mentioned in Ingestion Log")
if unprocessed_raw:
    for item in unprocessed_raw:
        lines.append(f"- `{item}`")
else:
    lines.append("- None detected.")
lines.append("")

lines.append("## Plugin Drift")
lines.append(f"- Declared plugins: {', '.join(plugins_declared) if plugins_declared else 'none'}")
lines.append(f"- Missing declared plugins: {', '.join(plugins_missing) if plugins_missing else 'none'}")
lines.append(f"- Installed but undeclared plugins: {', '.join(plugins_extra) if plugins_extra else 'none'}")
lines.append("")

lines.append("## Local Plugin Config Files")
if sensitive_files:
    for item in sorted(set(sensitive_files)):
        lines.append(f"- `{item}`")
else:
    lines.append("- None detected.")
lines.append("")

lines.append("## Absolute Path References")
if absolute_paths:
    for item in sorted(set(absolute_paths)):
        lines.append(f"- `{item}`")
else:
    lines.append("- None detected.")
lines.append("")

lines.append("## Next Actions")
lines.append("- Resolve broken links that point to active notes, or document them as accepted archive debt.")
lines.append("- Expand short notes that are active knowledge assets.")
lines.append("- Keep plugin `data.json` files local only.")
lines.append("- Replace hard-coded local paths with `BUNKER_HOME` or relative paths.")

report_path.write_text("\n".join(lines) + "\n")
print(f"Integrity report updated: {report_path}")
print(f"Integrity JSON updated: {json_path}")
PY
