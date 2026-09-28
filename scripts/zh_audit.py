#!/usr/bin/env python3
"""Text signals about the machine-translated Chinese summaries, and the queue of
them for a person to replace: docs/zh-queue.md.

Most Chinese summaries were machine-translated in bulk and carry
`zh_machine: true`. Every surface marks them (机翻), but nothing looked at what
the translations say: some keep half a sentence of the English, some drop the
figures a reader would act on. Three rules compare each translation with its
English:

  short    the Chinese has fewer than SHORT_RATIO as many characters as the English;
  numbers  a number the English gives does not appear in the Chinese;
  ascii    more than ASCII_SHARE of the Chinese is ASCII, i.e. mostly untranslated.

Each is a machine signal, not a verdict on a translation. The same rules fire
on some summaries a person wrote (the page counts how often), and a translation
none of them flags can still be wrong. So no README row, pattern page or site
card shows them: those show only the (机翻) mark, which is a fact about who
wrote the Chinese. The page lists every machine translation on a row at ★100 or
more, then the others a signal flags, most-starred band first (the band, not
the count: readme/rows.py STAR_BANDS), and caps the second list at SHOWN rows.

lint.py --base REV asks new_translation_warnings() about the rows a change adds
(rows whose slug catalog.json lacks where this history left REV, see
fork_point), and warns when a machine translation there drops a number. Only
new rows: the rows already filed are this page's business, and a warning
repeated on every run is a log nobody reads.

Names were tried as a fourth rule and dropped (docs/method.md has the numbers).
Capitalised English words missing from the Chinese
(`\\b[A-Z][A-Za-z0-9]{2,}\\b`) flag most summaries a person wrote too, since
every English sentence starts with one. Words with a capital after the first
letter (TypeSafe, MCP, OpenRouter) rarely fire on a person's translation, but
about half of their hits on machine translations leave out nothing except
"TypeSafe" or "AI" from a sentence that still says Jev or 智能体: a translation
style, not a loss.

The functions lint.py uses need nothing outside the standard library. The page
helpers (build_review_queue, readme.rows) are imported inside the functions that
draw the page, because readme.rows reads patterns.json and taxonomy.json when
imported, and a broken label file must reach lint's own report, not stop the
import.

Stdlib only, like the rest of scripts/.

Run: python3 scripts/zh_audit.py            # write docs/zh-queue.md
     python3 scripts/zh_audit.py --check    # exit 1 if the page is stale
     python3 scripts/zh_audit.py --json     # every machine translation's measurements, on stdout
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass

SCRIPTS = pathlib.Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

OUT = ROOT / "docs" / "zh-queue.md"
COMMAND = "python3 scripts/zh_audit.py"

SHORT_RATIO = 0.3  # the median machine translation is about 0.38 of its English
ASCII_SHARE = 0.6
SIGNALS = ("short", "numbers", "ascii")
# The first list takes every machine translation from this band up
# (readme/rows.py STAR_BANDS: 2 is ★100+); the second is capped at SHOWN rows.
MOST_SEEN_BAND = 2
SHOWN = 200
LOST_SHOWN = 6  # numbers printed per row before "…"

# A separator between digit groups: "2 000", "2,000" and "2000" are one number.
# NFKC runs first, so full-width digits and commas and the no-break spaces are
# plain ASCII by then. Exactly three digits must follow, so "4,5" or "1, 2" stay apart.
GROUPED = re.compile(r"(?<=\d)[, ](?=\d{3}(?!\d))")
NUMBER = re.compile(r"\d+(?:\.\d+)*")


def numbers(text: str) -> list[str]:
    """The numbers in a text, in order, each once, with digit groups joined."""
    plain = GROUPED.sub("", unicodedata.normalize("NFKC", text))
    return list(dict.fromkeys(NUMBER.findall(plain)))


def lost_numbers(english: str, chinese: str) -> tuple[str, ...]:
    """Numbers the English gives that the Chinese does not, in English order."""
    kept = set(numbers(chinese))
    return tuple(n for n in numbers(english) if n not in kept)


def text_of(entry: dict, key: str) -> str:
    value = entry.get(key)
    return value if isinstance(value, str) else ""


@dataclass(frozen=True)
class Audit:
    """One row's measurements. `signals` is what the rules make of them."""

    slug: str
    ratio: float  # characters in the Chinese per character of the English
    lost: tuple[str, ...]  # numbers the English gives and the Chinese does not
    ascii: float  # share of the Chinese that is ASCII

    @property
    def signals(self) -> tuple[str, ...]:
        found = (self.ratio < SHORT_RATIO, bool(self.lost), self.ascii > ASCII_SHARE)
        return tuple(name for name, hit in zip(SIGNALS, found) if hit)


