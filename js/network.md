# XMLHttpRequest — The Only Network API

> QML JS has no fetch(), no axios, no npm HTTP libraries. XMLHttpRequest is the only option.

---

RULE: Use `XMLHttpRequest` for HTTP in QML JS (it is the only option)
RULE: For complex networking, use C++ `QNetworkAccessManager` exposed to QML
RULE: Never use fetch(), axios, or any npm-based HTTP library in QML

## Correct Pattern
```qml
function loadData(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                callback(JSON.parse(xhr.responseText));
            } else {
                console.log("HTTP error: " + xhr.status);
            }
        }
    };
    xhr.open("GET", url);
    xhr.send();
}
```

## Better: Move to C++
```cpp
// Expose a clean API to QML — handles auth, retries, error mapping
class ApiClient : public QObject {
    Q_OBJECT
    Q_INVOKABLE void fetchData(const QString &endpoint);
signals:
    void dataReady(const QVariantMap &data);
    void errorOccurred(const QString &message);
};
```

---

See [engine.md](engine.md) for why `fetch()` and `async/await` are banned in V4.
See [glue-code.md](glue-code.md) for why complex networking belongs in C++, not QML JS.
See [validation.md](validation.md) for validating network responses at the C++ boundary.
