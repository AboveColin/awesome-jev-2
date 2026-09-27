"""Paths, taxonomy labels, and how one catalogue row is written.

Shared by sections.py (the READMEs) and pages.py (docs/by-pattern/), so a row,
its caveat tags and its display order read the same on both.
"""

from __future__ import annotations

import json
import pathlib

import _stats
from _github import SELF as REPO

from .strings import ZH_MACHINE

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
SUMMARY_SOURCE_LABELS = {
    s["key"]: (s["en"], s["zh"], s["blurb_en"], s["blurb_zh"]) for s in _TAXONOMY["summary_sources"]
}
# summary_source values a summary is marked with wherever it is shown: the
# project's own words. `curated` is how a list is read anyway, so it gets none.
MARKED_SOURCES = ("upstream-description", "upstream-description-stale")

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
    """The row's summary with its provenance marks: whose words it is
    (summary_source), then, for Chinese, whether a model translated it."""
    text = entry["summary_zh"] if lang == "zh" else entry["summary"]
    source = entry.get("summary_source")
    if source in MARKED_SOURCES:
        text += f" <sub>({label(SUMMARY_SOURCE_LABELS, source, lang)})</sub>"
    if lang == "zh" and entry.get("zh_machine"):
        text += " <sub>(机翻)</sub>"
    return esc(text)


def source_marks(lang: str) -> dict[str, str]:
    """The two marks by name, for the sentences that explain them."""
    return {
        "upstream_mark": label(SUMMARY_SOURCE_LABELS, MARKED_SOURCES[0], lang),
        "stale_mark": label(SUMMARY_SOURCE_LABELS, MARKED_SOURCES[1], lang),
    }


# Stars print as a band, never as the count, and rows sort by the band. The
# weekly refresh re-reads every count; printed and sorted exactly, one refresh
# rewrote over a thousand generated lines (b8bae37: 220 rows, every one of them a
# star count only, 32 generated files) and reordered rows on the pattern pages,
# for a precision no reader of a list needs. Now only a row that crosses a floor
# changes a line.
# catalog.json keeps the exact count, and the site and the MCP server show and
# sort by it. Floors low to high; a count under the first prints nothing.
STAR_BANDS = (
    (10, "★10+"),
    (100, "★100+"),
    (1_000, "★1k+"),
    (10_000, "★10k+"),
    (100_000, "★100k+"),
)


def star_band(stars: int | None) -> int:
    """How many band floors the count reaches: 0 (none, or under 10) to 5."""
    return sum(1 for floor, _ in STAR_BANDS if (stars or 0) >= floor)


def star_label(stars: int | None) -> str:
    """The band as a list prints it, e.g. "★1k+"; empty under the first floor."""
    band = star_band(stars)
    return STAR_BANDS[band - 1][1] if band else ""


def stars_note(strings: dict, *, catalog: str) -> str:
    """The sentence that says what a band is and how rows are ordered.

    `catalog` is the relative link to catalog.json from the page it goes on.
    """
    lang = strings["lang_code"]
    labels = [label_ for _, label_ in STAR_BANDS]
    bands = strings["list_sep"].join(labels[:-1]) + strings["list_and"] + labels[-1]
    note = strings["stars_note"].format(
        bands=bands, floor=STAR_BANDS[0][0], catalog=catalog, site=f"{SITE}?lang={lang}"
    )
    if lang == "zh" and "stars_note" in ZH_MACHINE:
        note += " <sub>(机翻)</sub>"
    return note


def sort_key(entry: dict) -> tuple:
    """Official first, then rows with code, then star band, then title.

    The band, not the count (see STAR_BANDS): inside a band rows go by title,
    so a count that moves inside its band moves no row.

    Slug is the final tie-break. Forks often share a title and a band (several
    rows are all "jev-mcp" with a handful of stars), and without it their order
    was their position in catalog.json, so re-sorting the file reshuffled the
    README.
    """
    return (
        not entry.get("official", False),
        not entry.get("has_code", False),
        -star_band(entry.get("stars")),
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
        stars = star_label(entry.get("stars"))
        if stars:
            bits.append(stars)
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


def split_unindexed(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """A pattern's rows, and apart from them the ones not yet indexed by pattern.

    Only an overview listing has any (_stats.not_indexed_by_pattern): projects
    and plugins with code filed under overview with no reading recorded. They
    stay under overview in catalog.json; a list shows them last, under their
    own heading, so that a reader browsing by pattern does not take "the rules
    placed nothing here" for "this surveys the space". Both keep their order.
    """
    later = [entry for entry in rows if _stats.not_indexed_by_pattern(entry)]
    return [entry for entry in rows if not _stats.not_indexed_by_pattern(entry)], later


def unindexed_note(strings: dict, key: str, **values: object) -> str:
    """The paragraph under a "not yet indexed by pattern" heading (`key` is
    unindexed_readme or unindexed_page), marked where a model wrote the Chinese."""
    note = strings[key].format(**values)
    if strings["lang_code"] == "zh" and key in ZH_MACHINE:
        note += " <sub>(机翻)</sub>"
    return note


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
