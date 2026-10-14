# Install and verify Bunker OS

[Documentation](README.md) · [Next: daily workflow](usage-guide.md)

Use the repository as a new Obsidian vault first. You can add local search and OpenCode without running n8n. Commands below assume a Bash shell on Linux, macOS, or a compatible environment such as WSL.

## Requirements by task

| Dependency | Required for | Verification |
|---|---|---|
| Git | Clone and inspect repository changes | `git --version` |
| Obsidian | Visual editing, links, graph, and dashboard | Open the app |
| Bash | Repository shell scripts | `bash --version` |
| Python 3.10+ with SQLite FTS5 | Search, sanitizer, integrity, and locking tools | Run the FTS5 probe below |
| OpenCode + configured model provider | Agent skills and synthesis | `opencode --version` |
| Node.js/npm (`npx`) | MCPVault started by the supplied OpenCode setup | `node --version` and `npx --version` |
| Go 1.22+ | Optional local capture server; full regression checks | `go version` |
| PyYAML | YAML validation in `make test-core`/`make test` | `python3 -c 'import yaml'` |
| Docker Engine + Compose plugin | Optional n8n service | `docker compose version` |

The Python retrieval engine uses the standard library. PyYAML is a development/check dependency, not a retrieval dependency. POSIX locking uses `fcntl`; use WSL or another POSIX environment for those tools on Windows. Native Windows execution of the entire script suite is not established.

## Clone and open the vault

```bash
git clone https://github.com/Haiagari/opencode-obsidian.git
cd opencode-obsidian
bash bin/setup-vault.sh
```

In Obsidian, choose **Manage Vaults → Open folder as vault** and select `opencode-obsidian`, the repository root. Open `wiki/index.md` and `wiki/meta/dashboard.md`. The root contains the `.obsidian/` settings as well as the `wiki/` notes; opening only `wiki/` uses a different vault root and does not load those settings.

### What setup changes

`bin/setup-vault.sh` creates the source, wiki, and template folders and rewrites these Obsidian files:

- `.obsidian/graph.json`: graph filtering and color groups.
- `.obsidian/app.json`: file-explorer exclusion preferences.
- `.obsidian/appearance.json`: enabled CSS snippets.

If the Excalidraw manifest exists but `main.js` is missing, setup downloads version `2.22.0`, verifies the pinned SHA-256, and publishes the runtime only after verification. This step needs network access and `curl`. A mismatch stops setup. Review and back up existing Obsidian settings before rerunning it against a customized vault.

The final console output contains legacy Claude Code and visual-layout instructions. The script does not install a Claude Code plugin, and it does not guarantee every referenced workspace/canvas exists. Use the OpenCode path below and the files present in your clone.

## Verify local retrieval

Check your Python/SQLite build:

```bash
python3 - <<'PYTHON'
import sqlite3, sys
assert sys.version_info >= (3, 10), 'Python 3.10+ required'
db = sqlite3.connect(':memory:')
db.execute('CREATE VIRTUAL TABLE probe USING fts5(content)')
print('Python and SQLite FTS5 ready')
PYTHON
```

Build the index and run a first search:

```bash
python3 scripts/retrieve.py build
python3 scripts/retrieve.py status
python3 scripts/retrieve.py "knowledge" --top 5
```

`build` reports indexed pages/chunks; `status` identifies the database; search returns JSON with ranked note paths. Markdown inside `wiki/` is indexed except descendants of `meta/` and `archive/`. Files in `.raw/` are not searchable wiki notes. See [Architecture](architecture.md#retrieval-internals) for these distinctions.

## Add OpenCode and the vault connection

OpenCode is optional for manual editing and local search. Configure a model provider in your OpenCode installation, then inspect the repository's setup utility:

```bash
# Review the implementation before it changes your user configuration.
less extensions/operations/bin/setup-opencode.sh
bash bin/setup-opencode.sh
```

The utility installs a selected set of bundled skills under `~/.config/opencode/skills/` and configures `obsidian-vault` in `~/.config/opencode/opencode.json`. It backs up replaced skill directories and the config, and pins MCPVault at `@bitbonsai/mcpvault@0.16.0` with `npx`.

The script writes a `type: "stdio"` entry with `command`/`args`. Confirm your installed OpenCode release accepts that configuration; the local setup tests do not establish compatibility with every runtime version. If OpenCode rejects it, adapt the entry to your runtime's supported MCP schema while keeping the pinned command and correct vault root.

Restart OpenCode in the repository folder. Confirm it can read `wiki/hot.md` and list notes through the configured vault connection. If skills or MCP fail to load, use [Troubleshooting](troubleshooting.md); direct Python search remains usable.

The setup script installs ten skills. Other bundled skills, including `wiki-retrieve`, `think`, and `evidence-index`, remain available in `skills/` but are not copied by that installer. The [skill catalog](commands-and-skills.md#bundled-skills) distinguishes bundled workflows from installer behavior.

## Use a separate existing vault

```bash
bash /path/to/opencode-obsidian/bin/setup-vault.sh /path/to/your-vault
```

This creates folders/settings there; it does not copy the repository's scripts or skills. The script also rewrites settings as described above. For retrieval from another vault, keep the tooling in this repository and set its root explicitly:

```bash
BUNKER_HOME=/path/to/your-vault python3 scripts/retrieve.py build
BUNKER_HOME=/path/to/your-vault python3 scripts/retrieve.py "topic" --top 5
```

The retrieval engine expects a `wiki/` folder under that root. Review each utility's path handling before using it with an alternate vault; not every script has identical environment-variable behavior.

## Check the publication boundary

This clone includes public seed notes and tracked source material. Before adding private sources:

```bash
git ls-files .raw wiki/sources wiki/.raw
git status --short
```

Ignore rules apply to new files, not existing tracked paths or public history. The [security reference](security-boundaries.md) describes the boundary; the [daily guide](usage-guide.md) explains review before publication.

## Development validation

For contributors, install the YAML dependency in an isolated environment and make Go available:

```bash
python3 -m venv /path/to/bunker-dev-venv
source /path/to/bunker-dev-venv/bin/activate
python3 -m pip install PyYAML
make test
```

The checks use local fixtures and static workflow validation. They do not start Docker or prove configured remote services work. Continue with the [first complete knowledge loop](usage-guide.md#first-complete-knowledge-loop).
