---
type: meta
title: "HANDOVER"
updated: 2026-05-14
status: active
---

# Agent Handover Protocol (AHP)

**Status**: Core Standard
**Version**: 1.0
**Parent**: [[_index]]

> Protocolo para la transferencia de estado y contexto entre diferentes agentes (OpenCode, Goose, Hermes, etc.) asegurando continuidad sin pérdida de información.

## 📋 Estructura del Handover
Cada sesión exitosa DEBE generar un archivo en `wiki/meta/handovers/YYYY-MM-DD-session-name.md` siguiendo esta estructura:

### 1. Mission Status (Estado de Misión)
- **Goal**: Qué estábamos tratando de lograr.
- **Outcome**: Éxito / Parcial / Fallo.
- **Current Blockers**: Qué nos frenó.

### 2. Context Anchors (Anclas de Contexto)
- **Active Files**: Archivos modificados en esta sesión.
- **New Entities**: Nuevas herramientas o proyectos registrados.
- **Decision Log**: Referencia a ADRs o comparativas creadas.

### 3. Procedural Memory (Lo que el próximo agente debe saber)
- **Gotchas**: Errores encontrados y cómo se solucionaron.
- **Patterns**: Qué patrones se aplicaron (ej. Hermes, DeepTutor).

### 4. Next Actions (Backlog Inmediato)
- [ ] Tarea 1 (Prioridad)
- [ ] Tarea 2

## 🔄 Cómo Leer un Handover
El agente entrante DEBE:
1. Buscar el último archivo en `wiki/meta/handovers/`.
2. Leer el `ENV-STATUS` para sincronizar versiones.
3. Cargar las `Next Actions` en su `todo` list.

---
**Last Updated**: 2026-04-19
