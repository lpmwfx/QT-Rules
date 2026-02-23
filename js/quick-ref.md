# Common AI Mistakes — Quick Reference

> A lookup table of what AI generates (wrong) and the correct Qt/QML pattern.

---

| AI Writes | Problem | Correct Qt Pattern |
|-----------|---------|-------------------|
| `async/await` | Not in V4 | Callback or C++ signal |
| `fetch()` | Not in V4 | XMLHttpRequest or C++ QNetworkAccessManager |
| `setTimeout()` | Not in V4 | `Timer { }` component |
| `import {...} from` | Not in V4 | `.pragma library` + QML import |
| `?.` optional chain | Not in V4 | `(x && x.y) ? x.y : default` |
| `??` nullish | Not in V4 | `(x !== null && x !== undefined) ? x : default` |
| `class Foo {}` | Not in V4 | Plain object or C++ QObject |
| `Array.includes()` | Not in V4 | `indexOf(x) !== -1` |
| `Object.keys().map()` | Partial | `for (var key in obj)` loop |
| `template ${tag}` | Partial (Qt 6.x) | Works in Qt 6, check version |
| `let`/`const` in loop | Partial | Use `var` in `for` loops if scoping issues |
| `...spread` on object | Not in V4 | Manual property copy |
| npm packages in QML | Impossible | Write in C++ or .pragma library |
| DOM manipulation | No DOM in QML | QML property bindings |

---

See [engine.md](engine.md) for the full BANNED list and correct replacement patterns.
See [pragma-library.md](pragma-library.md) for how `.pragma library` replaces ESM imports.
See [network.md](network.md) for the XMLHttpRequest pattern replacing fetch().
