# Documentación visual

Cuatro ilustraciones raster coordinadas muestran el producto sin sustituir las guías textuales. Se reutilizan en el README y en las páginas que explican cada flujo.

| Ilustración | Qué explica | Se usa en |
|---|---|---|
| [Arquitectura general](architecture-overview.png) | OpenCode, skills/scripts, vault Markdown, FTS5/BM25, API local e integración n8n separada | [README](../../README.md#architecture), [arquitectura](../../wiki/concepts/opencode-obsidian-architecture.md) |
| [Ingesta](ingestion-illustration.png) | Diferencia entre el flujo de wiki-ingest y la captura de API al inbox | [API local](../local-ingest-api.md), [flujo del vault](../../wiki/concepts/vault-flow.md) |
| [Consulta](retrieval-illustration.png) | Markdown como fuente de verdad, construcción del índice local y síntesis de resultados | [README](../../README.md#bm25--sqlite-fts5-text-retrieval) |
| [Límites de confianza](trust-boundaries-illustration.png) | Fuente no confiable, límites del sanitizer, revisión humana, API local y webhooks inactivos | [Security boundaries](../security-boundaries.md) |

Las imágenes son explicativas. Los límites y el comportamiento detallado se documentan en las guías vinculadas; la ilustración no reemplaza esos contratos.
