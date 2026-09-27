#!/usr/bin/env python3
"""Write docs/review-queue.md: the rows a script singles out for a person to read.

Every entry on the page is a machine signal: a path, a string or a combination
of fields matched a rule. None is a finding about the row, and nothing here is
written back into catalog.json. Whoever reads a row records the decision in that
row, as each section says, and the row leaves the page at the next regeneration.

Lint could warn once per row instead, but dozens or hundreds of warnings on
every run is a log nobody reads. The same rules count their rows in
_stats.compute(), so docs/status.md publishes the numbers and this page names
the rows.

One section per signal. A section is a function in SECTIONS that takes the
catalogue and returns a Section; add a function there to add a signal. The
Chinese is model-written, and the page says so once at the top.

Stdlib only, like the rest of scripts/.

Run: python3 scripts/build_review_queue.py
     python3 scripts/build_review_queue.py --check    # exit 1 if the page is stale
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import urllib.parse
from dataclasses import dataclass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import _stats  # noqa: E402
from _github import repo_of  # noqa: E402
from classify import classify_broad, suggest  # noqa: E402
from readme.rows import star_band, star_label  # noqa: E402

ROOT = _stats.ROOT
OUT = ROOT / "docs" / "review-queue.md"
SITE = "https://kydlikebtc.github.io/awesome-jev/"


@dataclass(frozen=True)
class Section:
    """One machine signal and the rows it currently marks."""

    key: str  # the HTML anchor; other pages link to it, so keep it stable
    title_en: str
    title_zh: str
    about_en: str  # what the rule matches, and why that is not a verdict
    about_zh: str
    leave_en: str  # what a person records to take a row off the page
    leave_zh: str
    columns: tuple[tuple[str, str], ...]  # (en, zh) per column
    rows: tuple[tuple[str, ...], ...]  # Markdown cells, one tuple per row


def cell(text: str) -> str:
    """Outside text as an inline code cell: no backtick can close it early,
    no pipe can split the table, no newline can end the row."""
    clean = text.replace("`", "'").replace("\n", " ").replace("|", "\\|")
    return f"`{clean}`"


def row_link(entry: dict) -> str:
    slug = entry["slug"]
    return f"[{slug}]({SITE}?lang=en#{urllib.parse.quote(slug)})"


def file_link(entry: dict) -> str:
    path = entry["evidence"]["path"]
    repo = repo_of(entry)
    if not repo:
        return cell(path)
    return f"[{cell(path)}](https://github.com/{repo}/blob/HEAD/{urllib.parse.quote(path, safe='/')})"


EVIDENCE_COLUMNS = (("Row", "行"), ("Kind", "类型"), ("Cited file", "引用的文件"), ("Matched", "匹配文本"))


def evidence_rows(catalog: list[dict], signal) -> tuple[tuple[str, ...], ...]:
    marked = sorted((e for e in catalog if signal(e)), key=lambda e: e["slug"])
    return tuple(
        (row_link(e), cell(e["kind"]), file_link(e), " ".join(cell(m) for m in e["evidence"]["matched"]))
        for e in marked
    )


def examples_dir(catalog: list[dict]) -> Section:
    return Section(
        key="examples-dir",
        title_en="Evidence read from an examples directory",
        title_zh="证据取自 examples 目录",
        about_en=(
            "The cited file sits under an `examples/` or `example/` directory and the row does not "
            "record `evidence.kind`. An SDK's examples are often its clearest call site; a project's "
            "examples can also be all it has, and say little about how it uses Jev itself. The path "
            "cannot tell which."
        ),
        about_zh=(
            "引用的文件位于 `examples/` 或 `example/` 目录下，而该行没有记录 `evidence.kind`。"
            "SDK 的示例往往就是最清楚的调用点；但一个项目的示例也可能是它仅有的调用，"
            "说明不了它自己如何使用 Jev。单凭路径无法判断是哪一种。"
        ),
        leave_en=(
            "To take a row off, read the file and set `evidence.kind`: `call-site` when it is the "
            "project's own use of Jev, `example-only` when it is only an example. Citing a better "
            "file from the project's own code instead also takes it off."
        ),
        leave_zh=(
            "移出方法：读这个文件，然后设置 `evidence.kind`——它就是项目自身对 Jev 的使用时设为 "
            "`call-site`，只是示例时设为 `example-only`。改为引用项目自身代码中更合适的文件，也会让它移出。"
        ),
        columns=EVIDENCE_COLUMNS,
        rows=evidence_rows(catalog, _stats.examples_unjudged),
    )


def single_model_name(catalog: list[dict]) -> Section:
    names = ", ".join(cell(name) for name in _stats.MODEL_NAMES_AND_HOST)
    return Section(
        key="single-model-name",
        title_en="Evidence resting on one model name or the API host",
        title_zh="证据只靠一个模型名或 API 主机",
        about_en=(
            f"The only string in `evidence.matched` is one of {names}. Any file that configures Jev "
            "contains one of them (a settings file, a pricing table, a model list) whether or not it "
            "calls the API, so the weekly text check can keep passing after the call itself is gone."
        ),
        about_zh=(
            f"`evidence.matched` 里唯一的字符串是 {names} 之一。任何配置 Jev 的文件都会包含它们"
            "（设置文件、价格表、模型列表），不论是否真的调用 API；所以即使调用本身已经删除，"
            "每周的文本检查也可能继续通过。"
        ),
        leave_en=(
            "To take a row off, add a second string from the call itself (an import, the method "
            "called, a question type) to `evidence.matched`, then run "
            "`python3 scripts/verify_claims.py --only <slug>` to confirm the file holds every string."
        ),
        leave_zh=(
            "移出方法：从调用本身再取一个字符串（import、被调用的方法、问题类型）加入 "
            "`evidence.matched`，然后运行 `python3 scripts/verify_claims.py --only <slug>`，"
            "确认文件含有每一个字符串。"
        ),
        columns=EVIDENCE_COLUMNS,
        rows=evidence_rows(catalog, _stats.single_model_name),
    )


def by_band(entries) -> list[dict]:
    """Most-starred band first, then by title: the order a person with an hour
    would read them in. The band, not the count (readme/rows.py STAR_BANDS),
    so the weekly star refresh moves a row only when it crosses a floor."""
    return sorted(entries, key=lambda e: (-star_band(e.get("stars")), e["title"].lower(), e["slug"]))


def patterns_cell(patterns) -> str:
    return " ".join(cell(p) for p in patterns)


def tool_selection_broad_words(catalog: list[dict]) -> Section:
    marked = by_band(e for e in catalog if _stats.tool_selection_broad_only(e))
    return Section(
        key="tool-selection-broad-words",
        title_en="Tool selection resting on words the keyword rules no longer count",
        title_zh="工具选择只靠关键词规则已不再计入的词",
        about_en=(
            "The row carries `tool-selection`, and the keyword rules suggest it for the row's summary "
            "and title only as they stood until 2026-09-27. They then counted \"control\", \"harness\" "
            "and \"screen\" on their own, and \"robot\", \"autonomous\" and \"drive\" with no word for "
            "deciding or acting beside them; the rules in `scripts/classify.py` no longer do. The bulk "
            "passes took the rules' patterns, so a row here may never have been read against "
            "tool-selection, or a person may have agreed with it without recording so. The rules read "
            "a project's GitHub description at discovery; the summary stands in for it here."
        ),
        about_zh=(
            "该行带有 `tool-selection`，而关键词规则只有按 2026-09-27 之前的写法才会从它的摘要和标题建议这个模式。"
            "当时的规则单凭 \"control\"、\"harness\"、\"screen\" 就算数，\"robot\"、\"autonomous\"、"
            "\"drive\" 旁边没有表示决定或动作的词也算数；`scripts/classify.py` 里现在的规则不再这样。"
            "批量收录时直接采用了规则给出的模式，所以这里的行可能从未有人对照 tool-selection 读过，"
            "也可能有人读过并同意，只是没有记录。规则在发现阶段读的是项目的 GitHub 描述；这里以摘要代替。"
        ),
        leave_en=(
            "To take a row off, read the project against [`tool-selection`](patterns.md#tool-selection). "
            "If nothing in it decides which tool or action comes next, replace `tool-selection` in "
            "`patterns` with the pattern it does show, or with `overview`. Either way, set "
            "`patterns_reviewed` to the date you read it; that alone takes off a row whose "
            "`tool-selection` was right."
        ),
        leave_zh=(
            "移出方法：对照 [`tool-selection`](patterns.md#tool-selection) 阅读该项目。"
            "如果其中没有任何东西在决定下一步调用哪个工具或采取哪个动作，就把 `patterns` 里的 `tool-selection` "
            "换成它实际体现的模式，或换成 `overview`。无论哪种情况，都把阅读日期写入 `patterns_reviewed`；"
            "`tool-selection` 本来就对的行，只写这个日期也会移出。"
        ),
        columns=(
            ("Row", "行"),
            ("Stars", "星标"),
            ("Patterns in the row", "该行的模式"),
            ("Suggested until 2026-09-27", "2026-09-27 之前的建议"),
            ("Suggested now", "现在的建议"),
        ),
        rows=tuple(
            (
                row_link(e),
                star_label(e.get("stars")),
                patterns_cell(e["patterns"]),
                patterns_cell(suggest(e, classify_broad)[1]),
                patterns_cell(suggest(e)[1]),
            )
            for e in marked
        ),
    )


def unsorted_overview(catalog: list[dict]) -> Section:
    marked = by_band(e for e in catalog if _stats.not_indexed_by_pattern(e))

    def suggestion(entry: dict) -> str:
        found = suggest(entry)[1]
        return "—" if found == [_stats.OVERVIEW] else patterns_cell(found)

    return Section(
        key="unsorted-overview",
        title_en="Overview rows with code, not yet indexed by pattern",
        title_zh="带代码、尚未按模式索引的 overview 行",
        about_en=(
            "The row is a project or a plugin with code, its only pattern is `overview`, and it records no "
            "`patterns_reviewed`. `overview` is for a row that surveys the model or the space "
            "([patterns.md](patterns.md#overview)); it is also what the keyword rules suggest when nothing "
            "matches, and the bulk passes took the rules' patterns. The READMEs, the Overview page and the "
            "site list these rows apart, as not yet indexed by pattern. The last column is only a "
            "suggestion: what the keyword rules (`scripts/classify.py`) make of the row's summary and "
            "title, and a dash when none of them matches."
        ),
        about_zh=(
            "该行是带代码的项目或插件，唯一的模式是 `overview`，且没有记录 `patterns_reviewed`。"
            "`overview` 本是给介绍模型或整个领域的行用的（[patterns.md](patterns.md#overview)）；"
            "它也是关键词规则什么都没匹配到时给出的建议，而批量收录时直接采用了规则给出的模式。"
            "README、Overview 页面和站点把这些行单独列为“尚未按模式索引”。最后一列只是建议："
            "关键词规则（`scripts/classify.py`）根据该行摘要和标题给出的结果，没有任何规则匹配时显示为破折号。"
        ),
        leave_en=(
            "To take a row off, read the project against [the patterns](patterns.md). Put the patterns it "
            "shows in `patterns`, or keep `overview` if it surveys the space, and set `patterns_reviewed` "
            "to the date you read it."
        ),
        leave_zh=(
            "移出方法：对照[决策模式](patterns.md)阅读该项目。把它体现的模式写进 `patterns`；"
            "如果它确实是在介绍整个领域，就保留 `overview`。然后把阅读日期写入 `patterns_reviewed`。"
        ),
        columns=(
            ("Row", "行"),
            ("Kind", "类型"),
            ("Stars", "星标"),
            ("Keyword rules suggest (a suggestion)", "关键词规则的建议（仅供参考）"),
        ),
        rows=tuple(
            (row_link(e), cell(e["kind"]), star_label(e.get("stars")), suggestion(e)) for e in marked
        ),
    )


SECTIONS = (examples_dir, single_model_name, tool_selection_broad_words, unsorted_overview)

HEADER = "<!-- Written by scripts/build_review_queue.py from catalog.json. Edit those, not this file. -->"
PROVENANCE = (
    "<sub>The Chinese on this page is model-written and has not been reviewed by a person. · "
    "本页中文由模型撰写（机翻），未经人工审校。</sub>"
)
INTRO_EN = (
    "Rows a script has singled out for a person to read. Each entry is a machine signal (a path, "
    "a string or a combination of fields matched a rule), not a finding about the row, and nothing on this page is written "
    "into `catalog.json`. Whoever reads a row records the decision in it, as each section says, and "
    "the row leaves this page when it is next regenerated. [status.md](status.md) publishes the "
    "counts."
)
INTRO_ZH = (
    "脚本挑出、需要人来读的行。每一项都是机器信号（某个路径、字符串或字段组合命中了规则），"
    "不是对该行的结论，本页内容也不会写回 `catalog.json`。读过某一行的人按各节所说把判断记进该行，"
    "下次重新生成时它就会离开本页。数量见 [status.md](status.md)。"
)


def table(columns: tuple[tuple[str, str], ...], rows) -> list[str]:
    head = " | ".join(f"{en} · {zh}" for en, zh in columns)
    return [f"| {head} |", "|" + "|".join(" --- " for _ in columns) + "|"] + [
        "| " + " | ".join(cells) + " |" for cells in rows
    ]


def render(catalog: list[dict]) -> str:
    sections = [build(catalog) for build in SECTIONS]
    out = [HEADER, "", "# Review queue · 复核队列", "", PROVENANCE, "", INTRO_EN, "", INTRO_ZH, ""]
    out += table(
        (("Signal", "信号"), ("Rows", "行数")),
        [(f"[{s.title_en} · {s.title_zh}](#{s.key})", str(len(s.rows))) for s in sections],
    )
    for s in sections:
        out += ["", f'<a id="{s.key}"></a>', "", f"## {s.title_en} · {s.title_zh}", ""]
        out += [s.about_en, "", s.about_zh, "", s.leave_en, "", s.leave_zh, ""]
        out += table(s.columns, s.rows) if s.rows else ["Nothing is on this list. · 此列表为空。"]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="exit 1 instead of writing a stale page")
    args = parser.parse_args(argv)

    catalog = json.loads((ROOT / "catalog.json").read_text())
    text = render(catalog)
    counts = ", ".join(f"{build.__name__}: {len(build(catalog).rows)}" for build in SECTIONS)
    rel = OUT.relative_to(ROOT)
    current = OUT.read_text() if OUT.exists() else None
    if text == current:
        print(f"{rel} is current ({counts})")
        return 0
    if args.check:
        print(f"error: {rel} is stale; run python3 scripts/build_review_queue.py ({counts})", file=sys.stderr)
        return 1
    OUT.write_text(text)
    print(f"wrote {rel} ({counts})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
