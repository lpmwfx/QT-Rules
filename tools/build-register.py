#!/usr/bin/env python3
"""Build register.jsonl — JSONL index with RAG tags for QT/ markdown files."""

import json
import re
from pathlib import Path

QT_DIR = Path(__file__).resolve().parent.parent
OUTPUT = QT_DIR / "register.jsonl"

CONCEPT_MAP = {
    "ownership": ["lifetime", "memory-management"],
    "parent-child": ["lifetime", "memory-management"],
    "threading": ["concurrency", "threads"],
    "thread": ["concurrency", "threads"],
    "connections": ["signals-slots", "event-handling"],
    "signal": ["signals-slots", "event-handling"],
    "signals": ["signals-slots", "event-handling"],
    "model": ["data-model", "mvc"],
    "model-view": ["data-model", "mvc"],
    "types": ["type-conversion", "type-safety"],
    "bindings": ["declarative", "reactive"],
    "binding": ["declarative", "reactive"],
    "layout": ["positioning", "responsive"],
    "loader": ["lazy-loading", "performance"],
    "property": ["data-binding", "q-property"],
    "q-property": ["data-binding", "q-property"],
    "q-object": ["meta-object", "moc"],
    "q-invokable": ["qml-integration", "api-exposure"],
    "async": ["concurrency", "event-loop"],
    "errors": ["error-handling"],
    "pin": ["memory-safety", "move-semantics"],
    "bridge": ["interop", "ipc"],
    "bridge-ipc": ["interop", "ipc"],
    "config": ["configuration", "settings"],
    "config-paths": ["configuration", "file-paths"],
    "validation": ["schema", "type-checking"],
    "scope": ["encapsulation", "isolation"],
    "states": ["state-management", "visual-states"],
    "performance": ["optimization"],
    "engine": ["js-engine", "v4"],
    "engine-ownership": ["lifetime", "qml-engine"],
    "network": ["http", "api"],
    "startup": ["initialization", "boot"],
    "testing": ["test", "quality"],
    "build-system": ["build-system", "cmake"],
    "mvvm-bridge": ["architecture", "pattern"],
    "layers": ["architecture", "separation"],
    "principles": ["architecture", "design"],
    "contract": ["protocol", "interface"],
    "enforcement": ["linting", "quality"],
    "data-types": ["configuration", "state-management"],
    "core-isolation": ["architecture", "separation"],
    "cxx-qt": ["ffi", "bridge"],
    "pragma-library": ["modules", "code-organization"],
    "glue-code": ["integration", "adapter"],
    "standalone": ["modules", "isolation"],
    "file-size": ["code-organization", "maintainability"],
    "file-organization": ["code-organization", "structure"],
    "required-properties": ["type-safety", "encapsulation"],
    "qml-rules": ["declarative", "ui-patterns"],
    "qt-mapping": ["api-mapping", "implementation"],
    "ai-traps": ["anti-patterns", "common-mistakes"],
    "licensing": ["license", "lgpl", "compliance"],
}

STOP_WORDS = frozenset([
    "the", "a", "an", "is", "are", "not", "and", "or", "for", "in",
    "on", "with", "to", "of", "by", "from", "at", "but", "vs", "it",
    "no", "do", "how", "why", "what", "when", "who", "than", "that",
    "its", "you", "be",
])


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def collect_files():
    """Collect all .md files in ordered categories."""
    files = []

    root_readme = QT_DIR / "README.md"
    if root_readme.exists():
        files.append(("root", root_readme))

    for subdir in ["build-rules", "cpp", "js", "qml", "rust"]:
        dir_path = QT_DIR / subdir
        if not dir_path.is_dir():
            continue
        md_files = sorted(dir_path.glob("*.md"), key=lambda f: f.name)
        readme = dir_path / "README.md"
        ordered = []
        if readme.exists():
            ordered.append(readme)
        ordered.extend(f for f in md_files if f.name != "README.md")
        for f in ordered:
            files.append((subdir, f))

    return files


# ---------------------------------------------------------------------------
# Basic field extraction
# ---------------------------------------------------------------------------

def extract_title(lines):
    """First H1 heading."""
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_subtitle(lines):
    """First blockquote after H1."""
    found_h1 = False
    parts = []
    for line in lines:
        if not found_h1 and line.startswith("# "):
            found_h1 = True
            continue
        if found_h1:
            if line.startswith("> "):
                parts.append(line[2:].strip())
            elif parts:
                break
            elif line.strip() == "":
                continue
            else:
                break
    return " ".join(parts)


def extract_sections(lines):
    """All ## and ### headings."""
    sections = []
    for line in lines:
        m = re.match(r"^(#{2,3})\s+(.+)", line)
        if m:
            sections.append(m.group(2).strip())
    return sections


def extract_rules(lines):
    """Lines starting with RULE: — strip prefix."""
    result = []
    for line in lines:
        s = line.strip()
        if s.startswith("RULE: "):
            result.append(s[6:])
    return result


