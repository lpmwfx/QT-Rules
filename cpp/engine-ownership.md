# QML Engine Ownership Rules

> Objects returned from Q_INVOKABLE are owned by the QML engine and may be garbage collected.

---

RULE: Objects returned from Q_INVOKABLE are owned by QML engine (GC'd)
RULE: Objects set as context properties are NOT owned by QML
RULE: Use `QQmlEngine::setObjectOwnership()` to control explicitly
RULE: If QML deletes a C++ object you still hold a pointer to — crash

## Danger Zone
```cpp
// QML takes ownership — C++ pointer becomes dangling
Q_INVOKABLE QObject* createWidget() {
    auto *w = new MyWidget();  // QML engine will delete this
    m_widgets.append(w);       // C++ still holds pointer — CRASH later
    return w;
}
```

## Safe Pattern
```cpp
Q_INVOKABLE QObject* createWidget() {
    auto *w = new MyWidget();
    QQmlEngine::setObjectOwnership(w, QQmlEngine::CppOwnership);  // C++ manages
    m_widgets.append(w);
    return w;
}
```

See [ownership.md](ownership.md) for Qt parent-child ownership model.
See [q-invokable.md](q-invokable.md) for Q_INVOKABLE methods that return objects.
