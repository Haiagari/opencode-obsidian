# Optional n8n extension

This directory contains the optional n8n/AOC automation extension. The core vault, ingestion, retrieval, integrity checks, and `make test-core` do not require Docker or this extension's local configuration.

## Setup

1. Install Docker Engine and the Docker Compose plugin.
2. Copy `.env.example` to `.env`, fill values locally, and restrict the file (`chmod 600 .env`). Never commit `.env`.
3. From this directory, start the service with `docker compose up -d` or `./setup.sh`.
4. Import `workflows/bunker-ultimate-alerter.json` only as inactive. Keep it inactive until receiver authentication is configured on its Webhook node using Header Auth bound to a strong, unique local secret; only then may you activate it. The workflow does not validate the sender's HMAC header.
5. Use `../../bin/bunker-alert.sh` from this directory for legacy callers, or `bin/bunker-alert.sh` here for the implementation. Set `AOC_WEBHOOK_SECRET` to a strong, unique local secret before sending alerts. Ingestion alerts are opt-in: run with `BUNKER_N8N_ALERTS=1`.
6. Export workflows with `./sync-flows.sh` from the repository root, or `bin/sync-flows.sh` from this directory.

Optional diagnostics: run `./bin/check-n8n.sh` to validate configuration and service state. Workflow JSON validation is available with `make test-workflows`; compose syntax is covered by `make test-yaml-extensions`.
