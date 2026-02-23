# JS in QML Is Glue Code — Not Business Logic

> JS in QML files is ONLY for UI wiring. Business logic belongs in C++ or Rust.

---

RULE: JS in QML files is ONLY for UI glue (signal wiring, simple transforms)
RULE: Business logic belongs in C++ or Rust, exposed via Q_INVOKABLE or signals
RULE: Max 5-10 lines of JS in any signal handler
RULE: If a JS function exceeds 15 lines, it belongs in C++/Rust

## Why
- V4 is 10-100x slower than C++ for computation
- V4 has no optimizer comparable to V8/JIT
- JS in QML is not testable without running the QML engine
- JS in QML is not type-checked by any tool

## What AI Does (Wrong)
```qml
// AI puts logic in QML — WRONG
function processFiles(fileList) {
    var result = [];
    for (var i = 0; i < fileList.length; i++) {
        var file = fileList[i];
        if (file.endsWith(".qml") || file.endsWith(".js")) {
            var parts = file.split("/");
            var name = parts[parts.length - 1];
            var category = categorize(name);
            result.push({ name: name, category: category, path: file });
        }
    }
    result.sort(function(a, b) { return a.name.localeCompare(b.name); });
    return result;
}
```

## What to Write Instead
```cpp
// C++ backend — testable, fast, type-safe
Q_INVOKABLE QVariantList processFiles(const QStringList &fileList);
```
```qml
// QML — thin glue only
ListView {
    model: backend.processFiles(workspace.files)
}
```

---

See [performance.md](performance.md) for why JS in QML is slow and when C++ is required.
See [validation.md](validation.md) for how to keep validation logic in C++, not QML JS.
See [types.md](types.md) for type discipline in QML properties.
