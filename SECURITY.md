# Security Policy for Bunker OS

## Reporting Vulnerabilities

If you find a security vulnerability, **do not open a public issue**. Contact [Haiagari on GitHub](https://github.com/Haiagari) privately.

## Scope

This policy covers:
- OpenCode skills in `skills/`
- Scripts in `bin/` and `scripts/`
- Optional n8n workflows in `extensions/n8n/`
- Hooks in `hooks/hooks.json`
- Tests in `tests/`

See [Security Boundaries](docs/security-boundaries.md) for the local trust model and known limits.

## What the current checks cover

- `make test-scripts` checks shell scripts in the configured `bin/` and `extensions/` paths against a limited set of secret patterns. It is not a whole-repository secret scanner and cannot guarantee that credentials are absent.
- `make test` validates the Python tests, workflow JSON connections, and configured YAML files.
- The ingestion sanitizer is a best-effort heuristic. It is not a complete prompt-injection detector or a trust boundary; sanitized text remains untrusted.
- The n8n Compose service binds to host loopback by default. Review the Compose file and local environment before changing its exposure.

## n8n workflow status and limitations

- **Bunker AOC v4 Enterprise is inactive and experimental.** Its webhook workflow does not implement receiver authentication or source-based rate limiting. AI parsing failures now route to human review rather than auto-creating a standard issue. Do not activate it or expose it to a network until the missing ingress controls are implemented and tested.
- **Bunker Ultimate Alerter is inactive.** The alert sender can sign requests with HMAC, but the reviewed receiver does not validate that signature. Sender-side signing alone does not authenticate a webhook.
- **Bunker Health Check is a manual smoke workflow.** It returns a static status value; it does not monitor services or run on a schedule.
- Do not expose n8n publicly. A reverse proxy alone does not replace authentication, request validation, or rate limiting.

## Best Practices

1. Never commit `.env` files, API keys, tokens, or credentials.
2. Use environment variables or n8n's credential store for secrets.
3. Run `make test` before pushing. Its script checks are limited and are not a substitute for a dedicated secret scanner.
4. Keep the n8n image pin deliberate and review release notes before upgrading.
5. Keep experimental webhook workflows inactive until their authentication and abuse controls are in place.

## Secure Defaults

```bash
# Run the configured script checks
make test-scripts

# Verify vault integrity
./bin/bunker-check.sh

# Inspect any local listener on the default n8n port
ss -tlnp 2>/dev/null | grep 5678
```
