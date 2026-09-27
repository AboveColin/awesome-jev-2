"""Paths, taxonomy labels, and how one catalogue row is written.

Shared by sections.py (the READMEs) and pages.py (docs/by-pattern/), so a row,
its caveat tags and its display order read the same on both.
"""

from __future__ import annotations

import json
import pathlib

from _github import SELF as REPO

ROOT = pathlib.Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog.json"
PATTERNS_FILE = ROOT / "patterns.json"
RETIRED = ROOT / "retired.json"

REPO_URL = f"https://github.com/{REPO}"
RAW = f"https://raw.githubusercontent.com/{REPO}/main"
SITE = "https://kydlikebtc.github.io/awesome-jev/"


# The taxonomy lives in patterns.json so build_readme, build_assets and the MCP
# server all read one copy. Three embedded copies was three chances to drift.
_PATTERNS = json.loads(PATTERNS_FILE.read_text())["patterns"]
PATTERN_ORDER = [p["key"] for p in _PATTERNS]
PATTERN_LABELS = {
    p["key"]: (p["en"], p["zh"], p["blurb_en"], p["blurb_zh"]) for p in _PATTERNS
}

# Kind and flag labels live in taxonomy.json, which the site also reads at
# runtime. Two embedded copies had already drifted on three flag labels.
_TAXONOMY = json.loads((ROOT / "taxonomy.json").read_text())
KIND_ORDER = [k["key"] for k in _TAXONOMY["kinds"]]
FLAG_ORDER = [f["key"] for f in _TAXONOMY["flags"]]
KIND_LABELS = {
    k["key"]: (k["en"], k["zh"], k["blurb_en"], k["blurb_zh"]) for k in _TAXONOMY["kinds"]
}
FLAG_LABELS = {
    f["key"]: (f["en"], f["zh"], f["blurb_en"], f["blurb_zh"]) for f in _TAXONOMY["flags"]
}

LANG_LABELS = {
    "python": "Py",
    "typescript": "TS",
    "javascript": "JS",
    "go": "Go",
    "rust": "Rs",
    "shell": "sh",
    "java": "Java",
    "ruby": "Rb",
    "php": "PHP",
    "csharp": "C#",
    "elixir": "Ex",
    "lua": "Lua",
    "swift": "Swift",
    "kotlin": "Kt",
    "haskell": "Hs",
    "c": "C",
    "cpp": "C++",
}


def esc(text: str) -> str:
    """Escape what would break a markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ").strip()


def anchor(text: str) -> str:
    """GitHub's heading-to-anchor rule, enough of it for our headings."""
    slug = text.lower()
    slug = "".join(ch for ch in slug if ch.isalnum() or ch in " -_\u4e00-\u9fff")
    return slug.strip().replace(" ", "-")


def label(mapping: dict, key: str, lang: str, *, field: int = 0) -> str:
    entry = mapping.get(key)
    if entry is None:
        raise KeyError(
            f"no display label for {key!r}. Add it to patterns.json or taxonomy.json when you add a schema enum value."
        )
    index = field + (1 if lang == "zh" else 0)
    if index >= len(entry):
        raise KeyError(f"label {key!r} has no field {field} for language {lang!r}")
    return entry[index]


def summary_of(entry: dict, lang: str) -> str:
    text = entry["summary_zh"] if lang == "zh" else entry["summary"]
    if lang == "zh" and entry.get("zh_machine"):
        text += " <sub>(机翻)</sub>"
    return esc(text)


def flags_of(entry: dict, lang: str) -> str:
    tags = [
        f"`{label(FLAG_LABELS, flag, lang)}`"
        for flag in FLAG_ORDER
        if flag in entry.get("flags", [])
    ]
    return " ".join(tags) if tags else "—"


def sort_key(entry: dict) -> tuple:
    """Official first, then rows with code, then stars, then title.

    Slug is the final tie-break. Forks often share a title and a star count
    (several rows are all "jev-mcp" with ★2), and without it their order was
    their position in catalog.json, so re-sorting the file reshuffled the README.
    """
    return (
        not entry.get("official", False),
        not entry.get("has_code", False),
        -(entry.get("stars") or 0),
        entry["title"].lower(),
        entry["slug"],
    )


def entry_list(entries: list[dict], strings: dict, *, notes: bool = False, readme_layout: bool = False) -> list[str]:
    """Render rows as a list rather than a table.

    Tables lose here. GitHub sizes columns by content, so with 148 rows the
    title column gets squeezed until names wrap onto three lines while the
    summary column hogs the width — measured at a 61px median row height and a
    46px title column. A list has no columns to fight over: one line of title
    and summary, one dim line of signals, and long titles simply wrap normally.

    `notes=True` adds the full note as a third line, for the curated sections
    where there are a handful of rows and the note is why the row is there.
    """
    lang = strings["lang_code"]
    if not entries:
        return [strings["no_entries"], ""]

    lines = []
    for entry in sorted(entries, key=sort_key):
        head = f"- **[{esc(entry['title'])}]({entry['url']})**"
        if entry.get("official"):
            head += " ⭐"
        if readme_layout:
            lines.extend([head + "<br>", f"  {summary_of(entry, lang)}<br>"])
        else:
            lines.append(f"{head} — {summary_of(entry, lang)}")

        # Signals go on a dim second line: kind, popularity, author, language,
        # primitives, then caveats last so they read as the final word.
        bits = [f"`{label(KIND_LABELS, entry['kind'], lang)}`"]
        if entry.get("stars") is not None:
            bits.append(f"★{entry['stars']:,}")
        if entry.get("author"):
            bits.append(esc(entry["author"]["name"]))
        for item in entry.get("languages", []):
            bits.append(f"`{LANG_LABELS.get(item, item)}`")
        for item in entry.get("question_types", []):
            bits.append(f"`{item}`")
        flags = [
            f"`{label(FLAG_LABELS, flag, lang)}`"
            for flag in FLAG_ORDER
            if flag in entry.get("flags", [])
        ]
        if flags and not readme_layout:
            bits.append("⚠ " + " ".join(flags))
        lines.append(f"  <sub>{' · '.join(bits)}</sub>")
        if flags and readme_layout:
            caution = "注意" if lang == "zh" else "Caveats"
            lines.extend(["", f"  **{caution}:** " + " · ".join(flags)])

        if notes:
            note = entry.get("notes_zh" if lang == "zh" else "notes")
            if note:
                if readme_layout:
                    lines.extend(["", f"  > {esc(note)}"])
                else:
                    lines.append(f"  <sub>{esc(note)}</sub>")
        lines.append("")
    return lines


def group_by_pattern(catalog: list[dict]) -> dict[str, list[dict]]:
    """Rows per pattern, each list already in display order."""
    by_pattern: dict[str, list[dict]] = {key: [] for key in PATTERN_ORDER}
    for entry in catalog:
        for pattern in entry["patterns"]:
            by_pattern[pattern].append(entry)
    return {key: sorted(rows, key=sort_key) for key, rows in by_pattern.items()}


def page_name(key: str, lang: str) -> str:
    """File name of a pattern's page, mirroring README.md / README.zh-CN.md."""
    return f"{key}.zh-CN.md" if lang == "zh" else f"{key}.md"


def site_link(key: str, lang: str) -> str:
    # The site reads ?p= for the pattern filter and ?lang= for the language, so a
    # reader who came from the Chinese README lands on the Chinese site.
    return f"{SITE}?p={key}&lang={lang}"
