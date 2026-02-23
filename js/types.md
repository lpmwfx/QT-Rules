# Type Discipline in QML JS

> Property types are the ONLY type-safety QML gives you — use them.

---

RULE: Always declare type on QML properties — never use `var` for known types
RULE: Use `var` ONLY when the type is genuinely dynamic
RULE: Property types are the ONLY type-safety QML gives you — use them

## What AI Does (Wrong)
```qml
// AI uses var for everything — WRONG
property var userName: ""
property var fileCount: 0
property var isVisible: true
property var fileList: []
```

## What to Write Instead
```qml
// Typed properties — QML engine can optimize these
property string userName: ""
property int fileCount: 0
property bool isVisible: true
property list<string> fileList
```

## When `var` Is Acceptable
```qml
// Truly dynamic: could be string, int, object, or null
property var selectedItem: null

// Complex object from C++ that has no QML type
property var configData: backend.getConfig()
```

---

See [performance.md](performance.md) for why typed properties allow engine optimization.
See [glue-code.md](glue-code.md) for keeping QML JS minimal so types stay manageable.
See [validation.md](validation.md) for validating dynamic data at the C++ boundary.
