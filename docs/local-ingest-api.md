# Local Ingest API

`bin/ingest_server.go` is an optional loopback HTTP endpoint for placing short notes in `wiki/inbox/`. It is separate from the n8n extension. It does not create wiki concepts, update `wiki/index.md`, or publish changes; an agent or a person must review and file the inbox note.

![Ingestion paths: reviewed source workflow and local API inbox capture](diagrams/ingestion-illustration.png)

The API route ends at the inbox; it does not bypass review or file notes into the knowledge base automatically.

## Start it

Requirements: Go 1.22 or newer and Python 3.10 or newer. From the repository root:

```bash
export BUNKER_INGEST_TOKEN="$(openssl rand -hex 32)"
go run ./bin/ingest_server.go
```

The default listener is `127.0.0.1:9090`. The server refuses to start without a token of at least 32 characters and rejects non-loopback binds. Plain HTTP is therefore limited to the local machine. Remote access through a tunnel or reverse proxy is unsupported by this server; use a separately authenticated and TLS-protected service if that changes.

Optional settings:

| Variable | Default | Purpose |
|---|---|---|
| `BUNKER_INGEST_BIND` | `127.0.0.1:9090` | Loopback address and port |
| `BUNKER_INGEST_TOKEN` | required | Bearer or `X-Bunker-Token` credential; at least 32 characters |
| `BUNKER_INBOX_DIR` | `wiki/inbox` | Local inbox path |
| `BUNKER_SANITIZER_PATH` | `scripts/sanitize_ingest.py` | Best-effort sanitizer executable script |

## Requests and limits

```bash
curl -H "Authorization: Bearer $BUNKER_INGEST_TOKEN" \
  -H 'Content-Type: text/plain' --data-binary 'A note to review' \
  http://127.0.0.1:9090/ingest
```

`GET /health` returns a static process response. `POST /ingest` requires authentication, is limited to 10 MiB, sanitizes input before writing, stores files with mode `0600`, uses opaque SHA-256-based filenames, and returns `409` instead of overwriting a note with the same content. Request and response timeouts are configured. The sanitization step is heuristic; stored text remains untrusted and must be reviewed.

To index filed wiki notes, run `python3 scripts/retrieve.py build`. The API itself does not ingest or interpret web URLs. Use the `wiki-ingest` skill for source-driven page creation.

## Tests

`go test bin/ingest_server.go bin/ingest_server_test.go` exercises authentication, local-only configuration, sanitization, payload size, duplicate writes, and permissions without opening a network listener.
