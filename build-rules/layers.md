# Layer Architecture

> Four layers. Each has one role. Dependencies point inward.

---

## Overview

```
┌─────────────────────────────────────────────────┐
│  UI Layer (Qt/QML)                               │
│  Role: Render + emit events                      │
├─────────────────────────────────────────────────┤
│  Bridge (UI ↔ Backend Adapter)                   │
│  Role: Contract + codec + transport              │
├─────────────────────────────────────────────────┤
│  Immutable Core                                  │
│  Role: Pure logic (reduce, normalize, select)    │
├─────────────────────────────────────────────────┤
│  Mutable PAL (Platform Abstraction Layer)        │
│  Role: Perform side effects                      │
└─────────────────────────────────────────────────┘
```

---

## UI Layer (Qt/QML)

**Role:** Render from read-only state and theme tokens; emit events.

**Allowed in UI:**

* Pure rendering and binding.
* Ephemeral UI-only state (hover, open/closed) if it does not affect domain correctness.

**Forbidden in UI:**

* Business logic.
* Any hidden constants for sizes/limits.
* Direct I/O (network, filesystem) except through the bridge.

---

## Immutable Core

**Role:** Pure logic.

* `reduce(state, event, config) -> { newState, effects }`
* `normalize(state, config) -> normalizedState`
* `selectors(state, config) -> viewModel` (optional)

**Rules:**

* No I/O.
* No reading "global config" implicitly; config is **injected** as input.
* No time access; time arrives as an event.

---

## Mutable PAL (Platform Abstraction Layer)

**Role:** Perform side effects.

* Filesystem, networking, crypto, timers, system info, databases, IPC transport.
* PAL returns results as **events** back into the core.

---

## Bridge (UI ↔ Backend Adapter)

**Role:** Contract + codec + transport.

* Receives UI events and forwards them.
* Applies patches from backend to UI state store.
* Can be:

  * In-process adapter (function calls)
  * Local IPC (QLocalSocket / DBus / WebSocket)
  * Remote transport (TLS WebSocket / HTTP)

The contract MUST remain stable across transports.
