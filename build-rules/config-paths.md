# Config Paths — Qt Standard Locations

> QT-BuildRules §3.1 defines config layering (base/override/runtime) but doesn't
> map to actual filesystem paths on Linux/Flatpak. This file fills that gap.

---

## Principle

Config files must be discoverable via `QStandardPaths` and XDG conventions.
No hardcoded absolute paths. No user-home assumptions.

---

## Path Resolution

### XDG Base Directories (Linux/BSD)

| Purpose | XDG Variable | Default | Qt API |
|---------|-------------|---------|--------|
| User config | `$XDG_CONFIG_HOME` | `~/.config` | `QStandardPaths::ConfigLocation` |
| System config | `$XDG_CONFIG_DIRS` | `/etc/xdg` | `QStandardPaths::ConfigLocation` (all) |
| User data | `$XDG_DATA_HOME` | `~/.local/share` | `QStandardPaths::AppDataLocation` |
| Runtime | `$XDG_RUNTIME_DIR` | `/run/user/<uid>` | `QStandardPaths::RuntimeLocation` |
| Cache | `$XDG_CACHE_HOME` | `~/.cache` | `QStandardPaths::CacheLocation` |

### Mapping to BuildRules Config Layers

```
conf/base/         →  Shipped with app binary (resource or install dir)
                      QStandardPaths::AppDataLocation + "/conf/base"
                      Example: /usr/share/<appname>/conf/base/

conf/override/     →  User overrides
                      QStandardPaths::ConfigLocation + "/<appname>"
                      Example: ~/.config/<appname>/

conf/runtime/      →  Ephemeral, not persisted across reboots
                      QStandardPaths::RuntimeLocation + "/<appname>"
                      Example: /run/user/1000/<appname>/

memory/            →  Session state (persisted)
                      QStandardPaths::AppDataLocation + "/memory"
                      Example: ~/.local/share/<appname>/memory/

schemas/           →  Shipped with app (same as base)
                      QStandardPaths::AppDataLocation + "/schemas"
```

---

## Resolution Order

```cpp
QStringList configPaths(const QString &appName) {
    QStringList paths;

    // 1. Base (shipped defaults — read-only)
    paths << QStandardPaths::locate(QStandardPaths::AppDataLocation,
                                     "conf/base", QStandardPaths::LocateDirectory);

    // 2. Override (user customization — read-write)
    paths << QStandardPaths::writableLocation(QStandardPaths::ConfigLocation)
              + "/" + appName;

    // 3. Runtime (ephemeral — optional)
    QString runtime = QStandardPaths::writableLocation(QStandardPaths::RuntimeLocation);
    if (!runtime.isEmpty()) {
        paths << runtime + "/" + appName;
    }

    return paths;
}
```

Merge strategy: later paths override earlier. `conf/base` is complete;
`conf/override` may be partial (only keys that differ).

---

## Flatpak Sandbox

Flatpak remaps XDG paths into the sandbox:

| Standard path | Flatpak remapped |
|---------------|-----------------|
| `~/.config/<app>` | `~/.var/app/<app-id>/config/` |
| `~/.local/share/<app>` | `~/.var/app/<app-id>/data/` |
| `~/.cache/<app>` | `~/.var/app/<app-id>/cache/` |
| `/run/user/<uid>` | Available inside sandbox |

RULE: Use `QStandardPaths` exclusively — never construct paths manually
RULE: `QStandardPaths` handles Flatpak remapping automatically
RULE: Never use `QDir::homePath()` + hardcoded relative path

```cpp
// WRONG — breaks in Flatpak
QString configDir = QDir::homePath() + "/.config/myapp";

// CORRECT — works everywhere
QString configDir = QStandardPaths::writableLocation(QStandardPaths::ConfigLocation) + "/myapp";
```

---

## Socket Paths

IPC sockets live under runtime dir (see IPC-CONTRACT.md):

```cpp
QString socketPath = QStandardPaths::writableLocation(QStandardPaths::RuntimeLocation)
                     + "/" + appName + "/" + cfg.mcp.socket_name;
```

RULE: Socket dir must be created at startup if it doesn't exist
RULE: Clean up socket file on shutdown (or check for stale socket on startup)
RULE: Socket path must come from config — not hardcoded

---

## Memory Persistence Path

```cpp
QString memoryPath = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation)
                     + "/memory/last_session.json";
```

Atomic write pattern (from BuildRules §4.3):

```cpp
void persistMemory(const QVariantMap &memory, const QString &path) {
    QString tmpPath = path + ".tmp";
    QSaveFile file(tmpPath);  // QSaveFile handles atomic rename
    if (file.open(QIODevice::WriteOnly)) {
        file.write(QJsonDocument::fromVariant(memory).toJson());
        file.commit();  // atomic rename
    }
}
```

Note: `QSaveFile::commit()` does write-tmp-then-rename. This matches the
BuildRules §4.3 requirement without manual fsync/rename.

---

## Environment Variable Overrides

For development and testing, allow env vars to override config locations:

```cpp
QString configBase = qEnvironmentVariable("MYAPP_CONF_BASE",
    QStandardPaths::locate(QStandardPaths::AppDataLocation, "conf/base",
                           QStandardPaths::LocateDirectory));

QString configOverride = qEnvironmentVariable("MYAPP_CONF_OVERRIDE",
    QStandardPaths::writableLocation(QStandardPaths::ConfigLocation) + "/myapp");
```

RULE: Env var overrides are for dev/test only
RULE: Production uses QStandardPaths exclusively
RULE: Document env vars in bootstrap.json or README

---

## Checklist

- [ ] All config paths use `QStandardPaths` — no hardcoded paths
- [ ] `conf/base` ships as read-only app data
- [ ] `conf/override` writes to user config location
- [ ] Memory persists to app data location via `QSaveFile`
- [ ] Socket path uses runtime location
- [ ] App works in Flatpak sandbox without path changes
- [ ] Env var overrides documented for dev/test
