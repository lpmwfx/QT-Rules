# C++ in Qt — Rules and AI Anti-Patterns

> Qt has its own ownership model, threading model, and type system.
> AI trained on modern C++ (non-Qt) will fight these and produce broken code.

---

## The Problem

AI generates standard C++ for Qt projects. But Qt predates modern C++ conventions
and has its own object model built on QObject, moc, signals/slots, and parent-child
ownership. AI that ignores these produces code that leaks, crashes, or deadlocks.

**General C++ rules:** See `~/.rules/Cpp/RULES` — this file adds Qt-specific rules on top.

---

## File Index

| File | Topic |
|------|-------|
| [ownership.md](ownership.md) | Qt Parent-Child ownership vs smart pointers |
| [q-object.md](q-object.md) | Q_OBJECT macro — required for signals/slots |
| [threading.md](threading.md) | QThread and worker-object pattern |
| [q-property.md](q-property.md) | Q_PROPERTY — required for QML exposure |
| [q-invokable.md](q-invokable.md) | Q_INVOKABLE — the QML call interface |
| [connections.md](connections.md) | Signal/slot connection types |
| [types.md](types.md) | Qt types vs standard C++ types |
| [model-view.md](model-view.md) | Model/View — QAbstractListModel for QML |
| [engine-ownership.md](engine-ownership.md) | QML engine ownership rules |
| [quick-ref.md](quick-ref.md) | Common AI mistakes — quick reference table |
