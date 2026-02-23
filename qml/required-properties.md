# Required Properties (Qt 6)

> Use required property for delegate properties in Qt 6.
> This replaces the old model.roleName attached property pattern.

---

RULE: Use `required property` for delegate properties in Qt 6
RULE: This replaces the old `model.roleName` attached property pattern
RULE: Required properties are type-checked and produce clear error messages

### What AI Does (Wrong — Mixes Qt 5 and 6 Patterns)
```qml
// Qt 5 pattern — still works but deprecated in Qt 6
delegate: Item {
    Text { text: model.name }       // magic attached property
    Text { text: modelData.path }   // inconsistent
}
```

### What to Write Instead
```qml
// Qt 6 pattern — explicit, type-safe
delegate: Item {
    required property string name
    required property string path
    required property int index

    Text { text: name }
    Text { text: path }
}
```

---

See [scope.md](scope.md) — required properties solve the same problem as id references across files.
See [models.md](models.md) — C++ model roles map directly to required properties in delegates.
See [signals.md](signals.md) — data flows down via required properties, events flow up via signals.
See [quick-ref.md](quick-ref.md) — quick reference table of common mistakes.
