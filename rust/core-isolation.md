# Core Logic Isolation

> Core Rust code has NO Qt dependency. The cxx-qt bridge is a thin adapter between core and Qt.

---

RULE: Core Rust code has NO Qt dependency — pure Rust crate
RULE: cxx-qt bridge is an ADAPTER — thin layer between core and Qt
RULE: Core crate compiles and tests without Qt installed
RULE: Same hexagonal pattern as C++ Qt apps (see hexagon.md)

### Project Structure
```
my-qt-app/
├── core/                    # Pure Rust — no Qt
│   ├── Cargo.toml           # Only serde, thiserror, etc.
│   └── src/
│       ├── lib.rs
│       ├── model.rs         # Domain types (std::string, PathBuf)
│       └── commands.rs      # Business logic
│
├── qt-bridge/               # cxx-qt adapter
│   ├── Cargo.toml           # Depends on core + cxx-qt
│   ├── build.rs             # cxx-qt build setup
│   └── src/
│       ├── lib.rs
│       ├── backend.rs       # #[cxx_qt::bridge] — maps core → Qt
│       └── models.rs        # QAbstractListModel implementations
│
├── app/                     # C++ entry point
│   ├── CMakeLists.txt       # Links qt-bridge, Qt6, QML
│   ├── main.cpp             # QGuiApplication + QML engine
│   └── qml/
│       └── Main.qml
│
└── config/
    └── theme.toml
```

### Dependency Direction
```
app/ (C++ main) → depends on qt-bridge + Qt6
qt-bridge/      → depends on core + cxx-qt
core/           → depends on NOTHING from Qt
```

BANNED: `use cxx_qt_lib::*` in core crate
BANNED: Qt types in core function signatures
BANNED: Core tests that require QApplication

See [types.md](types.md) for how to convert between Rust and Qt types at the bridge boundary.
See [errors.md](errors.md) for the Result-to-signal pattern at the bridge layer.
See [cxx-qt.md](cxx-qt.md) for the bridge declaration that connects core to Qt.
