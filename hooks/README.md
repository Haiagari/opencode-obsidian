# Lifecycle hooks

[Documentation](../docs/README.md) · [Context workflow](../docs/usage-guide.md#resume-a-session)

`hooks/hooks.json` contains lifecycle configuration inherited from the plugin workflow. It is a configuration asset, not evidence that a given OpenCode release automatically loads or executes it. Verify compatibility and registration in the installed runtime before relying on context restoration.

## Checked-in events

| Event | Entries | Behavior described by the config |
|---|---|---|
| `SessionStart` (`startup\|resume`) | Command + prompt | Prints/requests reading `wiki/hot.md` when it exists |
| `PostCompact` | Command + prompt | Prints/requests rereading hot context after compaction |
| `Stop` | Command + prompt | Detects tracked wiki changes and requests a factual hot-cache update |

There is no `PostToolUse` event or auto-commit hook in the current file. No hook pushes to GitHub. A hot-cache update is a prompt instruction, not a deterministic file write performed by the shell command.

## Verify context restoration

1. Configure the hook asset only through a mechanism your runtime supports.
2. Start a session in the vault root and ask the agent to report a harmless fact from `wiki/hot.md`.
3. After context compaction, confirm the same context is available.
4. If the hook did not run, read `wiki/hot.md`, then `wiki/index.md` directly and inspect runtime registration/logs.

Claude-specific settings paths and historical Claude hook issues are not instructions for configuring OpenCode. Runtime behavior must be verified locally; checked-in hook JSON and static checks cannot establish that compatibility.

## Writes and limits

If an agent updates shared `wiki/hot.md` or `wiki/log.md`, use the repository's locking protocol as described in [Commands](../docs/commands-and-skills.md#shared-file-writes). The Stop command checks tracked changes with `git diff --name-only HEAD`; newly untracked wiki files alone may not trigger its change message.

Commands guard against missing wiki/context files and finish harmlessly in non-vault sessions. Hooks remain local and mutable; they are context assistance rather than a server-enforced security policy.
