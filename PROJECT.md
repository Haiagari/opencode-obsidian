# opencode-obsidian — Bunker OS v1.3.1

This repository is an OpenCode agent environment and an Obsidian wiki vault.

**Version:** 1.3.1  
**Status:** Local-first operational knowledge system with n8n automation  
**Tests:** 430 (Makefile + GitHub Actions CI)  
**Vault path:** current repository root. Use `BUNKER_HOME` to override script resolution.

---

## Core Identity

Bunker OS is not a traditional application. It is a local-first knowledge operating system for:

- AI session continuity
- structured research (**autoresearch**, **/think** framework)
- audit evidence preservation (**SHA256 checksums**)
- project intelligence
- agent-guided workflow (**n8n AOC v4**, **Dead Letter Queue**)
- BM25 text retrieval (**zero-dependency, agent-synthesized**)
- governance and decisions
- visual command center operations

---

## Architecture Layers

```text
Capture       → wiki/inbox, .raw, ingest server, handovers
Normalize     → _templates, skills/wiki-ingest
Classify      → wiki/sources, entities, concepts, projects, comparisons
Evidence      → report.zip, security-audit-report.json, evidence index
Governance    → BUNKER_RULES, ADR template, knowledge supply chain
Automation    → bin/ (Sync ops) + n8n (Async flows, alerts, DLQ)
Retrieval     → BM25 index (pure Python, zero deps) + OpenCode synthesis
Testing       → 5 suites: workflows n8n, wiki integrity, scripts, YAML, retrieve
Agent Runtime → agents, commands, skills (13), hooks (7)
Visualization → dashboard, canvases, Obsidian graph
```

---

## v1.3.1 Changelog

### Added
- **Autoresearch**: 3-round autonomous research loop with Exa + webfetch
- **wiki-retrieve**: BM25 text retrieval — pure Python, zero deps, agent-synthesized
- **/think framework**: 10-principle framework for architectural decisions
- **GitHub Actions CI**: 5 suites run on every push/PR to main
- **Dead Letter Queue**: global error trigger for n8n
- **AOC v4 Enterprise**: 37 nodes, AI triage, GitHub issues + 3 notification channels

### Testing
- `Makefile` with 5 targets: workflows, wiki, scripts, YAML, retrieve
- 344 workflow connection tests
- 61 script tests (syntax, secrets, executables)
- 21 vault integrity tests
- YAML tests (CI + docker-compose)
- BM25 text retrieval tests

### Infrastructure
- docker-compose: production tuning (concurrency, metrics, log format, data prune)
- `.env`: AOC v4 variables, removed dead API keys
- n8n: MCP endpoint configured, concurrency limit
- PostCompact hook improved with `cat` command
- Stop hook with auto-update hot.md prompt

### Documentation
- README, PROJECT, WIKI rewritten in English at claude-obsidian level
- CONTRIBUTING.md and SECURITY.md added

---

## Skills (13 repo + 6 ECC global)

### Bundled in this repo

| Skill | Description |
|-------|-------------|
| `autoresearch` | 3-round autonomous web research |
| `wiki-retrieve` | BM25 text retrieval (stdlib Python) |
| `think` | 10-principle framework for decisions |
| `wiki-ingest` | Ingest sources into wiki |
| `wiki-query` | Query the wiki |
| `wiki-lint` | Vault health check |
| `save` | Save conversation as note |
| `wiki` | Wiki orchestrator |
| `canvas` | Visual canvas layer |
| `defuddle` | Web extraction wrapper |
| `evidence-index` | Evidence indexing |
| `obsidian-bases` | Bases schema reference |
| `obsidian-markdown` | OFM syntax reference |

### Provided by ECC global config

| Skill | Description |
|-------|-------------|
| `code-review` | Code quality review |
| `security-review` | Security review |
| `infra-design` | Infrastructure design |
| `tdd-workflow` | TDD red-green-refactor |
| `verification-loop` | Build/test/lint pre-PR |
| `work-unit-commits` | Organized commits |

---

## The n8n Orchestrator Role

n8n acts as the asynchronous execution engine and "nervous system" of the Bunker:

- **Security & Decoupling**: API keys and external integrations live in n8n, keeping bash scripts clean and secure. Scripts fire webhooks to `localhost:5678`.
- **Agentic MCP Bridge**: Gives OpenCode "hands" to trigger complex pipelines (e.g., assisted remediation) in a sandboxed manner.
- **Complex Pipelines**: Manages retries, conditional logic, and LLM evaluations via visually orchestrated flows stored in `automation/n8n-lab`.

---

## Operational Entry Points

| Purpose | File/Command |
|---|---|
| Active context | `wiki/hot.md` |
| Main map | `wiki/index.md` |
| Dashboard | `wiki/meta/dashboard.md` |
| Agent queue | `wiki/meta/agent-queue.md` |
| Integrity scan | `./bin/wiki-integrity.sh` |
| Evidence indexing | `./bin/evidence-index.sh` |
| Full local check | `./bin/bunker-check.sh` |
| Full test suite | `make test` |
| BM25 text retrieval | `python3 scripts/retrieve.py "query"` |
| Autoresearch | `/autoresearch [topic]` via OpenCode |
| n8n status | `docker ps --filter name=n8n` |

---

## Safety Model

- Scripts resolve the vault through `BUNKER_HOME` or repository root.
- External-effect scripts default to dry-run.
- Ingest server binds to `127.0.0.1:9090` by default.
- Evidence artifacts are indexed, not modified.
- n8n secrets managed via `.env` (gitignored) + n8n credential vault.

---

## Cross-Project Access

To use this brain from another project, point that project to the vault root and follow the read order:

1. `wiki/hot.md`
2. latest `wiki/meta/handovers/*`
3. `wiki/index.md`
4. specific notes only when needed

Avoid hard-coded absolute paths. Use `BUNKER_HOME` or project-local configuration.

---

MIT License © 2026 | **Haiagari**
