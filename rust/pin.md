# Pin — Qt Objects Cannot Move

> Qt stores internal pointers that break on move. All QObject types in Rust must be Pin.

---

RULE: All QObject types in Rust must be `Pin<&mut T>`
RULE: cxx-qt generates Pin-based APIs — follow them, don't fight them
RULE: Never try to move, clone, or mem::swap a Qt object
RULE: Pin is NOT optional — Qt stores internal pointers that break on move

### What AI Does (Wrong)
```rust
// AI tries to own/move Qt objects — WRONG
let mut backend = Backend::new();
let moved = backend;  // MOVE — Qt's internal pointers now dangle

// AI tries to put Qt objects in Vec
let mut widgets: Vec<Widget> = vec![];
widgets.push(widget);  // MOVE into Vec — Qt object is corrupted
```

### What to Write Instead
```rust
// cxx-qt handles Pin automatically in generated code
// You work with Pin<&mut T> in method implementations

impl qobject::Backend {
    fn handle_command(self: Pin<&mut Self>, cmd: &str) {
        // self is pinned — cannot move, cannot take ownership
        // this is correct — Qt object stays in place
        self.set_user_name(QString::from(cmd));
    }
}
```

### Why Pin Matters
Qt stores `this` pointers internally:
- Signal/slot connections hold raw pointers to QObject
- Parent-child tree uses raw pointers
- QML engine caches property accessor pointers
- Moving the object in memory breaks ALL of these

See [ownership.md](ownership.md) for how Qt parent-child ownership interacts with Rust.
See [cxx-qt.md](cxx-qt.md) for how the bridge generates Pin-based APIs.
See [quick-ref.md](quick-ref.md) for the full anti-pattern table.
