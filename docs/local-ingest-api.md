# Local memo capture API

[Documentation](README.md) · [Daily workflow](usage-guide.md) · [Security boundaries](security-boundaries.md)

`bin/ingest_server.go` accepts short text memos into `wiki/inbox/` on the same machine. It adds simple keyword-based metadata and preserves content for review. It does not create concept/entity pages, update the main index, run retrieval, or publish changes.

This is separate from the Obsidian Local REST API plugin and the OpenCode MCPVault connection.

## Start the server

Use Go 1.22+ and Python 3.10+. Run from the repository root so default paths resolve correctly. Keep the token in local process environment rather than a tracked config file:

```bash
export BUNKER_INGEST_TOKEN="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
go run ./bin/ingest_server.go
```

The token must be at least 32 characters. The default listener is `127.0.0.1:9090`; non-loopback binds are rejected. The server uses plain HTTP on loopback and has no built-in remote TLS/auth gateway. Remote exposure is outside the current supported contract.

The client must receive the same token through a trusted local channel. An independently generated token in a second terminal will not authenticate. Do not log or commit the token.

## Configuration

| Variable | Default | Effect |
|---|---|---|
| `BUNKER_INGEST_TOKEN` | Required | Accepted bearer or `X-Bunker-Token` credential |
| `BUNKER_INGEST_BIND` | `127.0.0.1:9090` | Loopback host and port |
| `BUNKER_INBOX_DIR` | `<working-directory>/wiki/inbox` | Note destination |
| `BUNKER_SANITIZER_PATH` | `<working-directory>/scripts/sanitize_ingest.py` | Python sanitizer path |

`BUNKER_HOME` does not configure this Go server. Use its explicit path variables or start it from the repository root. Python must be available as `python3` on the server's `PATH`.

## Send a memo

From a client shell already holding the same token:

```bash
curl --fail-with-body \
  -H "Authorization: Bearer $BUNKER_INGEST_TOKEN" \
  -H 'Content-Type: text/plain' \
  --data-binary 'Review the deployment rollback checklist.' \
  http://127.0.0.1:9090/ingest
```

Success returns HTTP `200` with `saved as memo-<digest>.md`. Alternatively, supply `X-Bunker-Token`. That header takes precedence if present. The body is treated as text; the handler does not require or parse a JSON schema and does not validate the declared content type.

### Routes and responses

| Route / condition | Response |
|---|---|
| `GET /health` or `HEAD /health` | `200`; JSON process status (`HEAD` has no response body on the wire) |
| `POST /ingest`, valid authenticated text | `200`; stored basename |
| Wrong method on a registered route | `405` |
| Missing/incorrect ingest credential | `401` |
| Blank text before/after sanitization | `400` |
| Duplicate sanitized content | `409`; existing note preserved |
| Body above 10 MiB or body read error | `413` |
| Sanitizer execution/timeout failure or storage failure | `500` |
| Unknown route | `404` |

`/health` is unauthenticated and returns static process status. It does not verify inbox write access, sanitizer availability, or dependency readiness. No rate limiter is implemented in this server.

## Storage behavior

The sanitizer runs with a 10-second context timeout. The server trims the output and uses the first eight bytes of its SHA-256 as a sixteen-character filename suffix. This keeps memo text out of filenames but is not encryption; identical sanitized content produces the same destination and a `409` on repeat.

Notes are written through temporary files with mode `0600` and atomically linked without overwrite. A newly created inbox requests mode `0700`; an existing directory's permissions are not reset by `MkdirAll`. Inspect the directory permissions if it existed before startup.

Keyword classification checks, in order:

1. Bug/error terms: `bug` type.
2. Decision/architecture terms: `decision` type.
3. Task/review terms: `task` type.
4. Otherwise: `memo` type.

A decision-like memo containing `ioutil` also triggers a narrow legacy grep of `bin/`; if matches exist, a compliance paragraph is appended. This is not AST/data-flow analysis or a general security scanner.

## Review and search

Open the created inbox note and decide whether to file, merge, discard, or keep it pending. Link useful knowledge into the appropriate wiki pages and preserve provenance. Then refresh retrieval:

```bash
python3 scripts/retrieve.py build
```

Inbox Markdown is eligible for default FTS indexing, so an indexed inbox note is not automatically reviewed knowledge. The [daily guide](usage-guide.md) explains filing and the [architecture guide](architecture.md) explains index selection.

## Timeouts and validation

Server limits: read headers 5 seconds, request read/write 15 seconds each, idle connection 60 seconds. These timeouts and the size limit do not replace authentication or provide remote-service readiness.

```bash
go test bin/ingest_server.go bin/ingest_server_test.go
```

Handler tests exercise authentication, methods, limits, sanitizer usage, duplicates, permissions, and local configuration without opening a network socket. Local lifecycle tests exercise the capture-to-vault path; they do not prove a deployed listener or external service is healthy.
