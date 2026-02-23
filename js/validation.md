# Validation at Boundaries

> QML JS has no Zod, no schema validation. The C++ layer does this.

---

RULE: Validate data from C++ -> QML at the C++ side BEFORE exposing to QML
RULE: QML JS has no Zod, no schema validation — the C++ layer does this
RULE: JSON from external sources: parse and validate in C++, expose typed QVariant to QML

## Pattern
```cpp
// C++ boundary — validate, then expose safe data
QVariantMap ApiClient::parseResponse(const QByteArray &json) {
    QJsonParseError err;
    auto doc = QJsonDocument::fromJson(json, &err);
    if (err.error != QJsonParseError::NoError) {
        emit errorOccurred("Invalid JSON: " + err.errorString());
        return {};
    }
    // validate schema...
    return doc.object().toVariantMap();
}
```

```qml
// QML just uses safe data — no validation needed
Text {
    text: apiClient.lastResponse.title
}
```

---

See [network.md](network.md) for how to structure C++ network clients exposed to QML.
See [glue-code.md](glue-code.md) for why business logic (including validation) belongs in C++.
See [types.md](types.md) for using typed QML properties to maintain type safety.
