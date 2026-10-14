# Daily knowledge workflow

[Documentation](README.md) · [Commands & skills](commands-and-skills.md) · [Troubleshooting](troubleshooting.md)

Capture useful material, review it, connect it to existing notes, and retrieve it when needed. You can curate Markdown manually in Obsidian or use OpenCode to assist. The local staging command and capture API collect input; they do not perform the agent's filing work.

![Sources and memos pass through review before becoming connected, retrievable knowledge](diagrams/knowledge-workflow.png)

*The existing illustration shows the working loop. The vault-shaped container represents storage, not encryption or a security guarantee.*

## First complete knowledge loop

Use a harmless local Markdown source to verify the whole path before adding personal material. From the repository root:

```bash
example_dir="$(mktemp -d)"
cat > "$example_dir/bunker-demo-source.md" <<'NOTE'
# Bunker demo: deployment checklist
Before deployment, record the change, check rollback steps,
and verify that service health is observable.
NOTE
bash bin/bunker-ingest.sh "$example_dir/bunker-demo-source.md"
```

Expected output includes `Sanitized source staged at .raw/bunker-demo-source.md`. A second staging attempt with that filename is refused, even if the input changed; keep the staged copy or deliberately choose another source filename.

### Review and file it

In OpenCode, request:

```text
ingest .raw/bunker-demo-source.md
Focus on deployment checks and rollback. Reuse relevant existing notes.
Keep source provenance and report the pages changed.
```

The `wiki-ingest` skill checks previously processed source hashes, sanitizes a temporary analysis copy, looks for existing pages, and creates or updates useful notes. It also instructs the agent to update the index, log, hot cache, and source manifest. Those are agent workflow instructions; the staging script does not execute them.

Review the resulting notes in Obsidian. Check that the source supports the claims, that existing pages were reused, and that links resolve. A short input may justify one page; no page quota is required.

Without OpenCode, create a Markdown source summary in `wiki/sources/`, link an existing concept or write a new one where justified, and add it to `wiki/index.md`. The [wiki schema](../WIKI.md) provides note templates. Keep facts, interpretation, and uncertainty distinguishable.

### Rebuild and retrieve

```bash
python3 scripts/retrieve.py build
python3 scripts/retrieve.py "rollback" --top 5
```

A filed page containing the term should appear in `candidates`. If only the staged `.raw/` file exists, an empty result is expected: source staging and wiki filing are separate steps. Open the returned `path`, read the full note, and follow its source reference.

Remove the temporary input directory when finished; the staged source and filed notes remain available for review.

## Where knowledge belongs

| Material | Destination | Review question |
|---|---|---|
| Local input staged for analysis | `.raw/` | Is the input suitable to process? |
| Short API capture | `wiki/inbox/` | Should this memo become a note, task, decision, or nothing? |
| External-source summary | `wiki/sources/` | Does it identify the source and distinguish evidence from interpretation? |
| Reusable explanation | `wiki/concepts/` | Does it add knowledge beyond an existing concept? |
| Person, project, organization, or tool | `wiki/entities/` | Will this entity matter in future queries? |
| Saved analysis | `wiki/questions/` | Does the answer cite the notes supporting it? |
| Decision/session from `save` | `wiki/meta/` | Does it preserve rationale and next steps? |

The `save` skill places decisions and session summaries in `wiki/meta/`; that folder is excluded from default FTS indexing. Read those notes through the index/hot cache or directly. See [Wiki schema](../WIKI.md) for the full conventions and privacy distinctions.

## Search with purpose

```bash
python3 scripts/retrieve.py status
python3 scripts/retrieve.py "deployment" --top 5
python3 scripts/retrieve.py "deployment rollback" --top 3
```

Search is lexical, with prefix matching and BM25 ranking. Multiple terms narrow the query because the engine joins them with the default FTS conjunction. If results disappear, start with one distinctive term. Search does not infer synonyms or run semantic embeddings.

The JSON result includes a note path, title, chunk position, score, and preview. Scores compare matches within a query; they are not probabilities or confidence judgments. Refresh after filing, editing, deleting, or moving notes.

For synthesis in OpenCode:

```text
what do you know about deployment rollback?
Compare the relevant wiki notes and cite the evidence for each recommendation.
```

The agent should state gaps when the vault lacks evidence. A plausible answer without source support is not stored knowledge.

## Save a useful conversation

```text
save this as Deployment rollback decision
Preserve the decision, alternatives, evidence, and next action.
```

The `save` skill chooses a note type, links related pages, and updates context. Check the saved note rather than assuming all conversation content belongs in the vault. Keep reusable conclusions; avoid unnecessary personal or operational details.

## Resume a session

Read in this order:

1. `wiki/hot.md` for recent facts and active threads.
2. The latest local handover in `wiki/meta/handovers/`, if one exists.
3. `wiki/index.md` to locate relevant pages.
4. The source and concept notes needed for the current task.

A clean clone may have no handovers; they are local/private state. Hooks are runtime-dependent, so verify that context was read. See [Hooks](../hooks/README.md) for what the checked-in configuration actually does.

## Maintain without silently rewriting knowledge

```bash
bash bin/wiki-integrity.sh
python3 scripts/retrieve.py build
```

The integrity scan writes `wiki/meta/INTEGRITY-REPORT.md` and `.json`. Inspect broken links, orphan candidates, short notes, and missing metadata. A short note or orphan is a maintenance signal, not an instruction to delete it. The raw-source heuristic uses a separate ingestion log and can flag sources already processed by a skill manifest; confirm before repeating ingestion.

If two notes disagree, identify their source/date/context and flag the conflict on both pages. Resolve it deliberately instead of replacing the older claim without explanation.

Use `bin/vault-lock.sh` for cooperating writes to shared context/log files; see the [command reference](commands-and-skills.md#shared-file-writes).

## Review before committing

```bash
git status --short
git diff -- wiki/ docs/
git diff --cached
```

`bash bin/wiki-sync.sh` is a dry run. `--apply` stages a broad set of paths and creates a local commit; it does not push. Inspect what will be included before choosing to apply it. `bunker-push.sh` is a different optional utility that can publish changes.

Private inbox/source files may be ignored, while existing tracked notes remain public. Check tracked paths before writing private information; see [Security boundaries](security-boundaries.md).

## Optional capture and automation

The [Local Ingest API](local-ingest-api.md) is useful for short authenticated memos on the same machine. Review inbox notes before integrating them. The [n8n extension](N8N-SETUP.md) is separate and is not required for this loop; its webhook receivers remain inactive.
