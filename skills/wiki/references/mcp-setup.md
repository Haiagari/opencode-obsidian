# MCP Setup for OpenCode

MCP (Model Context Protocol) allows OpenCode to connect directly to tools, external services, and automation pipelines without copy-pasting.

> [!important] OpenCode MCP Configuration
> OpenCode reads MCP servers from the root `mcp` block in `~/.config/opencode/opencode.json` (or `.opencode/opencode.json`).
> OpenCode supports:
> - `type: "remote"` with `url`, optional `enabled`, and optional `oauth` (see `OPENCODE_MCP_GUIDE.md`).
> - `type: "local"` with `command` and `args` array.
>
> *(Do not use legacy Claude Code CLI `claude mcp add...` commands or `type: "http"`).*

---

## 1. Remote MCP: n8n Automation Engine

To connect OpenCode to the local n8n instance (`n8n_meco_lab`), configure a remote MCP endpoint:

In `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "n8n-mcp": {
      "type": "remote",
      "url": "http://localhost:5678/mcp-server/http",
      "enabled": true,
      "oauth": false
    }
  }
}
```

Authenticate if required:
```bash
opencode mcp auth n8n-mcp
```

Verify connection:
```bash
opencode mcp list
opencode mcp auth list
opencode mcp debug n8n-mcp
```

---

## 2. Vault Access Options

### Option A: Obsidian CLI (Native & Recommended for Obsidian v1.12+)

No MCP server or plugin required. OpenCode interacts with your vault via CLI:

```bash
obsidian-cli read /path/to/vault wiki/index.md
obsidian-cli write /path/to/vault wiki/new-note.md < content.md
obsidian-cli search /path/to/vault "query term"
```

### Option B: Local Filesystem MCP (`@bitbonsai/mcpvault`)

Runs locally via OpenCode `local` MCP configuration:

In `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "obsidian-vault": {
      "type": "local",
      "command": ["npx", "-y", "@bitbonsai/mcpvault@latest", "/absolute/path/to/your/vault"],
      "enabled": true
    }
  }
}
```

Tools provided: `read_note`, `search_notes`, `create_note`, `update_note`, `get_frontmatter`, `update_frontmatter`, `list_all_tags`.

### Option C: Local REST API Plugin + MCP (`mcp-obsidian`)

1. Install "Local REST API" community plugin in Obsidian.
2. Configure local MCP in `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "obsidian-vault": {
      "type": "local",
      "command": ["uvx", "mcp-obsidian"],
      "environment": {
        "OBSIDIAN_API_KEY": "<YOUR_KEY>",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124",
        "NODE_TLS_REJECT_UNAUTHORIZED": "0"
      },
      "enabled": true
    }
  }
}
```

---

## 3. Verification

Check OpenCode MCP status:

```bash
opencode mcp list
```

In OpenCode chat, run `/mcp` to inspect available tools.

