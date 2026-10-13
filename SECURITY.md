# Security Policy for Bunker OS

## Reporting Vulnerabilities

If you find a security vulnerability, **do not open a public issue**.

Contact directly:
- GitHub: [Haiagari](https://github.com/Haiagari)
- Repo: [opencode-obsidian](https://github.com/Haiagari/opencode-obsidian)

Vulnerabilities will be addressed within 48 business hours.

## Scope

This policy covers:
- OpenCode skills in `skills/`
- Scripts in `bin/` and `scripts/`
- Optional n8n workflows in `extensions/n8n/`
- Hooks in `hooks/hooks.json`
- Tests in `tests/`

## Existing Security Measures

### Secrets
- No hardcoded API keys in scripts (verified by `make test-scripts`)
- Optional extension keys live in `extensions/n8n/.env` (gitignored) or in n8n credential vault
- Test suite scans for secret patterns on every run

### n8n
- AOC v4 webhook supports `x-aoc-secret` header
- Rate limiting by source implemented in the pipeline
- Secret redaction in logs and payloads
- Dry-run mode by default (`AOC_DRY_RUN=true`)

### Network
- Ingest server binds to `127.0.0.1:9090` by default
- n8n exposes only on localhost
- Autoresearch validates and sanitizes URLs before fetch
- Content sanitization: prevents wikilink injection and scripts in external sources

### Dependencies
- n8n container with version pinning
- Secret scanning in test suite
- npm audit as recommended practice

## Best Practices

1. **Never commit** `.env`, API keys, tokens, or credentials
2. **Use environment variables** for sensitive configuration
3. **Run `make test`** before pushing (includes secret scanning)
4. **Keep n8n updated** (regular docker pull)
5. **Do not expose n8n to the internet** without a reverse proxy with SSL
6. **Configure `x-aoc-secret`** before activating the AOC v4

## Secure Defaults

```bash
# Verify no secrets in repo
make test-scripts

# Verify vault integrity
./bin/bunker-check.sh

# Optional n8n listener check (only relevant when the extension is running)
ss -tlnp 2>/dev/null | grep 5678 | grep -v 0.0.0.0 || netstat -tlnp 2>/dev/null | grep 5678 | grep -v 0.0.0.0
```