def extract_banned(lines):
    """Lines starting with BANNED: — strip prefix."""
    result = []
    for line in lines:
        s = line.strip()
        if s.startswith("BANNED: "):
            result.append(s[8:])
    return result


# ---------------------------------------------------------------------------
# Code-block helpers
# ---------------------------------------------------------------------------

def _first_code_line(block_lines):
    """First non-empty, non-comment line from a code block.
    Falls back to first non-empty line if all are comments."""
    first_nonempty = None
    for line in block_lines:
        s = line.strip()
        if not s:
            continue
        if first_nonempty is None:
            first_nonempty = s
        if s.startswith("//") or s.startswith("#") or s.startswith("--"):
            continue
        return s
    return first_nonempty or ""


def _code_blocks_in_section(lines, start_idx):
    """Extract fenced code blocks from start_idx until next heading of same/higher level."""
    heading_match = re.match(r"^(#{1,6})\s+", lines[start_idx])
    if not heading_match:
        return []
    heading_level = len(heading_match.group(1))

    blocks = []
    in_block = False
    current = []

    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        h = re.match(r"^(#{1,6})\s+", line)
        if h and len(h.group(1)) <= heading_level:
            break
        if line.strip().startswith("```"):
            if not in_block:
                in_block = True
                current = []
            else:
                in_block = False
                if current:
                    blocks.append(current)
                current = []
        elif in_block:
            current.append(line)

    return blocks


def _table_column_values(lines, start_idx, heading_level, col_pattern):
    """Extract cleaned cell values from a table column matching col_pattern."""
    values = []
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        h = re.match(r"^(#{1,6})\s+", line)
        if h and len(h.group(1)) <= heading_level:
            break
        if "|" not in line:
            continue
        if not re.search(col_pattern, line, re.IGNORECASE):
            continue
        # Found header row — identify column index
        cells = line.split("|")
        col_idx = None
        for idx, cell in enumerate(cells):
            if re.search(col_pattern, cell, re.IGNORECASE):
                col_idx = idx
                break
        if col_idx is None:
            continue
        # Skip separator row, read data rows
        for j in range(i + 2, len(lines)):
            dline = lines[j]
            if not dline.strip().startswith("|"):
                break
            dcells = dline.split("|")
            if col_idx < len(dcells):
                val = _clean_table_cell(dcells[col_idx])
                if val:
                    values.append(val)
        break
    return values


def _clean_table_cell(cell):
    """Remove markdown backtick formatting from a table cell."""
    cell = cell.strip()
    cell = re.sub(r"`([^`]*)`", r"\1", cell)
    return cell.strip()


# ---------------------------------------------------------------------------
# Anti-pattern / correct-pattern extraction
# ---------------------------------------------------------------------------

_RE_AI_HEADING = re.compile(r"^(#{2,3})\s+.*What AI.*", re.IGNORECASE)
_RE_CORRECT_HEADING = re.compile(
    r"^(#{2,3})\s+(?:What to Write Instead|The Fix|Correct Pattern)",
    re.IGNORECASE,
)


def extract_anti_patterns(lines):
    """Extract anti-patterns from 'What AI ...' heading sections."""
    patterns = []
    for i, line in enumerate(lines):
        m = _RE_AI_HEADING.match(line)
        if not m:
            continue
        heading_level = len(m.group(1))
        blocks = _code_blocks_in_section(lines, i)
        if blocks:
            for block in blocks:
                fcl = _first_code_line(block)
                if fcl:
                    patterns.append(fcl)
        else:
            vals = _table_column_values(
                lines, i, heading_level, r"AI\s*(?:pattern|writes|default)"
            )
            patterns.extend(vals)
    return patterns


def extract_correct_patterns(lines):
    """Extract correct patterns from 'What to Write Instead' / 'The Fix' / 'Correct Pattern' sections."""
    patterns = []
    for i, line in enumerate(lines):
        m = _RE_CORRECT_HEADING.match(line)
        if not m:
            continue
        blocks = _code_blocks_in_section(lines, i)
        for block in blocks:
            fcl = _first_code_line(block)
            if fcl:
                patterns.append(fcl)
    return patterns


def extract_quick_ref_patterns(lines):
    """Extract anti/correct patterns from quick-ref markdown tables."""
    anti = []
    correct = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "|" in line and re.search(r"AI\s+Writes", line, re.IGNORECASE):
            cells = line.split("|")
            ai_col = None
            correct_col = None
            for idx, cell in enumerate(cells):
                if re.search(r"AI\s+Writes", cell, re.IGNORECASE):
                    ai_col = idx
                if re.search(r"Correct", cell, re.IGNORECASE):
                    correct_col = idx
            # Skip separator row
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                dcells = lines[j].split("|")
                if ai_col is not None and ai_col < len(dcells):
                    val = _clean_table_cell(dcells[ai_col])
                    if val:
                        anti.append(val)
                if correct_col is not None and correct_col < len(dcells):
                    val = _clean_table_cell(dcells[correct_col])
                    if val:
                        correct.append(val)
                j += 1
            i = j
            continue
        i += 1
    return anti, correct


