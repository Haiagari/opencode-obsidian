---
type: meta
title: "OBSIDIAN PLUGINS"
updated: 2026-05-14
status: active
---

# Obsidian Plugin Setup (Bunker Edition)

> Estos plugins son los que permiten que Obsidian sea el "Panel de Control" del ecosistema agéntico.

## Local Config Policy

These plugin state files are intentionally local and may remain in the vault:

- `.obsidian/plugins/calendar/data.json`
- `.obsidian/plugins/thino/data.json`
- `.obsidian/plugins/obsidian-excalidraw-plugin/data.json`

Never commit `.obsidian/plugins/obsidian-local-rest-api/data.json`. Use `data.example.json` and `SECURITY-NOTE.md` instead.

## 💎 1. Dataview / Obsidian Bases
**Para qué**: Generar tablas dinámicas de tus agentes y proyectos.
- **Instalación**: Buscalo en Community Plugins.
- **Configuración**: Habilitar "JavaScript Queries".

## 🔌 2. OpenCode / MCP Client
**Para qué**: Conectar Obsidian con el servidor MCP de n8n y Trivy.
- **Instalación**: Sigue los pasos en [[MCP-CONFIG]].
- **Uso**: Podrás disparar el Alerter de n8n desde un botón en Obsidian.

## 🎨 3. Templater
**Para qué**: Usar los templates de `_templates/` con lógica dinámica.
- **Configuración**: Apuntar la carpeta de templates a `_templates/`.

## 🖼️ 4. Obsidian Banners
**Para qué**: Para que el banner SVG que creamos hoy se vea arriba de cada nota.
- **Configuración**: Habilitar banners por defecto.

---
**Last Updated**: 2026-04-19
