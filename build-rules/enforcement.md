# Enforcement, Repo Structure, and Definition of Done

> How we prevent "cheating". Where files go. When a feature is compliant.

---

## No-Literals Policy

* UI files (`qml/`, `ui.code/`) must not contain numeric literals for layout/limits.
* Backend rule files must not contain magic thresholds.

Enforce via:

* CI grep/lint rule (deny patterns)
* allowlist for rare cases

See [ai-traps.md](ai-traps.md) for how AI tends to introduce hidden literals.

---

## Coverage Checks

* Every token key referenced in UI must exist in base config.
* Every constraint referenced in core must exist in base config.

---

## Logging/Diagnostics

* Missing key -> explicit error log with key name and access site.
* Config reload events are logged with hash/version.

---

## Repository Structure (Recommended)

* `qml/` UI components
* `ui.code/` pure UI helpers
* `conf/`

  * `base/` full defaults
  * `override/` user/customer
  * `runtime/` optional
* `core/` immutable reducers/selectors/normalizers
* `pal/` platform services & I/O
* `bridge/` contract/codec/transport
* `memory/` session snapshots
* `schemas/` config + memory schema
* `migrations/` config & memory migrations

---

## Definition of Done (Architecture Compliance)

A feature is compliant when:

* All thresholds/sizes/limits/flags it uses are in `conf/base` with schema.
* UI emits events only; state changes arrive as patches.
* Core logic is deterministic and testable without I/O.
* Any I/O is done in PAL, returning events.
* UI and backend can run split with the same contract (even if transport is inproc by default).
