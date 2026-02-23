# Common AI Mistakes — Quick Reference

> One table of everything AI gets wrong in QML, with the correct pattern.

---

| AI Writes | Problem | Correct QML Pattern | Details |
|-----------|---------|---------------------|---------|
| `property = value` in handler | Breaks binding | Let binding auto-update, or `Qt.binding()` | [bindings.md](bindings.md) |
| 400-line QML files | Unmaintainable | Max 150 lines, extract components | [file-size.md](file-size.md) |
| `x:` / `y:` for layout | Breaks on resize | `anchors` or `Layout` | [layout.md](layout.md) |
| JS if/else for visual state | Imperative, no animation | `states` + `PropertyChanges` | [states.md](states.md) |
| `visible: false` for heavy items | Wastes memory | `Loader { active: condition }` | [loader.md](loader.md) |
| JS arrays as model | Slow, no notifications | `QAbstractListModel` from C++ | [models.md](models.md) |
| JS callbacks between components | Wrong paradigm | QML signals | [signals.md](signals.md) |
| `id` reference across files | Breaks encapsulation | Pass via `required property` | [scope.md](scope.md) |
| `model.roleName` in Qt 6 | Deprecated pattern | `required property type name` | [required-properties.md](required-properties.md) |
| `Timer { repeat: true }` for polling | Often unnecessary | C++ signal on data change | [signals.md](signals.md) |
| Inline Component (100+ lines) | Unreadable | Separate .qml file | [file-size.md](file-size.md) |
| `Math.round(parent.width * 0.3)` | Fragile layout | `Layout.preferredWidth` or anchors | [layout.md](layout.md) |
| `onCompleted: { ... 30 lines }` | Logic in QML | Move to C++ init method | [models.md](models.md) |
| `children[0]`, `parent.parent` | Fragile tree walking | Named properties, proper API | [scope.md](scope.md) |
