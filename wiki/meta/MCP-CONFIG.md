---
type: meta
title: "MCP CONFIG"
updated: 2026-05-14
status: active
---

# Model Context Protocol (MCP) Configuration

> Este documento detalla cómo "enchufar" herramientas externas al cerebro de los agentes para que operen de forma nativa sobre el Bunker.

## 🛡️ Trivy (Security Audit)
Permite al agente realizar escaneos de vulnerabilidades y secretos en lenguaje natural.

**Estado**: ⏸️ Deshabilitado en `opencode.json` para reducir ruido cognitivo. Usar `bin/audit-repo.sh` para ejecuciones manuales.

## 📡 n8n (Advanced AI Orchestration - MCP)
**Estado**: ✅ Conectado en `opencode.json` (SSE SSE Mode).

---
**Last Updated**: 2026-04-20
