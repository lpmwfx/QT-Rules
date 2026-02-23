# File Organization

> Each .qml file = one visual component. Group by role. Keep it flat.

---

```
qml/
├── Main.qml              # Entry point — composition only
├── components/
│   ├── Sidebar.qml       # One concept per file
│   ├── FileTree.qml
│   ├── TabBar.qml
│   └── StatusBar.qml
├── delegates/
│   ├── FileDelegate.qml  # ListView/TreeView delegates
│   └── TabDelegate.qml
├── dialogs/
│   ├── SettingsDialog.qml
│   └── AboutDialog.qml
├── pages/
│   ├── WelcomePage.qml
│   └── WorkspacePage.qml
└── singletons/
    └── Theme.qml          # qmldir registered singleton
```

RULE: Each .qml file = one visual component
RULE: delegates/ for ListView/TreeView delegates
RULE: singletons/ for shared state (Theme, App config)
RULE: Never put .js helper files alongside .qml — put shared JS in a lib/ folder with `.pragma library`

---

See [file-size.md](file-size.md) — max 150 lines per file; extract when a subtree exceeds 50 lines.
See [loader.md](loader.md) — dialogs and heavy pages are good candidates for Loader.
See [required-properties.md](required-properties.md) — delegates in delegates/ should use required properties.
See [quick-ref.md](quick-ref.md) — quick reference table of common mistakes.