def audit(entry: dict) -> Audit:
    english, chinese = text_of(entry, "summary"), text_of(entry, "summary_zh")
    return Audit(
        slug=text_of(entry, "slug") or "?",
        ratio=len(chinese) / max(len(english), 1),
        lost=lost_numbers(english, chinese),
        ascii=sum(ord(ch) < 128 for ch in chinese) / max(len(chinese), 1),
    )


def machine(catalog: list[dict]) -> list[dict]:
    return [e for e in catalog if e.get("zh_machine") is True]


def hand(catalog: list[dict]) -> list[dict]:
    return [e for e in catalog if e.get("zh_machine") is not True]


def tally(entries: list[dict]) -> dict[str, int]:
    """Rows per signal, and rows with any."""
    found = [audit(e).signals for e in entries]
    return {**{name: sum(name in s for s in found) for name in SIGNALS}, "any": sum(bool(s) for s in found)}


# ---- new rows (lint.py --base) -----------------------------------------------


def git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")


def fork_point(rev: str, root: pathlib.Path = ROOT) -> str:
    """Where this checkout's history left REV: `git merge-base REV HEAD`, as
    check_generated.py compares a pull request. On a pull request's merge
    commit in CI that is REV itself (HEAD^1). A row REV gained after the fork
    point is then not taken for one this change adds. REV as given when git
    finds no merge base (unrelated history, or no HEAD yet)."""
    done = git(root, "merge-base", rev, "HEAD")
    return done.stdout.strip() if done.returncode == 0 and done.stdout.strip() else rev


def catalog_at(rev: str, root: pathlib.Path = ROOT) -> tuple[list | None, str]:
    """catalog.json at the fork point from REV (see fork_point), and which
    commit that is; or None and why it cannot be read."""
    commit = fork_point(rev, root)
    done = git(root, "show", f"{commit}:catalog.json")
    if done.returncode:
        return None, (done.stderr.strip().splitlines() or [f"git show exited {done.returncode}"])[-1]
    try:
        data = json.loads(done.stdout)
    except json.JSONDecodeError as exc:
        return None, f"not JSON ({exc})"
    if not isinstance(data, list):
        return None, "not an array of rows"
    return data, commit


def added_rows(catalog: list, base: list) -> list[tuple[int, dict]]:
    """(index, row) for each row of `catalog` whose slug `base` does not have."""
    known = {e.get("slug") for e in base if isinstance(e, dict)}
    return [(i, e) for i, e in enumerate(catalog) if isinstance(e, dict) and e.get("slug") not in known]


def new_translation_warnings(catalog: list, base: list) -> list[tuple[str, str]]:
    """(where, message) for each row `catalog` adds to `base` whose machine
    translation leaves out a number the English gives."""
    found = []
    for i, entry in added_rows(catalog, base):
        if entry.get("zh_machine") is not True:
            continue
        lost = audit(entry).lost
        if lost:
            found.append((
                f"catalog.json[{i}]",
                f"{entry.get('slug', '?')}: new row whose machine-translated summary_zh leaves out "
                f"{', '.join(lost)} from the English summary; put the missing numbers in the Chinese too, unless "
                f"they do not belong there (a text comparison by {COMMAND}, not a reading)",
            ))
    return found


def new_rows_since(catalog: list, rev: str, root: pathlib.Path = ROOT) -> tuple[list[tuple[str, str]], str]:
    """new_translation_warnings() against catalog.json where this history left
    REV, and one line for the log saying what was compared."""
    base, commit = catalog_at(rev, root)
    if base is None:
        return [], f"no new-row translation warnings; catalog.json at {rev} cannot be read: {commit}"
    found = new_translation_warnings(catalog, base)
    added = added_rows(catalog, base)
    machine = sum(1 for _, e in added if e.get("zh_machine") is True)
    return found, (
        f"{len(added)} row(s) added since {rev} ({commit[:12]}), {machine} with a machine-translated "
        f"summary_zh; {len(found)} leave out a number the English gives"
    )


# ---- the page ----------------------------------------------------------------

HEADER = "<!-- Written by scripts/zh_audit.py from catalog.json. Edit those, not this file. -->"
PROVENANCE = (
    "<sub>The Chinese on this page is model-written and has not been reviewed by a person. · "
    "本页中文由模型撰写（机翻），未经人工审校。</sub>"
)
CLAIM = "../CONTRIBUTING.md#claim-a-translation"


