# Optional n8n automation

[Documentation](README.md) · [Architecture](architecture.md) · [Security boundaries](security-boundaries.md)

n8n is an optional integration layer under `extensions/n8n/`. Obsidian, local staging, search, and integrity checks work without it. Treat the checked-in workflows as reviewed development assets with different levels of completion.

## Current workflow state

| Workflow | Checked-in state | Current behavior / limit |
|---|---|---|
| Bunker Health Check | Manual trigger | Returns static status; not service monitoring |
| Bunker Ultimate Alerter | Inactive | Sender can add HMAC, but receiver does not verify it |
| Bunker AOC v4 Enterprise | Inactive | Experimental triage/integration graph; missing inbound authentication and source rate limiting |
| Bunker Dead Letter Queue | Inactive | Error normalization/storage with notification placeholder; requires live wiring and validation |

Keep the AOC and alert webhook receivers inactive. Importing JSON or passing static checks is not sufficient reason to activate them. The [security reference](security-boundaries.md) lists the missing ingress controls.

## Prepare and start the local service

Use Docker Engine and its Compose plugin. From the repository root:

```bash
cp extensions/n8n/.env.example extensions/n8n/.env
chmod 600 extensions/n8n/.env
```

Configure the environment values locally. Never commit the file or paste its contents into a report. Start from the extension directory:

```bash
cd extensions/n8n
docker compose config --quiet
./setup.sh
```

The script checks Docker availability and starts Compose. Open `http://localhost:5678` to configure the local instance and import only the workflows you intend to inspect. The configured container name is `n8n_meco_lab`.

## Network and persistence

The repository pins `docker.n8n.io/n8nio/n8n:2.43.4`, publishes `127.0.0.1:5678:5678`, mounts workflow assets read-only at `/data/workflows`, and keeps writable n8n state in the `n8n_data` volume. It configures `America/Lima`, execution-data pruning, and concurrency settings. These settings do not establish production readiness or authenticate webhook callers.

Stopping the service preserves its data volume:

```bash
# From extensions/n8n/
docker compose stop
```

Back up optional service state separately from the Markdown vault. Review image upgrades deliberately and validate workflow compatibility before changing the pin.

## Checks and diagnosis

From the repository root:

```bash
make test-workflows
make test-yaml-extensions
bash extensions/n8n/bin/check-n8n.sh
```

| Check | What it establishes | What it does not establish |
|---|---|---|
| Workflow tests | Checked-in graph/connection validity and inactive webhook boundary | Credentials, remote API availability, live execution |
| YAML validation | Compose file parses | Effective deployment or service readiness |
| `check-n8n.sh` | Local env exists, Compose config validates, named container is listed as running | HTTP readiness, credential validity, workflow health |
| Manual Health Check | Its static workflow executes in the local instance | Monitoring of services/dependencies |

If the live/config check fails, inspect the Docker daemon and local configuration. Use `docker compose logs --tail 100 n8n` from the extension directory for a local review; redact credentials and private payloads before sharing output.

## Optional MCP

An n8n service on port 5678 does not automatically provide an MCP endpoint. Register a remote connection only after you have actually configured the endpoint, verified its authentication, and checked the schema accepted by your installed OpenCode version. No local MCP credentials are shipped in this repository.

Use [OpenCode setup](install-guide.md#add-opencode-and-the-vault-connection) for the separate Obsidian vault connection. It does not configure n8n.

## Alerts and compatibility entry points

`bin/bunker-alert.sh` and root `sync-flows.sh` are compatibility wrappers for the extension implementations. Staging alerts are opt-in with `BUNKER_N8N_ALERTS=1`; leave that off while webhook receivers are inactive. A sender secret/signature alone does not supply the receiver verification that is missing here.

See the [extension README](../extensions/n8n/README.md) and actual scripts before exporting or invoking integrations. Failed optional notifications do not undo a successfully staged local source.
