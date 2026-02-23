# Q_OBJECT Macro — Always Required for Signals/Slots

> Missing Q_OBJECT causes silent failures — moc skips the class entirely.

---

RULE: Every QObject subclass with signals, slots, or Q_PROPERTY MUST have Q_OBJECT
RULE: Missing Q_OBJECT causes silent failures — moc skips the class
RULE: Q_OBJECT must be the FIRST thing in the class (private section)

## What AI Does (Wrong)
```cpp
// AI forgets Q_OBJECT — signals silently don't work
class FileWatcher : public QObject {
    // Q_OBJECT missing!
public:
    void startWatching();
signals:
    void fileChanged(const QString &path);  // NEVER EMITTED — moc doesn't see it
};
```

## What to Write Instead
```cpp
class FileWatcher : public QObject {
    Q_OBJECT  // MUST be here
public:
    explicit FileWatcher(QObject *parent = nullptr);
    void startWatching();
signals:
    void fileChanged(const QString &path);
};
```

See [connections.md](connections.md) for signal/slot connection patterns.
See [q-property.md](q-property.md) for Q_PROPERTY which also requires Q_OBJECT.
See [q-invokable.md](q-invokable.md) for Q_INVOKABLE which also requires Q_OBJECT.
