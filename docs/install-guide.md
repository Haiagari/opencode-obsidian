# Bunker OS Install Guide

Bunker OS is a local-first knowledge workflow built around an Obsidian Markdown vault. OpenCode skills and scripts support capture, organization, and retrieval. Docker and n8n are optional.

## Prerequisites

- [Git](https://git-scm.com/)
- [Obsidian](https://obsidian.md/)
- [OpenCode](https://opencode.ai/) (optional, for the bundled agent workflow)

## Install as an Obsidian vault

```bash
git clone https://github.com/Haiagari/opencode-obsidian.git
cd opencode-obsidian
bash bin/setup-vault.sh
```

In Obsidian, choose **Manage Vaults → Open folder as vault** and select the cloned repository. Open the same repository in OpenCode to use its instructions, skills, and scripts.

The setup script creates the local `.raw/` input folder and Obsidian vault configuration. It does not install a Claude Code marketplace plugin.

## Use an existing vault

The setup script accepts an alternate vault path:

```bash
bash /path/to/opencode-obsidian/bin/setup-vault.sh /path/to/your-vault
```

This creates the basic Obsidian and wiki folders in the target vault. To use the bundled OpenCode workflow, open the cloned Bunker OS repository in OpenCode and follow its `AGENTS.md` and `WIKI.md` instructions. Review those files before copying or running repository scripts against a separate vault.

## First steps

1. Open the vault in Obsidian and review `wiki/index.md`.
2. Put a source document in `.raw/`.
3. In OpenCode, ask it to ingest the file (for example, `ingest notes.md`). The workflow sanitizes untrusted input before organizing notes.
4. Search the resulting wiki with the bundled retrieval tools or ask OpenCode about a topic.

The exact number and type of notes created depends on the source and the ingestion task.

## Privacy and Git

The repository is public. New files in `.raw/` and `wiki/sources/` are ignored by Git, but some files in those folders are already tracked in public history. Git ignore rules do not make existing tracked files private. Check before adding sensitive information:

```bash
git ls-files .raw wiki/sources
```

Never place credentials, private source documents, or personal notes in tracked files. Use `git status --short` before committing.

## Optional extensions

- **n8n:** Optional workflows under `extensions/n8n/`. See [N8N-SETUP.md](N8N-SETUP.md). The AOC and alert webhook workflows are inactive prototypes; do not activate or expose them until their authentication and abuse controls are implemented and tested.
- **Host and GitHub utilities:** Read [operations guidance](../extensions/operations/README.md) before running tools that affect your host or repositories.

## Validation

Run the repository checks from its root:

```bash
make test-core
make test-extensions
make test
```

YAML checks require PyYAML. The GitHub Actions workflow installs this dependency before running the suite.

