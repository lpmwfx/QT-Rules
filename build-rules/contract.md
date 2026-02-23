# The Contract — Events, Patches, and Effects

> How layers communicate. Transport-agnostic protocol.

---

## Event Rules

* UI never "sets state" directly.
* UI emits events with name + payload.

**Event envelope (transport agnostic):**

* `type`: string (e.g., `ui.event`)
* `name`: string (e.g., `WindowResized`)
* `id`: unique id (optional)
* `ts`: timestamp (optional; if present, comes from PAL/clock)
* `payload`: object

See [mvvm-bridge.md](mvvm-bridge.md) for how events map to MVVM AppCommands.

---

## Patch Rules

Backend updates UI via patches.

**Patch ops (minimum):**

* `set(path, value)`
* `unset(path)`
* optional list ops:

  * `append(path, value)`
  * `remove(path, selector)`

Paths must be stable, predictable, and versioned.

See [qt-mapping.md](qt-mapping.md) for concrete `applyPatch()` implementation.

---

## Effects

Core outputs effects that PAL executes.

* Effects are commands like `ReadFile`, `HttpRequest`, `StartTimer`.
* PAL returns result events like `FileReadOk`, `HttpResponse`, `TimerTick`.

See [threading.md](threading.md) for how effects cross thread boundaries.
