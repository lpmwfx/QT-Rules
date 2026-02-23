# Testing Strategy — Per Layer

> QT-BuildRules defines four layers (UI, Core, PAL, Bridge) but no test strategy.
> This file defines what to test, how, and with what tools for each layer.

---

## Principle

The architecture enables testing by design:

- **Core** is pure logic with no I/O → unit tests with no setup
- **PAL** is isolated side effects → integration tests with real OS resources
- **Bridge** is contract + codec → contract tests with serialized fixtures
- **UI** binds to Store → visual/binding tests via QtQuickTest

---

## 1. Core Tests (Unit — No I/O, No Qt)

### What to test
- Reducer: `reduce(state, event, config) → {newState, effects}`
- Normalizer: `normalize(state, config) → normalizedState`
- Selectors: `selectors(state, config) → viewModel`

### How
Core has **zero** external dependencies. Tests run without Qt, without filesystem, without network.

**C++ (doctest/Catch2):**
```cpp
TEST_CASE("reduce: AddFolder adds to workspace") {
    State state = initial_state();
    Config config = test_config();
    auto [next, effects] = reduce(state, Event::AddFolder{"/tmp/project"}, config);

    CHECK(next.workspace.folders.size() == 1);
    CHECK(next.workspace.folders[0] == "/tmp/project");
    CHECK(effects.size() == 1);  // ScanDirectory effect
}

TEST_CASE("normalize: clamps folders to max_workspace_sources") {
    Config config = test_config();
    config.limits.max_workspace_sources = 2;
    State state = state_with_folders(5);

    auto result = normalize(state, config);
    CHECK(result.workspace.folders.size() == 2);
}
```

**Rust (cargo test):**
```rust
#[test]
fn reduce_add_folder() {
    let state = State::default();
    let config = test_config();
    let (next, effects) = reduce(&state, &Event::AddFolder("/tmp/project".into()), &config);

    assert_eq!(next.workspace.folders.len(), 1);
    assert!(matches!(effects[0], Effect::ScanDirectory { .. }));
}
```

### Rules
- Core tests MUST compile and run without Qt installed
- Core tests MUST NOT touch filesystem, network, or system clock
- Config is constructed in-test, not loaded from file
- Test helper: `test_config()` returns a minimal valid Config with known values

---

## 2. PAL Tests (Integration — Real OS)

### What to test
- Filesystem adapter: read/write/scan with real tmpdir
- Network adapter: localhost socket connect/send/recv
- Terminal adapter: PTY spawn, write, read output
- Timer adapter: fires events at expected intervals

### How
PAL tests use real OS resources via temporary directories and loopback sockets.

**C++ (doctest + QTest):**
```cpp
TEST_CASE("LinuxFs::readDir lists files") {
    QTemporaryDir tmp;
    QFile(tmp.filePath("a.txt")).open(QIODevice::WriteOnly);
    QFile(tmp.filePath("b.txt")).open(QIODevice::WriteOnly);

    LinuxFs fs;
    auto result = fs.readDir(tmp.path().toStdString());

    CHECK(result.success);
    CHECK(result.data.size() == 2);
}
```

**Rust (tempfile crate):**
```rust
#[test]
fn fs_adapter_reads_directory() {
    let tmp = tempfile::tempdir().unwrap();
    std::fs::write(tmp.path().join("a.txt"), "").unwrap();

    let fs = LinuxFsAdapter::new();
    let result = fs.read_dir(tmp.path());

    assert!(result.is_ok());
    assert_eq!(result.unwrap().len(), 1);
}
```

### Rules
- PAL tests MAY use real filesystem (via tmpdir — cleaned up automatically)
- PAL tests MAY use real sockets (loopback only)
- PAL tests MUST NOT depend on specific system state (installed packages, user dirs)
- PAL tests run slower — separate from core unit tests in CI

---

## 3. Bridge Tests (Contract — Serialization Fixtures)

### What to test
- Event serialization: event → codec → bytes → codec → event (roundtrip)
- Patch serialization: same roundtrip
- Contract stability: golden files that fail if format changes

### How
Golden file tests catch accidental contract breaks.