def rules() -> tuple[tuple[str, str, str], ...]:
    """(signal, rule in English, rule in Chinese)."""
    short, share = f"{SHORT_RATIO:.0%}", f"{ASCII_SHARE:.0%}"
    return (
        (
            "short",
            f"The Chinese has fewer than {short} as many characters as the English.",
            f"中文的字符数不到英文的 {short}。",
        ),
        (
            "numbers",
            "A number the English gives does not appear in the Chinese. Digit groups are joined "
            "first, so 2 000, 2,000 and 2000 are one number; a number written out in words is not read.",
            "英文给出的某个数字在中文里找不到。比较前先合并数字分组，所以 2 000、2,000 与 2000 "
            "算同一个数；用文字写出的数不计。",
        ),
        (
            "ascii",
            f"More than {share} of the Chinese is ASCII (Latin letters, digits, spaces and ASCII "
            "punctuation): mostly left untranslated.",
            f"中文摘要里超过 {share} 的字符是 ASCII（拉丁字母、数字、空格与 ASCII 标点），大部分没有翻译。",
        ),
    )


def queue_order(entries: list[dict]) -> list[dict]:
    """Most-starred band first, then the rows more signals flag, then by title."""
    from readme.rows import star_band

    return sorted(
        entries,
        key=lambda e: (-star_band(e.get("stars")), -len(audit(e).signals), e["title"].lower(), e["slug"]),
    )


def two_places(value: float, *, up: bool) -> str:
    """A share to two places, rounded away from its rule's threshold, so a
    0.2996 flagged as below 0.3 never prints as 0.30 (nor a 0.6004 above 0.6
    as 0.60)."""
    scaled = value * 100
    return f"{(math.ceil(scaled) if up else math.floor(scaled)) / 100:.2f}"


def signals_cell(found: Audit) -> str:
    from build_review_queue import cell

    parts = []
    if "short" in found.signals:
        parts.append(f"{cell('short')} {two_places(found.ratio, up=False)}")
    if found.lost:
        shown = " ".join(cell(n) for n in found.lost[:LOST_SHOWN])
        parts.append(f"{cell('numbers')} {shown}{' …' if len(found.lost) > LOST_SHOWN else ''}")
    if "ascii" in found.signals:
        parts.append(f"{cell('ascii')} {two_places(found.ascii, up=True)}")
    return " · ".join(parts) or "—"


def rows_table(entries: list[dict]) -> list[str]:
    from build_review_queue import row_link, table
    from readme.rows import star_label

    return table(
        (("Row", "行"), ("Stars", "星标"), ("Signals", "信号")),
        [(row_link(e), star_label(e.get("stars")), signals_cell(audit(e))) for e in entries],
    )


def split(catalog: list[dict]) -> tuple[list[dict], list[dict]]:
    """(every machine translation at MOST_SEEN_BAND or above, the other flagged ones), each in queue order."""
    from readme.rows import star_band

    ordered = queue_order(machine(catalog))
    top = [e for e in ordered if star_band(e.get("stars")) >= MOST_SEEN_BAND]
    rest = [e for e in ordered if star_band(e.get("stars")) < MOST_SEEN_BAND and audit(e).signals]
    return top, rest


