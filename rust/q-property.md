# Q_PROPERTY from Rust

> Use #[qproperty(Type, name)] on the qobject struct. cxx-qt generates getter, setter, and NOTIFY signal automatically.

---

RULE: Use `#[qproperty(Type, name)]` attribute on the qobject struct
RULE: cxx-qt generates getter, setter, and NOTIFY signal automatically
RULE: The Rust struct field holds the value — cxx-qt bridges it to Qt

### What AI Does (Wrong)
```rust
// AI tries to implement Q_PROPERTY manually — fighting the framework
impl Backend {
    pub fn get_user_name(&self) -> String {
        self.user_name.clone()
    }
    pub fn set_user_name(&mut self, name: String) {
        self.user_name = name;
        // How to emit NOTIFY? AI is stuck.
    }
}
```

### What to Write Instead
```rust
#[cxx_qt::bridge]
mod ffi {
    unsafe extern "RustQt" {
        #[qobject]
        #[qml_element]
        #[qproperty(QString, user_name)]
        #[qproperty(i32, file_count)]
        #[qproperty(bool, is_loading)]
        type Backend = super::BackendRust;
    }
}

#[derive(Default)]
pub struct BackendRust {
    user_name: QString,
    file_count: i32,
    is_loading: bool,
}

// cxx-qt automatically generates:
// - user_name() getter
// - set_user_name() setter
// - user_name_changed() signal
// Same for file_count and is_loading
```

See [types.md](types.md) for which types to use in property declarations.
See [signals.md](signals.md) for custom signals beyond the auto-generated NOTIFY.
See [cxx-qt.md](cxx-qt.md) for the full bridge declaration pattern.
