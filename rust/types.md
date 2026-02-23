# Type Mapping: Rust ↔ Qt

> Use cxx-qt-lib types at the Qt/Rust boundary. Convert to standard Rust types in core logic.

---

RULE: Use cxx-qt-lib types for Qt/Rust boundary
RULE: Convert to standard Rust types in core logic
RULE: Never pass `String` directly to Qt — use `QString`

| Rust Type | Qt Type | cxx-qt-lib |
|-----------|---------|------------|
| `String` / `&str` | `QString` | `cxx_qt_lib::QString` |
| `Vec<T>` | `QList<T>` | `cxx_qt_lib::QVector` |
| `HashMap` | `QHash` / `QVariantMap` | `cxx_qt_lib::QMap` |
| `bool` | `bool` | direct |
| `i32` | `int` | direct |
| `f64` | `double` | direct |
| `PathBuf` | `QUrl` or `QString` | Convert via String |

### Conversion Pattern
```rust
// At the bridge boundary — convert between worlds
impl qobject::Backend {
    #[qinvokable]
    fn open_directory(self: Pin<&mut Self>, path: &QString) {
        // Qt → Rust
        let rust_path = std::path::PathBuf::from(path.to_string());

        // Core logic uses standard Rust types
        match core::scan_directory(&rust_path) {
            Ok(entries) => {
                // Rust → Qt
                let qt_entries: Vec<QString> = entries
                    .iter()
                    .map(|e| QString::from(e.to_str().unwrap_or_default()))
                    .collect();
                // ...
            }
            Err(e) => self.error_occurred(&QString::from(&e.to_string())),
        }
    }
}
```

See [core-isolation.md](core-isolation.md) for why core logic uses standard Rust types only.
See [q-property.md](q-property.md) for using these types in property declarations.
See [errors.md](errors.md) for handling conversion errors at the boundary.
