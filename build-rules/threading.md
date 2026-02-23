# Threading Model — Who Runs Where

> QT-BuildRules §2 defines layers (UI, Core, PAL, Bridge) but does not specify
> which thread each layer runs on. This file fills that gap.

---

## The Rule

Qt enforces one absolute constraint: **QML and QWidget operations MUST happen on the GUI thread.** Everything else is negotiable.

---

## Thread Map

```
┌─────────────────────────────────────────────────────────┐
│ GUI Thread (QCoreApplication::exec)                      │
│                                                          │
│  QML Engine         — all rendering, binding evaluation  │
│  Store singleton    — state reads, token lookups         │
│  Bridge (inbound)   — receives patches, updates Store    │
│  Event dispatch     — Store.dispatch() → serializes      │
│                       event and hands off to bridge      │
│                                                          │
│  RULE: No blocking I/O on this thread. Ever.             │
│  RULE: No computation > 5ms on this thread.              │
└───────────────────────────┬─────────────────────────────┘
                            │ events (async)
                            │ patches (queued back)
┌───────────────────────────▼─────────────────────────────┐
│ Core Thread (dedicated worker)                           │
│                                                          │
│  Reducer            — reduce(state, event, config)       │
│  Normalizer         — normalize(state, config)           │
│  Selectors          — compute view model from state      │
│  Effect emitter     — outputs effect commands            │
│                                                          │
│  RULE: Pure logic. No Qt types. No I/O.                  │
│  RULE: Receives events from Bridge, sends patches back.  │
└───────────────────────────┬─────────────────────────────┘
                            │ effects (async)
                            │ results (events back)
┌───────────────────────────▼─────────────────────────────┐
│ PAL Threads (one or more workers)                        │
│                                                          │
│  Filesystem ops     — read, write, scan, watch           │
│  Network ops        — HTTP, socket connect/send/recv     │
│  Terminal/PTY       — spawn, read, write, resize         │
│  Timers             — periodic ticks as events           │
│  Crypto             — hashing, signing                   │
│                                                          │
│  RULE: Each PAL operation returns result as event.       │
│  RULE: Never touches QML or GUI objects.                 │
│  RULE: May use Qt types (QFile, QProcess, QLocalSocket)  │
│        but never QML types (QQuickItem, etc.)            │
└─────────────────────────────────────────────────────────┘
```

---

## Cross-Thread Communication

### GUI ↔ Core: Queued signals or channels

**Option A: Qt queued connection (in-process bridge)**
```cpp
// Bridge object lives on GUI thread
// Core object lives on core thread
// Qt::QueuedConnection auto-detected via moveToThread

connect(bridge, &Bridge::eventReady,
        core,   &Core::handleEvent);       // GUI → Core (queued)

connect(core,   &Core::patchReady,
        bridge, &Bridge::applyPatch);      // Core → GUI (queued)
```

**Option B: Channel (Rust or std::sync::mpsc)**
```rust
let (event_tx, event_rx) = std::sync::mpsc::channel();  // GUI → Core
let (patch_tx, patch_rx) = std::sync::mpsc::channel();   // Core → GUI

// GUI side: poll patch_rx via QTimer at 16ms (60fps)
// Core side: block on event_rx, process, send patches
```

### Core ↔ PAL: Effects as commands, results as events

```
Core emits:    Effect::ReadFile { path, id }
PAL executes:  std::fs::read_to_string(path)
PAL returns:   Event::FileReadOk { id, content }
               Event::FileReadErr { id, error }
```

No shared mutable state between Core and PAL. Communication is message-passing only.

---

## Qt Event Loop Ownership

RULE: `QCoreApplication::exec()` owns the main event loop — it runs on the GUI thread
RULE: `QThread` provides a secondary event loop for worker objects
RULE: Never run a second event loop (no nested `exec()`, no tokio runtime)
RULE: Use `QTimer::singleShot(0, ...)` to defer work to next event loop iteration on GUI thread

### Polling patches on GUI thread

```cpp
// Bridge polls for patches from Core at frame rate
QTimer *pollTimer = new QTimer(this);
pollTimer->setInterval(16);  // from conf: timing.ui_poll_interval_ms
connect(pollTimer, &QTimer::timeout, this, [this]() {
    while (auto patch = patchChannel.tryRecv()) {
        store->applyPatch(*patch);  // updates QML-bound properties
    }
});
pollTimer->start();
```

---

## What AI Gets Wrong

| AI pattern | Problem | Correct pattern |
|-----------|---------|-----------------|
| Blocking I/O on GUI thread | Freezes UI | Move to PAL thread |
| `std::thread` for Qt work | No event loop for signals | `QThread` + worker object |
| Shared mutex between GUI and Core | Deadlock risk, blocks UI | Message-passing (channels or queued signals) |
| Direct `Store.state` mutation from worker | QML binding breaks, race condition | Send patch via channel, apply on GUI thread |
| `QThread::run()` subclass | Outdated pattern | Worker object + `moveToThread` |
| tokio/async-std runtime | Competes with Qt event loop | std::thread or QThread for blocking work |

---

## Thread Safety Checklist

- [ ] All QML property writes happen on GUI thread
- [ ] Core thread never imports Qt GUI/Quick modules
- [ ] PAL threads never touch QML objects
- [ ] Cross-thread communication is channels or queued connections
- [ ] No `std::mutex` shared between GUI thread and any other
- [ ] Poll timer interval is configurable (`timing.ui_poll_interval_ms`)
