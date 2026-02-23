# Vanilla JS Files in Qt Projects (Non-QML)

> Qt projects sometimes include standalone JS files that run under Node.js, not the V4 engine.

---

Qt projects sometimes include standalone JS files for:
- Build scripts (using Node.js tooling)
- Code generators
- Test runners
- Configuration processors

RULE: Standalone JS files (NOT loaded by QML) follow ~/.rules/JS/RULES
RULE: QML-loaded JS files follow the rules in this directory
RULE: Never mix the two — a .js file is either QML-loaded or standalone, never both

## How to Tell
- Loaded by QML: referenced via `import "file.js" as Logic` in .qml
- Loaded by QML: used as `.pragma library` JS module
- Standalone: runs under Node.js, has `import`/`require`, has `package.json`

---

See [pragma-library.md](pragma-library.md) for QML's own JS module system.
See [engine.md](engine.md) for what V4 supports vs. web JS.
