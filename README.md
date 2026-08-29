# opencode-obsidian (Bunker OS)

<p align="center">
  <img src="wiki/meta/banner-opencode-obsidian.png" alt="Bunker OS" width="100%" />
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"></a>
  <a href="PROJECT.md"><img src="https://img.shields.io/badge/Version-v1.4.0-blue?style=flat-square" alt="Version"></a>
  <a href="Makefile"><img src="https://img.shields.io/badge/Tests-passing-brightgreen?style=flat-square" alt="Tests"></a>
  <a href=".github/workflows/test.yml"><img src="https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat-square&logo=githubactions" alt="CI"></a>
  <a href="automation/n8n-lab"><img src="https://img.shields.io/badge/n8n-Automation-8B5CF6?style=flat-square" alt="n8n"></a>
  <a href="https://opencode.ai"><img src="https://img.shields.io/badge/OpenCode-Ready-8B5CF6?style=flat-square" alt="OpenCode"></a>
  <a href="https://obsidian.md"><img src="https://img.shields.io/badge/Obsidian-Vault-7C3AED?style=flat-square&logo=obsidian" alt="Obsidian"></a>
</p>

<p align="center">
  <b>Bunker OS</b> is a local-first knowledge operating system built on Obsidian.<br>
  It turns AI sessions, research, audits, evidence, and decisions into persistent operational assets —<br>
  automation via n8n, text retrieval via SQLite FTS5 + BM25, and a full orchestration pipeline for OpenCode.
</p>

<p align="center">
  Based on the <a href="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f">LLM Wiki pattern</a> by Andrej Karpathy · forked from <a href="https://github.com/AgriciDaniel/claude-obsidian">claude-obsidian</a>
</p>

<p align="center">
  <img src="wiki/meta/description.png" alt="Bunker OS Overview" width="100%" />
</p>

<br>

## Table of Contents

