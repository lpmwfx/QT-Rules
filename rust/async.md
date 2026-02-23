# Async: Qt Event Loop, Not Tokio

> Qt has its own event loop. Do not run Tokio or async-std alongside it. Use threads and channels instead.

---

RULE: Do NOT use tokio or async-std runtime alongside Qt's event loop
RULE: Qt has its own event loop (QCoreApplication::exec) — it must be primary
RULE: For async work, use QThread + channels or spawn_blocking from Qt thread
RULE: Bridge async Rust to Qt via channels, not runtime integration

### What AI Does (Wrong)
```rust
// AI starts tokio runtime inside Qt app — TWO event loops competing
#[tokio::main]
async fn main() {
    let app = QApplication::new();
    // tokio event loop AND Qt event loop — they fight for the thread
    app.exec();
}
```

```rust
// AI uses .await inside a Qt slot — WRONG (Qt slots are sync)
impl qobject::Backend {
    fn fetch_data(self: Pin<&mut Self>) {
        let data = http_client.get(url).await;  // Can't await in Qt context
    }
}
```

### What to Write Instead
```rust
// Pattern 1: std::thread + channel for heavy work
impl qobject::Backend {
    fn fetch_data(self: Pin<&mut Self>) {
        let (tx, rx) = std::sync::mpsc::channel();

        std::thread::spawn(move || {
            let result = blocking_http_get(&url);
            let _ = tx.send(result);
        });

        // Poll from Qt side (via QTimer or similar)
        // Or use cxx-qt's threading support
    }
}
```

```rust
// Pattern 2: cxx-qt threading helpers
// Use cxx-qt's CxxQtThread to safely invoke back on the Qt thread
impl qobject::Backend {
    fn fetch_data(self: Pin<&mut Self>) {
        let qt_thread = self.qt_thread();

        std::thread::spawn(move || {
            let result = blocking_http_get(&url);
            qt_thread.queue(move |mut backend| {
                backend.as_mut().set_data(QString::from(&result));
                backend.as_mut().data_ready(&QString::from(&result));
            });
        });
    }
}
```

BANNED: `#[tokio::main]` in Qt applications
BANNED: `.await` inside cxx-qt method implementations
BANNED: Running two event loops (tokio + Qt)

See [signals.md](signals.md) for emitting signals from the queued callback.
See [errors.md](errors.md) for handling errors in async patterns.
See [pin.md](pin.md) for why `Pin<&mut Self>` is used in all method signatures.
