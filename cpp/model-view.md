# Model/View — Use It, Don't Reinvent It

> Use QAbstractListModel for QML ListView data with proper change notifications.

---

RULE: Use `QAbstractListModel` for QML ListView data
RULE: Implement `roleNames()`, `rowCount()`, `data()` minimum
RULE: Emit `beginInsertRows`/`endInsertRows` for proper QML update
RULE: Never populate a QML ListModel from C++ in a loop

## What AI Does (Wrong)
```cpp
// AI creates a flat list and exposes it — no change notifications
Q_INVOKABLE QVariantList getFiles() {
    QVariantList list;
    for (auto &f : files) list.append(toVariant(f));
    return list;  // QML gets a snapshot — never updates
}
```

## What to Write Instead
```cpp
class FileModel : public QAbstractListModel {
    Q_OBJECT
    enum Roles { NameRole = Qt::UserRole + 1, PathRole, SizeRole };

    QHash<int, QByteArray> roleNames() const override {
        return {{NameRole, "name"}, {PathRole, "path"}, {SizeRole, "size"}};
    }

    int rowCount(const QModelIndex &) const override { return m_files.size(); }

    QVariant data(const QModelIndex &index, int role) const override {
        const auto &f = m_files[index.row()];
        switch (role) {
            case NameRole: return f.name;
            case PathRole: return f.path;
            case SizeRole: return f.size;
        }
        return {};
    }

    void addFile(const FileEntry &entry) {
        beginInsertRows({}, m_files.size(), m_files.size());
        m_files.append(entry);
        endInsertRows();
    }

private:
    QVector<FileEntry> m_files;
};
```

See [q-object.md](q-object.md) — models require Q_OBJECT macro.
See [types.md](types.md) for type conversion between core and Qt model layer.
See [q-property.md](q-property.md) for exposing the model instance to QML.
