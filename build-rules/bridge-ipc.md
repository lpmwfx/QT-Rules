# Bridge & IPC Rules

> Adapter pattern. Transport-agnostic. Qt-specific options where needed.

---

## Adapter Pattern

Bridge is split into:

* **Contract** (event/patch/effect schema)
* **Codec** (JSON/CBOR/MessagePack)
* **Transport** (inproc/IPC/remote)

UI and backend must not depend on transport.

See [contract.md](contract.md) for the event/patch/effect protocol.
See [mvvm-bridge.md](mvvm-bridge.md) for how this maps to MVVM.

---

## IPC Options (Guideline)

* Desktop-local: `QLocalSocket` / `QLocalServer`
* System-integration: DBus (Linux)
* Cross-platform and future-remote: WebSocket

Pick one transport as default; keep contract stable.

---

## Bootstrap Minimum

There is a minimal bootstrap to locate config/endpoint:

* `bootstrap.json` or environment variables

Bootstrap must contain only what is necessary to reach full config.

See [config-paths.md](config-paths.md) for where bootstrap and config files live on disk.
