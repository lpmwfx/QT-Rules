# Build Rules — Config-Driven, Stateless UI/Core with Bridge

**Goal (non-negotiable):** Everything that can vary must be changeable through **configuration and data**, not by editing code. Code is the **engine**; configuration is the **product**.

These rules are **language-agnostic** except where Qt/QML or the UI↔Backend Bridge makes it necessary.

---

## Files

### Architecture Spec (from original QT-BuildRules)

| File | Content |
|------|---------|
| [principles.md](principles.md) | Core principles: no hidden values, stateless code, determinism, replaceability |
| [layers.md](layers.md) | Layer architecture: UI, Core, PAL, Bridge — roles and boundaries |
| [data-types.md](data-types.md) | Config (layered), Memory (session continuity), Runtime State |
| [startup.md](startup.md) | Boot sequence, config reload policy, persistence cadence |
| [contract.md](contract.md) | Event/Patch/Effect protocol between layers |
| [qml-rules.md](qml-rules.md) | QML-specific: tokens only, design-system wrappers, read-only state |
| [bridge-ipc.md](bridge-ipc.md) | Bridge adapter pattern, IPC transport options, bootstrap |
| [validation.md](validation.md) | Schema validation, versioning, migration, safe-mode |
| [enforcement.md](enforcement.md) | No-literals policy, coverage checks, repo structure, Definition of Done |

### Implementation Details (gap-fillers)

| File | Content |
|------|---------|
| [threading.md](threading.md) | Thread model — GUI, Core, PAL thread boundaries and communication |
| [testing.md](testing.md) | Test strategy per layer (core unit, PAL integration, bridge contract, QML binding, E2E) |
| [qt-mapping.md](qt-mapping.md) | How Store/dispatch/patch map to concrete Qt APIs (QObject, Q_PROPERTY, QVariantMap) |
| [config-paths.md](config-paths.md) | Config file locations via QStandardPaths, XDG, Flatpak sandbox |
| [mvvm-bridge.md](mvvm-bridge.md) | Reconciling reducer/event/patch with MVVM AppCommand/ViewEvent |
| [build-system.md](build-system.md) | CMake (C++ Qt) and Cargo+CMake (Rust Qt via cxx-qt) project setup |
| [ai-traps.md](ai-traps.md) | AI anti-patterns specific to config-driven architecture |

---

## Reading Order

1. **principles.md** — the non-negotiable rules
2. **layers.md** — understand the four layers
3. **mvvm-bridge.md** — how this aligns with MVVM
4. **contract.md** — how layers communicate
5. **data-types.md** — config, memory, runtime state
6. **qt-mapping.md** — concrete Qt implementation
7. **threading.md** — which thread runs what
8. Remaining files as needed
