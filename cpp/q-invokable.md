# Q_INVOKABLE — The QML Call Interface

> Methods callable from QML MUST be Q_INVOKABLE or public slots.

---

RULE: Methods callable from QML MUST be `Q_INVOKABLE` or `public slots`
RULE: Q_INVOKABLE for command-style methods (user actions)
RULE: Return types must be QML-compatible (QString, QVariant, QVariantList, QVariantMap)
RULE: Use QVariantMap for structured data — not custom types without Q_GADGET

## What AI Does (Wrong)
```cpp
// AI forgets Q_INVOKABLE — QML can't call it
class Controller : public QObject {
    Q_OBJECT
public:
    void openFile(const QString &path);  // invisible to QML
};
```

```cpp
// AI returns C++ types that QML can't handle
Q_INVOKABLE std::vector<FileEntry> getFiles();  // QML can't use std::vector
Q_INVOKABLE std::optional<Config> getConfig();   // QML can't use std::optional
```

## What to Write Instead
```cpp
class Controller : public QObject {
    Q_OBJECT
public:
    Q_INVOKABLE void openFile(const QString &path);
    Q_INVOKABLE QVariantList getFiles();    // QML-friendly
    Q_INVOKABLE QVariantMap getConfig();     // QML-friendly
};
```

See [q-object.md](q-object.md) — Q_INVOKABLE requires Q_OBJECT macro.
See [q-property.md](q-property.md) for exposing values (data bindings) to QML.
See [types.md](types.md) for Qt vs standard C++ type boundaries.
See [engine-ownership.md](engine-ownership.md) for ownership of objects returned via Q_INVOKABLE.
