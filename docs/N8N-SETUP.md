# Optional n8n extension

n8n is an optional integration layer. It is not required for the Obsidian vault, local capture, search, or integrity checks. The extension is located in `extensions/n8n/`.

## Set it up

1. Install Docker Engine and the Docker Compose plugin.
2. From the repository root, create a local environment file and restrict its permissions:

   ```bash
   cp extensions/n8n/.env.example extensions/n8n/.env
   chmod 600 extensions/n8n/.env
   ```

3. Configure the values locally. Never commit or print `.env` contents.
4. Start the service from the extension directory:

   ```bash
   cd extensions/n8n
   ./setup.sh
   ```

5. Open `http://localhost:5678` and import only the workflows you intend to use.

The Compose service is pinned to n8n `2.43.4`, binds to host loopback, and mounts workflow assets read-only. Update the image pin deliberately when upgrading. Review [Security boundaries](security-boundaries.md) before enabling any workflow that accepts requests from outside the local process.

## Optional MCP connection

If you have configured a local n8n MCP endpoint, OpenCode can register it in `~/.config/opencode/opencode.json`:

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

Configure authentication for your local n8n setup. Do not commit tokens or credentials.

## Validate and diagnose

- Static checks without starting Docker: `make test-workflows` and `make test-yaml-extensions`.
- Optional live/config diagnostics: `extensions/n8n/bin/check-n8n.sh` (requires Docker and the local `.env`).
- Full repository checks: `make test`; core-only checks: `make test-core`.

The root-level `bin/bunker-alert.sh` and `sync-flows.sh` paths remain compatibility wrappers for scripts under `extensions/n8n/bin/`.
