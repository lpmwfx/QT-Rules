# Ownership: Qt Parent-Child, Not Smart Pointers

> QObject-derived classes use parent-child lifetime — parent deletes children automatically.

---

RULE: QObject-derived classes use parent-child ownership — parent deletes children
RULE: Use `new` with parent pointer — Qt manages lifetime
RULE: `std::unique_ptr` only for non-QObject types or explicit detach scenarios
RULE: Never `delete` a QObject that has a parent
RULE: Never `std::unique_ptr<QObject>` with a parent set — double delete

## What AI Does (Wrong)
```cpp
// AI uses modern C++ ownership — WRONG for QObject
auto label = std::make_unique<QLabel>("Hello");
auto layout = std::make_unique<QVBoxLayout>();
layout->addWidget(label.release());  // ownership confusion
```

```cpp
// AI deletes manually — CRASH (parent already owns it)
auto *button = new QPushButton("OK", parentWidget);
// ... later ...
delete button;  // DOUBLE DELETE — parent will also delete it
```

## What to Write Instead
```cpp
// Qt ownership — parent deletes children automatically
auto *label = new QLabel("Hello", this);     // 'this' is parent
auto *button = new QPushButton("OK", this);
auto *layout = new QVBoxLayout(this);        // layout takes ownership of widgets
layout->addWidget(label);
layout->addWidget(button);
// No delete needed — destroyed when parent is destroyed
```

## When Smart Pointers ARE Correct
```cpp
// Non-QObject types — standard C++ rules apply
auto config = std::make_unique<AppConfig>(loadToml("theme.toml"));

// QObject without parent (rare — document why)
// Explicitly managed lifetime, e.g., moved to thread
auto worker = std::make_unique<Worker>();  // no parent
worker->moveToThread(&workerThread);       // thread takes conceptual ownership
```

See [engine-ownership.md](engine-ownership.md) for QML engine ownership interactions.
See [quick-ref.md](quick-ref.md) for common AI mistakes related to ownership.
