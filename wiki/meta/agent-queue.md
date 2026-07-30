---
type: agent-queue
title: "Agent Queue"
updated: 2026-05-14
status: active
tags: [agents, workflow, operations, bunker-os]
related: [[dashboard]], [[evidence-index]], [[INTEGRITY-REPORT]]
---

# Agent Queue

This file is the operational queue for humans and agents. Keep it small, concrete, and reviewable.

## Pending Ingest

- [ ] Review `.raw/llm-wiki-pattern-research.md` against `wiki/meta/ingestion-log.md`.
- [ ] Review `.raw/mcp-security.txt` against `wiki/meta/ingestion-log.md`.

## Pending Lint

- [ ] Resolve active broken links listed in `wiki/meta/INTEGRITY-REPORT.md`.
- [ ] Expand active short notes listed in `wiki/meta/INTEGRITY-REPORT.md`.
- [ ] Add frontmatter to active notes missing metadata.

## Pending Evidence

- [x] Index `report.zip` in `wiki/meta/evidence-index.md`.
- [x] Index `security-audit-report.json` in `wiki/meta/evidence-index.md`.
- [ ] Decide whether `report.zip` should remain packed or be extracted into a future evidence folder.

## Pending Governance

- [ ] Convert major architecture changes into ADR/AgDR records when they become decisions.
- [ ] Review whether archive broken links should remain accepted historical debt.

## Pending Handover

- [ ] Generate a handover after each completed release phase.
