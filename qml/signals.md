# Signals and Connections — Not Callbacks

> QML uses signals for component communication, not JS callbacks.
> Parent communicates down via properties. Child communicates up via signals.

---

RULE: QML uses signals — not JS callbacks — for component communication
RULE: Parent communicates down via properties
RULE: Child communicates up via signals
RULE: Sibling communication goes through parent or shared model

### What AI Does (Wrong)
```qml
// AI passes JS callbacks — web pattern, wrong in QML
FileList {
    onFileSelected: function(callback) {
        callback(selectedFile)  // JS callback — loses QML context
    }
}
```

### What to Write Instead
```qml
// Child declares signal
// FileList.qml
Item {
    signal fileSelected(string path)

    delegate: MouseArea {
        onClicked: fileSelected(model.path)
    }
}

// Parent connects to signal
FileList {
    onFileSelected: (path) => preview.load(path)
}
```

---

See [scope.md](scope.md) — signals respect file scope; id references across files do not.
See [required-properties.md](required-properties.md) — pass data down with required properties, signal up.
See [models.md](models.md) — C++ models use signals for data change notifications.
See [quick-ref.md](quick-ref.md) — quick reference table of common mistakes.
