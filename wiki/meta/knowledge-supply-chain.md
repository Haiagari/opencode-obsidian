---
type: governance
title: "Knowledge Supply Chain"
updated: 2026-05-14
status: active
tags: [knowledge, governance, workflow, bunker-os]
related: [[dashboard]], [[agent-queue]], [[evidence-index]]
---

# Knowledge Supply Chain

Bunker OS treats knowledge like an operational supply chain. Every valuable input should move from raw capture to reusable, governed knowledge.

```text
Source → Ingest → Normalize → Classify → Evidence → Decision → Action → Handover → Reuse
```

## Stages

| Stage | Purpose | Current locations |
|---|---|---|
| Source | Preserve the original input | `.raw/`, `report.zip`, external links |
| Ingest | Capture into the vault | `wiki/inbox/`, `bin/ingest_server.go` |
| Normalize | Convert raw input into structured notes | `_templates/`, `skills/wiki-ingest/` |
| Classify | Place knowledge in the right domain | `wiki/sources/`, `wiki/entities/`, `wiki/concepts/`, `wiki/projects/`, `wiki/comparisons/` |
| Evidence | Preserve proof and checksums | `wiki/meta/evidence-index.md`, `wiki/meta/evidence-manifest.json` |
| Decision | Record architectural choices | `wiki/meta/ADR-TEMPLATE.md`, future ADR/AgDR notes |
| Action | Execute safe local automation | `bin/` |
| Handover | Preserve continuity | `wiki/meta/handovers/`, `wiki/hot.md` |
| Reuse | Make context searchable and visual | `wiki/index.md`, canvases, dashboard |

## Rules

1. Raw sources stay raw.
2. Evidence stays immutable.
3. Interpretations live in wiki notes, not inside original artifacts.
4. Major decisions require ADR/AgDR.
5. Every session that changes direction should produce a handover.
6. Automation defaults to dry-run unless explicitly approved with `--apply`.

## Quality Gates

Before closing a release or major session:

```bash
./bin/bunker-check.sh
```

The check must report no critical failures before external sync or handover.
