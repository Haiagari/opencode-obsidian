# Optional operations extension

These host/repository-operation utilities are kept for compatibility and are not part of the core personal-knowledge workflow. They may invoke Trivy, GitHub CLI, or mutate Git state; read each command before use and explicitly authorize actions such as `--apply`.

Implementations live in `bin/`. Existing `bin/<name>.sh` entry points remain executable compatibility shims and forward arguments to the corresponding implementation:

- `audit-repo.sh` — Trivy repository scan.
- `bunker-github-setup.sh` — dry-run by default; `--apply` updates repository metadata only and leaves branch protection unchanged.
- `bunker-pulse.sh` — issue/triage workflow; default dry-run has no filesystem writes, while `--apply` archives a memo on a review branch, pushes that branch, and creates a GitHub issue and draft PR. It requires a clean worktree on the configured base branch.
- `bunker-push.sh` — stages, commits, and pushes; use only when explicitly intended.
- `bunker-scaffold.sh` — creates project scaffolding in the current working directory.
- `setup-multi-agent.sh` and `setup-opencode.sh` — configure local agent skill/MCP setup.
- `setup-opencode.sh` backs up overwritten skill folders and OpenCode config before installing. It pins MCPVault at `0.16.0`; review that dependency before updating the version.

These are optional utilities, not required for capture, sanitization, retrieval, or vault integrity.
