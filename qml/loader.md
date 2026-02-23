# Loader for On-Demand Creation

> Use Loader for heavy components that may not be needed.
> Setting visible: false still creates the component and keeps it in memory.

---

RULE: Use `Loader` for heavy components that may not be needed
RULE: Use `Loader` for conditional content (not `visible: false`)
RULE: Setting `visible: false` still creates and keeps the component in memory

### What AI Does (Wrong)
```qml
// AI hides everything — all created at startup, all in memory
SettingsPanel { visible: settingsOpen }
HelpDialog { visible: helpOpen }
SearchOverlay { visible: searchActive }
// 500 QML items created even when user never opens settings
```

### What to Write Instead
```qml
// Loader — created only when needed
Loader {
    active: settingsOpen
    sourceComponent: SettingsPanel {}
}

Loader {
    active: helpOpen
    source: "HelpDialog.qml"
}
```

---

See [file-size.md](file-size.md) — extract heavy subtrees into separate files so Loader can load them.
See [states.md](states.md) — for lightweight visual switches, states may suffice; Loader is for heavy content.
See [quick-ref.md](quick-ref.md) — quick reference table of common mistakes.
