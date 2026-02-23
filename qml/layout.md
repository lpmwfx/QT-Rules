# Anchors and Layouts — Never Absolute Position

> Use anchors for parent-relative positioning. Use Layouts for arranged children.
> Never use x:/y: for static layout.

---

RULE: Use `anchors` for parent-relative positioning
RULE: Use `RowLayout`/`ColumnLayout`/`GridLayout` for arranged children
RULE: Never use `x:`/`y:` for static layout (only for animation/drag)
RULE: Never mix anchors and Layouts on the same item

### What AI Does (Wrong)
```qml
// AI uses absolute positioning — BREAKS on resize
Rectangle {
    x: 20
    y: 50
    width: 300
    height: 400
}

Text {
    x: parent.width / 2 - width / 2  // manual centering
    y: parent.height / 2 - height / 2
}
```

### What to Write Instead
```qml
// Anchors — responsive
Rectangle {
    anchors.fill: parent
    anchors.margins: 20
}

Text {
    anchors.centerIn: parent
}
```

```qml
// Layout — children arranged automatically
ColumnLayout {
    spacing: 8

    Label { text: "Title"; Layout.fillWidth: true }
    TextField { Layout.fillWidth: true }
    Button { text: "Submit"; Layout.alignment: Qt.AlignRight }
}
```

BANNED: `x:` / `y:` for layout (only for drag, animation, or Canvas)
BANNED: Manual `width: parent.width - 40` calculations
BANNED: Mixing `anchors` with `Layout.*` on the same item

---

See [bindings.md](bindings.md) — layout expressions are bindings; imperative assignment breaks them.
See [quick-ref.md](quick-ref.md) — quick reference table of common mistakes.
