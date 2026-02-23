# Ownership: Qt Parent-Child vs Rust Ownership

> Rust's single-owner model and Qt's parent-child tree are fundamentally different. Mixing them causes double frees or dangling pointers.

---

RULE: QObject parent-child ownership is managed by Qt, not Rust
RULE: Rust code does NOT own QObject instances created for QML
RULE: Use references and lifetimes — never Box<QObject> or Rc<QObject>
RULE: Let cxx-qt handle the ownership bridge

### The Conflict
```
Rust says: One owner. Owner drops → memory freed.
Qt says:   Parent owns children. Parent drops → children freed.

If Rust owns a QObject AND Qt parent also owns it → double free.
If Rust drops early → Qt holds dangling pointer → crash.
```

### What AI Does (Wrong)
```rust
// AI applies Rust ownership — CONFLICT with Qt
let widget = Box::new(MyWidget::new());  // Rust owns it
parent.add_child(&widget);               // Qt parent also "owns" it
// When Box drops → freed. When parent drops → double free.
```

### What to Write Instead
```rust
// Let Qt own the object — Rust holds a reference via cxx-qt
// cxx-qt bridges handle this automatically:

#[cxx_qt::bridge]
mod ffi {
    unsafe extern "RustQt" {
        #[qobject]
        #[qml_element]
        type FileModel = super::FileModelRust;

        // Methods operate on Pin<&mut Self> — no ownership transfer
        #[qinvokable]
        fn load_directory(self: Pin<&mut FileModel>, path: &QString);
    }
}
```

See [pin.md](pin.md) for why Qt objects cannot be moved in memory.
See [cxx-qt.md](cxx-qt.md) for how the bridge handles ownership safely.
See [errors.md](errors.md) for how to handle errors without returning Result across the boundary.
See [quick-ref.md](quick-ref.md) for the full anti-pattern table.
