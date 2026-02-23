# QML Rules — Anti-Patterns AI Gets Wrong

> QML is declarative. AI writes it imperatively.
> This mismatch causes broken bindings, layout bugs, and unmaintainable code.

---

## The Problem

AI models generate QML that looks correct but violates QML's declarative nature.
Training data contains imperative UI code (React setState, Flutter rebuild, web DOM),
and AI applies those patterns to QML. The result: broken bindings, silent failures,
and components that cannot be composed.

---

## File Index

| # | File | Topic |
|---|------|-------|
| 1 | [bindings.md](bindings.md) | Bindings Are Sacred — Never Assign Imperatively |
| 2 | [file-size.md](file-size.md) | Keep QML Files Small and Focused |
| 3 | [layout.md](layout.md) | Anchors and Layouts — Never Absolute Position |
| 4 | [states.md](states.md) | Use States, Not If/Else JS |
| 5 | [loader.md](loader.md) | Loader for On-Demand Creation |
| 6 | [models.md](models.md) | Models — Use C++ Models, Not JS Arrays |
| 7 | [signals.md](signals.md) | Signals and Connections — Not Callbacks |
| 8 | [scope.md](scope.md) | id References — Scope Matters |
| 9 | [required-properties.md](required-properties.md) | Required Properties (Qt 6) |
| 10 | [quick-ref.md](quick-ref.md) | Common AI Mistakes — Quick Reference |
| 11 | [file-organization.md](file-organization.md) | File Organization |
