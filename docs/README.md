# Documentation · Bunker OS

Bunker OS keeps knowledge in a portable Obsidian vault and adds local tools and optional agent workflows. Start with an end-to-end task, then use the technical references when you need a specific contract or behavior.

[Project overview](../README.md) · [Install](install-guide.md) · [Daily use](usage-guide.md) · [Command reference](commands-and-skills.md)

## Start with a working vault

| Step | Guide | What you should have afterwards |
|---|---|---|
| 1. Prepare the workspace | [Installation](install-guide.md) | Open vault, verified Python/FTS5, optional OpenCode connection |
| 2. Complete the knowledge loop | [Daily use](usage-guide.md) | A reviewed note, source links, and a retrievable result |
| 3. Understand the implementation | [Architecture](architecture.md) | Component roles, storage paths, and optional-service boundaries |
| 4. Operate it deliberately | [Commands & skills](commands-and-skills.md) | Commands, effects, outputs, and skill entry points |
| 5. Diagnose problems | [Troubleshooting](troubleshooting.md) | A way to distinguish setup, data, index, and integration failures |

## Technical references

| Reference | Covers |
|---|---|
| [Security boundaries](security-boundaries.md) | Data exposure, sanitization, local access, locks, and webhook limits |
| [Local Ingest API](local-ingest-api.md) | Configuration, authentication, request/response contract, and errors |
| [n8n setup](N8N-SETUP.md) | Local service setup, workflow state, credentials, and static/live checks |
| [Wiki schema](../WIKI.md) | Note types, source provenance, context caches, and filing conventions |
| [Hooks](../hooks/README.md) | Checked-in lifecycle configuration and runtime compatibility |
| [Operations extension](../extensions/operations/README.md) | Optional utilities that can change host or Git state |

## Existing visual assets

The [illustration catalog](diagrams/README.md) displays the two generated illustrations and links to their guides. The [project README](../README.md) displays the existing banner and system map. Images are embedded with repository-relative Markdown paths so they work on GitHub and in a local clone.

| Asset | Where to see it | Purpose |
|---|---|---|
| Existing project banner | [Project overview](../README.md) | Ecosystem identity; the README distinguishes visual vision from shipped features |
| System map | [Architecture](architecture.md) | Local workspace, vault, retrieval, tools, and optional automation |
| Knowledge workflow | [Daily use](usage-guide.md) | Capture, review, filing, and retrieval |

## Project records

- [Product direction](product-direction.md): scope, principles, current capabilities, and acceptance criteria for future improvements.
- [Repository audit](repository-audit.md): findings and implementation evidence from the project review; a dated record rather than a live service-status page.
- [v1.3.0 delivery record](releases/v1.3.0-local-knowledge-os.md): historical release summary.
- [Archived industry briefing](archive/BUNKER-v2.3-BRIEFING.md): background research, separate from the implementation guides.

For changes, use [Contributing](../CONTRIBUTING.md). For agent operating instructions, use [AGENTS](../AGENTS.md). For vulnerability reporting, use [Security](../SECURITY.md).
