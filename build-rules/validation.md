# Validation, Safe-Mode, and Migration

> Schema validation on every load. Versioned migration. Never silently ignore.

---

## Schema Validation

* Every config namespace has schema.
* On startup: validate merged config.
* On reload: validate before applying.

See [startup.md](startup.md) for the full boot sequence.

---

## Versioning & Migration

* Config has `config.version`.
* Memory has `memory.version`.
* Provide migrations:

  * key renames
  * moved paths
  * defaults added (in base conf)

---

## Safe-Mode

If override config is invalid:

* fallback to base config
* disable remote overrides
* show a clear diagnostic banner/log

Never silently ignore.

See [data-types.md](data-types.md) for the config layering model (base/override/runtime).