# ---------------------------------------------------------------------------
# Cross-references, code languages, Qt APIs
# ---------------------------------------------------------------------------

def extract_refs(text):
    """Cross-referenced .md filenames from markdown links."""
    refs = re.findall(r"\[.*?\]\(([^)]+\.md)\)", text)
    seen = set()
    unique = []
    for ref in refs:
        if ref not in seen:
            seen.add(ref)
            unique.append(ref)
    return unique


def extract_code_languages(text):
    """Language tags from fenced code blocks."""
    langs = re.findall(r"^```(\w+)", text, re.MULTILINE)
    return sorted(set(langs))


def extract_qt_apis(text):
    """Qt API names: Q[A-Z]..., Q_..., cxx-qt attributes."""
    apis = set()
    for m in re.finditer(r"\bQ[A-Z][A-Za-z]{2,}\b", text):
        val = m.group()
        if val != "QML":
            apis.add(val)
    for m in re.finditer(r"\bQ_[A-Z_]{2,}\b", text):
        apis.add(m.group())
    for m in re.finditer(
        r"#\[(cxx_qt::bridge|qobject|qsignal|qproperty|qml_element|qinvokable)\]",
        text,
    ):
        apis.add("#[" + m.group(1) + "]")
    return sorted(apis)


# ---------------------------------------------------------------------------
# Concepts and tags
# ---------------------------------------------------------------------------

def derive_concepts(title, sections, stem):
    """Derive semantic concepts from filename stem and headings."""
    concepts = set()
    key = stem.lower()
    if key in CONCEPT_MAP:
        concepts.update(CONCEPT_MAP[key])
    for word in re.findall(r"[a-z][-a-z]+", title.lower()):
        if word in CONCEPT_MAP:
            concepts.update(CONCEPT_MAP[word])
    for section in sections:
        for word in re.findall(r"[a-z][-a-z]+", section.lower()):
            if word in CONCEPT_MAP:
                concepts.update(CONCEPT_MAP[word])
    return sorted(concepts)


def build_tags(title, qt_apis, code_languages, concepts):
    """Build merged, deduplicated, sorted tag set."""
    tags = set()
    for word in re.findall(r"[a-zA-Z][-a-zA-Z]+", title):
        w = word.lower()
        if len(w) > 2 and w not in STOP_WORDS:
            tags.add(w)
    for api in qt_apis:
        tags.add(api.lower())
    tags.update(code_languages)
    tags.update(concepts)
    return sorted(tags)


# ---------------------------------------------------------------------------
# Main parse
# ---------------------------------------------------------------------------

def parse_file(category, filepath):
    """Parse a single markdown file into a register entry."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    rel_path = filepath.relative_to(QT_DIR).as_posix()

    if filepath.name == "README.md":
        file_type = "readme"
    elif filepath.name == "quick-ref.md":
        file_type = "quick-ref"
    else:
        file_type = "content"

    title = extract_title(lines)
    subtitle = extract_subtitle(lines)
    sections = extract_sections(lines)
    rules = extract_rules(lines)
    banned = extract_banned(lines)

    if file_type == "quick-ref":
        anti_patterns, correct_patterns = extract_quick_ref_patterns(lines)
    else:
        anti_patterns = extract_anti_patterns(lines)
        correct_patterns = extract_correct_patterns(lines)

    refs = extract_refs(text)
    code_languages = extract_code_languages(text)
    has_examples = bool(re.search(r"```\w+", text))
    qt_apis = extract_qt_apis(text)
    concepts = derive_concepts(title, sections, filepath.stem)
    tags = build_tags(title, qt_apis, code_languages, concepts)

    return {
        "file": rel_path,
        "category": category,
        "type": file_type,
        "title": title,
        "subtitle": subtitle,
        "sections": sections,
        "rules": rules,
        "banned": banned,
        "anti_patterns": anti_patterns,
        "correct_patterns": correct_patterns,
        "refs": refs,
        "code_languages": code_languages,
        "has_examples": has_examples,
        "tags": tags,
        "qt_apis": qt_apis,
        "concepts": concepts,
    }


def main():
    files = collect_files()
    entries = []

    for category, filepath in files:
        entry = parse_file(category, filepath)
        entries.append(entry)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    total_rules = sum(len(e["rules"]) for e in entries)
    total_banned = sum(len(e["banned"]) for e in entries)
    total_tags = sum(len(e["tags"]) for e in entries)

    print(f"Wrote {len(entries)} entries to register.jsonl")
    print(
        f"Validation: {len(entries)} entries, "
        f"{total_rules} rules, {total_banned} banned, "
        f"{total_tags} total tags"
    )


if __name__ == "__main__":
    main()
