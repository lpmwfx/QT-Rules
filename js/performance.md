# Performance Rules

> If it runs per-frame or per-delegate: it must be C++.

---

RULE: Avoid creating JS objects in hot paths (bindings, delegates)
RULE: Use C++ models (QAbstractListModel) — not JS arrays — for ListView
RULE: Never use JS `for` loops to populate ListModel — populate from C++
RULE: Avoid string concatenation in bindings — use Qt.formatString or C++
RULE: Keep signal handlers under 5 lines — defer to C++ for heavy work

## Why JS in QML Is Slow
- No JIT in V4 (only interpreter)
- Every JS<>QML boundary has marshalling cost
- JS objects are dynamically typed — no optimization
- GC pauses are noticeable in UI thread

## The Rule of Thumb
If it runs once (startup, button click): JS is fine
If it runs per-frame or per-delegate: must be C++

---

See [glue-code.md](glue-code.md) for the 15-line limit and when to move logic to C++.
See [types.md](types.md) for using typed properties to enable engine optimization.
See [engine.md](engine.md) for what the V4 engine actually supports.
