# Build System — CMake and Cargo for Qt Projects

> QT-BuildRules defines architecture but not how to build it.
> This file covers CMake (C++ Qt) and Cargo + CMake (Rust Qt via cxx-qt).

---

## Principle

The build must enforce the architecture:
- **core/** compiles without Qt
- **adapters/** compiles with Qt
- **app/** links both and runs QML

Each layer is a separate build target. If core/ accidentally imports Qt, the build fails.

---

## 1. CMake — C++ Qt Project

### Top-Level CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.20)
project(myapp VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

# Strict warnings
add_compile_options(-Wall -Wextra -Wpedantic -Werror)

# Find Qt
find_package(Qt6 REQUIRED COMPONENTS Core Quick QuickControls2)
find_package(KF6Kirigami)  # optional, for KDE apps

add_subdirectory(core)
add_subdirectory(adapters)
add_subdirectory(app)
```

### core/CMakeLists.txt — No Qt Dependency

```cmake
add_library(core STATIC
    src/command.cpp
    src/event.cpp
    src/viewmodel.cpp
    src/model.cpp
    src/config.cpp
)

target_include_directories(core PUBLIC include/)

# ONLY standard library + serde libs — NO Qt
target_link_libraries(core PRIVATE
    nlohmann_json::nlohmann_json  # for TOML/JSON parsing
)

# Verify: no Qt headers in core
# CI check: grep -r "Qt" core/include/ core/src/ should find nothing
```

### adapters/CMakeLists.txt — Qt Allowed Here

```cmake
add_library(adapters STATIC
    src/qml_view.cpp
    src/jsonrpc.cpp
    src/linux_fs.cpp
    src/qprocess_pty.cpp
    src/unix_socket.cpp
    src/store.cpp
    src/bridge.cpp
)

target_include_directories(adapters PUBLIC include/)

target_link_libraries(adapters
    PUBLIC core                           # depends on core interfaces
    PRIVATE Qt6::Core Qt6::Quick          # Qt allowed in adapters
)
```

### app/CMakeLists.txt — Wiring Only

```cmake
add_executable(myapp
    main.cpp
    qml.qrc
)

target_link_libraries(myapp PRIVATE
    core
    adapters
    Qt6::Core
    Qt6::Quick
    Qt6::QuickControls2
)

# Install config files
install(DIRECTORY conf/base/ DESTINATION share/myapp/conf/base)
install(DIRECTORY schemas/ DESTINATION share/myapp/schemas)
```

### QML Resources (qml.qrc)

```xml
<RCC>
    <qresource prefix="/qml">
        <file>qml/Main.qml</file>
        <file>qml/components/Sidebar.qml</file>
        <file>qml/components/AxButton.qml</file>
        <!-- ... -->
    </qresource>
</RCC>
```

Or use CMake `qt_add_qml_module()` for Qt 6.2+:

```cmake
qt_add_qml_module(myapp
    URI App
    VERSION 1.0
    QML_FILES
        qml/Main.qml
        qml/components/Sidebar.qml
        qml/components/AxButton.qml
)
```

---

## 2. Cargo + CMake — Rust Qt via cxx-qt

### Workspace Structure

```
myapp/
├── Cargo.toml              # Workspace root
├── core/
│   ├── Cargo.toml          # Pure Rust — no Qt
│   └── src/lib.rs
├── qt-bridge/
│   ├── Cargo.toml          # cxx-qt bridge
│   ├── build.rs            # cxx-qt-build
│   └── src/lib.rs
├── app/
│   ├── CMakeLists.txt      # Qt app entry
│   ├── main.cpp
│   └── qml/Main.qml
└── CMakeLists.txt          # Top-level, calls corrosion for Rust
```

### Cargo.toml (Workspace)

```toml
[workspace]
members = ["core", "qt-bridge"]

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
toml = "0.8"
thiserror = "2"
```

### core/Cargo.toml — No Qt

```toml
[package]
name = "myapp-core"
version = "0.1.0"
edition = "2021"

[dependencies]
serde.workspace = true
toml.workspace = true
thiserror.workspace = true

[dev-dependencies]
tempfile = "3"
```

### qt-bridge/Cargo.toml — cxx-qt

```toml
[package]
name = "myapp-qt-bridge"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["staticlib"]

[dependencies]
myapp-core = { path = "../core" }
cxx = "1"
cxx-qt = "0.7"
cxx-qt-lib = "0.7"

[build-dependencies]
cxx-qt-build = "0.7"
```

### qt-bridge/build.rs

```rust
use cxx_qt_build::CxxQtBuilder;

fn main() {
    CxxQtBuilder::new()
        .file("src/backend.rs")
        .file("src/models.rs")
        .build();
}
```

### CMakeLists.txt (Top-Level) — Corrosion

```cmake
cmake_minimum_required(VERSION 3.20)
project(myapp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Quick)

# Build Rust crates via Corrosion
include(FetchContent)
FetchContent_Declare(
    Corrosion
    GIT_REPOSITORY https://github.com/corrosion-rs/corrosion.git
    GIT_TAG v0.5
)
FetchContent_MakeAvailable(Corrosion)

corrosion_import_crate(MANIFEST_PATH Cargo.toml CRATES myapp-qt-bridge)

add_subdirectory(app)
```

### app/CMakeLists.txt

```cmake
add_executable(myapp main.cpp)

target_link_libraries(myapp PRIVATE
    myapp-qt-bridge   # Rust staticlib via Corrosion
    Qt6::Core
    Qt6::Quick
)

qt_add_qml_module(myapp
    URI App
    VERSION 1.0
    QML_FILES qml/Main.qml
)
```

---

## 3. Build Targets and Isolation Check

### Architecture Enforcement via Build

| Target | Allowed dependencies | Forbidden |
|--------|---------------------|-----------|
| core (C++ lib or Rust crate) | Standard library, serde, JSON/TOML parser | Qt, QML, OS-specific APIs |
| adapters / qt-bridge | core + Qt6::Core + Qt6::Quick | Direct OS calls not through port |
| app | adapters + core + Qt | Everything (wiring only) |

### CI Verification

```bash
# Core must build without Qt
cd core && cmake -B build && cmake --build build
# If this fails, Qt leaked into core

# Rust core must build without Qt
cd core && cargo build
cd core && cargo test
# If this needs Qt installed, cxx-qt leaked into core
```

---

## 4. Debug and Release Profiles

### CMake

```cmake
# Debug: sanitizers + debug symbols
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_compile_options(-fsanitize=address,undefined -g)
    add_link_options(-fsanitize=address,undefined)
endif()

# Release: LTO + strip
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
    add_compile_options(-O2)
endif()
```

### Cargo

```toml
# Cargo.toml
[profile.dev]
opt-level = 0

[profile.release]
opt-level = 2
lto = true
strip = true
```

---

## 5. Config Installation

Config files from `conf/base/` are installed as read-only app data:

```cmake
install(DIRECTORY conf/base/ DESTINATION ${CMAKE_INSTALL_DATADIR}/myapp/conf/base)
install(DIRECTORY schemas/ DESTINATION ${CMAKE_INSTALL_DATADIR}/myapp/schemas)
```

At runtime, the app finds them via `QStandardPaths::AppDataLocation`
(see config-paths.md).
