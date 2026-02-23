# QML-Specific Rules

> Tokens only. Design-system wrappers. Read-only state.

---

## Tokens Only

All UI sizing/styling must reference tokens/constraints.

Forbidden in QML:

* hard-coded numbers for sizes/spacing/limits
* hard-coded font sizes
* implicit "magic" defaults used without explicit token mapping

Allowed:

* animation durations if tokenized (recommended) or on allowlist

---

## Design-System Components

All standard controls must be wrapped:

* `AxButton`, `AxCard`, `AxList`, `AxWindow`, `AxInput`, ...

Wrappers must:

* read tokens
* clamp by constraints
* expose minimal API

See [qt-mapping.md](qt-mapping.md) for concrete `AxButton` wrapping example.

---

## Read-Only State

QML binds to a single state source (Store):

* `Store.state` (runtime)
* `Store.tokens` (theme)
* `Store.constraints` (policy)

QML writes only through:

* `Store.dispatch(event)`

See [qt-mapping.md](qt-mapping.md) for how Store maps to QObject singleton with Q_PROPERTY.
