# Signals from Rust — Use cxx-qt Macros

> Declare signals via #[qsignal] in the cxx-qt bridge. Never invent manual signal emission APIs.

---

RULE: Declare signals via #[qsignal] attribute in cxx-qt bridge
RULE: Emit signals through the generated API — not manual C++ calls
RULE: Signal emission must happen on the Qt thread that owns the object

### What AI Does (Wrong)
```rust
// AI tries to emit signals manually — WRONG
impl Backend {
    fn process(&mut self) {
        // AI invents signal emission — no such API exists in Rust
        self.emit_signal("dataReady", &[result.into()]);
    }
}
```

### What to Write Instead
```rust
#[cxx_qt::bridge]
mod ffi {
    unsafe extern "RustQt" {
        #[qobject]
        type Backend = super::BackendRust;

        #[qsignal]
        fn data_ready(self: Pin<&mut Backend>, data: &QString);

        #[qsignal]
        fn error_occurred(self: Pin<&mut Backend>, message: &QString);
    }
}

impl qobject::Backend {
    fn process(self: Pin<&mut Self>) {
        match do_work() {
            Ok(data) => self.data_ready(&QString::from(&data)),
            Err(e) => self.error_occurred(&QString::from(&e.to_string())),
        }
    }
}
```

See [errors.md](errors.md) for the full Result-to-signal pattern.
See [async.md](async.md) for emitting signals from background threads via `qt_thread.queue()`.
See [cxx-qt.md](cxx-qt.md) for the bridge declaration pattern.
See [q-property.md](q-property.md) for auto-generated NOTIFY signals from properties.
