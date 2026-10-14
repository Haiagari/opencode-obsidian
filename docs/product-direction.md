# Product direction

[Documentation](README.md) · [Current architecture](architecture.md) · [Repository audit](repository-audit.md)

Bunker OS serves a person who wants useful knowledge to survive beyond a chat, browser tab, or working session. The central artifact is an inspectable Markdown vault; local tools and agent workflows make capture, synthesis, retrieval, and continuity easier.

## Intended use

| Situation | Useful outcome |
|---|---|
| Learning a technical topic | Source-linked concepts that can be revisited and compared |
| Working on a project over several sessions | Decisions, context, and next steps that do not depend on chat history |
| Collecting articles and notes | Selective filing with provenance rather than a growing unreviewed pile |
| Preparing a decision | Retrieved evidence, visible uncertainty, and documented rationale |

The current system is a personal workspace, not a hosted multi-user knowledge platform or an enforced enterprise security gate. The existing banner illustrates a broader ecosystem; a React dashboard/OZY service is not implemented in this repository.

## Design principles

- **Portable knowledge:** Markdown remains readable and editable without a service.
- **Derived search:** indexes support the vault and can be rebuilt from files.
- **Selective filing:** reuse existing concepts and create pages when they add durable value.
- **Reviewable automation:** distinguish collected input, reviewed notes, agent inference, and published content.
- **Local independence:** core capture/search/maintenance do not require n8n. Model-assisted synthesis follows the configured provider's data boundary.
- **Evidence-based claims:** document actual behavior and test limits instead of assigning unsupported security or production guarantees.

## Capability maturity

| Area | Current implementation | Boundary |
|---|---|---|
| Vault | Markdown, links, templates, visual assets | User-curated; tracked content is public |
| Local retrieval | Incremental SQLite FTS5/BM25 | Lexical matching; no semantic confidence judgment |
| Source staging | Sanitized copy, no overwrite | Not automatic wiki synthesis |
| Agent workflows | Bundled ingest/query/save/research skills | Runtime/tool compatibility and output need review |
| File coordination | POSIX advisory locks and atomic replacement | Cooperating local writers only |
| Local memo API | Token, loopback, limits, inbox writes | No remote-service contract or rate limiter |
| n8n | Optional Compose/workflow assets | Webhook receivers inactive; live integrations incomplete |

## Improvement priorities and completion criteria

| Priority | Completion should demonstrate |
|---|---|
| Clear onboarding | A clean clone reaches a verified first note and search result, with setup effects documented |
| Reliable continuity | A resumed session can recover facts/decisions from explicit notes and context, without assuming hooks ran |
| Better retrieval UX | Selection rules and stale-index behavior are visible; users can open supporting source notes |
| Safer filing | Provenance, duplicates, and contradictions can be reviewed before knowledge is published |
| Optional webhook readiness | Authentication, validation, payload/abuse limits, and negative integration tests precede activation |

These are acceptance criteria, not delivery promises or completed features. The [repository audit](repository-audit.md) preserves review findings; the [security reference](security-boundaries.md) owns the current control limits.

## Evaluate progress with real tasks

Verify the complete source-to-note-to-query loop, resuming a project after losing chat context, and recovering the index from Markdown. Track incorrect filing, unsupported answers, duplicate notes, and setup friction alongside successful checks. A large number of notes or a passing static workflow test alone does not demonstrate a useful product.