def render(catalog: list[dict]) -> str:
    from build_review_queue import table
    from readme.rows import STAR_BANDS

    top, rest = split(catalog)
    band = STAR_BANDS[MOST_SEEN_BAND - 1][1]
    ours, theirs = machine(catalog), hand(catalog)
    counted_ours, counted_theirs = tally(ours), tally(theirs)
    shown = rest[:SHOWN]

    out = [HEADER, "", "# Translation queue · 翻译队列", "", PROVENANCE, ""]
    out += [
        f"Chinese summaries a model translated (`zh_machine: true`), for a person to replace with a "
        f"translation of their own. {len(ours)} of the catalogue's {len(catalog)} rows have one; "
        f"{len(theirs)} have a Chinese summary a person wrote. Rows more readers see come first: every "
        f"machine translation on a row at {band}, then the others at least one signal flags, most-starred "
        "band first. A signal is a text comparison a script makes between a translation and its English, "
        "not a verdict on the translation: the table below counts how often each also fires on a summary "
        "a person wrote, and a translation none of them flags can still be wrong. No README row, pattern "
        "page or site card shows the signals; they show only the `(机翻)` mark. To take some rows, see "
        f"[Claim a translation]({CLAIM}). A row leaves this page when a translation a person wrote "
        "replaces its Chinese and `zh_machine` comes off.",
        "",
        f"由模型翻译的中文摘要（`zh_machine: true`），等待有人换成自己的译文。目录 {len(catalog)} 行中有 "
        f"{len(ours)} 行是机翻，{len(theirs)} 行的中文摘要由人撰写。看到的读者越多越靠前：先列出 {band} "
        "各行的全部机翻，再按星标区间从高到低列出至少被一项信号标出的其他机翻。信号是脚本把译文与英文对照"
        "得出的文本比较，不是对译文的结论：下表列出每项信号在人写摘要上同样触发的次数，而没有被任何信号"
        "标出的译文也可能有错。README 各行、模式页面和站点卡片都不显示这些信号，只显示 `(机翻)` 标记。"
        f"认领方法见[认领翻译]({CLAIM})。当一行的中文换成人写的译文、并去掉 `zh_machine` 后，它就会离开本页。",
        "",
    ]
    out += table(
        (("Signal", "信号"), ("Rule", "规则"), ("Machine translations", "机翻"), ("Written by a person", "人写")),
        [
            (f"`{name}`", f"{en} · {zh}", f"{counted_ours[name]} of {len(ours)}", f"{counted_theirs[name]} of {len(theirs)}")
            for name, en, zh in rules()
        ]
        + [("any · 任一", "At least one of the three. · 三项中至少一项。",
            f"{counted_ours['any']} of {len(ours)}", f"{counted_theirs['any']} of {len(theirs)}")],
    )
    out += ["", '<a id="most-starred"></a>', "", f"## Every machine translation at {band} · {band} 的全部机翻", ""]
    out += [
        f"{len(top)} rows, most-starred band first, then the rows more signals flag. A dash means no "
        "signal fires, not that the translation is right. · "
        f"共 {len(top)} 行，按星标区间从高到低，再按命中信号的多少排列。破折号表示没有信号触发，不代表译文无误。",
        "",
    ]
    out += rows_table(top) if top else ["Nothing is on this list. · 此列表为空。"]
    out += ["", '<a id="flagged"></a>', "", "## Other machine translations a signal flags · 被信号标出的其他机翻", ""]
    out += [
        f"{len(rest)} rows below {band}, in the same order. · 共 {len(rest)} 行，低于 {band}，顺序同上。",
        "",
    ]
    out += rows_table(shown) if shown else ["Nothing is on this list. · 此列表为空。"]
    if len(rest) > len(shown):
        more = len(rest) - len(shown)
        out += [
            "",
            f"…and {more} more, in the same order; `{COMMAND} --json` lists every machine translation. · "
            f"另有 {more} 行未列出，顺序相同；`{COMMAND} --json` 会列出全部机翻。",
        ]
    return "\n".join(out) + "\n"


def report(catalog: list[dict]) -> dict:
    """What --json prints: the rules, the counts, and every machine translation in queue order."""
    from readme.rows import star_label

    return {
        "rules": {name: en for name, en, _ in rules()},
        "machine": {"rows": len(machine(catalog)), **tally(machine(catalog))},
        "hand": {"rows": len(hand(catalog)), **tally(hand(catalog))},
        "rows": [
            {
                "slug": found.slug,
                "stars": star_label(e.get("stars")),
                "signals": list(found.signals),
                "ratio": round(found.ratio, 3),
                "lost": list(found.lost),
                "ascii": round(found.ascii, 3),
            }
            for e in queue_order(machine(catalog))
            for found in (audit(e),)
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="exit 1 instead of writing a stale page")
    mode.add_argument("--json", action="store_true", help="print every machine translation's measurements")
    args = parser.parse_args(argv)

    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    if args.json:
        json.dump(report(catalog), sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    from readme.rows import STAR_BANDS

    top, rest = split(catalog)
    counted = tally(machine(catalog))
    band = STAR_BANDS[MOST_SEEN_BAND - 1][1]
    counts = (
        f"{len(machine(catalog))} machine translations; "
        + ", ".join(f"{name} {counted[name]}" for name in (*SIGNALS, "any"))
        + f"; listed {len(top)} at {band} and {min(len(rest), SHOWN)} of {len(rest)} flagged below it"
    )
    text = render(catalog)
    rel = OUT.relative_to(ROOT)
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if text == current:
        print(f"{rel} is current ({counts})")
        return 0
    if args.check:
        print(f"error: {rel} is stale; run {COMMAND} ({counts})", file=sys.stderr)
        return 1
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {rel} ({counts})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
