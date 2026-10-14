# Install Bunker OS

Bunker OS is an Obsidian vault that can be used on its own. OpenCode is optional; it adds the bundled skills and agent workflows.

## Requirements

- Git, to get the repository
- Obsidian, to open and edit the vault
- OpenCode, only if you want to use the included agent workflows

Python 3.10+, Go, and Docker are needed only for specific tools described in their reference guides.

## Install the repository as a vault

Clone the repository and run its setup script:

```bash
git clone https://github.com/Haiagari/opencode-obsidian.git
cd opencode-obsidian
bash bin/setup-vault.sh
```

The script creates local vault folders and Obsidian settings. If the checked-in Excalidraw plugin manifest is present but its runtime is missing, setup downloads the pinned release and verifies its SHA-256 checksum.

In Obsidian, choose **Manage Vaults → Open folder as vault** and select the cloned `opencode-obsidian` folder. To use the agent workflows, open that same folder in OpenCode and follow the repository's [`AGENTS.md`](../AGENTS.md) and [`WIKI.md`](../WIKI.md).

The setup script currently prints some legacy Claude Code instructions at the end. They are not the setup path for this repository; use OpenCode as described above. The script does not install a Claude Code plugin.

## Use an existing vault

The script can create the basic vault folders in another location:

```bash
bash /path/to/opencode-obsidian/bin/setup-vault.sh /path/to/your-vault
```

Review `AGENTS.md` and `WIKI.md` before using the bundled workflows or scripts against a separate vault. They may create or update notes there.

## Make your first note

Open the [daily use guide](usage-guide.md) for the capture, review, filing, and search workflow. It includes the commands for ingesting a local source and searching the vault.

## Privacy and Git

This repository is public. Ignore rules only apply to new, untracked files; they do not encrypt files or erase content already present in Git history. Check tracked paths before adding private material:

```bash
git ls-files .raw wiki/sources
git status --short
```

Never put credentials, private source documents, or personal notes in tracked files. See [Security boundaries](security-boundaries.md) for the complete safeguards and limitations.

## Optional tools

- [Local Ingest API](local-ingest-api.md) — authenticated, loopback-only capture for short notes.
- [n8n extension](N8N-SETUP.md) — optional automation that requires Docker.
- [Operations tools](../extensions/operations/README.md) — host and repository utilities; read their guidance before running them.

## Validate the repository

Run checks from the repository root when contributing:

```bash
make test-core
make test-extensions
make test
```

See [CONTRIBUTING](../CONTRIBUTING.md) for the contribution workflow.
