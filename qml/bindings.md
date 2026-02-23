# Bindings Are Sacred — Never Assign Imperatively

> QML properties bind to expressions — they re-evaluate automatically.
> Imperative assignment breaks this contract permanently.

---

RULE: QML properties bind to expressions — they re-evaluate automatically
RULE: Imperative assignment (`property = value`) BREAKS the binding permanently
RULE: If you must reset a value, re-establish the binding with `Qt.binding()`

### What AI Does (Wrong)
```qml
// AI writes imperative — BREAKS binding
Rectangle {
    id: box
    color: theme.backgroundColor  // binding

    function onThemeChanged() {
        box.color = theme.backgroundColor  // BREAKS binding — now static
    }
}
```

### What to Write Instead
```qml
// Declarative — binding is always live
Rectangle {
    color: theme.backgroundColor  // auto-updates when theme changes
}
```

### When You Must Assign Dynamically
```qml
// Re-establish binding explicitly
Component.onCompleted: {
    box.color = Qt.binding(function() { return theme.backgroundColor; })
}
```

BANNED: Imperative property assignment to a bound property
BANNED: Using `onXChanged` handlers to propagate values that should be bindings

---

See [states.md](states.md) — states use PropertyChanges which preserve bindings.
See [quick-ref.md](quick-ref.md) — quick reference table of common mistakes.
