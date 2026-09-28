#!/usr/bin/env python3
"""Write docs/shape.md and docs/shape.zh-CN.md: the catalogue's shape as a dataset.

Which languages the rows record, how they reach Jev, star bands by kind,
languages by decision pattern, which patterns are filed together and how the
rows spread over their authors. Every number comes from _stats.shape(), the
one definition counts.py prints too, computed from catalog.json, compat.json,
patterns.json and the entry schema when the pages are written.

The pages describe what this catalogue holds: what the sibling directories
and this repository's discovery found and a person filed. That is not the
ecosystem at large, and each section says what its count can and cannot show.
Stars are printed as bands (readme.rows.STAR_BANDS), a popularity signal and
not a quality verdict, so a count moving inside its band changes nothing here.
No author is named. The Chinese page's prose is model-written and says so at
the top.

Stdlib only, like the rest of scripts/.

Run: python3 scripts/build_shape.py
     python3 scripts/build_shape.py --check    # exit 1 if a page is stale
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import dataclass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import _stats  # noqa: E402
from readme.rows import STAR_BANDS, page_name  # noqa: E402

ROOT = _stats.ROOT
DOCS = ROOT / "docs"
PAGES = {"en": "shape.md", "zh": "shape.zh-CN.md"}
HEADER = (
    "<!-- Written by scripts/build_shape.py from catalog.json, compat.json, patterns.json and the entry schema. "
    "Edit those, not this file. -->"
)

TEXT = {
    "en": {
        "title": "The catalogue's shape",
        "nav": "[awesome-jev](../README.md) · [中文](shape.zh-CN.md)",
        "provenance": "",
        "intro": (
            "Counts that describe this catalogue as a dataset, regenerated from `catalog.json` whenever it "
            "changes; the newest link check behind them is dated **{last_sweep}**. They describe what the "
            "catalogue holds, which is what reached it through the sibling directories, this repository's "
            "discovery and its contributors, not the ecosystem at large. A star band is a popularity signal, not a quality "
            "verdict, and nothing here was run or reproduced by this repository. `python3 scripts/counts.py` "
            "prints the same numbers as text; the headline figures are on [the status page](status.md)."
        ),
        "languages_h": "Languages",
        "languages_intro": (
            "Rows recording each language (`languages`; a row may record several). {none} rows record none."
        ),
        "language": "Language",
        "rows": "Rows",
        "platforms_h": "How rows reach Jev",
        "platforms_intro": (
            "`platforms` records how a row reaches Jev. Discovery does not tag it: "
            "`scripts/discover_candidates.py` and the drafts it writes leave the field to the person adding a "
            "row, and `typesafe-api` is what a row records when nobody named another route. So the first group "
            "below counts that default at least as much as a finding: a row that reaches Jev through a "
            "pass-through may record `typesafe-api` alone ([compatibility](compatibility.md)). Each row counts "
            "in exactly one group."
        ),
        "group": "Group",
        "tiers": {
            "typesafe-api-only": "`typesafe-api` and nothing else",
            "compat-surface": (
                "At least one value another surface in [the compatibility table](compatibility.md) stands for "
                "(a gateway, SDK or framework), and not `self-hosted`"
            ),
            "no-surface": (
                "Besides `typesafe-api`, only values no compatibility surface stands for (a host, tool or "
                "framework the example runs in, or a route that table does not describe), and not `self-hosted`"
            ),
            "self-hosted": "`self-hosted`, whatever else is recorded",
            "none": "No value recorded",
        },
        "values_intro": "Every value rows record, with the compatibility surfaces that stand for it:",
        "value": "Value",
        "surfaces": "Compatibility surface",
        "licences_h": "Licences",
        "licences": (
            "The licences the linked repositories declare are counted on [the sources page](sources.md#licences), "
            "beside what this repository's own licence covers."
        ),
        "stars_h": "Stars by kind",
        "stars_intro": (
            "Rows of each kind per star band, from GitHub's count at the last weekly refresh; a row without a "
            "repository has no count. The median is the band of the middle row (the lower of two). A band is "
            "a popularity signal, not a quality verdict, and says nothing about upkeep."
        ),
        "kind": "Kind",
        "with_stars": "With a star count",
        "under": "under {floor}",
        "median": "Median band",
        "by_pattern_h": "Languages by decision pattern",
        "by_pattern_intro": (
            "Rows per pattern recording each of the {n} most recorded languages; the rest share one column. A "
            "row recording two languages counts in both, and a row filed under two patterns counts in both."
        ),
        "pattern": "Pattern",
        "other_languages": "Other languages",
        "no_language": "None recorded",
        "pairs_h": "Patterns filed together",
        "pairs_intro": (
            "{multi} rows are filed under more than one pattern. The {n} pairs most often filed on the same row:"
        ),
        "pair": "Patterns",
        "authors_h": "Authors",
        "authors": (
            "{rows} rows name an author; they name {authors} different ones, compared by display name without "
            "regard to case. {one} of them have one row here, {two} two, and {many} three or more; the most any "
            "one author has is {most}. No author is named on this page: it shows how concentrated the "
            "catalogue is, not who contributes to it."
        ),
        "footer": (
            "Generated by `scripts/build_shape.py` from `catalog.json`, `compat.json`, `patterns.json` and the "
            "entry schema; edit those, not this page."
        ),
    },
    "zh": {
        "title": "目录的形状",
        "nav": "[awesome-jev](../README.zh-CN.md) · [English](shape.md)",
        "provenance": "> 本页中文说明由模型撰写（机翻），未经人工审校。",
        "intro": (
            "把本目录当作一个数据集来描述的计数，每当 `catalog.json` 变化就重新生成；其背后最新一次链接检查的日期是 "
            "**{last_sweep}**。这些数字描述的是目录收录了什么——即经由兄弟目录、本仓库的发现流程和贡献者进入目录的内容——"
            "而不是整个生态。star 区间是热度信号，不是质量结论；这里的一切都没有被本仓库运行或复现。"
            "`python3 scripts/counts.py` 以文本形式打印同样的数字；主要数字见[状态页](status.md)。"
        ),
        "languages_h": "语言",
        "languages_intro": "记录了每种语言的行数（`languages`；一行可以记录多种语言）。有 {none} 行没有记录语言。",
        "language": "语言",
        "rows": "行数",
        "platforms_h": "各行如何接入 Jev",
        "platforms_intro": (
            "`platforms` 记录一行如何接入 Jev。发现流程不会标注它：`scripts/discover_candidates.py` 及其生成的草稿"
            "都把这个字段留给添加该行的人，而没有人写明其他路径时，一行记录的就是 `typesafe-api`。"
            "所以下面第一组的数字至少同样反映了这个默认值，而不只是发现：经由透传接入 Jev 的行也可能只记录 "
            "`typesafe-api`（见[兼容性](compatibility.md)）。每行恰好计入一组。"
        ),
        "group": "分组",
        "tiers": {
            "typesafe-api-only": "只有 `typesafe-api`",
            "compat-surface": "至少有一个值对应[兼容性表](compatibility.md)中的其他接入面（网关、SDK 或框架），且不含 `self-hosted`",
            "no-surface": (
                "除 `typesafe-api` 外只记录没有任何兼容性接入面对应的值（示例运行所在的主机、工具或框架，"
                "或该表未描述的路径），且不含 `self-hosted`"
            ),
            "self-hosted": "含 `self-hosted`，无论还记录了什么",
            "none": "未记录任何值",
        },
        "values_intro": "各行记录的每个值，以及对应它的兼容性接入面：",
        "value": "值",
        "surfaces": "兼容性接入面",
        "licences_h": "许可证",
        "licences": "被链接仓库声明的许可证统计在[来源页](sources.md#licences)，旁边说明了本仓库自身许可覆盖的范围。",
        "stars_h": "按类型看 star",
        "stars_intro": (
            "每种类型在各 star 区间的行数，取自最近一次每周刷新时 GitHub 的计数；没有仓库的行没有计数。"
            "中位数是居中那一行所在的区间（两行居中时取较低者）。区间是热度信号，不是质量结论，也不说明是否有人维护。"
        ),
        "kind": "类型",
        "with_stars": "有 star 计数",
        "under": "不足 {floor}",
        "median": "中位区间",
        "by_pattern_h": "按决策模式看语言",
        "by_pattern_intro": (
            "每个模式下记录了最常见的 {n} 种语言各自的行数；其余语言合为一列。记录两种语言的行在两列都计数，"
            "归入两个模式的行在两个模式下都计数。"
        ),
        "pattern": "模式",
        "other_languages": "其他语言",
        "no_language": "未记录",
        "pairs_h": "一起归档的模式",
        "pairs_intro": "有 {multi} 行归入了不止一个模式。最常出现在同一行上的 {n} 对模式：",
        "pair": "模式",
        "authors_h": "作者",
        "authors": (
            "有 {rows} 行写明了作者，共 {authors} 位不同的作者（按显示名比较，不区分大小写）。其中 {one} 位在本目录只有一行，"
            "{two} 位有两行，{many} 位有三行或更多；单个作者最多有 {most} 行。本页不列出任何作者的名字："
            "它显示的是目录的集中程度，而不是谁在贡献。"
        ),
        "footer": "由 `scripts/build_shape.py` 根据 `catalog.json`、`compat.json`、`patterns.json` 与条目 schema 生成；请修改这些文件，不要改本页。",
    },
}


@dataclass(frozen=True)
class Inputs:
    """What the pages are built from."""

    catalog: list
    patterns: list
    compat: dict
    schema: dict
    taxonomy: dict


def load() -> Inputs:
    catalog, _retired, patterns, compat, schema = _stats.load()
    taxonomy = json.loads((ROOT / "taxonomy.json").read_text())
    return Inputs(catalog, patterns, compat, schema, taxonomy)


def table(head: list[str], rows: list[list]) -> list[str]:
    cells = [[str(c).replace("|", "\\|") for c in row] for row in rows]
    return ["| " + " | ".join(head) + " |", "|" + "|".join(" --- " for _ in head) + "|"] + [
        "| " + " | ".join(row) + " |" for row in cells
    ]


def band_names(lang: str) -> list[str]:
    """Column names for star band 0 (under the first floor) and each band."""
    return [TEXT[lang]["under"].format(floor=STAR_BANDS[0][0]), *(name for _, name in STAR_BANDS)]


def pattern_name(patterns: list[dict], key: str, lang: str) -> str:
    name = next((p["zh" if lang == "zh" else "en"] for p in patterns if p["key"] == key), key)
    return f"[{name}](by-pattern/{page_name(key, lang)})"


def languages_section(shape: dict, lang: str) -> list[str]:
    text = TEXT[lang]
    out = [f"## {text['languages_h']}", "", text["languages_intro"].format(none=shape["rows_without_language"]), ""]
    return out + table([text["language"], text["rows"]], [[f"`{k}`", n] for k, n in shape["languages"].items()])


def platforms_section(shape: dict, compat: dict, lang: str) -> list[str]:
    text = TEXT[lang]
    out = [f"## {text['platforms_h']}", "", text["platforms_intro"], ""]
    out += table([text["group"], text["rows"]], [[text["tiers"][k], n] for k, n in shape["platform_tiers"].items()])
    claimed: dict[str, list[str]] = {}
    for surface in compat["platforms"]:
        for value in surface.get("catalog_platforms") or []:
            claimed.setdefault(value, []).append(f"`{surface['id']}`")
    out += ["", text["values_intro"], ""]
    rows = [[f"`{value}`", ", ".join(claimed.get(value, [])) or "—", n] for value, n in shape["platforms"].items()]
    return out + table([text["value"], text["surfaces"], text["rows"]], rows)


def stars_section(shape: dict, taxonomy: dict, lang: str) -> list[str]:
    text = TEXT[lang]
    kinds = {k["key"]: k["zh" if lang == "zh" else "en"] for k in taxonomy["kinds"]}
    bands = band_names(lang)
    rows = []
    for kind, row in shape["stars_by_kind"].items():
        if not row["rows"]:
            continue
        median = "—" if row["median_band"] is None else bands[row["median_band"]]
        rows.append([f"{kinds.get(kind, kind)} (`{kind}`)", row["rows"], row["with_stars"], *row["bands"], median])
    head = [text["kind"], text["rows"], text["with_stars"], *bands, text["median"]]
    return [f"## {text['stars_h']}", "", text["stars_intro"], ""] + table(head, rows)


def by_pattern_section(shape: dict, patterns: list[dict], lang: str) -> list[str]:
    text = TEXT[lang]
    top = shape["top_languages"]
    rows = []
    for key, langs in shape["languages_by_pattern"].items():
        other = sum(n for name, n in langs.items() if name not in top)
        rows.append([pattern_name(patterns, key, lang), *(langs.get(name, 0) for name in top), other])
    head = [text["pattern"], *(f"`{name}`" for name in top), text["other_languages"]]
    intro = text["by_pattern_intro"].format(n=len(top))
    return [f"## {text['by_pattern_h']}", "", intro, ""] + table(head, rows)


def pairs_section(shape: dict, patterns: list[dict], lang: str) -> list[str]:
    text = TEXT[lang]
    pairs = shape["pattern_pairs"]
    intro = text["pairs_intro"].format(multi=shape["multi_pattern_rows"], n=len(pairs))
    rows = [[f"{pattern_name(patterns, a, lang)} + {pattern_name(patterns, b, lang)}", n] for a, b, n in pairs]
    return [f"## {text['pairs_h']}", "", intro, ""] + table([text["pair"], text["rows"]], rows)


def authors_section(shape: dict, lang: str) -> list[str]:
    text = TEXT[lang]
    a = shape["authors"]
    body = text["authors"].format(
        rows=a["rows_naming_an_author"], authors=a["authors"], one=a["one_row"], two=a["two_rows"],
        many=a["three_or_more_rows"], most=a["most_rows_by_one_author"],
    )
    return [f"## {text['authors_h']}", "", body]


def render(inputs: Inputs, lang: str) -> str:
    text = TEXT[lang]
    shape = _stats.shape(inputs.catalog, inputs.patterns, inputs.compat, inputs.schema)
    out = [HEADER, "", f"# {text['title']}", "", f"<sub>{text['nav']}</sub>", ""]
    if text["provenance"]:
        out += [text["provenance"], ""]
    out += [text["intro"].format(last_sweep=_stats.newest_check(inputs.catalog)), ""]
    for section in (
        languages_section(shape, lang),
        platforms_section(shape, inputs.compat, lang),
        [f"## {text['licences_h']}", "", text["licences"]],
        stars_section(shape, inputs.taxonomy, lang),
        by_pattern_section(shape, inputs.patterns, lang),
        pairs_section(shape, inputs.patterns, lang),
        authors_section(shape, lang),
    ):
        out += section + [""]
    return "\n".join(out + ["---", "", text["footer"], ""])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="exit 1 instead of writing a stale page")
    args = parser.parse_args(argv)
    inputs = load()
    shape = _stats.shape(inputs.catalog, inputs.patterns, inputs.compat, inputs.schema)
    summary = (
        f"{shape['entries']} rows, {len(shape['languages'])} languages, {len(shape['platforms'])} platform values, "
        f"{shape['authors']['authors']} authors"
    )
    stale = []
    for lang, name in PAGES.items():
        path = DOCS / name
        page = render(inputs, lang)
        if path.exists() and path.read_text() == page:
            continue
        stale.append(name)
        if not args.check:
            path.write_text(page)
    if args.check and stale:
        print(f"error: docs/{' and docs/'.join(stale)} stale; run python3 scripts/build_shape.py ({summary})",
              file=sys.stderr)
        return 1
    print((f"wrote docs/{' and docs/'.join(stale)}" if stale else "docs/shape*.md are current") + f" ({summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
