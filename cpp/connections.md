# Signal/Slot Connection Types

> Use function pointer syntax for compile-time checked connections.

---

RULE: `connect()` with function pointers — not string-based `SIGNAL()`/`SLOT()`
RULE: Cross-thread connections are `Qt::QueuedConnection` by default (auto-detected)
RULE: Use `Qt::QueuedConnection` explicitly if in doubt about threads
RULE: Use `QObject::disconnect()` or connection handle to avoid dangling connections

## What AI Does (Wrong)
```cpp
// AI uses old string-based syntax — no compile-time check
connect(button, SIGNAL(clicked()), this, SLOT(handleClick()));  // typo = silent fail

// AI uses direct connection across threads — CRASH
connect(worker, &Worker::done, this, &App::updateUI, Qt::DirectConnection);
```

## What to Write Instead
```cpp
// Function pointer syntax — compile-time checked
connect(button, &QPushButton::clicked, this, &App::handleClick);

// Cross-thread — queued connection (auto or explicit)
connect(worker, &Worker::done, this, &App::updateUI);  // auto-detects queued

// Lambda with captured context
connect(button, &QPushButton::clicked, this, [this]() {
    // 'this' as context ensures disconnect on destruction
    doSomething();
});
```

BANNED: `SIGNAL()`/`SLOT()` string-based connections
BANNED: `Qt::DirectConnection` across threads
BANNED: Lambda without context object (dangling if target destroyed)

See [threading.md](threading.md) for cross-thread signal/slot patterns.
See [q-object.md](q-object.md) — signals and slots require Q_OBJECT macro.
