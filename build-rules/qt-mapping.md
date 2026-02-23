# Qt API Mapping — Store, Dispatch, Patches in Concrete Qt

> QT-BuildRules §6.3 says `Store.dispatch(event)` and `Store.state` but doesn't
> show how these map to actual Qt/QML mechanisms. This file fills that gap.

---

## The Problem

BuildRules uses abstract concepts (Store, dispatch, patch, tokens). AI needs to know
what Qt classes implement them. Without this mapping, AI will invent its own — wrong.

---

## Store = C++ QObject Singleton Exposed to QML

The Store is a `QObject` registered as a QML singleton. It holds the runtime state,
tokens, and constraints as Q_PROPERTYs with NOTIFY signals.

```cpp
class Store : public QObject {
    Q_OBJECT

    // Runtime state — updated by patches from Core
    Q_PROPERTY(QVariantMap state READ state NOTIFY stateChanged)

    // Theme tokens — loaded from conf, read-only to QML
    Q_PROPERTY(QVariantMap tokens READ tokens NOTIFY tokensChanged)

    // Constraints/policy — loaded from conf, read-only to QML
    Q_PROPERTY(QVariantMap constraints READ constraints NOTIFY constraintsChanged)

public:
    explicit Store(Bridge *bridge, QObject *parent = nullptr);

    QVariantMap state() const { return m_state; }
    QVariantMap tokens() const { return m_tokens; }
    QVariantMap constraints() const { return m_constraints; }

    // QML calls this to send events to Core
    Q_INVOKABLE void dispatch(const QVariantMap &event);

public slots:
    // Bridge calls this when patches arrive from Core
    void applyPatch(const QVariantMap &patch);

signals:
    void stateChanged();
    void tokensChanged();
    void constraintsChanged();

private:
    QVariantMap m_state;
    QVariantMap m_tokens;
    QVariantMap m_constraints;
    Bridge *m_bridge;
};
```

### Registration

```cpp
// main.cpp
qmlRegisterSingletonInstance("App", 1, 0, "Store", store);
```

```qml
// Usage in any QML file
import App 1.0

Text {
    text: Store.state.workspace.currentPath
    color: Store.tokens.colors.textPrimary
}

Button {
    onClicked: Store.dispatch({ name: "AddFolder", payload: { path: dialog.folder } })
}
```

---

## dispatch() = Serialize Event and Send to Bridge

```cpp
void Store::dispatch(const QVariantMap &event) {
    // Validate event has required fields
    if (!event.contains("name")) {
        qWarning() << "Store::dispatch: missing 'name' in event";
        return;
    }

    // Forward to bridge (which sends to Core thread)
    m_bridge->sendEvent(event);
}
```

The Bridge serializes the event and sends it to the Core thread via queued connection or channel (see threading.md).

---

## Patches = Targeted State Updates

When Core processes an event, it produces patches. The Bridge delivers them to Store on the GUI thread.

### Patch Format (QVariantMap)

```cpp
// set operation
QVariantMap patch = {
    {"op", "set"},
    {"path", "workspace.folders"},
    {"value", QVariantList{"/tmp/project-a", "/tmp/project-b"}}
};

// unset operation
QVariantMap patch = {
    {"op", "unset"},
    {"path", "workspace.currentFile"}
};
```

### applyPatch Implementation

```cpp
void Store::applyPatch(const QVariantMap &patch) {
    QString op = patch["op"].toString();
    QString path = patch["path"].toString();

    if (op == "set") {
        setNestedValue(m_state, path, patch["value"]);
        emit stateChanged();
    } else if (op == "unset") {
        removeNestedValue(m_state, path);
        emit stateChanged();
    }
}

// Helper: set value at dotted path in nested QVariantMap
void setNestedValue(QVariantMap &root, const QString &path, const QVariant &value) {
    QStringList keys = path.split(".");
    QVariantMap *current = &root;
    for (int i = 0; i < keys.size() - 1; ++i) {
        if (!current->contains(keys[i])) {
            current->insert(keys[i], QVariantMap{});
        }
        current = &(*current)[keys[i]].toMap();  // simplified — real impl needs care
    }
    current->insert(keys.last(), value);
}
```

