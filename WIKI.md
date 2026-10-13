# WIKI.md — Bunker OS Wiki Schema

> OpenCode skills handle all of this automatically.
> This file is the reference. Read it to understand how the system works.
> Based on the LLM Wiki pattern by Andrej Karpathy.

---

## What This Is

You are maintaining a persistent, compounding wiki inside an Obsidian vault.
You don't just answer questions. You build and maintain a structured knowledge
base that gets richer with every source added and every question asked.
The human curates sources and asks questions. You do all the writing,
cross-referencing, filing, and maintenance.

The wiki is the product. Chat is just the interface.

The key difference from RAG: the wiki is a persistent artifact. Cross-references
are already there. Contradictions have been flagged. Synthesis already reflects
everything that was read. Knowledge compounds like interest.

---

## 0 — Bootstrap

### 0.1 Verify OpenCode

```bash
which opencode 2>/dev/null && echo "OpenCode installed" || echo "Install OpenCode: https://opencode.ai"
```

### 0.2 Verify Obsidian

```bash
# Linux
flatpak list 2>/dev/null | grep -i obsidian && echo "FOUND via flatpak" || \
which obsidian 2>/dev/null && echo "FOUND in PATH" || echo "NOT FOUND"
```

### 0.3 Open the vault in Obsidian

1. Open Obsidian
2. Manage Vaults → Open folder as vault
3. Select the repository folder

### 0.4 First steps in OpenCode

```
ingest .raw/some-file.md     # Ingest a source
/autoresearch [topic]         # Research a new topic
/think [decision]             # 10-principle framework
lint the wiki                 # Vault health check
```

### 0.5 Verify n8n (optional)

```bash
docker ps --filter name=n8n
# Should show n8n_meco_lab running
```

---

## 1 — Vault Structure

```
.raw/           → fuentes inmutables — nunca modificar
wiki/           → base de conocimiento generada por IA
_templates/     → Obsidian Templater templates
```

Standard wiki structure:

```
wiki/
├── index.md            → master catalog of all pages
├── log.md              → chronological operation log (append-only)
├── hot.md              → hot cache: recent context (~500 words)
├── overview.md         → executive summary of the whole wiki
├── sources/            → one summary per external source
│   └── _index.md       → sub-index
├── entities/           → people, orgs, products, repos
│   └── _index.md
├── concepts/           → ideas, patterns, frameworks
│   └── _index.md
│   └── tech-stack/     → technical concepts with code
├── comparisons/        → side-by-side analyses
├── blueprints/         → executable architecture blueprints
├── projects/           → live projects
├── questions/          → archived answers to user queries
├── decisions/          → ADR / AgDR
├── meta/               → dashboard, handovers, intelligence, reports
└── canvases/           → Obsidian canvases
```

Dot-prefixed folders (`.raw/`) are hidden in Obsidian's file explorer and graph view.

---

## 2 — Transport (obsidian-vault MCP)

All skills read and write using the vault MCP tools:

| Operation | MCP Tool |
|-----------|----------|
| Read note | `obsidian-vault_read_note` |
| Search notes | `obsidian-vault_search_notes` |
| Create/update | `obsidian-vault_write_note` |
| Surgical edit | `obsidian-vault_patch_note` |
| Update frontmatter | `obsidian-vault_update_frontmatter` |
| Get metadata | `obsidian-vault_get_notes_info` |
| List structure | `obsidian-vault_list_directory` |

Do NOT use Write/Edit for files inside `wiki/`. Always use MCP tools to maintain consistency with Obsidian.

---

## 3 — Hot Cache

`wiki/hot.md` is a ~500-word summary of the most recent context. It exists
so any session (or another project pointing at this vault) can get recent
context without crawling the full wiki.

Update hot.md:
- After every ingest
- After any significant query exchange
- At the end of every session
- After `/autoresearch`

Format:

```markdown
---
type: meta
title: "Hot Cache"
updated: YYYY-MM-DD
tags: [meta, hot-cache, context]
status: evergreen
related: []
---

# Recent Context — Bunker OS v1.3.1

## Current Focus
[One line on what is being worked on]

## Key Recent Facts
- [Relevant fact 1]
- [Relevant fact 2]

## Recent Changes
- Created: [[Page 1]], [[Page 2]]
- Updated: [[Page 3]]

## Active Threads
- Current research topic
- Next planned step
```

