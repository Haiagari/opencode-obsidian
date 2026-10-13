---
type: governance
title: "Bunker OS Governance"
updated: 2026-05-14
status: active
tags: [governance, agents, safety, bunker-os]
related: [[dashboard]], [[knowledge-supply-chain]], [[workflows]], [[ADR-TEMPLATE]]
---

# Bunker OS Governance

## Operating Principles

- Local-first by default.
- Evidence before interpretation.
- Dry-run before external effects.
- No destructive migrations without explicit approval.
- Preserve existing links unless a migration plan exists.
- Agents write into known locations and leave handovers.

## Decision Rules

Create an ADR/AgDR when a change affects:

- vault structure
- agent behavior
- evidence policy
- external integrations
- security posture
- long-term naming or architecture

Use `wiki/meta/ADR-TEMPLATE.md`.

## Automation Rules

Scripts that may commit, push, create PRs, call webhooks, or archive user notes must default to dry-run.

Other external-effect operations require explicit `--apply`:

- `bin/wiki-sync.sh --apply`
- `bin/bunker-push.sh --apply`
- `bin/bunker-pulse.sh --apply`

Alert sending is a direct-send exception, not an `--apply`-gated operation. Invoke `./bin/bunker-alert.sh "target" "LEVEL" "message"`; it requires a strong local `AOC_WEBHOOK_SECRET`. Keep the n8n receiver workflow inactive until its Webhook node is configured with Header Auth.

## Evidence Rules

- `report.zip` remains original evidence.
- `security-audit-report.json` remains original audit output.
- Checksums are recorded in `wiki/meta/evidence-manifest.json`.
- Historical evidence must be marked as historical when paths do not match the current repo.

## Agent Rules

Agents must:

1. Read `wiki/hot.md` first.
2. Read the latest handover.
3. Use `wiki/meta/agent-queue.md` for pending work.
4. Update `wiki/log.md` for meaningful changes.
5. Run `bin/wiki-integrity.sh` after creating or moving notes.
