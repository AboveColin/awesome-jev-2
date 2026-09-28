"""docs/by-pattern/: every row of one decision pattern on its own page.

The README shows the first rows of each pattern and links here for the rest.
"""

from __future__ import annotations

import pathlib

from .rows import (
    PATTERN_LABELS,
    ROOT,
    anchor,
    entry_list,
    group_by_pattern,
    label,
    marked,
    page_name,
    site_link,
    split_unindexed,
    stars_note,
    unindexed_note,
)
from .strings import EN, ZH

PAGES_DIR = ROOT / "docs" / "by-pattern"


def render_page(key: str, rows: list[dict], strings: dict) -> str:
    """One pattern's complete list, as its own linkable page."""
    lang = strings["lang_code"]
    name = label(PATTERN_LABELS, key, lang)
    readme = "README.zh-CN.md" if lang == "zh" else "README.md"
    other = page_name(key, "en" if lang == "zh" else "zh")

    out = [
        f"# {name}",
        "",
        f"<sub>[awesome-jev](../../{readme}) · "
        f"{strings['page_other_lang'].format(other=other)}</sub>",
        "",
        f"_{label(PATTERN_LABELS, key, lang, field=2)}_",
        "",
        strings["page_intro"].format(
            n=len(rows),
            readme=f"../../{readme}#{anchor(name)}",
            site=site_link(key, lang),
        ),
        "",
        stars_note(strings, catalog="../../catalog.json"),
        "",
        marked(strings, "call_site_note"),
        "",
    ]
    indexed, later = split_unindexed(rows)
    out.extend(entry_list(indexed, strings))
    if later:
        out += ['<a name="unindexed"></a>', "", f"## {strings['unindexed_h']}", ""]
        out += [
            unindexed_note(
                strings, "unindexed_page", n=len(later),
                patterns="../patterns.md#overview", queue="../review-queue.md#unsorted-overview",
            ),
            "",
        ]
        out.extend(entry_list(later, strings))
    out += ["---", "", strings["page_footer"], ""]
    return "\n".join(out)


def write_pattern_pages(catalog: list[dict]) -> list[pathlib.Path]:
    """Write one page per live pattern per language, and remove any others.

    docs/by-pattern/ belongs to this script and nothing else, so a page for a
    pattern that no longer has entries is deleted rather than left behind. A
    stale page would still be served, still be linked from somewhere, and still
    look authoritative — the same failure as a hand-written count left at 148.
    """
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for key, rows in group_by_pattern(catalog).items():
        if not rows:
            continue
        for strings in (EN, ZH):
            path = PAGES_DIR / page_name(key, strings["lang_code"])
            path.write_text(render_page(key, rows, strings))
            written.append(path)
    for path in PAGES_DIR.glob("*.md"):
        if path not in written:
            path.unlink()
            print(f"removed {path.relative_to(ROOT)}: its pattern has no entries")
    return written
