---
type: concept
title: "Vault Flow — Obsidian Knowledge Management"
domain: ai-engineering
created: 2026-04-22
updated: 2026-10-13
tags:
  - workflow
  - knowledge-base
  - opencode
  - obsidian
status: active
related:
  - "[[index]]"
  - "[[hot]]"
  - "[[log]]"
  - "[[mcp-governance]]"
sources: []
---

# Vault Flow — Obsidian Knowledge Management

![Ingestion flow](../../docs/diagrams/ingestion-illustration.png)

For query and security views, see the [retrieval illustration](../../docs/diagrams/retrieval-illustration.png) and [security boundary guide](../../docs/security-boundaries.md). The Go local capture API only adds a note to the review inbox; it is not the semantic wiki-ingestion workflow.

## Definition

Workflow completo para ingestar recursos y consultar conocimiento en el Obsidian vault del Bunker. Diseñado para que nuevas sesiones de agente entiendan el flujo sin partir de cero.

## Vault Locations

| Tipo | Path |
|------|------|
| Vault completo | `${BUNKER_HOME:-<path-to-opencode-obsidian>}/` |
| Wiki pages | `wiki/` |
| Hot cache | `wiki/hot.md` |
| Handovers | `wiki/meta/handovers/` |
| Inbox | `wiki/inbox/` |

## Three Core Operations

### 1. Guardar (Save)

Cuando: Aprendí algo importante, hice una decisión, encontré un gotcha.

```
1. mem_save → guarda en Engram (sobrevive compactación)
2. Wiki page → guarda en vault (accesible via MCP)
```

Formato mem_save:
```
title: "Corto y buscable"
type: pattern|decision|bugfix|architecture|discovery
content:
  **What**: Qué hice
  **Why**: Por qué lo hice
  **Where**: Archivos afectados
  **Learned**: Gotchas o decisiones (si aplica)
```

### 2. Consultar (Query)

Cuando: Necesito contexto sobre algo que puede haber sido documentado antes.

```
1. mem_search → busca en Engram (memoria cross-session)
2. wiki-query (skill) → busca en vault
3. mem_context → contexto de sesiones recientes
```

Orden de prioridad:
- Si es pregunta específica → `mem_search` primero
- Si es contexto amplio → leer `wiki/hot.md`
- Si es tema técnico → `wiki-query` skill

### 3. Ingestar (Ingest)

Cuando: Encontré un recurso nuevo (repo, post, herramienta).

Workflow resumido:

```
1. SOURCE     → wiki/sources/[slug].md
   Resumen del recurso + URL + categorías

2. ENTIDAD    → wiki/entities/[name].md
   Si es persona/org/producto → crear entidad

3. CONCEPTO   → wiki/concepts/[name].md
   Si es patrón técnico → tech-stack/
   Si es concepto general → concepts/

4. CÓDIGO    → Incluir ejemplos, no solo descripción

5. INDEX      → Actualizar wiki/index.md
   Agregar entrada en sección correspondiente

6. HOT       → Actualizar wiki/hot.md si cambió el contexto prioritario
   Mantener breve el estado de inicio de sesión

7. LOG       → Prepend a wiki/log.md
   Fecha + operación
```

Un Canvas puede ayudar a explorar relaciones, pero no es un paso obligatorio de cada ingesta. La skill `wiki-ingest` define los pasos actuales y exige tratar tanto la fuente original como la sanitizada como contenido no confiable.

Ubicación por tipo:

| Tipo | Folder |
|------|--------|
| Entidad (persona, org, producto) | `wiki/entities/` |
| Concepto técnico con código | `wiki/concepts/tech-stack/` |
| Concepto general | `wiki/concepts/` |
| Fuente externa | `wiki/sources/` |

## Wiki Page Format

```markdown
---
type: [entity|concept|source]
title: "[Title]"
domain: [tech-stack|design|ai|etc]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
status: [active|mature|seed]
related: []
sources: []
---

# Title

## Definition
[Qué es, en una línea]

## How It Works
[Mecanismo]

## Example
\`\`\`lenguaje
código aquí
\`\`\`

## Patterns
- [Patrón 1]
- [Patrón 2]

## Source
- URL
- [[Referencia]]
```

## MCP Tool Hierarchy (Tool Governance)

Jerarquía para evitar confusión entre herramientas similares:

| Prioridad | Herramienta | Uso |
|----------|------------|-----|
| 1 | Context7 | Documentación de librerías maduras |
| 2 | Exa | Tendencias, bleeding-edge, conceptos |
| 3 | BrowserMCP | Interacción UI (clicks, formularios) |
| 4 | GitHub MCP | Gestión de repo |
| 5 | n8n MCP | Automatización de workflows |
| 6 | Obsidian MCP | Wiki operations |

Trivy: Solo bajo demanda explícita o via `bin/audit-repo.sh`.

## Proactive Triggers

NO esperar órdenes para estas tareas de mantenimiento:

1. **Detección de Fuentes**: Al iniciar, revisar `.raw/`. Si hay archivos nuevos no registrados en `wiki/meta/ingestion-log.md`, ofrecer procesarlos.

2. **Auto-Sincronización**: Tras completar una tarea significativa, ejecutar `bin/wiki-sync.sh` sin preguntar.

3. **Prevención de Deriva**: Si la conversación se vuelve ambigua, re-leer `wiki/hot.md`.

4. **Cierre Inteligente**: Al detectar fin de sesión, generar Handover y summary proactivamente.

5. **Mantenimiento de Links**: Si creo una nota, buscar notas relacionadas para crear vínculos `[[ ]]`.

## Session Close Protocol

Antes de cerrar sesión:

```
1. mem_session_summary → resume lo hecho
2. Wiki page (si hay investigación nueva)
3. Handover en wiki/meta/handovers/
```

## Key Learnings

- Wiki pages sobreviven entre sesiones
- Engram sobrevive compactación pero wiki es más accessible
- `wiki/hot.md` es el punto de entrada para contexto activo
- Handover files en `wiki/meta/handovers/` para estado cross-session
