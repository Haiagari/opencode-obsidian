---
type: meta
title: "INGEST PROTOCOL"
updated: 2026-05-14
status: active
---

# Ingestion Protocol (Bunker Core)

**Status**: Core Standard
**Type**: Procedural Memory
**Parent**: [[_index]]

> Este protocolo define cómo el agente debe procesar nueva información para asegurar que el conocimiento se componga de forma estructurada.

## 📥 El Ciclo de Ingestión
1. **Raw Capture**: El archivo se guarda en `.raw/` (fuente inmutable).
2. **Entity Extraction**: Identificar personas, herramientas, agentes y empresas.
3. **Concept Mapping**: Extraer patrones, arquitecturas y lecciones técnicas.
4. **Linkage**: Buscar notas existentes en la wiki para crear vínculos `[[ ]]`.
5. **Synchronization**: Actualizar la DB de la `ozy-api` y notificar vía Telegram.

## 📝 Reglas de Formateo
- **Entidades**: Usar template `_templates/entity.md`.
- **Conceptos**: Usar template `_templates/concept.md`.
- **Fuentes**: Crear una nota en `wiki/sources/` que resuma el documento original.

## 🤖 Trigger de Automatización
Al ejecutar `./bin/bunker-ingest.sh`, el agente debe disparar automáticamente la tarea de síntesis y creación de notas.

---
**Last Updated**: 2026-04-19
