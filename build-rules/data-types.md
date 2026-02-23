# Data Types — Config, Memory, Runtime State

> Three distinct data categories. Each has different lifecycle, storage, and rules.

---

## Config (Rules & Tokens)

Config is split by purpose:

* **Theme Tokens**: colors, typography, spacing, radii, elevations.
* **Constraints/Policy**: max/min sizes, resource budgets, limits.
* **Flows/Feature Flags**: enabled/disabled components, UI routes, feature gates.

**Config is layered:**

1. `conf/base/**` (complete defaults shipped with app)
2. `conf/override/**` (customer/device/user overrides)
3. `conf/runtime/**` (optional remote policy or ephemeral overrides)

**Config must be validated** against schema. Missing required keys must be treated as:

* Fail-fast error OR explicit safe-mode (see validation.md), never silent fallback to hidden code defaults.

See [config-paths.md](config-paths.md) for filesystem locations via QStandardPaths.

---

## Memory (Resume/Continuity)

Memory is **not config**. Memory is session continuity:

* last open route/page
* window geometry / splitters
* opened panels
* scroll positions
* last selected project/document IDs

Memory must be:

* small, stable, best-effort
* migrated across versions

Stored as:

* `memory/last_session.json` (or sqlite)

---

## Runtime State

Runtime state is the in-memory truth during execution.

* Derived from config + memory + external data.
* Must be normalized/clamped against constraints.

See [qt-mapping.md](qt-mapping.md) for how runtime state is exposed to QML via Store.
