# Contributing to Bunker OS

[Project overview](README.md) · [Documentation](docs/README.md) · [Security reporting](SECURITY.md)

Start from `main` and keep changes focused on the local knowledge workflow or a clearly scoped optional extension. Read `AGENTS.md` for repository operating rules; read `docs/security-boundaries.md` before changing capture or integration behavior.

## Development environment

| Dependency | Why it is needed |
|---|---|
| Git and Bash | Repository checks and shell fixtures |
| Python 3.10+ with SQLite FTS5 | Retrieval, locking, sanitizer, and lifecycle tests |
| PyYAML | CI and Compose YAML validation |
| Go 1.22+ | Optional API build/handler tests invoked by regression checks |
| POSIX environment | `fcntl` locks and shell tests; use WSL on Windows |

Docker, n8n credentials, a model provider, and OpenCode are not required to run the local regression suite. They are required only when exercising their respective live integrations. External ECC skill bundles are optional and are not supplied by this repository.

```bash
python3 -m venv /path/to/bunker-dev-venv
source /path/to/bunker-dev-venv/bin/activate
python3 -m pip install PyYAML
make test
```

## Change workflow

1. Create a branch from current `main`.
2. Implement the change and update the guide/reference describing its behavior.
3. Run the checks relevant to the changed component and the required `make test` gate.
4. Review the diff and staged paths for unintended files or private content.
5. Commit a descriptive change and open a PR to `main` with evidence and limitations.

Use conventional commit messages such as `fix: preserve existing staged sources`, `docs: explain retrieval boundaries`, or `test: cover duplicate inbox capture`.

## Validation

| Command | Covers |
|---|---|
| `make test-core` | YAML, wiki/scripts, retrieval, Python and local lifecycle checks |
| `make test-extensions` | n8n JSON connections and Compose YAML |
| `make test` | Both groups; required by CI |
| `go test bin/ingest_server.go bin/ingest_server_test.go` | Go handlers and configuration without a listener |

Use current test output rather than a fixed count copied from older releases. Tests validate local behavior and static assets; they do not certify live n8n credentials, provider availability, every OpenCode configuration schema, or semantic accuracy of generated notes.

### Documentation changes

Check local links, anchors, image paths/case, and rendering. Use the existing visual assets under `docs/diagrams/` and `wiki/meta/`; keep implementation claims tied to inspected code. Reference guides should have one canonical owner instead of copying entire contracts into several pages. Historical records should remain clearly labeled.

### Skills and script changes

Update `SKILL.md` when the user workflow changes. Add or adjust tests when behavior changes; explain any new writes, network requests, credentials, or publication effects. Keep staging, filing, indexing, and publishing distinct in documentation.

## Before opening the PR

- `make test` passes, with any skipped/dependent behavior disclosed.
- Guides and references describe the actual changed behavior.
- No credentials, private source documents, generated local state, or unintended assets are staged.
- Breaking behavior or setup changes have a migration note.
- The PR describes what changed, how it was checked, and what remains outside the validation.

```bash
git status --short
git diff --check
git diff --cached
```

## Reporting bugs

Include the branch/commit, OS, relevant tool versions, reproduction commands, expected behavior, and actual output. Use harmless sample input and remove credentials/private notes. For vulnerabilities, follow [SECURITY](SECURITY.md) instead of posting sensitive details in a public issue.
