# .pragma library — QML's JS Module System

> QML has its own module pattern for shared JS. It is NOT ESM.

---

RULE: Use `.pragma library` for shared utility functions
RULE: Library JS files have NO access to QML component scope (no `parent`, no `root`)
RULE: Library JS files are singletons — state persists across all importers

## Correct Pattern
```javascript
// utils.js
.pragma library

function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1048576).toFixed(1) + " MB";
}

function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}
```

```qml
// Usage in QML
import "utils.js" as Utils

Text {
    text: Utils.formatBytes(fileSize)
}
```

## What AI Does (Wrong)
```javascript
// AI writes ESM — FAILS in QML
export function formatBytes(bytes) { ... }
```

---

See [engine.md](engine.md) for the full BANNED list (including `import`/`export`).
See [standalone.md](standalone.md) for when regular JS modules (ESM/CJS) are acceptable.
See [glue-code.md](glue-code.md) for keeping .pragma library functions small and focused.