```cpp
TEST_CASE("Event::AddFolder roundtrip through JSON codec") {
    Event event = Event::AddFolder{"/tmp/project"};
    auto json = JsonCodec::encode(event);
    auto decoded = JsonCodec::decodeEvent(json);

    CHECK(decoded == event);
}

TEST_CASE("Patch format matches golden file") {
    Patch patch = Patch::set("workspace.folders[0]", "/tmp/project");
    auto json = JsonCodec::encode(patch);

    // Compare against checked-in golden file
    auto expected = readFile("testdata/patch_add_folder.json");
    CHECK(json == expected);
}
```

### Rules
- Golden files live in `testdata/` and are version-controlled
- Changing a golden file requires explicit approval (it's a contract change)
- Test both directions: encode and decode
- Test malformed input: corrupt JSON, missing fields, wrong types

---

## 4. UI Tests (QML — Binding and Visual)

### What to test
- QML bindings: Store property change → UI element updates
- Store.dispatch: user action → correct event emitted
- Token application: Theme values reach components
- State-driven visibility: Loader active, states, enabled/disabled

### How

**QtQuickTest (C++ + QML):**
```cpp
// tst_sidebar.cpp
#include <QtQuickTest>
QUICK_TEST_MAIN(sidebar)
```

```qml
// tst_sidebar.qml
import QtQuick
import QtTest

TestCase {
    name: "Sidebar"

    MockStore { id: store }
    Sidebar { id: sidebar; store: store }

    function test_folderCountUpdates() {
        store.state.workspace.folders = ["a", "b", "c"]
        compare(sidebar.folderCount, 3)
    }

    function test_dispatchOnClick() {
        var spy = createEventSpy(store, "dispatched")
        mouseClick(sidebar.addButton)
        compare(spy.count, 1)
        compare(spy.signalArguments[0][0].name, "AddFolder")
    }
}
```

### MockStore
A QML-compatible mock that records dispatched events and allows property manipulation:

```qml
// MockStore.qml
QtObject {
    property var state: ({
        workspace: { folders: [] }
    })
    property var tokens: ({
        sizes: { sidebarWidth: 260 },
        colors: { sidebarBg: "#232629" }
    })
    property var constraints: ({
        limits: { maxWorkspaceSources: 10 }
    })

    signal dispatched(var event)
    function dispatch(event) { dispatched(event) }
}
```

### Rules
- UI tests use MockStore — never real backend
- UI tests verify binding propagation, not business logic
- UI tests are fast (no I/O, no network)
- Run with `qmltestrunner` or QtQuickTest main

---

## 5. End-to-End Tests (Full Stack)

### What to test
- Boot sequence: config load → state init → UI renders
- User flow: action → event → reduce → patch → UI update
- IPC: JSON-RPC request → same event path → JSON-RPC response

### How
E2E tests wire all layers together with real config files.

```cpp
TEST_CASE("full flow: add folder") {
    auto config = loadConfig("testdata/conf/base");
    auto core = Core(config);
    auto pal = TestPal();  // records effects, returns canned results
    auto bridge = InProcessBridge(core, pal);
    auto store = Store(bridge);

    store.dispatch(Event::AddFolder{"/tmp/project"});
    bridge.processUntilIdle();

    CHECK(store.state().workspace.folders.size() == 1);
}
```

### Rules
- E2E tests use real config files from `testdata/conf/`
- E2E tests use TestPal (records effects, returns canned results)
- E2E tests verify the full pipeline, not individual units
- Run separately from unit tests (slower)

---

## Test Pyramid

```
          ╱╲
         ╱E2E╲          Few — full pipeline, slow
        ╱──────╲
       ╱  UI    ╲       Binding tests, QML visual
      ╱──────────╲
     ╱  Bridge    ╲     Contract roundtrip, golden files
    ╱──────────────╲
   ╱   PAL (integ)  ╲   Real OS resources, tmpdir
  ╱──────────────────╲
 ╱  Core (unit)       ╲  Fast, pure, many — the foundation
╱──────────────────────╲
```

Most tests are Core unit tests. They are fast, pure, and require no setup.

---

## CI Pipeline Order

```
1. core unit tests     (fast, no deps)
2. bridge contract     (fast, no deps)
3. pal integration     (needs OS, tmpdir)
4. ui qml tests        (needs Qt, QML engine)
5. e2e full stack      (needs everything)
```

Fail fast: if core tests fail, skip everything else.
