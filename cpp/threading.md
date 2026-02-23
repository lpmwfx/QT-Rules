# Threading: QThread, Not std::thread

> Qt has its own threading model with event loops — std::thread bypasses all of it.

---

RULE: Use `QThread` for threads that interact with Qt objects
RULE: Use `QtConcurrent::run` for fire-and-forget computation
RULE: Use worker-object pattern: create QObject, moveToThread, connect signals
RULE: Never access QWidget/QML from non-GUI thread
RULE: Queued connections for cross-thread signal/slot

## What AI Does (Wrong)
```cpp
// AI uses std::thread — no Qt event loop, no signal delivery
std::thread t([this]() {
    auto result = heavyComputation();
    emit resultReady(result);  // UNDEFINED — emit from non-Qt thread
});
t.detach();  // lost thread, no cleanup
```

```cpp
// AI subclasses QThread::run — outdated pattern
class Worker : public QThread {
    void run() override {
        // All logic in run() — wrong pattern since Qt 4.4
    }
};
```

## What to Write Instead
```cpp
// Worker-object pattern (correct since Qt 4.4)
class Worker : public QObject {
    Q_OBJECT
public slots:
    void process() {
        auto result = heavyComputation();
        emit resultReady(result);  // safe — runs in worker thread's event loop
    }
signals:
    void resultReady(const QVariantMap &data);
};

// Setup
auto *thread = new QThread(this);
auto *worker = new Worker();  // no parent — will be moved
worker->moveToThread(thread);

connect(thread, &QThread::started, worker, &Worker::process);
connect(worker, &Worker::resultReady, this, &App::handleResult);  // queued auto
connect(worker, &Worker::resultReady, thread, &QThread::quit);
connect(thread, &QThread::finished, worker, &QObject::deleteLater);

thread->start();
```

```cpp
// Simple one-shot computation
QFuture<Result> future = QtConcurrent::run([data]() {
    return heavyComputation(data);
});

auto *watcher = new QFutureWatcher<Result>(this);
connect(watcher, &QFutureWatcher<Result>::finished, this, [watcher, this]() {
    handleResult(watcher->result());
    watcher->deleteLater();
});
watcher->setFuture(future);
```

BANNED: `std::thread` for anything touching QObject
BANNED: Subclassing `QThread::run()` (use worker-object pattern)
BANNED: `QThread::terminate()` (causes undefined state)
BANNED: Accessing GUI from worker thread

See [connections.md](connections.md) for cross-thread connection types.
See [ownership.md](ownership.md) for lifetime management of worker objects.
