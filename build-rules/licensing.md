# Qt Licensing — LGPL Compliance for Commercial Products

> We use Qt Open Source (LGPL 3.0) by default.
> Commercial products MUST follow LGPL rules to avoid license violation.

---

RULE: Default to Qt Open Source (LGPL 3.0) — no commercial license required if LGPL is followed
RULE: Always link Qt dynamically — static linking triggers LGPL copyleft on your code
RULE: Never modify Qt source without releasing those modifications under LGPL
RULE: Ship a prominent LGPL notice in your application (About dialog, README, or LICENSE file)
RULE: Users must be able to re-link your application against a different Qt version
RULE: Check every Qt module's license before using it — some are GPL-only
RULE: Keep your proprietary code in core/ (no Qt dependency) — this is never at risk
BANNED: Static linking of Qt libraries in commercial/proprietary products
BANNED: Using GPL-only Qt modules in proprietary products without commercial license
BANNED: Tivoization — hardware that prevents users from replacing Qt libraries
BANNED: Hiding Qt usage — LGPL requires attribution and notice

---

## The License Landscape

Qt is available under three licenses:

| License | Cost | Requirement |
|---------|------|-------------|
| LGPL 3.0 | Free | Dynamic linking, attribution, re-link capability |
| GPL 3.0 | Free | Entire application must be GPL (copyleft) |
| Commercial | Paid | No restrictions on linking or distribution |

**We default to LGPL 3.0** — free, allows proprietary code, but has rules.

---

## LGPL Compliance Checklist

### 1. Dynamic Linking (Non-Negotiable)

```cmake
# CORRECT — dynamic linking (default in Qt)
find_package(Qt6 REQUIRED COMPONENTS Core Quick)
target_link_libraries(myapp PRIVATE Qt6::Core Qt6::Quick)
# Qt ships as .so / .dylib / .dll — this is dynamic by default
```

```cmake
# WRONG — static linking makes your entire app LGPL
# Do NOT set these for commercial products:
# set(BUILD_SHARED_LIBS OFF)
# -DCMAKE_FIND_LIBRARY_SUFFIXES=".a"
# -DQT_DEFAULT_MAJOR_VERSION=6 -DBUILD_STATIC=ON
```

RULE: CMake `find_package(Qt6)` defaults to shared libs — do not override this

### 2. Attribution and Notice

Your application must include:

- A statement that it uses Qt under LGPL 3.0
- A copy of the LGPL 3.0 license text (or link to it)
- A copy of the Qt license (found in Qt installation: `licenses/` directory)

```
# Example: About dialog or LICENSES.md
This application uses the Qt framework (https://www.qt.io)
licensed under the GNU Lesser General Public License v3.0.
See: https://www.gnu.org/licenses/lgpl-3.0.html
```

### 3. Re-Linking Capability

Users must be able to replace the Qt libraries your app ships with.
This means:

- Ship Qt as separate .so/.dll files (not embedded in your binary)
- Provide object files OR a re-linkable package so users can re-link against their own Qt
- Do not use Qt's static build for proprietary apps

### 4. Modification Disclosure

If you modify Qt source code:

- Release your modifications under LGPL 3.0
- Clearly mark what you changed
- Make modified source available to users

If you do NOT modify Qt: no source disclosure required for your own code.

---

## Qt Module License Map

Not all Qt modules are LGPL. Check before using:

### LGPL 3.0 (Safe for Commercial)

- Qt Core, Qt GUI, Qt Widgets
- Qt Quick, Qt QML
- Qt Network, Qt DBus
- Qt Concurrent, Qt SQL
- Qt SVG, Qt XML
- Qt Quick Controls 2
- Qt Multimedia (Qt 6)

### GPL Only (Requires Commercial License for Proprietary Use)

- Qt Charts
- Qt Data Visualization
- Qt Virtual Keyboard
- Qt Wayland Compositor (some parts)
- Qt CoAP, Qt MQTT, Qt OPC UA

RULE: Before adding a Qt module to CMakeLists.txt, verify its license at https://doc.qt.io/qt-6/licenses-used-in-qt.html

### KDE Frameworks (LGPL 2.1+)

KDE Frameworks (Kirigami, KConfig, etc.) are LGPL 2.1+ — compatible with commercial use under the same dynamic-linking rules.

---

## Architecture = License Protection

The layer architecture in build-rules/ naturally protects your IP:

```
core/           ← Your proprietary code. No Qt. LGPL does not touch this.
adapters/       ← Links Qt dynamically. Must follow LGPL rules.
app/            ← Wiring only. Links both. LGPL-compliant by dynamic linking.
```

RULE: core/ must never depend on Qt — this keeps your business logic outside LGPL scope
RULE: adapters/ links Qt dynamically — LGPL compliance is automatic with shared libs

---

## Build System Verification

### CMake Check

```cmake
# Add to top-level CMakeLists.txt for LGPL compliance verification
if(NOT BUILD_SHARED_LIBS)
    message(WARNING "Static build detected — verify LGPL compliance!")
endif()

# Ensure Qt is found as shared libraries
get_target_property(_qt_type Qt6::Core TYPE)
if(_qt_type STREQUAL "STATIC_LIBRARY")
    message(FATAL_ERROR "Qt linked statically — violates LGPL for proprietary code!")
endif()
```

### CI Check

```bash
# Verify no static Qt linking in final binary
ldd build/myapp | grep -i qt
# Should show: libQt6Core.so.6, libQt6Quick.so.6, etc.
# If no Qt .so appears, something is statically linked — STOP

# Verify LGPL notice exists
test -f LICENSES.md || test -f LICENSE-Qt || echo "FAIL: No Qt license notice"
```

---

## Flatpak / AppImage Distribution

When packaging as Flatpak or AppImage, Qt libraries are bundled.
This is LGPL-compliant because:

- Libraries are separate .so files inside the bundle (user can replace them)
- Flatpak: Qt is in the runtime, not your app (org.kde.Platform handles it)
- AppImage: include Qt .so files in `usr/lib/` and LGPL notice in `usr/share/licenses/`

RULE: Flatpak with org.kde.Platform or org.kde.Sdk runtime handles Qt LGPL automatically
RULE: AppImage must include Qt .so files as replaceable shared libs + LGPL notice

---

## Summary

| Do | Don't |
|----|-------|
| Link Qt dynamically (default) | Link Qt statically in proprietary apps |
| Include LGPL notice in app | Hide that you use Qt |
| Keep business logic in core/ (no Qt) | Put proprietary logic in Qt-dependent code |
| Check module license before use | Assume all Qt modules are LGPL |
| Ship Qt as separate .so/.dll | Embed Qt into a single binary |
| Use Flatpak runtime for Qt | Bundle Qt without re-link capability |