---

## Tokens = Config Loaded at Startup, Exposed as QVariantMap

```cpp
// At startup (see boot sequence in QT-BuildRules §4.1)
QVariantMap tokens = ConfigLoader::loadTokens("conf/base/theme.toml", "conf/override/theme.toml");
store->setTokens(tokens);
```

QML accesses tokens via binding:

```qml
Rectangle {
    color: Store.tokens.colors.sidebarBg
    width: Store.tokens.sizes.sidebarWidthDefault
}
```

Tokens change only on theme switch or config reload — not every frame. The NOTIFY signal triggers QML rebinding automatically.

---

## Design-System Components (AxButton etc.) = QML Wrappers

§6.2 says wrap all controls. These wrappers read tokens from Store:

```qml
// components/AxButton.qml
import QtQuick.Controls
import App 1.0

Button {
    id: root

    implicitWidth: Math.max(Store.tokens.sizes.buttonMinWidth, contentWidth + leftPadding + rightPadding)
    implicitHeight: Store.tokens.sizes.buttonHeight

    leftPadding: Store.tokens.sizes.buttonPaddingH
    rightPadding: Store.tokens.sizes.buttonPaddingH
    topPadding: Store.tokens.sizes.buttonPaddingV
    bottomPadding: Store.tokens.sizes.buttonPaddingV

    font.family: Store.tokens.fonts.uiFamily
    font.pixelSize: Store.tokens.fonts.uiSize

    background: Rectangle {
        color: root.down ? Store.tokens.colors.buttonPressed
             : root.hovered ? Store.tokens.colors.buttonHovered
             : Store.tokens.colors.buttonBg
        radius: Store.tokens.sizes.buttonRadius
    }

    contentItem: Text {
        text: root.text
        color: Store.tokens.colors.buttonFg
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
```

Usage:
```qml
AxButton {
    text: "Open Workspace"
    onClicked: Store.dispatch({ name: "OpenWorkspace" })
}
```

Zero hardcoded values in the wrapper. All visual properties come from Store.tokens.

---

## Constraints in QML

Constraints clamp behavior. QML reads them but never changes them:

```qml
ListView {
    model: Store.state.workspace.folders
    // Clamp visible count to policy limit
    interactive: count > 0
    clip: true

    // Visual constraint: sidebar min width from policy
    Layout.minimumWidth: Store.constraints.sizes.sidebarWidthMin
    Layout.preferredWidth: Store.tokens.sizes.sidebarWidthDefault
}
```

---

## Summary: Abstract → Qt Concrete

| BuildRules Concept | Qt Implementation |
|-------------------|-------------------|
| Store | `QObject` singleton with Q_PROPERTYs, registered via `qmlRegisterSingletonInstance` |
| Store.state | `Q_PROPERTY(QVariantMap state READ state NOTIFY stateChanged)` |
| Store.tokens | `Q_PROPERTY(QVariantMap tokens READ tokens NOTIFY tokensChanged)` |
| Store.constraints | `Q_PROPERTY(QVariantMap constraints READ constraints NOTIFY constraintsChanged)` |
| Store.dispatch(event) | `Q_INVOKABLE void dispatch(const QVariantMap &event)` → Bridge → Core thread |
| Patch | `QVariantMap { op, path, value }` applied on GUI thread via `applyPatch()` slot |
| Token reload | Replace `m_tokens`, emit `tokensChanged()`, QML rebinds automatically |
| AxButton / AxCard | QML files wrapping Qt Quick Controls, all values from Store.tokens |
| Event envelope | `QVariantMap { name, payload }` — serializable, transport-agnostic |
