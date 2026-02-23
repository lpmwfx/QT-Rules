# JavaScript in Qt/QML Apps — Rules and AI Anti-Patterns

> Qt's JS engine (V4) is NOT a browser, NOT Node.js, NOT V8.
> AI models trained on web JS will produce code that silently breaks in QML.

AI generates web-style JavaScript for QML because training data is 99% browser/Node.js.
QML's V4 engine supports a LIMITED subset of ECMAScript. What works in Chrome/Node often
fails silently or causes runtime errors in QML.

**This directory exists because AI WILL make these mistakes unless told not to.**

---

## File Index

| File | Topic |
|------|-------|
| [engine.md](engine.md) | V4 engine limits, BANNED APIs, correct replacements |
| [glue-code.md](glue-code.md) | JS in QML is glue code only — not business logic |
| [standalone.md](standalone.md) | Vanilla JS files in Qt projects (Node.js tooling) |
| [pragma-library.md](pragma-library.md) | `.pragma library` — QML's own JS module system |
| [network.md](network.md) | XMLHttpRequest — the only network API in QML |
| [types.md](types.md) | Type discipline in QML JS properties |
| [quick-ref.md](quick-ref.md) | Common AI mistakes — lookup table |
| [performance.md](performance.md) | Performance rules for JS in QML |
| [validation.md](validation.md) | Validation at boundaries (C++ side, not QML) |

---

## Summary

```
QML JS = glue code (< 15 lines per handler)
    |
    +-- UI wiring:     signal -> slot, property binding helpers
    +-- Simple math:    clamp, format, conditional text
    +-- Event mapping:  mouse/touch -> AppCommand
    +-- Nothing else.

C++ / Rust = business logic, networking, file I/O, validation
    |
    +-- Q_INVOKABLE methods for QML to call
    +-- Q_PROPERTY for QML to bind
    +-- Signals for QML to react to
    +-- All heavy computation, all data processing

Standalone JS = Node.js tools, generators, build scripts
    |
    +-- Follows ~/.rules/JS/RULES (ESM, Zod, JSDoc)
```
