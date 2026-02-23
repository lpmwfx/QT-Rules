# id References — Scope Matters

> id is scoped to the QML file where it is declared.
> Never rely on id from a parent file inside a component.

---

RULE: `id` is scoped to the QML file where it is declared
RULE: Never rely on `id` from a parent file inside a component
RULE: Pass data via properties, not via id references across files

### What AI Does (Wrong)
```qml
// Main.qml
Item {
    id: root
    property string currentPath: "/home"

    // AI assumes inner component can reach root.currentPath
    FileDelegate {
        // This works ONLY if FileDelegate is inline, not a separate file
        text: root.currentPath  // BREAKS if FileDelegate.qml is separate
    }
}
```

### What to Write Instead
```qml
// Main.qml — pass via property
FileDelegate {
    currentPath: root.currentPath
}

// FileDelegate.qml — declares its own property
Item {
    required property string currentPath
    Text { text: currentPath }
}
```

---

See [required-properties.md](required-properties.md) — required properties replace id-based data access in Qt 6.
See [signals.md](signals.md) — for upward communication, use signals instead of reaching up via id.
See [quick-ref.md](quick-ref.md) — quick reference table of common mistakes.
