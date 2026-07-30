---
type: meta
title: "ENV STATUS"
updated: 2026-05-14
status: active
---

# Environment Status (Poderes del Agente)

> Este archivo es la "conciencia del entorno" del agente. Se actualiza cada vez que el stack cambia para asegurar que las sugerencias de código sean compatibles.

## 💻 Sistema Operativo
- **OS**: Arch Linux (`6.19.11-arch1-1`)
- **Kernel**: x86_64 Linux

## 🛠️ Tech Stack (Core)
- **Go**: `1.26.2` (Modern Standard)
- **Node.js**: `25.9.0` (Latest/Experimental)
- **Docker**: `29.4.0` (v29 series)
- **Git**: `2.53.0`

## 🧰 Herramientas Disponibles (CLI)
- `gh` (GitHub CLI) → ✅ Instalado
- `rg` (ripgrep) → ✅ Instalado
- `fd` (fd-find) → ✅ Instalado

## ⚠️ Restricciones / Notas
- Al usar **Arch Linux**, priorizar paquetes de repos oficiales o AUR si es necesario.
- **Node 25** puede tener breaking changes con librerías legacy; preferir ESM.
- **Go 1.26** soporta las últimas features de iterators y optimizaciones.

## 4. MCP & Interoperability
- **MCP Native**: This environment is optimized for MCP. All `skills/` should strive for MCP-compliance.
- **Cross-Agent Awareness**: The vault is designed to be the "source of truth" for multiple agents (OpenCode, Goose, etc.).
- **Local Sovereignty**: All tools and data reside locally on this Arch Linux machine.

---
**Last Updated**: 2026-04-19
