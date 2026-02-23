# AI Anti-Patterns for Config-Driven Qt Architecture

> The other QT/ files cover language-specific anti-patterns (QML, JS, C++, Rust).
> This file covers architectural anti-patterns: what AI does wrong when implementing
> the config-driven, stateless-core, bridge-based architecture from QT-BuildRules.

---

## 1. AI Hardcodes Values That Belong in Config

The single most common AI violation. AI generates working code with literal values.
It looks correct. It compiles. It runs. But every literal is a frozen policy decision.

### What AI Does
```qml
Rectangle { width: 260; height: 600; color: "#232629" }
```
```cpp
if (sources.size() >= 10) return TooManySources;
```
```cpp
server.listen(path, 5);
```

### Why AI Does This
Training data is 99% code with hardcoded values. AI has no concept of
"this number is a policy decision that should be externalized."

### The Fix
Before writing any numeric literal, size, color, limit, timeout, or string:
ask "is this a policy decision?" If yes → it goes in `conf/base/*.toml`.

See `policy-mechanism.md` for exhaustive BANNED/REQUIRED examples per layer.

---

## 2. AI Puts Business Logic in QML

AI generates complex JavaScript functions inside QML signal handlers.
This violates both BuildRules (UI is read-only renderer) and QT-QML.md
(QML JS is glue code only).

### What AI Does
```qml
function processWorkspace(files) {
    var filtered = [];
    for (var i = 0; i < files.length; i++) {
        if (files[i].size < 1048576 && !files[i].hidden) {  // hardcoded limit!
            filtered.push(files[i]);
        }
    }
    filtered.sort(function(a, b) { return a.name.localeCompare(b.name); });
    filesModel.clear();
    for (var j = 0; j < filtered.length; j++) {
        filesModel.append(filtered[j]);
    }
}
```

Three violations:
1. Business logic in UI (filtering, sorting)
2. Hardcoded limit (1048576)
3. Imperative model mutation (should be patch from Core)

### The Fix
```qml
// UI dispatches intent only
Button {
    onClicked: Store.dispatch({ name: "RefreshWorkspace" })
}

// Core processes, PAL reads filesystem, patch arrives:
// Store.state.workspace.files is already filtered, sorted, clamped
ListView {
    model: Store.state.workspace.files
}
```

---

## 3. AI Mutates State Directly Instead of Dispatching

AI assigns properties imperatively in signal handlers instead of going
through Store.dispatch → Core → patch → Store.

### What AI Does
```qml
MouseArea {
    onClicked: {
        sidebar.visible = !sidebar.visible           // direct mutation
        Store.state.ui.sidebarOpen = sidebar.visible  // mutating Store!
    }
}
```

### Why This Breaks
- Store.state is read-only to QML (BuildRules §6.3)
- Direct mutation bypasses Core — no validation, no normalization
- Other consumers (JSON-RPC, test harness) don't see the change

### The Fix
```qml
MouseArea {
    onClicked: Store.dispatch({ name: "ToggleSidebar" })
}

// Core handles ToggleSidebar → produces patch:
// { op: "set", path: "ui.sidebarOpen", value: !current }
// Store applies patch → QML binding updates sidebar.visible

// Sidebar reads state declaratively
visible: Store.state.ui.sidebarOpen
```

---

## 4. AI Skips Config Validation

AI loads config and uses it directly. No schema check. No safe-mode fallback.
Missing keys cause runtime crashes instead of startup errors.

### What AI Does
```cpp
auto config = toml::parse_file("conf/base/theme.toml");
auto sidebarWidth = config["sizes"]["widgets"]["sidebar_width"].value_or(260);
//                                                               ^^^^^^^^
// Hidden default! BuildRules §3.1 says: "never silent fallback to hidden code defaults"
```

### The Fix
```cpp
auto config = toml::parse_file("conf/base/theme.toml");
auto result = schema::validate(config, "schemas/theme.schema.json");

if (!result.valid) {
    // Safe-mode: log error, fall back to base config only
    qCritical() << "Config validation failed:" << result.errors;
    config = loadBaseConfigOnly();  // known-good defaults
    showDiagnosticBanner("Config error — running in safe mode");
}

// No hidden defaults. If key is missing and schema says required → fail
auto sidebarWidth = config["sizes"]["widgets"]["sidebar_width"].value<int>();
```

---

## 5. AI Creates God-Object Store

AI puts all state, all methods, all signals on one massive QObject.
Hundreds of Q_PROPERTYs, dozens of Q_INVOKABLE methods.

