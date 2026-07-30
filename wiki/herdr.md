# HERRD — Guía Completa Definitiva

> Terminal workspace manager for AI coding agents.
> Versión: 0.7.5 | Licencia: Apache 2.0 | Autor: Oğulcan Çelik
> Repo: https://github.com/ogulcancelik/herdr | Web: https://herdr.dev

---

## Índice

1. [Introducción](#1-introducción)
2. [El Problema Que Resuelve](#2-el-problema-que-resuelve)
3. [Arquitectura Técnica](#3-arquitectura-técnica)
4. [Conceptos Fundamentales](#4-conceptos-fundamentales)
5. [Agents — El Corazón de Herdr](#5-agents--el-corazón-de-herdr)
6. [Instalación](#6-instalación)
7. [Primeros Pasos](#7-primeros-pasos)
8. [Interfaz de Usuario](#8-interfaz-de-usuario)
9. [Keybindings y Atajos](#9-keybindings-y-atajos)
10. [Comandos CLI](#10-comandos-cli)
11. [Socket API](#11-socket-api)
12. [Plugins](#12-plugins)
13. [Integraciones con Agents](#13-integraciones-con-agents)
14. [Modo Remoto y SSH](#14-modo-remoto-y-ssh)
15. [Configuración](#15-configuración)
16. [Persistencia y Sesiones](#16-persistencia-y-sesiones)
17. [Flujos de Trabajo Avanzados](#17-flujos-de-trabajo-avanzados)
18. [Agent Automation](#18-agent-automation)
19. [Comparativa con Alternativas](#19-comparativa-con-alternativas)
20. [Ecosistema y Comunidad](#20-ecosistema-y-comunidad)
21. [Desarrollo y Contribución](#21-desarrollo-y-contribución)
22. [Preguntas Frecuentes](#22-preguntas-frecuentes)
23. [Referencias y Recursos](#23-referencias-y-recursos)

---

## 1. Introducción

Herdr es un **multiplexor de terminal** construido específicamente para trabajar con **AI coding agents**. Está escrito en **Rust** de principio a fin, sin Electron, sin JavaScript, sin runtime externo. Es un único binario de ~8MB que corre en Linux, macOS y Windows.

La idea central es simple: en lugar de tener que abrir múltiples ventanas de terminal, pestañas de VSCode o sesiones de tmux para manejar varios agents de IA, herdr te da **una sola terminal con todo organizado**: paneles divididos, detección automática de agents, estado visible de cada uno, y la capacidad de que los agents se comuniquen entre sí.

No es un wrapper de tmux. No es "tmux con esteroides". Es una **arquitectura completamente nueva** diseñada alrededor del problema específico de orquestar agents de IA en la terminal.

### Filosofía de Diseño

El código fuente del proyecto (`AGENTS.md`) explicita estos principios:

1. **State separado del runtime**: `AppState` es pure data, testeable sin PTYs ni async. `PaneState` está separado de `PaneRuntime`. La lógica de workspaces no necesita terminales reales.
2. **Render puro**: `compute_view()` maneja geometría y mutaciones. `render()` toma `&AppState` y solo dibuja. Nunca se muta estado durante el renderizado.
3. **Sin god objects**: si un módulo está haciendo demasiadas cosas, se divide. `app/` ya está dividido en state, actions, input. Y se mantiene así.
4. **Código de plataforma aislado**: el comportamiento OS-specific vive en `src/platform/<os>.rs`. Solo traits compartidos, tipos, wrappers y contratos testeables en `src/platform/mod.rs`. Los módulos core no tienen `#[cfg(target_os)]`.
5. **Detección desacoplada**: el detector lee una captura de pantalla (bottom-buffer), nunca toca el parser ni el estado del viewport.
6. **Runtime/client boundary**: herdr está migrando hacia un protocolo server-owned, donde el TUI es un cliente más. El trabajo nuevo no debe profundizar el acoplamiento server/TUI actual.

---

## 2. El Problema Que Resuelve

### El escenario antes de herdr

Trabajás con coding agents (Claude Code, Codex, Cursor, etc.). Tu día se ve así:

- Abrís una terminal → corrés Claude Code para implementar una feature
- Abrís otra pestaña → corrés Codex para escribir tests
- Abrís una tercera → tenés el servidor de desarrollo corriendo
- Abrís una cuarta → monitoreás logs
- Querés que un agent revise el trabajo de otro → no hay forma, tenés que copiar y pegar manualmente
- Te desconectás del SSH → todo muere, perdés estado
- Querés ver rápidamente cuál agent está esperando tu input → tenés que switchear entre 5 pestañas

Cada vez que un agent necesita una decisión tuya (aprobar una tool call, responder una pregunta), se **bloquea** y no avanza hasta que switcheás a su pestaña, ves el mensaje, y respondés. Con 3-4 agents trabajando en paralelo, esto se vuelve inmanejable.

### Lo que herdr cambia

Herdr ataca todos esos problemas:

1. **Visibilidad unificada**: una sola terminal muestra todos tus agents, su estado (`blocked`, `working`, `done`, `idle`), y podés saltar al que necesita atención.
2. **Paralelismo real**: agents corriendo en paneles separados, cada uno en su propio PTY, sin interferencias.
3. **Persistencia**: detach y todo sigue corriendo. Reconnect y volvés exactamente a donde estabas.
4. **Comunicación entre agents**: via socket API, un agent puede crear paneles, enviar input, leer output, y esperar a que otro agent termine.
5. **Mouse + teclado**: elegís por momento. Click para enfocar, drag para resize, right-click para menús. Y si preferís teclado, tenés prefix mode estilo tmux.
6. **Plugins**: extensible sin modificar el core.

---

## 3. Arquitectura Técnica

### Diagrama de Arquitectura

```
┌──────────────────────────────────────────────────────────────────┐
│                    TU TERMINAL (TUI Cliente)                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  ratatui (rendering) + crossterm (terminal I/O)            │  │
│  │  - Renderiza workspaces, tabs, panes                       │  │
│  │  - Captura mouse, teclado                                   │  │
│  │  - Estado de UI puro (colores, layout, selección)          │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────────┘
                              │ socket IPC
                              │ (Unix socket / Windows named pipe)
┌─────────────────────────────▼────────────────────────────────────┐
│                     HERRD SERVER (Daemon)                         │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ PaneManager  │  │ AgentDetector │  │ SessionPersister       │  │
│  │ - PTY lifecycle│ │ - Manifests   │  │ - Serializa estado    │  │
│  │ - input/output │ │ - Screen snap │  │ - Restaura sesión     │  │
│  │ - resize       │ │ - Lifecycle   │  │ - Maneja handoff      │  │
│  └─────────────┘  └──────────────┘  └────────────────────────┘  │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ PluginEngine │  │ SocketAPI    │  │ IntegrationManager     │  │
│  │ - Manifests  │  │ - JSON reqs  │  │ - Lifecycle hooks     │  │
│  │ - Actions    │  │ - Events     │  │ - Agent integraciones │  │
│  │ - Panes      │  │ - Notify     │  │                        │  │
│  └─────────────┘  └──────────────┘  └────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  portable-pty + libghostty-vt (fork vendored)            │    │
│  │  - Emulación de terminal                                │    │
│  │  - Render de caracteres, colores, estilos               │    │
│  │  - Kitty graphics protocol (imágenes)                   │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### Stack Técnico Completo

#### Dependencias Core (de Cargo.toml)

- `base64` — Codificación base64
- `bincode` — Serialización binaria (serde)
- `bytes` — Manejo de buffers
- `clap` — CLI argument parser
- `clap_complete` — Generación de completions
- `crossterm` — Terminal I/O cross-platform
- `ctrlc` — Manejo de Ctrl+C
- `interprocess` — IPC (sockets/named pipes)
- `libc` — Llamadas C en Unix
- `portable-pty` — PTY management (fork vendored)
- `png` — Decodificación PNG (imágenes)
- `ratatui` — TUI rendering framework
- `regex` — Expresiones regulares
- `serde` — Serialización
- `serde_ignored` — Detectar campos no usados en config
- `serde_json` — JSON
- `sha2` — Hashing SHA-256
- `tokio` — Async runtime
- `toml` — Config parser
- `tracing` — Logging estructurado
- `tracing-subscriber` — Log output
- `unicode-width` — Ancho de caracteres Unicode
- `schemars` — JSON Schema generation

#### Dependencias Windows

- `windows-sys` — API de Windows: Threading, Console, Memory, Pipes, Jobs, Processes, Shell, UI, DataExchange

#### Innovación Técnica: Vendored libghostty-vt

Herdr vendea su propio fork de `libghostty-vt`, que es el motor de render de terminal del emulador **Ghostty**. Esto es inusual pero estratégico: en lugar de depender de una librería de terceros para el renderizado de terminal (como hace la mayoría de los multiplexores), herdr tiene control total sobre cómo se renderiza cada caracter, cada color, cada estilo.

Los parches locales sobre el código vendored se trackean en:
- `vendor/libghostty-vt.vendor.json` — commit upstream actual
- `vendor/libghostty-vt.patches.md` — documentación de cada patch
- `vendor/patches/libghostty-vt/` — archivos patch

Cada patch documenta: por qué existe, el issue de herdr relacionado, el PR/discusión upstream, el commit base vendored, archivos tocados, verificación, y condición exacta de remove.

#### Arquitectura de Módulos (src/)

```
src/
├── main.rs                    # Entry point, setup del server
├── build_info.rs              # Información de compilación
├── cli.rs                     # CLI principal (clap)
├── cli/                       # Subcomandos CLI
│   ├── agent.rs               #   agent subcommand
│   ├── pane.rs                #   pane subcommand
│   ├── workspace.rs           #   workspace subcommand
│   ├── tab.rs                 #   tab subcommand
│   ├── session.rs             #   session subcommand
│   ├── config.rs              #   config subcommand
│   ├── plugin.rs              #   plugin subcommand
│   ├── integration.rs         #   integration subcommand
│   ├── update.rs              #   update subcommand
│   └── ...                    #   otros subcomandos
├── server/                    # Servidor runtime
├── client/                    # Cliente TUI
├── app/                       # Estado y lógica de UI
│   ├── state.rs               # AppState puro (testeable sin PTYs)
│   ├── actions.rs             # Acciones de UI
│   └── input.rs               # Procesamiento de input
├── ui.rs                      # Render principal (ratatui)
├── ui/                        # Componentes de UI
│   ├── sidebar.rs             # Sidebar de workspaces/agents
│   ├── pane_widget.rs         # Widget de pane
│   ├── tab_bar.rs             # Barra de tabs
│   └── modals.rs              # Diálogos modales
├── pane.rs                    # Lógica de paneles (145KB!)
├── pane/                      # Submódulos de pane
│   ├── runtime.rs             # PaneRuntime (con PTY)
│   └── state.rs               # PaneState (puro)
├── workspace.rs               # Lógica de workspaces (54KB)
├── session.rs                 # Gestión de sesiones (36KB)
├── layout.rs                  # Algoritmos de layout (31KB)
├── raw_input.rs               # Procesamiento raw de input (83KB)
├── detect/                    # Detección de agents
│   ├── manifest.rs            # Parseo de manifiestos TOML
│   ├── detector.rs            # Detector de agents
│   └── manifests/             # Manifiestos incluidos
├── config.rs                  # Config parser
├── config/                    # Submódulos de config
├── protocol/                  # Wire protocol server/cliente
├── pty/                       # Abstracción de PTY
├── platform/                  # Código OS-specific
│   ├── mod.rs                 # Traits compartidos
│   ├── linux.rs / macos.rs / windows.rs
├── persist/                   # Serialización de sesión
├── remote/                    # Conexión remota SSH
├── plugin_command.rs          # Ejecución de plugins
├── plugin_paths.rs            # Resolución de rutas de plugins
├── events.rs                  # Sistema de eventos
├── ipc.rs                     # Comunicación IPC
├── kitty_graphics.rs          # Kitty graphics protocol (55KB)
├── selection.rs               # Selección de texto (17KB)
├── sound.rs                   # Sonidos (13KB)
├── update.rs                  # Sistema de actualización (117KB)
├── worktree.rs                # Git worktree integration (28KB)
├── handoff_runtime.rs         # Handoff runtime
├── agent_resume.rs            # Resume de agents
├── metadata_tokens.rs         # Tokens de metadata
├── terminal_modes.rs          # Modos de terminal
├── terminal_notify.rs         # Notificaciones de terminal
├── terminal_theme.rs          # Temas de terminal
├── noninteractive_process.rs  # Procesos no interactivos
├── checksum.rs                # Checksums
├── logging.rs                 # Logging (16KB)
├── popup_size.rs              # Tamaño de popups
├── product_announcements.rs   # Anuncios de producto
├── release_notes.rs           # Notas de release
├── render_prof.rs             # Profiling de render
└── build_info.rs              # Info de build
```

### Arquitectura Server/Cliente en Detalle

Herdr no es una aplicación monolítica. Tiene una arquitectura **server/cliente** con comunicación por socket IPC.

#### Server (Daemon)
- Corre como proceso en background
- Dueño de los PTYs (terminales virtuales)
- Maneja el ciclo de vida de paneles, tabs, workspaces
- Ejecuta la detección de agents
- Persiste y restaura el estado de sesión
- Expone una **socket API** para que agents y scripts se comuniquen
- Soporta **live handoff**: cuando actualizás herdr, el nuevo server toma el control sin matar los paneles

#### Cliente (TUI)
- Se conecta al server via socket Unix (Linux/macOS) o named pipe (Windows)
- Renderiza la interfaz con ratatui
- Maneja input de mouse y teclado
- Puede attach/detach sin afectar el server
- Múltiples clientes pueden conectarse al mismo server simultáneamente

#### Protocolo IPC
- Transporte: `interprocess` (sockets Unix / named pipes)
- Serialización: `bincode` (binario, rápido)
- Mensajes tipados con serde
- Versionado (`PROTOCOL_VERSION` en `src/protocol/wire.rs`)

---

## 4. Conceptos Fundamentales

### Pane (Panel)

Un **pane** es la unidad más básica: un terminal real con un proceso adentro.

```
┌─────────────────────┐
│ Pane w1:p1           │
│ $ claude             │
│                      │
│ ● Working...         │
│                      │
└─────────────────────┘
```

**Características:**
- Es un PTY real, no una simulación
- Corre cualquier comando (shell, agent, server, editor)
- Se puede dividir (split) a la derecha o abajo
- Se puede redimensionar con mouse o teclado
- Se puede renombrar para identificarlo fácilmente
- Tiene scrollback (historial)
- Soporta imágenes (Kitty graphics protocol)
- Soporta OSC 8 hyperlinks
- IDs estables no reutilizados: `w1:p1`, `w1:p2`, etc.

**Comandos de pane:**
```bash
herdr pane split --current --direction right --cwd "$PWD" --no-focus
herdr pane run w1:p2 "npm test"
herdr pane read w1:p2 --source recent-unwrapped --lines 120
herdr pane wait-output w1:p2 --match "PASS" --timeout 60000
```

**Fuentes de lectura de un pane:**
| Fuente | Descripción |
|--------|-------------|
| `visible` | Viewport actualmente renderizado |
| `recent` | Output renderizado reciente (incluye soft wraps) |
| `recent-unwrapped` | Output reciente con soft wraps unidos (ideal para logs) |
| `detection` | Bottom-buffer usado para detección de agents |

### Tab

Un **tab** es un conjunto de paneles con un layout específico.

```
┌──────Tab: agents──────┬──────Tab: logs──────┬──────Tab: server──┐
│  ┌────────┬────────┐  │  ┌────────────────┐  │  ┌────────────────┐│
│  │ claude │ codex  │  │  │ tail -f app.log│  │  │ npm run dev    ││
│  ├────────┴────────┤  │  └────────────────┘  │  └────────────────┘│
│  │ sidebar         │  │                      │                    │
│  └─────────────────┘  │                      │                    │
└────────────────────────┴──────────────────────┴────────────────────┘
```

**Características:**
- Contiene 1 o más paneles en un layout
- Se pueden crear, renombrar, reordenar y cerrar
- ID: `w1:t1`, `w1:t2` (workspace-prefixed)
- Navegación por teclado (`prefix+n/p`) o mouse

### Workspace

Un **workspace** es el contenedor de proyecto. Es la unidad principal de organización.

```
┌──────────────────────────────────────────────────────────────┐
│  Workspace: mi-feature (w1)                                   │
│  ┌──────Tab: dev──────────┬──────Tab: review──────┐           │
│  │ claude codeando        │ codex revisando       │           │
│  │ npm run dev            │                        │           │
│  └────────────────────────┴────────────────────────┘           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Sidebar: ● blocked ● working ◌ idle ◌ done              │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**Características:**
- Un workspace por proyecto activo
- La sidebar muestra el estado del workspace según el peor estado de sus agents
- Se pueden crear, renombrar, cerrar
- ID: `w1`, `w2`

### Session

Una **session** es el namespace completo del server de herdr: todos los workspaces, tabs, paneles, agents y su estado.

```
Session: default
├── Workspace w1: mi-feature
│   ├── Tab w1:t1: dev
│   │   ├── Pane w1:p1 (claude ● working)
│   │   └── Pane w1:p2 (npm run dev)
│   ├── Tab w1:t2: review
│   │   └── Pane w1:p3 (codex ◌ idle)
│   └── Tab w1:t3: logs
│       └── Pane w1:p4 (tail -f)
└── Workspace w2: side-project
    └── Tab w2:t1
        └── Pane w2:p1 (opencode ● blocked)
```

**Características:**
- Persistida en disco, sobrevive a reinicios
- Se puede tener múltiples sessions con **named sessions**
- Cada session tiene su propio server, sockets, y estado
- `herdr session attach <nombre>` para switchear

### Named Sessions

Las named sessions son espacios de trabajo completamente aislados:

```bash
herdr session attach work       # Session para el laburo
# ... trabajás con tus agents ...
ctrl+b q                        # detach
herdr session attach side-project  # Session personal
# ... trabajás en otra cosa ...
ctrl+b q
herdr session attach work       # Volvés al laburo
```

Cada una tiene: su propio server process, sockets IPC, estado persistido, workspaces/tabs/paneles independientes.

### Relación entre Conceptos

```
Herdr Instance
└── Server process
    └── Session (default o named)
        ├── Workspace w1
        │   ├── Tab w1:t1
        │   │   ├── Pane w1:p1 (agent corriendo)
        │   │   └── Pane w1:p2 (terminal)
        │   └── Tab w1:t2
        │       └── Pane w1:p3 (server)
        └── Workspace w2
            └── Tab w2:t1
                └── Pane w2:p1 (otro agent)
```

Las IDs siguen el patrón:
- Workspace: `w1`, `w2`, `w3`
- Tab: `w1:t1`, `w1:t2` (prefijo de workspace)
- Pane: `w1:p1`, `w1:p2` (prefijo de workspace)

Las IDs cerradas no se reutilizan. Si movés un pane a otro workspace, recibe una nueva ID calificada por workspace.

### Múltiples Clientes

Varios clientes TUI pueden conectarse al mismo server simultáneamente:

```bash
# Terminal 1
herdr                                    # primer cliente
# Terminal 2 (otra ventana/SSH)
herdr                                    # segundo cliente, mismo server
# Terminal 3 (SSH desde el teléfono)
herdr                                    # tercer cliente
```

Todos ven el mismo estado. Cada uno tiene su propio viewport y foco.

---

## 5. Agents — El Corazón de Herdr

### ¿Qué es un Agent para Herdr?

Un **agent** es un proceso que herdr reconoce dentro de un pane. La detección puede ocurrir de dos maneras:

1. **Screen Detection**: herdr lee el bottom-buffer del terminal y lo compara contra manifiestos TOML que describen cómo se ve cada agent en cada estado.
2. **Lifecycle Hooks**: el agent reporta su estado directamente a herdr a través de hooks instalados por las integraciones.

### Agents Soportados

| Agent | Autoridad de Estado | Rol de Integración |
|-------|-------------------|-------------------|
| **Pi** | Lifecycle hooks + screen manifest | Estado + sesión |
| **OMP** | Lifecycle hooks | Estado |
| **Kimi Code CLI** | Lifecycle hooks + screen manifest | Estado + sesión |
| **Hermes Agent** | Lifecycle hooks + screen manifest | Estado + sesión |
| **OpenCode** | Lifecycle plugin + screen manifest | Estado + sesión |
| **Kilo Code CLI** | Lifecycle plugin + screen manifest | Estado + sesión |
| **MastraCode** | Lifecycle hooks | Estado + sesión |
| **Claude Code** | Screen manifest | Sesión |
| **Codex** | Screen manifest | Sesión |
| **GitHub Copilot CLI** | Screen manifest | Sesión |
| **Devin CLI** | Screen manifest | Sesión |
| **Qoder CLI** | Screen manifest | Sesión |
| **Droid** | Screen manifest | Sesión |
| **Cursor Agent CLI** | Screen manifest | Sesión |
| **Amp** | Screen manifest | Ninguna |
| **Grok CLI** | Screen manifest | Ninguna |
| **Antigravity CLI** | Screen manifest | Ninguna |
| **Kiro CLI** | Screen manifest | Ninguna |
| **Maki** | Screen manifest | Ninguna |

Detectados pero menos probados: Gemini CLI, Cline.

### Estados de un Agent

| Estado | Significado | Implicancia |
|--------|-------------|-------------|
| **blocked** | El agent necesita input, aprobación o decisión | Atenderlo urgente |
| **working** | El agent está procesando activamente | Dejarlo laburar |
| **done** | Terminó y no lo has visto aún | Revisarlo |
| **idle** | Terminó y ya fue visto | No requiere atención |
| **unknown** | No se puede clasificar | Revisar manualmente |

### State Rollups

Herdr agrega el estado hacia arriba en la jerarquía:

```
Workspace w1 (BLOCKED)     ← blocked porque tiene un agent blocked
├── Tab t1 (WORKING)       ← working por el agent codeando
│   ├── Pane p1: claude (● WORKING)
│   └── Pane p2: npm dev
└── Tab t2 (BLOCKED)       ← blocked por el agent esperando input
    └── Pane p3: codex (● BLOCKED)
```

Regla: si **algún** agent está `blocked` → todo es blocked. Si no hay blocked pero hay `working` → todo es working. Si no hay blocked ni `working` pero hay `done` → todo es done.

### Screen Detection (Detección por Pantalla)

1. herdr identifica el **foreground process** en cada pane
2. Si es un agente conocido, lee el **bottom-buffer** del terminal (no el viewport scrolleado)
3. Evalúa los **manifiestos TOML** contra esa captura
4. Clasifica el estado según qué reglas del manifiesto matchean

La detección usa el bottom-buffer, no el viewport. El scroll del usuario no afecta la detección.

### Lifecycle Hooks

Para agents con integraciones completas, herdr instala hooks que el agent llama directamente:
- Cuando empieza a trabajar → `state: working`
- Cuando espera input → `state: blocked`
- Cuando termina → `state: done`

Ventaja: más preciso que screen detection, no depende de cómo se ve la UI del agent.

Agents con hooks completos: Pi, OMP, OpenCode (plugin), Kilo Code CLI, MastraCode, Kimi Code CLI, Hermes Agent.

Agents con integración parcial (solo sesión): Claude Code, Codex, Copilot CLI, Devin CLI, Qoder CLI, Droid, Cursor Agent CLI.

### Instalar Integraciones

```bash
herdr integration status
herdr integration install claude
herdr integration install codex
herdr integration install opencode
herdr integration status
```

### Detección en VMs y Sandboxes

```bash
HERDR_AGENT=claude fence -- claude           # Linux
HERDR_AGENT=claude nono run --profile claude -- claude  # macOS
```

### Manifiestos de Detección

Archivos TOML. Origen:
- **Bundled**: dentro del binario (`src/detect/manifests/`)
- **Remotos**: herdr.dev, cacheados localmente
- **Override local**: `~/.config/herdr/agent-detection/<agent>.toml`

El override local siempre gana.

```bash
herdr server reload-agent-manifests
herdr server update-agent-manifests
```

### Explicar Estado de un Agent

```bash
herdr agent explain w1:p1
herdr agent explain w1:p1 --json
```

El explain output muestra: agente detectado, estado final, si screen detection fue skippeada, fuente del manifiesto, versión, override local, regla que matcheó, evidencia visible.

### Labels Personalizadas

```bash
herdr agent rename w1:p1 "reviewer"
herdr agent rename "reviewer" --clear
```

### Metadata Tokens

```bash
herdr pane report-agent w1:p1 --source custom:indexer --agent docs-bot --state working
herdr pane report-metadata w1:p1 --source custom:indexer-display --token summary=indexing
```

### Direct Attach

```bash
herdr agent attach reviewer
herdr agent attach reviewer --takeover
```

---

## 6. Instalación

### Linux / macOS

```bash
curl -fsSL https://herdr.dev/install.sh | sh
```

### macOS (Homebrew)

```bash
brew install herdr
```

### Nix

```bash
nix profile install github:ogulcancelik/herdr
```

### Mise

```bash
mise use -g herdr
```

### Windows

```bash
powershell -ExecutionPolicy Bypass -c "irm https://herdr.dev/install.ps1 | iex"
```

### Desde fuente

```bash
git clone https://github.com/ogulcancelik/herdr
cd herdr
cargo build --release
```

### Verificar

```bash
herdr --version
```

### Directorios

```
~/.config/herdr/
├── config.toml
├── herdr.log / herdr-client.log / herdr-server.log
├── agent-detection/
└── plugins/
```

---

## 7. Primeros Pasos

### 1. Arrancar

```bash
cd ~/mi-proyecto
herdr
```

### 2. Workspace

```bash
prefix+Shift+n       # Nueva workspace
```

### 3. Dividir paneles

Mouse: click derecho → Split Right/Down
Teclado: `prefix+v` (derecha), `prefix+-` (abajo)

### 4. Agent

En un pane, ejecutá tu agente normalmente:

```bash
claude
# o codex, opencode, etc.
```

Herdr lo detecta automáticamente.

### 5. Sidebar

`prefix+b` para toggle. Ahí ves el estado de todos tus workspaces y agents.

### 6. Detach/Reattach

```bash
ctrl+b q   # Detach (server sigue corriendo)
herdr      # Reattach desde cualquier terminal
```

### 7. Parar todo

```bash
herdr server stop
```

---

## 8. Interfaz de Usuario

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ [workspace: mi-feature] [tab: dev] [tab: review] ...  [+][x]        │
├──────────────────────────────────────┬──────────────────────────────┤
│  ┌──────────────────────┬──────────┐│  ● sidebar                   │
│  │  claude codeando     │  codex   ││  w1: mi-feature             │
│  │  ● working           │  ● blocked││  ├─ t1 ●                   │
│  ├──────────────────────┴──────────┤│  └─ t2 ◌                   │
│  │  npm run dev (logs)            ││  w2: side-project           │
│  └─────────────────────────────────┘│  └─ t1 ●                   │
├──────────────────────────────────────┴──────────────────────────────┤
│ [status bar: agents, workspace, version]                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Interacción con Mouse

| Acción | Resultado |
|--------|-----------|
| Click en un pane | Lo enfoca |
| Click en una tab | Cambia a esa tab |
| Click en sidebar | Salta a workspace/agent |
| Drag borders | Redimensiona |
| Right-click | Menú contextual |
| Drag seleccionar texto | Copia al clipboard |
| Doble-click en texto | Copia palabra |
| Ctrl+click en URL | Abre en browser |

### Copy Mode

`prefix+[` para copy mode. Navegación vi-style, búsqueda con `/`, selección con `v`, copia con `y`.

---

## 9. Keybindings y Atajos

### Las 5 Esenciales

| Acción | Tecla |
|--------|-------|
| Nueva tab | `prefix+c` |
| Split derecha / abajo | `prefix+v` / `prefix+-` |
| Mover paneles | `prefix+h/j/k/l` |
| Navegación workspaces | `prefix+w` |
| Detach | `prefix+q` |

### Paneles

| Acción | Tecla |
|--------|-------|
| Zoom pane | `prefix+z` |
| Cerrar pane | `prefix+x` |
| Swap pane | `prefix+Shift+h/j/k/l` |
| Resize mode | `prefix+r` |
| Copy mode | `prefix+[` |

### Tabs

| Acción | Tecla |
|--------|-------|
| Siguiente / anterior | `prefix+n` / `prefix+p` |
| Ir a tab 1-9 | `prefix+1..9` |
| Renombrar | `prefix+Shift+t` |
| Cerrar | `prefix+Shift+x` |

### Workspaces y Sesión

| Acción | Tecla |
|--------|-------|
| Nueva workspace | `prefix+Shift+n` |
| Renombrar workspace | `prefix+Shift+w` |
| Cerrar workspace | `prefix+Shift+d` |
| Goto picker | `prefix+g` |
| Toggle sidebar | `prefix+b` |
| Ver bindings | `prefix+?` |

### Prefix-Free (atajos directos)

Configurables con `ctrl+alt` como base:

```toml
[keys]
focus_pane_left = ["prefix+h", "ctrl+alt+h"]
focus_pane_down = ["prefix+j", "ctrl+alt+j"]
focus_pane_up = ["prefix+k", "ctrl+alt+k"]
focus_pane_right = ["prefix+l", "ctrl+alt+l"]
```

### Cambiar Prefix

```toml
[keys]
prefix = "ctrl+a"
```

---

## 10. Comandos CLI

### Generales

```bash
herdr                                    # Launch/attach TUI
herdr status                             # Estado server + client
herdr --remote <host>                   # Attachar remoto
herdr --session <nombre>                # Sesión nombrada
herdr --version                          # Versión
herdr update                             # Actualizar
```

### Workspace

```bash
herdr workspace list
herdr workspace create
herdr workspace rename <id> <nombre>
herdr workspace close <id>
```

### Tab

```bash
herdr tab list --workspace <id>
herdr tab create --workspace <id>
herdr tab rename <id> <nombre>
herdr tab close <id>
```

### Pane

```bash
herdr pane split --current --direction right|down
herdr pane run <id> "comando"
herdr pane read <id> --source visible|recent|recent-unwrapped|detection
herdr pane wait-output <id> --match "texto" --timeout 60000
herdr pane list --workspace <id>
herdr pane zoom <id>
herdr pane close <id>
herdr pane rename <id> "nombre"
```

### Agent

```bash
herdr agent list
herdr agent start <nombre> --kind <kind> --pane <id>
herdr agent prompt <nombre> "mensaje" --wait
herdr agent read <nombre> --source recent-unwrapped
herdr agent wait <nombre> --until blocked --timeout 30000
herdr agent send-keys <nombre> ctrl+c
herdr agent explain <nombre> --json
herdr agent attach <nombre>
herdr agent rename <pane-id> "nombre"
```

### Session

```bash
herdr session list
herdr session attach <nombre>
```

### Server

```bash
herdr server stop
herdr server reload-config
herdr server reload-agent-manifests
```

### Plugin

```bash
herdr plugin install owner/repo[/subdir]
herdr plugin link /path
herdr plugin list
herdr plugin uninstall <id>
herdr plugin action list --plugin <id>
herdr plugin action invoke <id.action>
```

### Integration

```bash
herdr integration install <agent>
herdr integration status
```

---

## 11. Socket API

Además del CLI, herdr expone una **socket API** JSON para que scripts y agents se comuniquen programáticamente.

### Conectarse

```bash
echo "$HERDR_SOCKET_PATH"
# /run/user/1000/herdr/herdr-default.sock
```

### Métodos

- `workspace/create`, `workspace/list`
- `tab/create`, `tab/list`
- `pane/split`, `pane/run`, `pane/read`, `pane/wait_output`
- `agent/list`, `agent/start`, `agent/prompt`, `agent/wait`, `agent/read`, `agent/get`

### Eventos

- `workspace.created/closed`
- `tab.created/closed`
- `pane.created/closed/output`
- `agent.state_changed/created/destroyed`
- `plugin.action.triggered`

### Ejemplo de automation

```bash
herdr agent wait feature --until done --timeout 300000
herdr pane split --current --direction right --cwd "$PWD" --no-focus
herdr agent start reviewer --kind codex --pane "$PANE_ID"
herdr agent prompt reviewer "Review the diff" --wait
herdr agent read reviewer --source recent-unwrapped --lines 200
```

---

## 12. Plugins

### ¿Qué es?

Un directorio con `herdr-plugin.toml` y comandos ejecutables. Cualquier lenguaje: Bash, Python, Node, Rust, Go, Lua...

### Manifest

```toml
id = "example.workspace-tools"
name = "Workspace Tools"
version = "0.1.0"
min_herdr_version = "0.7.0"
platforms = ["linux", "macos", "windows"]

[[actions]]
id = "apply"
title = "Apply layout"
contexts = ["workspace"]
command = ["node", "dist/apply.js"]

[[panes]]
id = "board"
title = "Project board"
placement = "overlay"
command = ["herdr-board"]

[[events]]
on = "worktree.created"
command = ["herdr", "workspace", "list"]
```

### Instalación

```bash
herdr plugin install owner/repo[/subdir]
herdr plugin link /path
herdr plugin list
herdr plugin action invoke example.layout.apply
herdr plugin pane open --plugin example.layout --entrypoint board
```

### Entorno del Plugin

| Variable | Descripción |
|----------|-------------|
| `HERDR_SOCKET_PATH` | Socket del server |
| `HERDR_BIN_PATH` | Binario de herdr |
| `HERDR_ENV=1` | Dentro de herdr |
| `HERDR_PLUGIN_ID` | ID del plugin |
| `HERDR_PLUGIN_CONFIG_DIR` | Config del plugin |
| `HERDR_PLUGIN_STATE_DIR` | Estado del plugin |
| `HERDR_PLUGIN_CONTEXT_JSON` | Contexto de invocación |

### Marketplace

[herdr.dev/plugins](https://herdr.dev/plugins) — índice automático de repos con topic `herdr-plugin`. Se refresca cada 30 min.

---

## 13. Integraciones con Agents

```bash
herdr integration status
herdr integration install claude
herdr integration install codex
herdr integration install opencode
```

Las integraciones instalan lifecycle hooks que el agent usa para reportar estado directamente a herdr, sin depender de screen detection.

---

## 14. Modo Remoto y SSH

### 3 Formas

| Situación | Comando |
|-----------|---------|
| Ya estás en SSH | `herdr` (como tmux) |
| Thin client local | `herdr --remote <host>` |
| Desktop features | `herdr --remote <host>` (clipboard bridging) |
| Desde el teléfono | SSH + `herdr` |

### SSH normal

```bash
ssh usuario@servidor
herdr
```

### Thin client

```bash
herdr --remote workbox
herdr --remote ssh://usuario@servidor:2222
```

### SSH config

```
Host workbox
  HostName servidor.example.com
  User usuario
  Port 2222
```

---

## 15. Configuración

`~/.config/herdr/config.toml`

### Secciones

```toml
[ui]
mouse_capture = true
sidebar_position = "left"
sidebar_width = 30

[theme]
mode = "dark"

[keys]
prefix = "ctrl+b"
focus_pane_left = ["prefix+h", "ctrl+alt+h"]

[notifications]
sound = true
agent_blocked = true
agent_done = true

[update]
channel = "stable"
check_interval_hours = 24

[remote]
trusted_hosts = ["workbox"]
```

### Recargar

```bash
herdr server reload-config
```

---

## 16. Persistencia y Sesiones

### ¿Qué se Persiste?

- Workspaces (IDs, nombres, orden)
- Tabs (IDs, nombres, layout)
- Paneles (IDs, comandos, CWD, tamaño)
- Agents (tipo, nombre, estado)
- Worktrees de git
- Layout completo

### Restauración

Cuando ejecutás `herdr`:
1. Si el server ya está corriendo → attach directo
2. Si no → restaura la última sesión desde disco

### Live Handoff

Cuando actualizás con `herdr update`, el nuevo server toma el control **sin matar los paneles**. Los agents no notan nada.

---

## 17. Flujos de Trabajo Avanzados

### Feature + Tests Paralelos

```bash
herdr workspace create user-auth
herdr pane split --current --direction right
herdr agent start feature --kind claude --pane w1:p1
herdr agent start tester --kind codex --pane w1:p2
herdr agent wait feature --until done --timeout 300000
herdr agent wait tester --until done --timeout 300000
```

### Revisión Cruzada

```bash
herdr agent wait feature --until done
herdr pane split --current --direction right --cwd "$PWD" --no-focus
herdr agent start reviewer --kind codex --pane "$PANE_ID"
herdr agent prompt reviewer "Review the implementation" --wait
herdr agent read reviewer --source recent-unwrapped --lines 300
```

### Pipeline Feature → Review → Merge

```bash
herdr agent wait feature --until done --timeout 600000
herdr pane split --current --direction right --cwd "$PWD" --no-focus
herdr agent start reviewer --kind codex --pane "$PANE_ID"
herdr agent prompt reviewer "Review all changes in git diff" --wait
REVIEW=$(herdr agent read reviewer --source recent-unwrapped --lines 500)
if echo "$REVIEW" | grep -q "FAIL"; then
  echo "⚠️  Problemas encontrados"
else
  echo "✅ Review passed"
fi
```

### Múltiples Proyectos

```bash
herdr workspace create main-feature
herdr workspace create hotfix
herdr workspace create research
# La sidebar muestra el estado de los 3 workspaces
```

### Named Sessions

```bash
herdr session attach work
# ... laburar ...
ctrl+b q
herdr session attach side-project
# ... proyecto personal ...
ctrl+b q
herdr session attach work
```

### Recuperación de Agent

```bash
herdr agent explain w1:p1
herdr agent read w1:p1 --source recent-unwrapped --lines 100
herdr agent send-keys w1:p1 ctrl+c
```

---

## 18. Agent Automation

### Variables de Entorno para Agents

```bash
HERDR_ENV=1
HERDR_WORKSPACE_ID=w1
HERDR_TAB_ID=w1:t1
HERDR_PANE_ID=w1:p1
HERDR_SOCKET_PATH=/run/...
HERDR_BIN_PATH=/usr/bin/herdr
```

### Skill para Agents

Herdr incluye un `SKILL.md` listo para Claude/OpenCode que le enseña al agent a:
- Verificar que está dentro de herdr (`test "$HERDR_ENV" = 1`)
- Crear paneles hermanos (split, cwd preservado, no focus)
- Arrancar agents (`herdr agent start`)
- Enviar prompts (`herdr agent prompt --wait`)
- Leer resultados (`herdr agent read`)
- Esperar estados (`herdr agent wait --until blocked`)

### Reglas de Coordinación

1. Usar `--no-focus` para background
2. Usar IDs explícitos, no depender del foco de otro cliente
3. Parsear IDs de respuestas JSON
4. No cerrar lo que no creaste
5. Preservar el working directory del caller

---

## 19. Comparativa con Alternativas

### vs tmux

| Aspecto | tmux | herdr |
|---------|------|-------|
| Propósito | Multiplexor genérico | Coding agents |
| RAM | ~1-2MB | ~8-15MB |
| Mouse | Configurable | Nativo + drag + right-click |
| Detección agents | ❌ | ✅ Manifiestos TOML |
| Socket API | ❌ | ✅ JSON |
| Plugins | tpm | Cualquier lenguaje |
| Imágenes | ❌ | ✅ Kitty protocol |
| Live handoff | ❌ | ✅ |

### vs zellij

| Aspecto | zellij | herdr |
|---------|--------|-------|
| Plugins | WASM | Cualquier lenguaje |
| Mouse | ✅ | ✅ |
| Detección agents | ❌ | ✅ |
| Socket API | ❌ | ✅ |

### vs VSCode

| Aspecto | VSCode | herdr |
|---------|--------|-------|
| RAM | ~300-500MB | ~8-15MB |
| Agents | Pestañas manuales | Gestión nativa |
| Remote | Remote SSH | SSH + `--remote` |

### Consumo

| App | RAM idle | RAM con 3 agents |
|-----|----------|-----------------|
| tmux | ~1MB | ~3MB |
| zellij | ~5MB | ~8MB |
| herdr | ~8MB | ~15MB |
| VSCode | ~300MB | ~500MB |
| Hyper (Electron) | ~150MB | ~200MB |

No es Electron. No tiene Chromium. Es Rust dibujando caracteres en tu terminal.

---

## 20. Ecosistema y Comunidad

### Repos

- [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr) — principal
- [herdr-plugin-examples](https://github.com/ogulcancelik/herdr-plugin-examples) — ejemplos de plugins
- [herdr-plugin-github-start](https://github.com/ogulcancelik/herdr-plugin-github-start) — arranca agent desde GitHub issue/PR
- [zarttic/herdr-zh](https://github.com/zarttic/herdr-zh) — fork en chino

### Canales

- **X**: [@herdrdev](https://x.com/herdrdev)
- **Web**: [herdr.dev](https://herdr.dev)
- **Docs**: [herdr.dev/docs](https://herdr.dev/docs)
- **Plugins**: [herdr.dev/plugins](https://herdr.dev/plugins)
- **Blog**: [herdr.dev/blog](https://herdr.dev/blog)

### Idiomas

English, 日本語, 简体中文

### Canales de Release

| Canal | Frecuencia |
|-------|-----------|
| **stable** | Cuando está listo |
| **preview** | Miércoles y viernes |

```bash
herdr channel set preview
herdr update
```

### Stats

- Creado: 27 marzo 2026
- Activo: commits diarios
- v0.7.5 actual
- Homebrew, Nix, Mise disponibles

---

## 21. Desarrollo y Contribución

### Compilar

```bash
git clone https://github.com/ogulcancelik/herdr
cd herdr
cargo build --release
```

### Tests

```bash
just test
just check
```

### Commits

Conventional commits, minúsculas, sin emojis, sin co-authored-by:

```
feat: add pane resize by keyboard
fix: handle SIGTERM in server handoff
refs #82
```

### Code Conventions

- No `unwrap()` en producción
- `#[allow]` solo con comentario
- Código platform-specific en `src/platform/`
- No agregar dependencias sin razón
- Protocol version contra último release

### Contribución Externa

1. Discussions primero
2. Issue aprobado por maintainer
3. PR solo después

---

## 22. Preguntas Frecuentes

**¿Es reemplazo de tmux?**
No exactamente. tmux es mejor para multiplexor genérico. herdr es mejor para agents.

**¿Puedo usarlo sin agents?**
Sí, funciona como multiplexor normal. Pero si no usás agents, tmux/zellij son más livianos.

**¿Consume mucho?**
~8-15MB RAM, 0% CPU idle.

**¿Funciona en Windows?**
Sí, beta.

**¿Funciona en SSH?**
Sí, 3 formas: SSH + herdr, `herdr --remote`, y desde el teléfono.

**¿Puedo tener múltiples sesiones?**
Sí, named sessions: `herdr session attach <nombre>`.

**¿Los agents siguen después de cerrar la terminal?**
Sí. El server corre en background.

**¿Cómo actualizo?**
`herdr update` — con live handoff.

**¿Cómo mato todo?**
`herdr server stop`.

**¿Hay plugins?**
Sí, marketplace en herdr.dev/plugins. Podés crear los tuyos en cualquier lenguaje.

**¿Funciona desde el teléfono?**
Sí, cualquier cliente SSH.

**¿Es gratis?**
Sí, Apache 2.0.

---

## 23. Referencias y Recursos

### Documentación

| Recurso | URL |
|---------|-----|
| Web | https://herdr.dev |
| Docs | https://herdr.dev/docs |
| Quick start | https://herdr.dev/docs/quick-start/ |
| Concepts | https://herdr.dev/docs/concepts/ |
| Keyboard | https://herdr.dev/docs/keyboard/ |
| CLI reference | https://herdr.dev/docs/cli-reference/ |
| Socket API | https://herdr.dev/docs/socket-api/ |
| Plugins | https://herdr.dev/docs/plugins/ |
| Marketplace | https://herdr.dev/plugins |
| Config | https://herdr.dev/docs/configuration/ |
| Integrations | https://herdr.dev/docs/integrations/ |
| Troubleshooting | https://herdr.dev/docs/troubleshooting/ |

### Repo

- https://github.com/ogulcancelik/herdr
- `AGENTS.md` — instrucciones para agents que trabajan en el repo
- `SKILL.md` — skill para Claude/OpenCode
- `CONTRIBUTING.md` — guía de contribución

### Comandos Rápidos

```bash
# Instalación
curl -fsSL https://herdr.dev/install.sh | sh

# Arrancar
herdr

# Detach
ctrl+b q

# Reattach
herdr

# Matar todo
herdr server stop

# Navegación
prefix+h/j/k/l     # Paneles
prefix+n/p         # Tabs
prefix+w           # Workspaces
prefix+c           # Nueva tab
prefix+v / prefix+-  # Split

# Agents
herdr agent list
herdr agent start <name> --kind codex --pane <id>
herdr agent prompt <name> "msg" --wait
herdr agent read <name> --source recent-unwrapped

# Remote
herdr --remote hostname

# Config
~/.config/herdr/config.toml
```

### Glosario

| Término | Definición |
|---------|-----------|
| **Pane** | Terminal real dentro de herdr |
| **Tab** | Conjunto de paneles con layout |
| **Workspace** | Contenedor de proyecto (grupo de tabs) |
| **Session** | Server completo con todos los workspaces |
| **Named session** | Sesión con nombre propio, aislada de otras |
| **Agent** | Proceso de IA detectado dentro de un pane |
| **Prefix** | Tecla de escape (`ctrl+b`) para comandos de herdr |
| **Screen detection** | Detección por análisis del bottom-buffer |
| **Lifecycle hook** | Reporte directo de estado del agent |
| **State rollup** | Agregación de estado de agent hacia workspace |
| **Live handoff** | Actualización sin matar paneles |
| **Direct attach** | Conectar terminal directamente a un pane/agent |
| **Manifiesto** | TOML que describe cómo detectar un agent |
| **Plugin** | Paquete extensible (cualquier lenguaje) |
| **Socket API** | API JSON sobre socket Unix/named pipe |
| **PTY** | Pseudoterminal |
| **Kitty graphics** | Protocolo para imágenes en terminal |

---

> *Fin del informe. herdr v0.7.5 — Rust, Apache 2.0, por Oğulcan Çelik.*
> *https://herdr.dev — https://github.com/ogulcancelik/herdr*