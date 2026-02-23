# Startup / Reload Model

> How the app boots, how config reloads, and when state is persisted.

---

## Boot Sequence

1. Load & merge `conf/base` + `conf/override` (+ optional runtime).
2. Validate config schema.
3. Load memory snapshot.
4. Initialize runtime state:

   * apply memory
   * `normalize(state, config)` (clamp, remove invalid panels/routes)
5. UI renders from state + tokens.
6. Background watchers (optional):

   * if config changes, re-validate and apply according to applyPolicy.

---

## Config Reload Policy

Config changes can be applied by policy (a config key):

* `config.applyPolicy = live | idle | nextLaunch`

Guideline:

* Theme tokens: usually safe to apply live.
* Constraints: apply live but clamp; may re-layout.
* Flows/features: often `idle` or `nextLaunch`.

---

## Persistence Cadence

* Persist memory on:

  * debounce (e.g., 250–1000ms)
  * app close
  * critical transitions

Persistence must be atomic:

* write temp → fsync (if available) → rename.

See [config-paths.md](config-paths.md) for `QSaveFile` pattern that implements atomic write.
