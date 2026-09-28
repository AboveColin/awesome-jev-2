"""The pages a README section links for the rest of its rows.

docs/by-pattern/ holds every row of one decision pattern on its own page, and
docs/measured.md (with docs/measured.zh-CN.md) every independent measurement
report. The README shows the first rows of each and links here for the rest.
"""

from __future__ import annotations

import pathlib

from .rows import (
    PATTERN_LABELS,
    ROOT,
    anchor,
    collection_link,
    direction_bit,
    direction_note,
    entry_list,
    group_by_pattern,
    is_measured,
    is_negative,
    negatives_link,
    sort_key,
    label,
    marked,
    measured_page,
    page_name,
    reports_link,
    site_link,
    split_unindexed,
    stars_note,
    unindexed_note,
)
from .strings import EN, ZH

DOCS_DIR = ROOT / "docs"
PAGES_DIR = DOCS_DIR / "by-pattern"


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
    if any(direction_bit(entry, strings) for entry in rows):
        out += [direction_note(strings, docs="../"), ""]
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


def render_measured_page(rows: list[dict], strings: dict) -> str:
    """Every independent measurement report and negative result, with every
    note and caveat tag.

    Laid out as the README's section used to print them all (the note is why a
    report is worth reading), with the section's own caveat that the
    measurements are their authors'. The negative results come first, under
    their own heading, then the rest, each in list order.
    """
    lang = strings["lang_code"]
    readme = "README.zh-CN.md" if lang == "zh" else "README.md"
    other = measured_page("en" if lang == "zh" else "zh")
    out = [
        f"# {strings['measured_h']}",
        "",
        f"<sub>[awesome-jev](../{readme}) · {strings['page_other_lang'].format(other=other)}</sub>",
        "",
        strings["measured_intro"],
        "",
        marked(
            strings, "measured_page_intro", n=len(rows), readme=f"../{readme}#{anchor(strings['measured_h'])}",
            path=collection_link("measured", lang), site=reports_link(lang),
        ),
        "",
        stars_note(strings, catalog="../catalog.json"),
        "",
        marked(strings, "call_site_note"),
        "",
    ]
    if any(direction_bit(entry, strings) for entry in rows):
        out += [direction_note(strings, docs=""), ""]
    negatives = sorted((entry for entry in rows if is_negative(entry)), key=sort_key)
    rest = sorted((entry for entry in rows if not is_negative(entry)), key=sort_key)
    if negatives:
        out += [f"## {strings['negative_h']}", "", marked(strings, "negative_note", site=negatives_link(lang)), ""]
        out.extend(entry_list(negatives, strings, notes=True, readme_layout=True, keep_order=True))
        out += [f"## {strings['others_h']}", ""] if rest else []
    out.extend(entry_list(rest, strings, notes=True, readme_layout=True, keep_order=True) if rest else [])
    out += ["---", "", strings["page_footer"], ""]
    return "\n".join(out)


def write_measured_pages(catalog: list[dict]) -> list[pathlib.Path]:
    """Write docs/measured.md and docs/measured.zh-CN.md, or remove them when
    the catalogue holds no independent report (the README then has no section
    to link them from)."""
    rows = [entry for entry in catalog if is_measured(entry)]
    written = []
    for strings in (EN, ZH):
        path = DOCS_DIR / measured_page(strings["lang_code"])
        if rows:
            path.write_text(render_measured_page(rows, strings))
            written.append(path)
        elif path.exists():
            path.unlink()
            print(f"removed {path.name} from docs/: the catalogue has no independent measurement report")
    return written
