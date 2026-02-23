# Qt Types vs Standard C++ Types

> Use Qt types at API boundaries, standard C++ in core logic, convert at the adapter layer.

---

RULE: Use Qt types in Qt API boundaries (signals, properties, QML interface)
RULE: Use standard C++ types in core/business logic (hexagon core)
RULE: Convert at the adapter boundary — never leak Qt types into core

## Boundary Rules
| Context | Use | Why |
|---------|-----|-----|
| QML property, signal param | `QString`, `QVariantMap`, `QStringList` | QML requires Qt types |
| Core/business logic | `std::string`, `std::vector`, `std::map` | No Qt dependency in core |
| File paths | `QString` in Qt API, `std::filesystem::path` in core | Platform compatibility |
| Adapter layer | Convert between | Clean boundary |

## What AI Does (Wrong)
```cpp
// AI mixes Qt types into core — breaks hexagonal isolation
// core/model.cpp — should have NO Qt imports
#include <QString>
struct FileEntry {
    QString name;  // Qt type in core — WRONG
    QString path;
};
```

## What to Write Instead
```cpp
// core/model.hpp — pure C++, no Qt
struct FileEntry {
    std::string name;
    std::string path;
};

// adapters/qt_bridge.cpp — convert at boundary
QVariantMap toQml(const FileEntry &entry) {
    return {
        {"name", QString::fromStdString(entry.name)},
        {"path", QString::fromStdString(entry.path)}
    };
}
```

See [q-property.md](q-property.md) for Qt types in Q_PROPERTY declarations.
See [q-invokable.md](q-invokable.md) for QML-compatible return types.
See [model-view.md](model-view.md) for type usage in model implementations.
