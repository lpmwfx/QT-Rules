# Error Handling: Result → Qt Signals

> Rust Result types must be mapped to Qt signals at the bridge boundary. Never let a panic cross FFI.

---

RULE: Rust `Result<T, E>` must be mapped to Qt signals at the boundary
RULE: `?` operator works inside Rust functions — but bridge methods must handle errors
RULE: Never let a panic cross the FFI boundary — it's undefined behavior
RULE: Use `catch_unwind` at bridge boundaries if panic is possible

### What AI Does (Wrong)
```rust
// AI uses ? in a cxx-qt invokable — error has nowhere to go
#[qinvokable]
fn load_file(self: Pin<&mut Self>, path: &QString) -> Result<(), ConfigError> {
    // cxx-qt can't return Result to QML — QML doesn't understand Rust errors
    let content = std::fs::read_to_string(path.to_string())?;
    Ok(())
}
```

### What to Write Instead
```rust
impl qobject::Backend {
    #[qinvokable]
    fn load_file(self: Pin<&mut Self>, path: &QString) {
        match self.do_load_file(path) {
            Ok(content) => self.file_loaded(&content),
            Err(e) => self.error_occurred(&QString::from(&e.to_string())),
        }
    }

    // Internal — can use ? freely
    fn do_load_file(&self, path: &QString) -> Result<QString, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path.to_string())?;
        Ok(QString::from(&content))
    }
}
```

BANNED: Returning `Result` from #[qinvokable] methods
BANNED: `unwrap()`/`expect()` in bridge code (panic crosses FFI → UB)
BANNED: `panic!()` in any cxx-qt method

See [signals.md](signals.md) for declaring the error_occurred and success signals.
See [async.md](async.md) for error handling in threaded patterns.
See [core-isolation.md](core-isolation.md) for keeping error-prone logic in the pure Rust core.
