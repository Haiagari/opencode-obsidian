# Optional n8n Extension Setup

n8n/AOC automation is optional and is not required for local capture, sanitization, retrieval, or vault integrity. The extension lives in `extensions/n8n/`.

The Compose service binds only to host loopback (`127.0.0.1:5678`), matching this local n8n setup. Its image is deliberately pinned to `2.43.4`; update the pin deliberately in `extensions/n8n/docker-compose.yml` when upgrading. Workflow assets are mounted read-only in the container, while the persistent `n8n_data` volume remains writable for n8n state.

## Prerequisites and setup

1. Install Docker Engine and the Docker Compose plugin.
2. From the repository root, copy `extensions/n8n/.env.example` to `extensions/n8n/.env`, configure it locally, and set restrictive permissions (`chmod 600 extensions/n8n/.env`). Never commit or print `.env` contents.
3. Start the optional service from the extension directory with `./setup.sh` (or `docker compose up -d`).
4. Open `http://localhost:5678` and import workflows from `extensions/n8n/workflows/` as needed. Keep `Bunker Ultimate Alerter` and `Bunker AOC v4 Enterprise` inactive. The alerter does not validate the sender's HMAC header, and AOC v4 does not implement receiver authentication or source-based rate limiting. Do not activate or expose either webhook workflow until the missing controls are implemented and tested. The Health Check workflow is a manual smoke test that returns static status; it is not a monitor.
5. Set `AOC_WEBHOOK_SECRET` to a strong, unique local secret before using the alert sender; it fails closed when unset.
6. To send alerts from ingestion, explicitly opt in with `BUNKER_N8N_ALERTS=1`. Normal ingestion does not contact n8n.

The legacy `bin/bunker-alert.sh` command delegates to `extensions/n8n/bin/bunker-alert.sh`. `sync-flows.sh` remains a repository-root compatibility wrapper for `extensions/n8n/bin/sync-flows.sh`.

## Optional MCP connection

In OpenCode's `~/.config/opencode/opencode.json`, an n8n instance may be registered as an optional remote MCP server:

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

Configure authentication according to the local n8n setup. Do not commit tokens or credentials.

## Diagnostics and validation

- Optional live/config diagnostics: `extensions/n8n/bin/check-n8n.sh` (requires Docker and local `.env`).
- Static extension validation, no Docker startup: `make test-workflows` and `make test-yaml-extensions`.
- Full repository validation: `make test`. Core-only validation without Docker/n8n: `make test-core`.
