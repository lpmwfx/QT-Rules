# Models — Use C++ Models, Not JS Arrays

> ListModel for static/small lists. QAbstractListModel for everything else.
> Never build models in JS — marshalling cost kills performance.

---

RULE: ListModel for static/small lists only (< 20 items)
RULE: QAbstractListModel (C++) for dynamic, large, or filtered lists
RULE: Never build models in JS — marshalling cost kills performance
RULE: Never use `model: myJsArray.length` with manual indexing

### What AI Does (Wrong)
```qml
// AI creates model from JS — SLOW, no roles, no change notifications
property var files: []

function loadFiles() {
    var result = []
    // ... JS loop building array ...
    files = result
}

ListView {
    model: files.length
    delegate: Text { text: files[index].name }  // no roles, no binding
}
```

### What to Write Instead
```cpp
// C++ model — fast, typed, proper change notifications
class FileListModel : public QAbstractListModel {
    Q_OBJECT
    enum Roles { NameRole = Qt::UserRole + 1, PathRole, SizeRole };
    // roleNames(), rowCount(), data() ...
};
```

```qml
ListView {
    model: fileListModel  // from C++ context
    delegate: Text { text: model.name }  // proper role binding
}
```

---

See [required-properties.md](required-properties.md) — Qt 6 delegates should use required properties instead of model.roleName.
See [signals.md](signals.md) — C++ models emit signals for data changes; no polling needed.
See [quick-ref.md](quick-ref.md) — quick reference table of common mistakes.
