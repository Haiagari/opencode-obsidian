#!/usr/bin/env bash
set -euo pipefail

# Updates repository description and topics only. Branch protection is managed
# separately in GitHub Settings and is intentionally never changed here.

REPO="${BUNKER_GITHUB_REPO:-Haiagari/opencode-obsidian}"
DESCRIPTION="Bunker OS: local-first personal knowledge workflow for an Obsidian vault."
TOPICS=(obsidian personal-knowledge local-first opencode knowledge-management)
MODE="${1:---dry-run}"

case "$MODE" in
  --dry-run)
    ;;
  --apply)
    command -v gh >/dev/null 2>&1 || {
      echo "Error: GitHub CLI (gh) is required for --apply." >&2
      exit 1
    }
    ;;
  *)
    echo "Usage: $0 [--dry-run|--apply]" >&2
    exit 2
    ;;
esac

printf 'Repository: %s\n' "$REPO"
printf 'Description: %s\n' "$DESCRIPTION"
printf 'Topics: %s\n' "${TOPICS[*]}"
echo "Branch protection: unchanged"

if [[ "$MODE" == "--dry-run" ]]; then
  echo "Dry run only. Re-run with --apply to update repository metadata."
  exit 0
fi

args=(repo edit "$REPO" --description "$DESCRIPTION")
for topic in "${TOPICS[@]}"; do
  args+=(--add-topic "$topic")
done

gh "${args[@]}"
echo "Repository metadata updated. Branch protection was not changed."
