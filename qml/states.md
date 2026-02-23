# Use States, Not If/Else JS

> QML states + PropertyChanges for multi-property visual switches.
> Transitions for animated state changes. Never toggle properties imperatively.

---

RULE: QML `states` + `PropertyChanges` for multi-property visual switches
RULE: Transitions for animated state changes
RULE: Never use JS if/else to toggle multiple properties imperatively

### What AI Does (Wrong)
```qml
// AI writes imperative state switching — WRONG
function setEditMode(editing) {
    if (editing) {
        nameLabel.visible = false
        nameField.visible = true
        nameField.text = nameLabel.text
        saveButton.visible = true
        editButton.visible = false
    } else {
        nameLabel.visible = true
        nameField.visible = false
        saveButton.visible = false
        editButton.visible = true
    }
}
```

### What to Write Instead
```qml
// Declarative states — clean, animatable
states: [
    State {
        name: "editing"
        PropertyChanges { target: nameLabel; visible: false }
        PropertyChanges { target: nameField; visible: true; text: nameLabel.text }
        PropertyChanges { target: saveButton; visible: true }
        PropertyChanges { target: editButton; visible: false }
    }
]

transitions: Transition {
    NumberAnimation { properties: "opacity"; duration: 150 }
}

// Trigger
MouseArea { onClicked: parent.state = "editing" }
```

---

See [bindings.md](bindings.md) — imperative assignment in if/else breaks bindings; states preserve them.
See [loader.md](loader.md) — for heavy conditional content, prefer Loader over state-based visibility.
See [quick-ref.md](quick-ref.md) — quick reference table of common mistakes.
