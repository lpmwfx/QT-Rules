# Common AI Mistakes — Quick Reference

> One-table summary of what AI gets wrong and the correct cxx-qt pattern.

---

| AI Writes | Problem | Correct cxx-qt Pattern |
|-----------|---------|----------------------|
| Raw FFI (`extern "C"`) | No moc, no safety | `#[cxx_qt::bridge]` |
| Moving QObject | Qt internal pointers break | Everything is `Pin<&mut T>` |
| `Box<QObject>` | Conflicts with Qt parent-child | Let Qt own via parent, Rust refs via cxx-qt |
| Manual signal emit | No such API in Rust | `#[qsignal]` attribute + generated method |
| `#[tokio::main]` | Two event loops | std::thread + `qt_thread.queue()` |
| `.await` in bridge method | Qt slots are sync | Spawn thread, queue result back |
| `Result` return from #[qinvokable] | QML can't handle Rust errors | Map to signal: ok → data signal, err → error signal |
| Manual getter/setter | Fighting cxx-qt | `#[qproperty(Type, name)]` |
| `String` in Qt API | Wrong type | `QString` via cxx-qt-lib |
| `unwrap()` in bridge | Panic crosses FFI → UB | Always handle with match |
| Qt types in core crate | Breaks isolation | Pure Rust core, convert at bridge |
| `Rc<RefCell<>>` for Qt object | Wrong ownership model | Qt parent-child + Pin |
| `Send + Sync` on QObject | Qt objects are NOT thread-safe | Use `qt_thread.queue()` for cross-thread |

### Detailed Rules by Topic

- Raw FFI vs cxx-qt: See [cxx-qt.md](cxx-qt.md)
- Pin and moving: See [pin.md](pin.md)
- Ownership conflicts: See [ownership.md](ownership.md)
- Signal emission: See [signals.md](signals.md)
- Event loops and async: See [async.md](async.md)
- Error handling: See [errors.md](errors.md)
- Properties: See [q-property.md](q-property.md)
- Type mapping: See [types.md](types.md)
- Core isolation: See [core-isolation.md](core-isolation.md)
