# Rust in Qt — Rules and AI Anti-Patterns

> Rust's ownership model and Qt's ownership model are fundamentally different.
> AI will try to apply Rust idioms that directly conflict with how Qt objects work.

**General Rust rules:** See `~/.rules/Rust/RULES` — this file adds Qt-specific rules on top.

---

## The Problem

AI generates idiomatic Rust for Qt bindings. But Qt's QObject model requires:
- Parent-child ownership (not Rust's single-owner model)
- Interior mutability via mutable pointers (not borrows)
- Pin-based stability (QObject cannot be moved in memory)
- Event loop integration (not Rust's async runtimes)

The two ownership models conflict. AI that ignores this produces code that either
doesn't compile or segfaults at runtime.

---

## File Index

| # | File | Topic |
|---|------|-------|
| 1 | [cxx-qt.md](cxx-qt.md) | cxx-qt Is the Bridge — Not Raw FFI |
| 2 | [pin.md](pin.md) | Pin — Qt Objects Cannot Move |
| 3 | [ownership.md](ownership.md) | Ownership: Qt Parent-Child vs Rust Ownership |
| 4 | [signals.md](signals.md) | Signals from Rust — Use cxx-qt Macros |
| 5 | [async.md](async.md) | Async: Qt Event Loop, Not Tokio |
| 6 | [errors.md](errors.md) | Error Handling: Result to Qt Signals |
| 7 | [q-property.md](q-property.md) | Q_PROPERTY from Rust |
| 8 | [types.md](types.md) | Type Mapping: Rust to Qt |
| 9 | [core-isolation.md](core-isolation.md) | Core Logic Isolation |
| 10 | [quick-ref.md](quick-ref.md) | Common AI Mistakes — Quick Reference |