Keep it under 500 words. It is a cache, not a journal. Overwrite it completely each time.

---

## 4 — Ingestion

### Single source ingest flow

1. Read the source completely. Do not skim.
2. Ask the user: "What should I emphasize?"
3. Create summary in `wiki/sources/` with full frontmatter.
4. Create or update entity pages (people, orgs, products).
5. Create or update concept pages.
6. Update `wiki/index.md` with new pages.
7. Update `wiki/hot.md` with ingest context.
8. Prepend entry to `wiki/log.md` (newest at TOP).
9. Check for contradictions with existing pages.
10. If contradictions found: add `> [!contradiction]` callouts on both pages.

### Source frontmatter

```markdown
---
type: source
title: "Source Title"
source_type: article|paper|doc|url
author: "Author Name"
date_published: YYYY-MM-DD
url: "https://..."
confidence: high|medium|low
tags: [research, topic]
---
```

### Entity frontmatter

```markdown
---
type: entity
title: "Entity Name"
domain: tech-stack
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [entity]
status: active
related: []
sources: []
---
```

### Concept frontmatter

```markdown
---
type: concept
title: "Concept Name"
domain: tech-stack
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [concept]
status: mature|active|seed
related: []
sources: []
---
```

### Log entry

```
## [YYYY-MM-DD] ingest | Title
- Source: `.raw/filename.md`
- Pages created: [[Page 1]], [[Page 2]]
- Pages updated: [[Page 3]]
- Key insight: One sentence
```

---

## 5 — Query

Three depth modes:

| Mode | Trigger | Reads | Token cost | Best for |
|------|---------|-------|------------|---------|
| **Quick** | Simple factual question | hot.md + index.md | ~1,500 | "What is X?", dates, lookups |
| **Standard** | Default (no flag) | hot.md + index + 3-5 pages | ~3,000 | Most questions |
| **Deep** | "thorough", "exhaustive" | Full wiki + optional retrieve | ~8,000+ | Synthesis, gaps, comparisons |

### If retrieve is available

1. Try `python3 scripts/retrieve.py status` to check if the index exists
2. If it exists: `python3 scripts/retrieve.py "query" --top 5`
3. Read top pages with `obsidian-vault_read_note`
4. Synthesize with citations

### If retrieve is NOT available (legacy)

1. Read `wiki/hot.md`
2. If not enough: read `wiki/index.md`
3. If more is needed: read relevant domain pages
4. Synthesize with citations

### Citations

Always cite the exact source: `(Source: [[Page Name]])`.
Do not cite training data. If it is not in the wiki, you do not know it.

---

## 6 — Lint (maintenance)

Run every 10-15 ingests or when the user says "lint the wiki".

### Health check categories

1. **Orphans**: pages with no incoming or outgoing links
2. **Dead links**: wikilinks pointing to non-existent pages
3. **Short notes**: pages with fewer than 3 lines of content
4. **Missing frontmatter**: pages without YAML frontmatter
5. **Stale claims**: unresolved `[!contradiction]` markers
6. **Unlinked sources**: `.raw/` files not referenced in the wiki
7. **Broken cross-references**: pages mentioning entities without links

Also use:

```bash
./bin/wiki-integrity.sh        # Automated integrity script
python3 scripts/retrieve.py status  # Verify BM25 index is up to date
```

---

## 7 — Autoresearch

See `skills/autoresearch/SKILL.md` for full instructions.

### Summary

```
Input: topic

Round 1. Broad search: 3-5 angles × 2-3 queries × 2-3 fetches
Round 2. Gap fill: targeted searches for contradictions
Round 3. Synthesis: one more pass if gaps remain → file to wiki

Filing:
  wiki/sources/ — one page per source found
  wiki/concepts/ — significant concepts
  wiki/entities/ — people, orgs, products
  Synthesis page: "Research: [Topic]"
```

### Configuration

Edit `skills/autoresearch/references/program.md` to change:
- Source preference (academic, official, news)
- Confidence scoring (high/medium/low)
- Max rounds (default 3) and max pages (default 15)
- Domain-specific rules

### Web egress hygiene

- Reject `file://`, `javascript:`, RFC1918 addresses
- Escape `[[` in external sources
- Reject `---` frontmatter delimiters in fetched content
- Truncate to 50KB

---

## 8 — Think Framework

