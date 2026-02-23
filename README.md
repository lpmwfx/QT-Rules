# Qt Rules — AI Anti-Pattern Guides + Config-Driven Architecture

Qt has its own ownership model, JS engine, and declarative UI paradigm.
AI models trained on web/standard-library code produce patterns that silently break in Qt.
These files document what AI gets wrong and what to write instead.

## MCP Server

Use these rules directly in Claude Code (or any MCP client):

```bash
pipx install git+https://github.com/lpmwfx/QT-RulesMCP.git
claude mcp add -s user qt-rules -- qt-rules-mcp
```

Tools: `search_rules`, `get_rule`, `get_context`, `get_learning_path`, `list_rules`

See [QT-RulesMCP](https://github.com/lpmwfx/QT-RulesMCP) for details.

## Language Rules (AI Anti-Patterns)

Each language has its own directory with one file per topic:

| Directory | Scope | Key Anti-Patterns Addressed |
|-----------|-------|----------------------------|
| [`qml/`](qml/README.md) | QML declarative UI | Imperative assignment breaks bindings, monolith files, absolute positioning, JS state logic instead of States, missing Loader, JS arrays instead of C++ models |
| [`js/`](js/README.md) | JavaScript inside Qt apps | V4 engine ≠ V8/Node — no async/await, no ESM, no fetch, no optional chaining. QML JS is glue code (≤15 lines), not business logic |
| [`cpp/`](cpp/README.md) | C++ with Qt framework | Parent-child ownership vs smart pointers, Q_OBJECT/Q_PROPERTY/Q_INVOKABLE, QThread worker pattern, signal/slot connection types, Qt↔std type boundaries |
| [`rust/`](rust/README.md) | Rust via cxx-qt | Pin (QObject can't move), ownership conflict (Qt parent-child vs Rust RAII), no tokio (Qt event loop is primary), Result→signal mapping, core isolation |

## Architecture Rules (Config-Driven)

All architecture rules live in [`build-rules/`](build-rules/README.md) — one file per topic.

| File | Content |
|------|---------|
| [principles.md](build-rules/principles.md) | Core principles: no hidden values, stateless code, determinism, replaceability |
| [layers.md](build-rules/layers.md) | Layer architecture: UI, Core, PAL, Bridge — roles and boundaries |
| [data-types.md](build-rules/data-types.md) | Config (layered), Memory (session continuity), Runtime State |
| [startup.md](build-rules/startup.md) | Boot sequence, config reload policy, persistence cadence |
| [contract.md](build-rules/contract.md) | Event/Patch/Effect protocol between layers |
| [qml-rules.md](build-rules/qml-rules.md) | QML-specific: tokens only, design-system wrappers, read-only state |
| [bridge-ipc.md](build-rules/bridge-ipc.md) | Bridge adapter pattern, IPC transport options, bootstrap |
| [validation.md](build-rules/validation.md) | Schema validation, versioning, migration, safe-mode |
| [enforcement.md](build-rules/enforcement.md) | No-literals policy, coverage checks, repo structure, Definition of Done |
| [threading.md](build-rules/threading.md) | Thread model — GUI, Core, PAL thread boundaries and communication |
| [testing.md](build-rules/testing.md) | Test strategy per layer (core unit, PAL integration, bridge contract, QML binding, E2E) |
| [qt-mapping.md](build-rules/qt-mapping.md) | How Store/dispatch/patch map to concrete Qt APIs (QObject, Q_PROPERTY, QVariantMap) |
| [config-paths.md](build-rules/config-paths.md) | Config file locations via QStandardPaths, XDG, Flatpak sandbox |
| [mvvm-bridge.md](build-rules/mvvm-bridge.md) | Reconciling reducer/event/patch with MVVM AppCommand/ViewEvent |
| [build-system.md](build-rules/build-system.md) | CMake (C++ Qt) and Cargo+CMake (Rust Qt via cxx-qt) project setup |
| [ai-traps.md](build-rules/ai-traps.md) | AI anti-patterns specific to config-driven architecture |

## Reading Order

**For language rules** — read based on languages in the Qt project:

1. **qml/** — always (every Qt Quick project has QML)
2. **js/** — if the project uses JavaScript in QML or standalone
3. **cpp/** — if the backend is C++
4. **rust/** — if the backend is Rust via cxx-qt

**For architecture rules** — read in this order:

1. **build-rules/principles.md** — the non-negotiable rules
2. **build-rules/layers.md** — understand the four layers
3. **build-rules/mvvm-bridge.md** — how this aligns with MVVM
4. **build-rules/contract.md** — how layers communicate
5. **build-rules/data-types.md** — config, memory, runtime state
6. **build-rules/qt-mapping.md** — concrete Qt implementation
7. **build-rules/threading.md** — which thread runs what
8. Remaining files as needed

## Relationship to Other Rules

```
~/.rules/GLOBAL          Universal rules (read first)
~/.rules/Cpp/RULES       General C++ rules (non-Qt)
~/.rules/Rust/RULES      General Rust rules (non-Qt)
~/.rules/JS/RULES        General JS rules (standalone, non-QML)
    │
    ▼
QT/cpp/                 Qt-specific C++ (adds to Cpp/RULES)
QT/rust/                Qt-specific Rust (adds to Rust/RULES)
QT/js/                  QML JS engine limits (replaces JS/RULES for QML-loaded JS)
QT/qml/                 QML declarative patterns (no general equivalent)
QT/build-rules/         Config-driven architecture (applies to all Qt projects)
```

General language rules apply to core/business logic.
QT/ rules apply at the Qt adapter boundary and in QML.
build-rules/ applies to the entire project architecture.

## The Core Problem

AI training data is dominated by web JS, standard C++, and standalone Rust.
Qt predates all of these conventions and has its own:

| Concept | Web/Standard | Qt |
|---------|-------------|-----|
| Ownership | RAII / GC | Parent-child tree |
| JS engine | V8 (ES2024+) | V4 (ES5 + partial ES6) |
| UI paradigm | Imperative DOM | Declarative bindings |
| Async | Promise/async-await | Event loop + signals |
| Modules | ESM import/export | `.pragma library` + QML imports |
| Threading | std::thread / tokio | QThread + worker object |
| Type exposure | export / pub | Q_PROPERTY + NOTIFY |
| Config | Hardcoded or .env | Layered TOML (base/override/runtime) |
| State management | Redux store / setState | Store singleton + dispatch + patch |

AI will default to the left column. These files teach it the right column.
