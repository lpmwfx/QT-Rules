# Keep QML Files Small and Focused

> One visual concept per file. Max 150 lines. Extract early.

---

RULE: Max 150 lines per QML file
RULE: One visual concept per file
RULE: Extract components when a subtree exceeds 50 lines
RULE: Inline `Component {}` only for delegates under 20 lines

### What AI Does (Wrong)
```qml
// AI creates 400-line monolith QML files
ApplicationWindow {
    // header (80 lines)
    // sidebar (120 lines)
    // content area (150 lines)
    // dialogs (50 lines)
    // 25 JS functions
}
```

### What to Write Instead
```qml
// Main.qml — composition only
ApplicationWindow {
    header: AppHeader {}

    SplitView {
        Sidebar {}
        ContentArea {}
    }
}
```

Each component is a separate .qml file with one responsibility.

---

See [file-organization.md](file-organization.md) — directory structure for organizing extracted components.
See [loader.md](loader.md) — use Loader for heavy components that may not be needed immediately.
See [quick-ref.md](quick-ref.md) — quick reference table of common mistakes.