### What AI Does
```cpp
class AppController : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString userName ...)
    Q_PROPERTY(QVariantList files ...)
    Q_PROPERTY(QVariantMap theme ...)
    Q_PROPERTY(bool sidebarOpen ...)
    Q_PROPERTY(int tabCount ...)
    // ... 50 more properties
    Q_INVOKABLE void openFile(const QString &path);
    Q_INVOKABLE void closeTab(int index);
    Q_INVOKABLE void toggleSidebar();
    // ... 30 more methods
};
```

### The Fix
Store has exactly three properties (state, tokens, constraints) and one method (dispatch).
Everything else is inside the state tree.

```cpp
class Store : public QObject {
    Q_OBJECT
    Q_PROPERTY(QVariantMap state READ state NOTIFY stateChanged)
    Q_PROPERTY(QVariantMap tokens READ tokens NOTIFY tokensChanged)
    Q_PROPERTY(QVariantMap constraints READ constraints NOTIFY constraintsChanged)
public:
    Q_INVOKABLE void dispatch(const QVariantMap &event);
    // That's it. No domain-specific methods on Store.
};
```

---

## 6. AI Mixes Config Layers

AI loads all config from one directory, or merges override into base
destructively, or reads override without base.

### What AI Does
```cpp
// Only loads override — base defaults missing for keys user didn't customize
auto config = loadToml("~/.config/myapp/theme.toml");
```

### The Fix
```cpp
// Load base first (complete defaults)
auto base = loadToml(basePath + "/theme.toml");

// Merge override on top (may be partial)
auto override = loadToml(overridePath + "/theme.toml");
auto merged = deepMerge(base, override);

// Validate merged result against schema
auto result = validate(merged, schema);
```

---

## 7. AI Calls OS Directly from Core

AI puts file I/O, network calls, or timer creation inside Core/ViewModel logic.
This violates both hexagonal isolation and BuildRules §2.2 (no I/O in Core).

### What AI Does
```cpp
// Inside ViewModel::handleAddFolder — WRONG
void ViewModel::handleAddFolder(const QString &path) {
    QDir dir(path);
    if (!dir.exists()) {
        emit errorOccurred("Directory not found");
        return;
    }
    auto entries = dir.entryInfoList();  // OS call in Core!
    // ...
}
```

### The Fix
```cpp
// Core outputs an effect — PAL executes it
std::pair<State, std::vector<Effect>> ViewModel::handle(
    const State &state, const AppCommand &cmd, const Config &config) {

    if (auto *add = std::get_if<AddFolder>(&cmd)) {
        return {state, {Effect::ScanDirectory{add->path}}};
    }
    // ...
}

// PAL (adapter) executes the effect
void LinuxPal::execute(const Effect &effect) {
    if (auto *scan = std::get_if<ScanDirectory>(&effect)) {
        QDir dir(QString::fromStdString(scan->path));
        if (!dir.exists()) {
            emit eventReady(Event::ScanFailed{scan->path, "Not found"});
            return;
        }
        auto entries = dir.entryInfoList();
        emit eventReady(Event::ScanComplete{scan->path, toEntries(entries)});
    }
}
```

---

## 8. AI Ignores Memory/Session Continuity

AI always starts fresh. No window geometry restore, no last-open-tab,
no scroll position. Users lose their place every launch.

### What AI Does
```cpp
int main() {
    QGuiApplication app(argc, argv);
    // Just opens default window at default size with default state
    // No memory load
}
```

### The Fix
```cpp
int main() {
    QGuiApplication app(argc, argv);

    auto config = loadAndValidateConfig();
    auto memory = loadMemory();  // last_session.json

    auto state = initState(config, memory);
    state = normalize(state, config);  // clamp invalid values

    auto store = new Store(state, config);
    // Window opens at last geometry, last tab selected, sidebar state restored
}
```

---

## Summary: AI Default → Config-Driven Correct

| AI Default | Config-Driven Correct |
|-----------|----------------------|
| Hardcoded values | Named keys in conf/base/*.toml |
| Logic in QML | Store.dispatch → Core → patch → QML binding |
| Direct state mutation | Dispatch event, apply patch |
| Load config without validation | Schema validate, safe-mode fallback |
| God-object controller | Store with 3 properties + 1 method |
| Single config file | Layered: base + override + runtime |
| OS calls in Core | Effect → PAL → event back |
| Fresh start every launch | Memory load → normalize → restore |
