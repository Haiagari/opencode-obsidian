# Optional operations extension

These host/repository-operation utilities are kept for compatibility and are not part of the core personal-knowledge workflow. They may invoke Trivy, GitHub CLI, or mutate Git state; read each command before use and explicitly authorize actions such as `--apply`.

Implementations live in `bin/`. Existing `bin/<name>.sh` entry points remain executable compatibility shims and forward arguments to the corresponding implementation:

- `audit-repo.sh` — Trivy repository scan.
- `bunker-github-setup.sh` — changes GitHub repository metadata and branch protection.
- `bunker-pulse.sh` — issue/triage workflow; default dry-run, `--apply` performs GitHub/Git operations.
- `bunker-push.sh` — stages, commits, and pushes; use only when explicitly intended.
- `bunker-scaffold.sh` — creates project scaffolding in the current working directory.
- `setup-multi-agent.sh` and `setup-opencode.sh` — configure local agent skill/MCP setup.

These are optional utilities, not required for capture, sanitization, retrieval, or vault integrity.
