# MVVM ↔ BuildRules Alignment

> QT-BuildRules §2.2 describes a reducer pattern. The existing KDE_QT/mvvm.md
> describes MVVM with AppCommand/ViewEvent. This file reconciles the two.

---

## The Conflict

**BuildRules says:**
```
reduce(state, event, config) → { newState, effects }
```
Unidirectional data flow. Elm/Redux-style. State is immutable. Core is a pure function.

**MVVM (mvvm.md) says:**
```
View → AppCommand → Exchange → ViewModel → ViewEvent → Exchange → View
```
MVVM with channels. ViewModel is stateful. Commands go in, events come out.

These are **two descriptions of the same architecture**, not a conflict.
The vocabulary differs. The data flow is identical.

---

## The Mapping

| BuildRules Term | MVVM Term | Same Thing |
|----------------|-----------|------------|
| Event (from UI) | AppCommand | User intent, transport-agnostic |
| reduce() | ViewModel.handle(cmd) | Process intent, produce result |
| newState | Updated Model | State after processing |
| effects | Outbound port calls | Side effects (file, network, PTY) |
| Patch (to UI) | ViewEvent | Pre-computed data for UI |
| PAL | Outbound Adapters | OS-specific implementations |
| Bridge | Exchange (channels) | The boundary between UI and logic |
| Store | View's state source | What QML binds to |

---

## Unified Model

The combined architecture uses MVVM vocabulary for the **layers** and BuildRules
vocabulary for the **data flow rules**:

```
┌─────────────────────────────────────────────────────────────┐
│ VIEW (QML)                                                   │
│                                                              │
│  Reads: Store.state (QVariantMap), Store.tokens, constraints │
│  Writes: Store.dispatch({ name: "AppCommand", payload })     │
│                                                              │
│  Store = QObject singleton (see qt-mapping.md)               │
│                                                              │
│  RULES from BuildRules:                                      │
│  - No hidden values (all from tokens/constraints)            │
│  - Read-only binding (never mutate state directly)           │
│  - Dispatch only (UI → event → bridge)                       │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ EXCHANGE / BRIDGE                                            │
│                                                              │
│  AppCommand flows View → ViewModel (queued connection)       │
│  ViewEvent flows ViewModel → View (patch applied to Store)   │
│                                                              │
│  RULES from BuildRules:                                      │
│  - Transport-agnostic contract                               │
│  - Codec layer (JSON for IPC, in-memory for direct)          │
│  - Same contract for QML, JSON-RPC, CLI, test harness        │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ VIEWMODEL (Core logic)                                       │
│                                                              │
│  handle(AppCommand, config) → { updatedState, effects }      │
│  normalize(state, config) → clampedState                     │
│  toViewEvent(state) → pre-computed data for View             │
│                                                              │
│  RULES from BuildRules:                                      │
│  - Config injected, never read implicitly                    │
│  - No I/O (effects are commands, PAL executes)               │
│  - Deterministic (same input → same output)                  │
│  - No Qt types (pure C++/Rust, hexagon core)                 │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ MODEL (Data)                                                 │
│                                                              │
│  Pure data types. Called by ViewModel.                        │
│  No config access (ViewModel passes what Model needs).       │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ PAL / OUTBOUND ADAPTERS                                      │
│                                                              │
│  Execute effects: ReadFile, HttpRequest, SpawnPty            │
│  Return results as events: FileReadOk, HttpResponse          │
│                                                              │
│  RULES from BuildRules:                                      │
│  - Side effects isolated here                                │
│  - Returns events, never mutates state directly              │
│  - May use Qt types (QFile, QProcess, QLocalSocket)          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## What BuildRules Adds to MVVM

MVVM (mvvm.md) defines the **layer separation**. BuildRules adds:

1. **Config layering** (base/override/runtime) — not in MVVM
2. **Memory/continuity** (session resume) — not in MVVM
3. **Boot sequence** (load config → validate → load memory → normalize → render)
4. **Config reload policy** (live/idle/nextLaunch)
5. **Validation & safe-mode** (schema, migration, fallback)
6. **No-literals enforcement** (CI grep, coverage checks)
7. **Determinism guarantee** (same input + config + memory → same state)

These are **additions**, not replacements. MVVM still governs layer separation.

---

## What MVVM Adds to BuildRules

BuildRules describes data flow abstractly. MVVM adds:

1. **AppCommand enum** — typed, serializable, named user intents
2. **ViewEvent enum** — typed, pre-computed display data
3. **Hexagonal ports** — explicit interfaces for outbound dependencies
4. **Thread boundary spec** — Exchange as the cross-thread boundary
5. **IPC for free** — JSON-RPC server is just another inbound adapter

---

## Terminology Convention

When writing Qt code, use **both vocabularies** depending on context:

| Context | Use |
|---------|-----|
| Naming classes and enums | MVVM: `AppCommand`, `ViewEvent`, `ViewModel` |
| Describing data flow rules | BuildRules: dispatch, event, patch, reduce |
| Config and tokens | BuildRules: `Store.tokens`, `conf/base`, constraint |
| Layer boundaries | MVVM: Exchange, Adapter, Port |
| Testing | BuildRules: core unit (pure), PAL integration, contract |
| Architecture docs | Both: "ViewModel processes AppCommands deterministically given config" |

---

## The Audit (Combined)

| Check | Source | Search for | Bug if |
|-------|--------|-----------|--------|
| Policy in mechanism | BuildRules §1.1 | Bare numeric in .cpp/.qml | Found |
| View has logic | MVVM | Business logic in QML | Found |
| Core has Qt | MVVM hexagon | `#include <Qt*>` in core/ | Found |
| State mutated in UI | BuildRules §6.3 | Direct property assignment (not dispatch) | Found |
| Config not injected | BuildRules §2.2 | Global config read in Core | Found |
| Non-deterministic Core | BuildRules §1.3 | `time()`, `rand()`, file read in Core | Found |
