# QML JS Is NOT Web JS

> Qt's V4 engine supports a LIMITED subset of ECMAScript. What works in Chrome/Node often fails silently or causes runtime errors in QML.

---

## What V4 Supports (Qt 6)
- ES5 fully
- ES6 partially: let/const, arrow functions, template literals, destructuring, for...of
- ES7: some (exponentiation)

## What V4 Does NOT Support
BANNED: `import`/`export` (ESM modules) — QML has its own module system
BANNED: `require()` — no CommonJS
BANNED: `async`/`await` — not available in V4
BANNED: `Promise` — not native in V4 (use Qt.callLater or C++ async)
BANNED: `fetch()` — no browser API (use XMLHttpRequest or C++ network)
BANNED: `setTimeout`/`setInterval` — use QML `Timer {}` component
BANNED: `console.error`/`console.warn` — use `console.log` only (or C++ logging)
BANNED: Optional chaining `?.` — not available in V4
BANNED: Nullish coalescing `??` — not available in V4
BANNED: Spread operator on objects `{...obj}` — limited support
BANNED: `Map`, `Set`, `WeakMap`, `WeakRef` — not available in V4
BANNED: `Symbol` — not available
BANNED: Classes with `class` keyword — use Qt.createComponent or plain objects
BANNED: `Array.from()`, `.includes()`, `.find()`, `.flat()` — limited availability
BANNED: `Object.entries()`, `Object.values()`, `Object.fromEntries()` — not available

## What AI Will Generate (Wrong)
```javascript
// AI writes this — FAILS in QML
const result = await fetchData(url);
const items = data?.items ?? [];
const merged = {...defaults, ...overrides};
import { validate } from './utils.js';
```

## What to Write Instead
```qml
// QML-correct patterns
Timer {
    id: pollTimer
    interval: 1000
    onTriggered: controller.refresh()
}

// Null-safe access
var items = (data && data.items) ? data.items : []

// Object merge (manual)
function merge(a, b) {
    var result = {};
    for (var key in a) result[key] = a[key];
    for (var key in b) result[key] = b[key];
    return result;
}
```

---

See [quick-ref.md](quick-ref.md) for a full table of AI mistakes and correct patterns.
See [pragma-library.md](pragma-library.md) for QML's own module system (replaces import/export).
See [network.md](network.md) for the correct networking API (replaces fetch).