See `skills/think/SKILL.md` for full instructions.

```
/think <problema>

1. OBSERVE (external)  → read raw inputs before interpreting
2. OBSERVE (internal)  → bias log, metacognition
3. LISTEN             → listen to the user, signals in the noise
4. THINK              → first principles, cheapest experiment
5. CONNECT (lateral)  → patterns in neighboring domains
6. CONNECT (system)   → integration with hooks/scripts/tests
7. FEEL               → how it lands on the user, intuition
8. ACCEPT             → humility, do not inflate findings
9. CREATE             → ship the smallest artifact
10. GROW              → save the lesson so it compounds

Use for architectural decisions, audits, post-mortems.
Do NOT use for one-line fixes or trivial lookups.

---

## 9 — BM25 Text Retrieval

See `skills/wiki-retrieve/SKILL.md` for full instructions.

BM25 is a pure text-based ranking algorithm. No embeddings, no LLM, no external services. OpenCode reads the results and synthesizes answers.

### Pipeline

```
query → BM25 (wiki page chunks, ~500 tokens each) → ranked top 5 → OpenCode reads & synthesizes
```

### Maintenance

```bash
python3 scripts/retrieve.py build     # Build/update index
python3 scripts/retrieve.py status    # Check status
python3 scripts/retrieve.py "query" --top 5  # Search
```

### Index states

- **build**: builds the BM25 index from scratch
- **query**: searches the index with BM25
- **status**: shows current index state (pages, chunks, terms)

---

## 10 — Contradictions

When new information contradicts an existing wiki page:

On the existing page:
```markdown
> [!contradiction] Conflict with [[New Source]]
> [[Existing Page]] says X. [[New Source]] says Y.
> Needs resolution. Check dates and primary sources.
```

On the new page:
```markdown
> [!contradiction] Contradicts [[Existing Page]]
> This source says Y, but existing wiki says X.
```

Do not silently overwrite claims. Flag and let the user decide.

---

## 11 — n8n Operations

See `extensions/n8n/` for optional workflow files. Core wiki workflows do not require Docker or n8n.

### Available workflows

| Workflow | File | Status |
|----------|------|--------|
| Health Check | `bunker-health-check.json` | 🟢 Active |
| Ultimate Alerter | `bunker-ultimate-alerter.json` | 🟢 Active |
| Dead Letter Queue | `bunker-dead-letter-queue.json` | ⚪ Inactive |
| AOC v4 Enterprise | `bunker-aoc-v4-enterprise.json` | ⚪ Inactive |

### AOC v4 Enterprise

Complete 37-node pipeline:
1. Webhook Entry → Ingress Guard → IF Valid
2. Redis Idempotency → IF Replay
3. AI Triage (OpenRouter) → Parse AI Decision
4. IF Create → GitHub Issue / IF Review → Issue HITL / IF Emergency → Emergency Queue
5. Build Notification → Slack / Telegram / Discord
6. Write Audit → Final Status → Respond

### Dead Letter Queue

Global error trigger that catches errors from all workflows:
1. Error Trigger → Normalize Error → IF Critical?
2. CRITICAL → Notify → Store in DLQ
3. WARNING → Store in DLQ

Persists last 200 errors in staticData.

---

## 12 — Testing

### Suites

```bash
make test                    # 430 tests, 5 suites
make test-workflows          # 344 n8n connection tests
make test-wiki               # 21 vault integrity tests
make test-scripts            # 61 script tests
make test-yaml               # 2 YAML tests
make test-retrieve           # 2 BM25 tests
```

### CI

`.github/workflows/test.yml`: runs all suites on every push/PR to main.

---

## 13 — Compounding Knowledge

Golden rules:

1. **Always update index, log, and hot cache** after every operation
2. **Always use frontmatter and wikilinks** — `[[Note Name]]`, not paths
3. **Never modify `.raw/`** — sources are immutable
4. **New entries go to the TOP of log.md** (prepend, not append)
5. **hot.md is overwritten completely** — it is a cache, not a journal
6. **Do not create duplicate pages** — always check the index first
7. **Keep pages short: 100-300 lines** — if it grows, split it
8. **Flag contradictions, do not silence them**
9. **Use MCP tools** for all wiki write operations
10. **Run `make test` before committing** changes to skills/scripts/tests

---

> Compounding knowledge is the highest-leverage habit a thinking person can build.
