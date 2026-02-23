# Q_PROPERTY — Required for QML Exposure

> Every value visible in QML MUST be a Q_PROPERTY with a NOTIFY signal.

---

RULE: Every value visible in QML MUST be a Q_PROPERTY
RULE: Q_PROPERTY must have NOTIFY signal for QML bindings to work
RULE: Missing NOTIFY = QML reads the value once, never updates

## What AI Does (Wrong)
```cpp
// AI exposes methods but no properties — QML can call but not bind
class Backend : public QObject {
    Q_OBJECT
public:
    Q_INVOKABLE QString userName() { return m_userName; }
    // QML cannot bind: Text { text: backend.userName } — static, never updates
};
```

## What to Write Instead
```cpp
class Backend : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString userName READ userName NOTIFY userNameChanged)
public:
    QString userName() const { return m_userName; }
    void setUserName(const QString &name) {
        if (m_userName != name) {
            m_userName = name;
            emit userNameChanged();
        }
    }
signals:
    void userNameChanged();
private:
    QString m_userName;
};
```

```qml
// Now QML can bind — auto-updates when signal fires
Text { text: backend.userName }
```

See [q-object.md](q-object.md) — Q_PROPERTY requires Q_OBJECT macro.
See [q-invokable.md](q-invokable.md) for exposing methods (commands) to QML.
See [types.md](types.md) for which types to use in Q_PROPERTY declarations.
