# cxx-qt Is the Bridge — Not Raw FFI

> Use cxx-qt for all Qt/Rust integration. Never write manual FFI for QObject methods.

---

RULE: Use cxx-qt for Qt/Rust integration — not raw cxx or bindgen
RULE: cxx-qt handles moc generation, Pin safety, and signal/slot wiring
RULE: Never write manual extern "C" bindings for QObject methods
RULE: All QML-exposed types go through #[cxx_qt::bridge]

### What AI Does (Wrong)
```rust
// AI writes raw FFI — WRONG for Qt objects
extern "C" {
    fn QWidget_new() -> *mut QWidget;
    fn QWidget_show(w: *mut QWidget);
}

unsafe {
    let w = QWidget_new();  // raw pointer, no ownership, no moc
    QWidget_show(w);
}
```

### What to Write Instead
```rust
#[cxx_qt::bridge]
mod ffi {
    unsafe extern "C++" {
        include!("cxx-qt-lib/qstring.h");
        type QString = cxx_qt_lib::QString;
    }

    unsafe extern "RustQt" {
        #[qobject]
        #[qml_element]
        #[qproperty(QString, user_name)]
        type Backend = super::BackendRust;
    }
}
```

See [pin.md](pin.md) for why cxx-qt generates Pin-based APIs.
See [signals.md](signals.md) for declaring signals via cxx-qt macros.
See [q-property.md](q-property.md) for property declarations.
See [quick-ref.md](quick-ref.md) for the full anti-pattern table.
