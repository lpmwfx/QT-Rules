# Common AI Mistakes — Quick Reference

> One-table summary of what AI gets wrong in Qt C++ and the correct patterns.

---

| AI Writes | Problem | Correct Qt Pattern |
|-----------|---------|-------------------|
| `std::make_unique<QWidget>()` | Conflicts with parent-child | `new QWidget(parent)` |
| Missing `Q_OBJECT` | moc ignores class, signals fail silently | Always add Q_OBJECT |
| `std::thread` for Qt work | No event loop, signal delivery fails | `QThread` + worker object |
| Missing `NOTIFY` on Q_PROPERTY | QML binding never updates | Always add NOTIFY signal |
| `SIGNAL()`/`SLOT()` strings | No compile-time check, typos = silent fail | Function pointer connect |
| Public method without Q_INVOKABLE | QML can't call it | Add Q_INVOKABLE |
| Returns `std::vector` to QML | QML can't use it | Return QVariantList |
| Qt types in core logic | Breaks hexagonal isolation | std types in core, convert at adapter |
| QVariantList instead of model | No change notifications, all-or-nothing updates | QAbstractListModel |
| `delete` a parented QObject | Double delete crash | Let parent manage lifetime |
| `QThread::run()` subclass | Outdated since Qt 4.4 | Worker-object + moveToThread |
| Lambda connect without context | Dangling if 'this' destroyed | Always pass context (3rd arg) |
| `QObject::findChild<>()` | Fragile tree walking | Store references, use proper API |
| `Qt::DirectConnection` cross-thread | Race conditions, crashes | Qt::AutoConnection (default) |

## Detailed Rules by Topic

- Ownership and parent-child: See [ownership.md](ownership.md)
- Q_OBJECT macro: See [q-object.md](q-object.md)
- Threading: See [threading.md](threading.md)
- Q_PROPERTY and NOTIFY: See [q-property.md](q-property.md)
- Q_INVOKABLE: See [q-invokable.md](q-invokable.md)
- Connection types: See [connections.md](connections.md)
- Qt vs std types: See [types.md](types.md)
- Model/View: See [model-view.md](model-view.md)
- QML engine ownership: See [engine-ownership.md](engine-ownership.md)