- [Why Bunker OS](#why-bunker-os)
- [Key Features](#key-features)
- [vs claude-obsidian](#vs-claude-obsidian)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [Skills](#skills)
- [n8n Automation](#n8n-automation)
- [Architecture](#architecture)
- [BM25 Text Retrieval](#bm25-text-retrieval)
- [Testing](#testing)
- [Repository Structure](#repository-structure)
- [FAQ](#faq)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

---

## Why Bunker OS

| Capability | Bunker OS | claude-obsidian | Smart Connections |
|---|:---:|:---:|:---:|
| Self-organizing wiki | Creates entities, concepts | ✅ | ❌ |
| n8n automation | Async + webhooks + DLQ | ❌ | ❌ |
| Autoresearch | 3-round web with gaps | ✅ | ❌ |
| Text retrieval | SQLite FTS5 + BM25 (incremental, zero deps) | BM25 + API | ❌ |
| Thinking framework | 10 principles | ✅ | ❌ |
| Tests + CI | 6 suites, GitHub Actions | ✅ | ❌ |
| Dead Letter Queue | Global error handler | ❌ | ❌ |
| Evidence vault | SHA256 checksums | ❌ | ❌ |
| Multi-channel alerts | Slack / Telegram / Discord (HMAC-signed) | ❌ | ❌ |
| Health monitoring | Active n8n workflow | ❌ | ❌ |
| Security & Guardrails | Anti-Prompt-Injection + HMAC Webhooks | ❌ | ❌ |
| Multi-methodology | ❌ (generic only) | LYT / PARA / Zettelkasten | ❌ |
| Multi-writer safe | ✅ (POSIX `fcntl.flock` + atomic rename) | Per-file locks | ❌ |
| Open source | MIT | MIT | Freemium |

> **Note on Smart Connections:** This column includes [Smart Connections](https://github.com/brianpetro/obsidian-smart-connections), an Obsidian community plugin that enables semantic search and RAG over vault notes. It is included for comparison as a complementary tool that works alongside Bunker OS. Bunker OS uses BM25 (keyword-based); Smart Connections uses vector embeddings (semantic). Both can run in the same vault.

> Bunker OS does not compete with claude-obsidian — it complements it. Where claude-obsidian is a researcher, Bunker OS is an operator. Both can coexist pointing at the same vault.

---

## Key Features

### 🧠 Knowledge

- **Persistent wiki** — 200+ pages of concepts, entities, sources, blueprints, and projects
- **Autoresearch** — 3-round autonomous web research: decomposes topics, searches, cross-references sources, and files everything into the wiki
- **SQLite FTS5 + BM25 search** — fast keyword and full-text search with incremental SHA-256 caching (`.vault-meta/fts5_index.db`), pure Python stdlib, zero external dependencies
- **`/think`** — 10-principle decision framework for architectural decisions and audits
- **Wiki-ingest** — source ingestion with automatic entity and concept extraction
- **Wiki-lint** — health check across 8 categories (orphans, dead links, missing frontmatter)

### ⚙️ Automation (n8n)

- **AOC v4 Enterprise** — pipeline: webhook → AI triage (OpenRouter) → GitHub issues → multi-channel notifications
- **Dead Letter Queue** — global error trigger that catches errors from *all* workflows
- **Health Check** — active workflow monitoring system status every 5 min
- **Ultimate Alerter** — multi-channel alerts (Slack / Telegram / Discord) with HMAC-SHA256 signature verification
- **Emergency Reprocessor** — auto-retry of failed events every 5 min

### 🛡️ Operations & Security

- **Multi-writer concurrency** — POSIX advisory locking (`fcntl.flock`) and atomic file replacement (`scripts/vault_lock.py`, `bin/vault-lock.sh`)
- **Defensive ingestion** — pre-ingest prompt injection sanitizer (`scripts/sanitize_ingest.py`) stripping invisible tokens, malicious HTML, and override directives
- **Webhook security** — HMAC-SHA256 signature generation (`bin/bunker-alert.sh`) for tamper-proof alerting
- **Test automation** — 6 suites (`make test` including `test-unit`), GitHub Actions CI on every push/PR
- **Evidence vault** — `report.zip` and `security-audit-report.json` indexed with SHA256
- **Integrity engine** — automated vault health scripts with Markdown + JSON reports
- **Command Center** — dashboard + agent queue + handovers + governance
- **OpenCode hooks** — `SessionStart` (reads `hot.md`), `PostCompact` (reloads after compaction), `Stop` (auto-updates `hot.md`)
- **13 OpenCode skills** ready to use

---

## vs claude-obsidian

| Dimension | Bunker OS | claude-obsidian |
|---|---|---|
| Version | v1.4.0 | v1.9.2 |
| Purpose | Operations + automation + security | PKM / second brain |
| Harness | OpenCode | Claude Code (plugin) |
| Language | English | English |
| Skills | 13 operational | 15 research |
| Async automation | n8n on Docker | None |
| Text retrieval | SQLite FTS5 + BM25 (incremental, stdlib) | BM25 + API + rerank |
| Tests | 6 suites (unit + integration + CI) | ~1,240 (9 suites) |
| Evidence checksums | ✅ | ❌ |
| Dead Letter Queue | ✅ | ❌ |
| Multi-channel alerts | Slack / Telegram / Discord (HMAC-SHA256) | ❌ |
| Security sanitization | Pre-ingest anti-injection | ❌ |
| Multi-methodology | ❌ | LYT / PARA / Zettelkasten |
| Multi-writer safe | ✅ (`fcntl.flock` + atomic rename) | ✅ |
| Plugin marketplace | ❌ | Claude Code plugin |
| Stars | — | 8.5k |

---

## Quick Start

### Option 1 — Clone as vault (recommended)

```bash
git clone https://github.com/Haiagari/opencode-obsidian.git
cd opencode-obsidian
```

Open the folder in **Obsidian**: *Manage Vaults → Open folder as vault → select `opencode-obsidian/`*.

Open **OpenCode** in the same folder, then start with `autoresearch` or `ingest [file]`.

### Option 2 — Reference from another project

Add to your `AGENTS.md`:

```markdown
## Wiki Knowledge Base
Path: /path/to/opencode-obsidian

When you need context:
1. Read wiki/hot.md first (recent context)
2. If not enough, read wiki/index.md
3. Only then read individual wiki pages
```

---

## Commands

### OpenCode Skills

| Command | Action |
|---|---|
| `autoresearch [topic]` | 3-round autonomous web research. Decomposes, searches, files |
| `retrieve [query]` | BM25 text search over wiki (no LLM needed for indexing) |
| `think [problem]` | 10-principle decision framework |
| `ingest [file]` | Ingest source: extract entities and concepts, create pages |
| `ingest all of these` | Batch ingestion with parallel processing |
| `what do you know about X` | Query the wiki: hot → index → pages → synthesize |
| `lint the wiki` | Health check: orphans, dead links, gaps |
| `save this` | Save current conversation as a wiki note |
| `wiki [setup/scaffold]` | Set up vault structure or create new knowledge base |
| `defuddle https://...` | Clean web page before ingesting; remove ads/boilerplate |
| `canvas` | Open or create visual canvas |
| `canvas add image [path]` | Add image to canvas |
| `index evidence` | Index audit artifacts (report.zip, JSON) with SHA256 checksums |
| `obsidian bases` | Create/edit Obsidian Bases (.base) database views |

#### CLI Scripts

```bash
make test                              # 6 suites (unit + integration)
./bin/bunker-check.sh                  # Local definition of done
./bin/wiki-integrity.sh                # Scan for orphans and broken links
./bin/evidence-index.sh                # Index evidence with SHA256
./bin/vault-lock.sh append wiki/log.md # Concurrency-safe atomic append
./bin/bunker-alert.sh target info "msg"# Send HMAC-SHA256 signed alert to n8n
./bin/bunker.sh init                   # Vault health check
./bin/wiki-sync.sh --apply             # Sync + commit wiki
python3 scripts/fts_engine.py index    # SQLite FTS5 incremental indexation
python3 scripts/fts_engine.py "query"  # SQLite FTS5 + BM25 ranked search
python3 scripts/sanitize_ingest.py doc # Pre-ingest prompt injection check
python3 scripts/retrieve.py "query"    # Legacy BM25 text retrieval
```

### `autoresearch` — autonomous research loop

Configurable at `skills/autoresearch/references/program.md`:

- Max rounds: 3
- Max pages per session: 15
- Source preference (academic, official, news)
- Confidence scoring (high/medium/low)
- Domain-specific rules

**Research flow:**
1. Round 1 — Broad search: Decompose into 3-5 angles, 2-3 queries each via Exa
2. Round 2 — Gap fill: Targeted searches for contradictions & gaps
3. Round 3 — Synthesis: One more pass if gaps remain
4. File to wiki

URL validation + content sanitization: rejects `file://` / `javascript://` / RFC1918, escapes `[[` in external sources, truncates to 50KB.

### `think` — 10-principle decision framework

```bash
think <problem statement>
```

Walks through 10 stages:

`OBSERVE (external)` → `OBSERVE (internal)` → `LISTEN` → `THINK` → `CONNECT (lateral)` → `CONNECT (system)` → `FEEL` → `ACCEPT` → `CREATE` → `GROW`

Use for non-trivial architectural decisions, audits, and post-mortems.

---

## Skills

*13 bundled in this repo + 6 provided by the ECC global config*

### Bundled in this repo

| Skill | Description |
|---|---|
| `autoresearch` | 3-round web research with Exa + webfetch |
| `wiki-retrieve` | BM25 & SQLite FTS5 text retrieval (stdlib Python, zero deps) |
| `think` | 10-principle decision framework |
| `wiki-ingest` | Ingest sources into the wiki |
| `wiki-query` | Query the wiki with synthesis |
| `wiki-lint` | Vault health check |
| `save` | Save conversation as wiki note |
| `wiki` | Wiki orchestrator (setup, scaffold, routing) |
| `canvas` | Obsidian canvas visual layer |
| `defuddle` | Web extraction wrapper |
| `evidence-index` | Evidence indexing with SHA256 |
| `obsidian-bases` | Obsidian Bases schema reference |
| `obsidian-markdown` | Obsidian Flavored Markdown reference |

### Provided by ECC global config

Not bundled in the repo, but available when the ECC skill bundle is installed.

*Note: ECC = Enterprise Cloud Config (or Enterprise Command Center). Define this in AGENTS.md or docs.*

| Skill | Description |
|---|---|
| `code-review` | Code quality review |
| `security-review` | OWASP security review |
| `infra-design` | Infrastructure design |
| `tdd-workflow` | TDD with red-green-refactor |
| `verification-loop` | Build + test + lint + security pre-PR |
| `work-unit-commits` | Commits organized by work unit |

---

## n8n Automation

n8n is the Bunker's async "nervous system." It runs on Docker and exposes an MCP bridge for OpenCode.

### Available Workflows

| Workflow | Nodes | Status | Description |
|---|:---:|---|---|
| Health Check | 2 | 🟢 Active | System health check every 5 min |
| Ultimate Alerter | 2 | 🟢 Active | Multi-channel alert via webhook (HMAC-SHA256) |
| Dead Letter Queue | 5 | ⚪ Inactive | Error trigger: captures all workflow errors |
| AOC v4 Enterprise | 37 | ⚪ Inactive | Pipeline: webhook → AI triage → GitHub → ... |

### AOC v4 Enterprise Pipeline

**Flow steps:**

1. **Ingress** — Webhook received → Ingress Guard validates → Check for replay via Redis
2. **Decision** — If replay detected: return cached response
3. **Triage** — If new: send to AI Triage (OpenRouter) for classification
4. **Routing** — Parse AI decision:
   - Create issue? → GitHub API
   - Review needed? → HITL queue
   - Emergency? → Emergency queue
   - Duplicate? → Skip
5. **Notifications** — Build notification message → Send via Slack, Telegram, Discord (parallel)
6. **Audit** — Write audit log → Return final status

**Diagram simplified (26 nodes represented) — workflow real tiene 37 nodos, ver `automation/n8n-lab/workflows/bunker-aoc-v4-enterprise.json` para el flujo completo con todos los pasos de validación y logging por canal.**

### Dead Letter Queue

**Flow:**

- Global Error Trigger captures errors from any workflow
- Normalizes error context
- Classifies severity: CRITICAL (auth, timeout, permissions) vs WARNING
- Stores in `staticData` (last 200 errors)
- Triggers notifications on CRITICAL

Catches errors from **any** workflow in the instance. Persists the last 200 errors for review and audit.

### Infrastructure

Configure environment variables in `automation/n8n-lab/.env`:

```yaml
N8N_CONCURRENCY_PRODUCTION_LIMIT=20   # High concurrency limit tuned for production
EXECUTIONS_DATA_PRUNE=true            # Auto cleanup
EXECUTIONS_DATA_MAX_AGE=168           # Keep execution data for 7 days
EXECUTIONS_DATA_PRUNE_MAX_COUNT=50000 # Max pruned execution entries
N8N_METRICS=true                      # Observability
N8N_LOG_FORMAT=json                   # Structured logs
```

Environment: PostgreSQL recommended, queue mode with Redis for horizontal scaling.

---

## Architecture

### Vault flow

```
.raw/ (untrusted source documents)
  ↓
sanitize_ingest.py (prompt injection / hidden tag neutralization)
  ↓
wiki-ingest (OpenCode skill with atomic vault locking)
  ↓ (extracts entities, concepts, sources)
wiki/ (persistent knowledge)
  ├── hot.md (recent context ~500 words)
  ├── index.md (master catalog)
  ├── log.md (append-only operation log via vault_lock.py)
  ├── sources/ (external source summaries)
  ├── entities/ (people, orgs, products)
  ├── concepts/ (ideas, patterns, frameworks)
  ├── meta/ (dashboards, handovers, evidence)
  └── ... (comparisons, questions, projects)
```

`wiki-ingest` extracts entities, concepts, and sources, then creates/updates pages and cross-references.

### Async automation & Security

```
OpenCode (skills) / Local CLI
  ├→ bin/bunker-alert.sh (HMAC-SHA256 signature)
  └→ n8n Docker (localhost:5678)
       ├→ Webhooks → AOC pipeline → GitHub Issues
       ├→ Schedule → Health Check (5 min)
       ├→ Schedule → Emergency Reprocessor (5 min)
       └→ Error Trigger → Dead Letter Queue
            ↓
         Notifications (Slack / Telegram / Discord)
```

---

## BM25 & SQLite FTS5 Text Retrieval

The Bunker includes a fast, zero-dependency text retrieval engine using SQLite FTS5 with native BM25 ranking (`-bm25(wiki_fts)`). No embeddings, no LLM calls, and zero external dependencies (pure Python standard library: `sqlite3`, `hashlib`).

OpenCode (the agent) receives the ranked chunks and applies its own model to understand and synthesize the answer. **The agent is the only intelligence in the loop.**

**Retrieval flow:**
```
Query
  ↓
SQLite FTS5 (`.vault-meta/fts5/vault_fts.db`) with BM25 Ranking
  ↓
Top K results (ranked by relevance)
  ↓
OpenCode reads & synthesizes
```

### Key Architectural Characteristics

- **Zero External Dependencies**: Built entirely on Python stdlib `sqlite3` with `PRAGMA journal_mode = WAL`.
- **Incremental Indexing**: Uses file modification times (`mtime`) and SHA-256 content hashes to only re-index modified or added notes.
- **Multilingual Tokenizer**: Uses `unicode61 remove_diacritics 2` for full-text search across English and Spanish.
- **High Performance**: Sub-millisecond keyword and BM25 ranking across thousands of chunks.

### Maintenance

```bash
# Build/update SQLite FTS5 incremental index
python3 scripts/fts_engine.py index

# Check status of index & tracked files
python3 scripts/fts_engine.py status

# Query via SQLite FTS5 engine
python3 scripts/fts_engine.py "n8n docker automation" --top 5
```

---

## Testing

### Suites

| Suite | Tests | What it validates |
|---|:---:|---|
| `test-workflows` | 186+ | All n8n JSONs parseable, valid connections, no orphans |
| `test-wiki` | 20+ | Essential files exist, valid frontmatter, docker running |
| `test-scripts` | 65+ | Bash syntax, shebang, executables, no secrets, `go vet` |
| `test-yaml` | 2 | CI and docker-compose YAML valid |
| `test-retrieve` | 2 | BM25 / FTS5 index exists, search returns results |
| `test-unit` | 11+ | Python unit tests (SQLite FTS5, POSIX File Locking, Prompt Sanitizer) |

### CI

Runs on every push/PR to `main` — 6 suites across Python + Go + bash.

```bash
make test    # Runs all 6 suites
```

### Secrets scanned

The test suite automatically checks for:

- OpenAI keys (`sk-...`)
- GitHub PAT (`ghp_...`, `gho_...`)
- AWS keys (`AKIA...`)
- Google API keys (`AIza...`)
- Slack tokens (`xox[baprs]-...`)

See [SECURITY.md](SECURITY.md) for the full security policy.

---

## Repository Structure

```
opencode-obsidian/
├── skills/                       13 repo skills + 6 ECC global
│   ├── autoresearch/             3-round autonomous research
│   ├── wiki-retrieve/            BM25 & FTS5 text retrieval
│   ├── think/                    10-principle framework
│   ├── wiki-ingest/              Source ingestion
│   ├── wiki-query/               Wiki querying
│   ├── wiki-lint/                Vault health check
│   ├── save/                     Save conversation
│   ├── wiki/                     Wiki orchestrator
│   ├── canvas/                   Visual canvas
│   ├── defuddle/                 Web extraction
│   ├── evidence-index/           Evidence indexing
│   ├── obsidian-bases/           Bases schema
│   └── obsidian-markdown/        OFM reference
├── agents/                       3 OpenCode agents
├── commands/                     Slash commands
├── hooks/
│   └── hooks.json                7 hooks across 4 events
├── scripts/                      Python + bash helpers
│   ├── fts_engine.py             SQLite FTS5 + BM25 incremental search engine
│   ├── vault_lock.py             POSIX advisory locking (`fcntl.flock`) & atomic ops
│   ├── sanitize_ingest.py        Pre-ingest prompt injection & payload sanitizer
│   ├── bm25-index.py             BM25 indexer
│   └── retrieve.py               Search orchestrator
├── tests/                        6 suites (unit + integration)
│   ├── test_workflow_connections.py
│   ├── test_wiki_integrity.sh
│   ├── test_scripts.sh
│   ├── test_fts_engine.py
│   ├── test_vault_lock.py
│   └── test_sanitize_ingest.py
├── Makefile                      Test targets & root runner
├── bin/                          16 shell scripts + Go source + binary
│   ├── bunker-check.sh           Full health check
│   ├── vault-lock.sh             CLI wrapper for atomic lock & write
│   ├── bunker-alert.sh           HMAC-SHA256 signed n8n alert trigger
│   ├── wiki-integrity.sh         Integrity scan
│   └── evidence-index.sh         Evidence indexing
├── automation/
│   └── n8n-lab/                  Docker + workflows (submodule)
│       ├── docker-compose.yml
│       ├── .env
│       └── workflows/
├── wiki/                         Obsidian vault (200+ pages)
│   ├── hot.md                    Recent context
│   ├── index.md                  Master catalog
│   ├── log.md                    Operation log
│   ├── sources/                  External sources
│   ├── entities/                 People, orgs, products
│   ├── concepts/                 Concepts and patterns
│   ├── meta/                     Dashboard, handovers, evidence
│   └── blueprints/               Architecture blueprints
├── .raw/                         Immutable source documents
├── .github/workflows/test.yml    CI: runs on push/PR
├── README.md                     This file
├── PROJECT.md                    Technical documentation
├── WIKI.md                       Wiki schema reference
├── BUNKER_RULES.md               Governance rules
├── AGENTS.md                     Agent instructions
├── CONTRIBUTING.md               Contribution guide
├── SECURITY.md                   Security policy
└── CHANGELOG.md                  Version history
```

---

## FAQ

<details>
<summary><b>What's the difference between Bunker OS and claude-obsidian?</b></summary><br>

Both projects share a common origin but diverged in purpose. claude-obsidian is a second brain for PKM/research. Bunker OS is an operations system with n8n automation, security, alerts, evidence, and dead letter queue handling. Use Bunker OS when you need async workflows + audit trails. Use claude-obsidian when you want to focus on research and note organization.

</details>

<details>
<summary><b>Can I use Bunker OS without OpenCode?</b></summary><br>

Technically yes (scripts are bash and Python, tests are Makefile, n8n is Docker), but the real value is in the OpenCode skills. Without OpenCode you lose autoresearch, think, wiki-ingest, and wiki-query.

</details>

<details>
<summary><b>Where is data stored?</b></summary><br>

Everything is local. The vault is a folder of Markdown files on your disk. n8n runs on local Docker. No cloud data.

</details>

<details>
<summary><b>How do I sync across devices?</b></summary><br>

The vault is a plain folder of files. Use Obsidian Sync, Syncthing, iCloud, Dropbox, or git.

</details>

<details>
<summary><b>How do I add a source to the wiki?</b></summary><br>

Drop the file in `.raw/` and say `ingest [filename]`. The skill extracts entities and concepts, creates pages, and updates indexes.

</details>

<details>
<summary><b>What is the Dead Letter Queue?</b></summary><br>

A global workflow that catches errors from any other n8n workflow. Classifies severity and persists to `staticData` for later review.

</details>

<details>
<summary><b>How do I activate the AOC v4 Enterprise?</b></summary><br>

Requires: OpenRouter API key, Discord webhook URL, and GitHub credentials in n8n.

**Steps:**
1. Set `OPENROUTER_API_KEY`, `DISCORD_WEBHOOK_URL`, `GITHUB_PAT` in `automation/n8n-lab/.env`
2. In n8n UI (http://localhost:5678), import the AOC v4 Enterprise JSON workflow
3. Toggle the workflow to "Active"
4. Check the Health Check dashboard to verify all channels are reachable

</details>

<details>
<summary><b>How do I rebuild the BM25 index after adding pages?</b></summary><br>

```bash
python3 scripts/retrieve.py build
```

</details>

<details>
<summary><b>Where are the tests?</b></summary><br>

```bash
make test    # 430 tests
```

</details>

---

## Requirements

| Component | Minimum | Notes |
|---|---|---|
| OpenCode | latest | https://opencode.ai |
| Obsidian | v1.6+ | Any modern version |
| Python | 3.10+ | For BM25 index + retrieve |
| Bash | 4.0+ | For operational scripts |
| Docker | latest | For n8n |
| Git | any | For vault versioning |

**Optional:**

- **ollama** — for local inference via OpenCode if configured
- **n8n** on Docker — for workflow automation
- **OpenRouter API key** — for AI triage in AOC v4

---

## Contributing

PRs welcome. Read first:

- [`PROJECT.md`](PROJECT.md) — technical documentation
- [`BUNKER_RULES.md`](BUNKER_RULES.md) — governance and standards
- [`CHANGELOG.md`](CHANGELOG.md) — version history

```bash
make test    # Run tests before pushing
```

---

## License

MIT License. See [LICENSE](LICENSE) for full text.

---

<p align="center">
  Based on the <a href="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f">LLM Wiki pattern</a> by Andrej Karpathy.
  <br>
  Built by <a href="https://github.com/Haiagari">Haiagari</a> for <a href="https://opencode.ai">OpenCode</a>.
  <br>
  <i>Compounding knowledge is the highest-leverage habit a thinking person can build.</i>
</p>
