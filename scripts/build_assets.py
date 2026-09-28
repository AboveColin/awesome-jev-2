#!/usr/bin/env python3
"""Generate the README's SVG figures from catalog.json.

Block characters (█▏▎) were doing this job before. They are fragile: width
depends on the reader's font, they cannot be coloured, and inside a markdown
table the label column gets squeezed until names wrap. A generated SVG renders
identically everywhere, carries colour, and gets the label space it needs.

Two palettes per figure, light and dark, paired with <picture> in the README so
the figure follows GitHub's theme instead of glowing in one of them.

Fonts are generic families only — an SVG referenced through <img> cannot load a
webfont, so anything exotic would silently fall back anyway.

Run: python3 scripts/build_assets.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

import _stats
import picker as picker_rules
from build_readme_cover import text_width

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"
PATTERNS_FILE = ROOT / "patterns.json"
OUT = ROOT / "docs" / "assets"

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

THEMES = {
    "dark": {
        "bg": "none",
        "fg": "#e6edf3",
        "dim": "#8b949e",
        "faint": "#6e7681",
        "rule": "#30363d",
        "track": "#21262d",
        "bar": "#f5a524",
        "bar2": "#8a5d14",
        "ok": "#3fb950",
        "warn": "#f85149",
        "cool": "#58a6ff",
    },
    "light": {
        "bg": "none",
        "fg": "#1f2328",
        "dim": "#59636e",
        "faint": "#818b98",
        "rule": "#d1d9e0",
        "track": "#eef1f4",
        "bar": "#bc7503",
        "bar2": "#e5b45f",
        "ok": "#1a7f37",
        "warn": "#cf222e",
        "cool": "#0969da",
    },
}

# Read from patterns.json rather than embedded, so a new pattern cannot be
# labelled in the README and left unlabelled in the figure.
PATTERNS = [
    (p["key"], p["en"], p["zh"])
    for p in json.loads(PATTERNS_FILE.read_text())["patterns"]
]

STRINGS = {
    "en": {
        "title": "Examples per decision pattern",
        "gap": "no examples yet",
        "sub": "{n} entries · {p} of {t} patterns covered · {d}",
        "prim_title": "What one request returns",
        "state": "state",
        "questions": "questions",
        "req": "one state, many questions — evaluated in parallel",
        # Two layers of evidence under each primitive, never added together.
        "read": "read by a person",
        "signal": "text signal only",
        "rows": "{n} rows",
        "legend": (
            "read by a person: rows whose question_types a person recorded from the code",
            "text signal only: its shape is in the cited file (primitives_seen); no reading records it",
        ),
        # The primitive picker (picker.json): its questions and leaves come from
        # that file; only these frame words live here.
        "pick_title": "Which primitive?",
        "pick_sub": "TypeSafe's own guidance as a decision list: read down, stop at the first yes",
        "pick_yes": "yes",
        "pick_no": "no",
        "pick_pattern": "pattern: {name}",
        "pick_counts": "{read} read by a person · {signal} text signal only",
        "pick_sources": "Sources, as docs.typesafe.ai names each page and heading",
        "pick_legend": (
            "Beside a primitive, rows filed under that pattern: those whose question_types a person "
            "recorded, and those where only the cited file's text shows it (primitives_seen). "
            "Never added together.",
            "Design guidance with its sources, not a recommendation of any catalogued row.",
        ),
        "pick_describe": (
            "Which primitive? A decision list drawn from TypeSafe's documentation. Each yes ends at, "
            "in order: {leaves}. If every answer is no: {last}."
        ),
    },
    "zh": {
        "title": "各决策模式下的例子数",
        "gap": "暂无例子",
        "sub": "{n} 条 · 覆盖 {p}/{t} 个模式 · {d}",
        "prim_title": "一次请求返回什么",
        "state": "状态",
        "questions": "问题",
        "req": "一个 state，多个 question —— 并行求值",
        # Model-written Chinese (I14), marked 机翻 at the end of the legend as
        # the README marks it.
        "read": "人读确认",
        "signal": "仅文本信号",
        "rows": "{n} 条",
        "legend": (
            "人读确认：有人读过代码、记入 question_types 的行",
            "仅文本信号：所引文件含其请求或回答结构（primitives_seen），人读记录中没有它 (机翻)",
        ),
        # Model-written Chinese (I25), marked 机翻 at the end of the legend, as
        # picker.json's own Chinese is marked by its zh_machine.
        "pick_title": "选哪个原语？",
        "pick_sub": "按 TypeSafe 官方文档整理的判断顺序：自上而下，遇到第一个「是」即停",
        "pick_yes": "是",
        "pick_no": "否",
        "pick_pattern": "模式：{name}",
        "pick_counts": "人读确认 {read} 条 · 仅文本信号 {signal} 条",
        "pick_sources": "来源：docs.typesafe.ai 上的页面与小节",
        "pick_legend": (
            "原语旁是归入该模式的行：question_types 中有人记录读到它的行，以及只有所引文件的文本显示它的行"
            "（primitives_seen）。两者从不相加。",
            "这是附有来源的设计指引，不是对任何收录条目的推荐。(机翻)",
        ),
        "pick_describe": (
            "选哪个原语？一份依据 TypeSafe 官方文档整理的判断顺序。每个「是」依次通向：{leaves}。"
            "全部为「否」时：{last}。"
        ),
    },
}

PRIMS = [
    (
        "choice",
        "◆",
        "1 of ≤255",
        "≤255 选项中的 1 个",
        "+ probabilities, confidence",
        "+ 概率分布、置信度",
    ),
    (
        "score",
        "▮",
        "2–10 levels",
        "2–10 个有序级别",
        "+ legend, probabilities, confidence",
        "+ 图例、概率、置信度",
    ),
    (
        "noul",
        "◐",
        "0–1 probability",
        "0–1 概率",
        "no confidence field",
        "不带 confidence 字段",
    ),
]


def picker_file(lang: str, theme: str) -> str:
    """The primitive picker's file name under docs/assets/."""
    return f"primitive-picker-{lang}-{theme}.svg"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def coverage_svg(
    counts: dict[str, int], lang: str, theme: str, total: int, today: str
) -> str:
    c = THEMES[theme]
    s = STRINGS[lang]
    label_w, gutter, bar_w, num_w = 168, 12, 380, 42
    row_h, top = 25, 62
    width = label_w + gutter + bar_w + gutter + num_w + 24
    height = top + len(PATTERNS) * row_h + 18
    peak = max(counts.values(), default=1) or 1
    covered = sum(1 for key, _, _ in PATTERNS if counts.get(key, 0))

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(s["title"])}">',
        f"<style>"
        f".t{{font:600 15px {MONO};fill:{c['fg']}}}"
        f".s{{font:11px {MONO};fill:{c['faint']}}}"
        f".l{{font:12.5px {SANS};fill:{c['dim']}}}"
        f".n{{font:600 12px {MONO};fill:{c['fg']}}}"
        f".g{{font:italic 11px {SANS};fill:{c['faint']}}}"
        f"</style>",
        f'<text x="12" y="22" class="t">{esc(s["title"])}</text>',
        f'<text x="12" y="40" class="s">'
        f"{esc(s['sub'].format(n=total, p=covered, t=len(PATTERNS), d=today))}</text>",
        f'<line x1="12" y1="50" x2="{width - 12}" y2="50" stroke="{c["rule"]}" stroke-width="1"/>',
    ]

    for i, (key, en, zh) in enumerate(PATTERNS):
        name = zh if lang == "zh" else en
        n = counts.get(key, 0)
        y = top + i * row_h
        out.append(f'<text x="12" y="{y + 12}" class="l">{esc(name)}</text>')
        out.append(
            f'<rect x="{label_w}" y="{y + 3}" width="{bar_w}" height="11" rx="1" fill="{c["track"]}"/>'
        )
        if n:
            w = max(round(n / peak * bar_w), 3)
            # Rounded at the data end, square at the baseline.
            out.append(
                f'<path d="M{label_w} {y + 3}h{w - 2}a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-{w - 2}z" '
                f'fill="{c["bar"] if n >= peak * 0.25 else c["bar2"]}"/>'
            )
            out.append(
                f'<text x="{label_w + bar_w + gutter}" y="{y + 13}" class="n">{n}</text>'
            )
        else:
            # Inside the track: an empty bar has the room, and the number
            # column is too narrow for a phrase.
            out.append(
                f'<text x="{label_w + 8}" y="{y + 12}" class="g">{esc(s["gap"])}</text>'
            )
            out.append(
                f'<text x="{label_w + bar_w + gutter}" y="{y + 13}" class="g">0</text>'
            )
    out.append("</svg>")
    return "\n".join(out)


def primitives_svg(lang: str, theme: str, layers: dict[str, dict[str, int]]) -> str:
    """The three primitives and, under each, how many rows a person read
    calling it and how many more only a text signal shows (_stats.primitive_layers)."""
    c = THEMES[theme]
    s = STRINGS[lang]
    width, height = 660, 286
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(s["prim_title"])}">',
        f"<style>"
        f".t{{font:600 15px {MONO};fill:{c['fg']}}}"
        f".g{{font:17px {MONO};fill:{c['ok']}}}"
        f".n{{font:600 14px {MONO};fill:{c['fg']}}}"
        f".d{{font:11.5px {SANS};fill:{c['dim']}}}"
        f".w{{font:11.5px {SANS};fill:{c['warn']}}}"
        f".k{{font:11px {MONO};fill:{c['faint']}}}"
        f".c{{font:600 12px {MONO};fill:{c['fg']}}}"
        f"</style>",
        f'<text x="12" y="21" class="t">{esc(s["prim_title"])}</text>',
        f'<text x="12" y="40" class="k">{esc(s["req"])}</text>',
    ]
    box_w, gap, top, box_h = 206, 15, 58, 172
    for i, (name, glyph, lim_en, lim_zh, note_en, note_zh) in enumerate(PRIMS):
        x = 12 + i * (box_w + gap)
        last = name == "noul"
        counts = layers.get(name, {})
        out += [
            f'<rect x="{x}" y="{top}" width="{box_w}" height="{box_h}" rx="3" '
            f'fill="none" stroke="{c["rule"]}"/>',
            f'<rect x="{x}" y="{top}" width="{box_w}" height="2" '
            f'fill="{c["warn"] if last else c["ok"]}"/>',
            f'<text x="{x + 14}" y="{top + 32}" class="g">{glyph}</text>',
            f'<text x="{x + 14}" y="{top + 58}" class="n">{name}</text>',
            f'<text x="{x + 14}" y="{top + 82}" class="d">'
            f"{esc(lim_zh if lang == 'zh' else lim_en)}</text>",
            f'<text x="{x + 14}" y="{top + 104}" class="{"w" if last else "d"}">'
            f"{esc(note_zh if lang == 'zh' else note_en)}</text>",
            f'<line x1="{x + 14}" y1="{top + 120}" x2="{x + box_w - 14}" y2="{top + 120}" '
            f'stroke="{c["rule"]}" stroke-width="1"/>',
            f'<text x="{x + 14}" y="{top + 140}" class="d">{esc(s["read"])}</text>',
            f'<text x="{x + box_w - 14}" y="{top + 140}" class="c" text-anchor="end">'
            f'{esc(s["rows"].format(n=counts.get("read", 0)))}</text>',
            f'<text x="{x + 14}" y="{top + 160}" class="k">{esc(s["signal"])}</text>',
            f'<text x="{x + box_w - 14}" y="{top + 160}" class="k" text-anchor="end">'
            f'{esc(s["rows"].format(n=counts.get("signal_only", 0)))}</text>',
        ]
    for n, line in enumerate(s["legend"]):
        out.append(f'<text x="12" y="{top + box_h + 22 + n * 17}" class="k">{esc(line)}</text>')
    out.append("</svg>")
    return "\n".join(out)


# ---- the primitive picker (picker.json) -------------------------------------
#
# A decision list, drawn down the left: each question in a box, its yes to the
# right ending at a leaf, its no down to the next question; the last no ends at
# a leaf across the full width. Text is wrapped by measured width
# (build_readme_cover.text_width) and a text that cannot fit fails the build,
# naming itself, instead of running over its box.

PICK_WIDTH = 720
PICK_Q_WIDTH = 296
PICK_GUTTER = 44
PICK_GAP = 26
PICK_LINES = 4
GLYPHS = {name: glyph for name, glyph, *_ in PRIMS}
_CJK_CHAR = "\u3400-\u9fff\u3000-\u303f\uff00-\uffef"
_OPEN, _CLOSE = "「『（“", "，。、；：？！）」』”"
# A CJK character (with any opening mark before it and closing mark after it),
# a run of other characters with its trailing space, or spaces alone: the units
# a line may break between.
_TOKEN = re.compile(
    rf"[{_OPEN}]*[{_CJK_CHAR}][{_CLOSE}]*|[^\s{_CJK_CHAR}]+[{_CLOSE}]*\s*|\s+"
)


class PickerLayoutError(ValueError):
    """A text in picker.json (or a frame string) does not fit its box."""


def wrap(what: str, text: str, width: float, size: float, *, mono: bool = False, bold: bool = False,
         lines: int = PICK_LINES) -> list[str]:
    """`text` broken into lines no wider than `width` px, at most `lines` of them."""
    out, line = [], ""
    for token in _TOKEN.findall(text):
        trial = line + token
        if line.strip() and text_width(trial.rstrip(), size, mono=mono, bold=bold) > width:
            out.append(line.rstrip())
            line = token.lstrip()
        else:
            line = trial
    if line.strip():
        out.append(line.rstrip())
    for piece in out:
        if text_width(piece, size, mono=mono, bold=bold) > width:
            raise PickerLayoutError(
                f"primitive picker: {what} has {piece!r}, about {text_width(piece, size, mono=mono, bold=bold):.0f}px "
                f"with no place to break, in a {width:.0f}px column. Shorten it in picker.json or build_assets.py."
            )
    if len(out) > lines:
        raise PickerLayoutError(
            f"primitive picker: {what} {text!r} takes {len(out)} lines where {lines} fit. "
            "Shorten it in picker.json or build_assets.py."
        )
    return out


def short_url(url: str) -> str:
    return url.removeprefix("https://")


def picker_description(picker: dict, lang: str) -> str:
    """The figure in words, for the README's alt text and the SVG's own label."""
    steps, last = picker_rules.walk(picker)
    sep = "；" if lang == "zh" else "; "
    return STRINGS[lang]["pick_describe"].format(
        leaves=sep.join(leaf[f"label_{lang}"] for _, leaf in steps), last=last[f"label_{lang}"]
    )


def picker_svg(lang: str, theme: str, picker: dict, by_pattern: dict[str, dict[str, dict[str, int]]]) -> str:
    """picker.json as a decision list, with the counts beside each leaf that
    names a primitive and a pattern (_stats.primitive_layers_by_pattern)."""
    c, s = THEMES[theme], STRINGS[lang]
    names = {key: (zh if lang == "zh" else en) for key, en, zh in PATTERNS}
    steps, last = picker_rules.walk(picker)
    number = {url: n for n, url in enumerate(picker_rules.sources(picker), 1)}
    width, qx, qw = PICK_WIDTH, 12, PICK_Q_WIDTH
    lx = qx + qw + PICK_GUTTER
    lw = width - 12 - lx
    body: list[str] = []

    def box(x: float, y: float, w: float, h: float, stripe: str) -> None:
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="none" stroke="{c["rule"]}"/>')
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="2" fill="{stripe}"/>')

    def marker(x: float, y: float, url: str) -> None:
        body.append(f'<text x="{x}" y="{y}" class="k" text-anchor="end">[{number[url]}]</text>')

    def leaf_lines(leaf: dict, w: float) -> tuple[list[str], list[str]]:
        what = f"leaf {leaf['id']!r}"
        note = wrap(f"{what} note_{lang}", leaf[f"note_{lang}"], w - 28, 11.5)
        extra = []
        if leaf.get("pattern_key"):
            extra.append(s["pick_pattern"].format(name=names[leaf["pattern_key"]]))
        counts = picker_rules.layers(leaf, by_pattern)
        if counts is not None:
            extra.append(s["pick_counts"].format(read=counts["read"], signal=counts["signal_only"]))
        for line in extra:
            wrap(f"{what} counts line", line, w - 28, 11, mono=True, lines=1)
        return note, extra

    def draw_leaf(leaf: dict, x: float, y: float, w: float, h: float) -> None:
        primitive = leaf.get("primitive")
        stripe = c["ok"] if primitive else c["bar"] if leaf.get("pattern_key") else c["dim"]
        box(x, y, w, h, stripe)
        label = leaf[f"label_{lang}"]
        wrap(f"leaf {leaf['id']!r} label_{lang}", label, w - 64, 13, bold=True, lines=1)
        glyph = f'<tspan class="g">{GLYPHS[primitive]}</tspan> ' if primitive else ""
        body.append(f'<text x="{x + 14}" y="{y + 22}" class="n">{glyph}{esc(label)}</text>')
        marker(x + w - 12, y + 21, leaf["source_url"])
        note, extra = leaf_lines(leaf, w)
        line_y = y + 22
        for line in note:
            line_y += 15
            body.append(f'<text x="{x + 14}" y="{line_y}" class="d">{esc(line)}</text>')
        for n, line in enumerate(extra):
            line_y += 15
            body.append(f'<text x="{x + 14}" y="{line_y}" class="{"k" if n == 0 else "c"}">{esc(line)}</text>')

    y = 58
    for index, (node, leaf) in enumerate(steps, 1):
        question = wrap(f"node {node['id']!r} question_{lang}", node[f"question_{lang}"], qw - 72, 12.5)
        note, extra = leaf_lines(leaf, lw)
        height = max(22 + len(question) * 16, 22 + (len(note) + len(extra)) * 15) + 12
        box(qx, y, qw, height, c["cool"])
        body.append(f'<text x="{qx + 14}" y="{y + 22}" class="c">{index}</text>')
        for n, line in enumerate(question):
            body.append(f'<text x="{qx + 34}" y="{y + 22 + n * 16}" class="q">{esc(line)}</text>')
        marker(qx + qw - 12, y + 21, node["source_url"])
        # yes: across to the leaf
        mid = y + 18
        body.append(f'<line x1="{qx + qw}" y1="{mid}" x2="{lx - 6}" y2="{mid}" stroke="{c["dim"]}"/>')
        body.append(f'<path d="M{lx - 6} {mid - 4}l6 4-6 4z" fill="{c["dim"]}"/>')
        body.append(f'<text x="{(qx + qw + lx) / 2}" y="{mid - 5}" class="a" text-anchor="middle">{esc(s["pick_yes"])}</text>')
        draw_leaf(leaf, lx, y, lw, height)
        # no: down to the next question, or to the last leaf
        top = y + height
        body.append(f'<line x1="{qx + 24}" y1="{top}" x2="{qx + 24}" y2="{top + PICK_GAP - 6}" stroke="{c["dim"]}"/>')
        body.append(f'<path d="M{qx + 20} {top + PICK_GAP - 6}l4 6 4-6z" fill="{c["dim"]}"/>')
        body.append(f'<text x="{qx + 32}" y="{top + PICK_GAP / 2 + 4}" class="a">{esc(s["pick_no"])}</text>')
        y = top + PICK_GAP

    note, extra = leaf_lines(last, width - 24)
    height = 22 + (len(note) + len(extra)) * 15 + 12
    draw_leaf(last, qx, y, width - 24, height)
    y += height + 26

    body.append(f'<text x="12" y="{y}" class="k">{esc(s["pick_sources"])}</text>')
    for url, n in number.items():
        y += 15
        line = f"[{n}] {short_url(url)}"
        wrap(f"source {url!r}", line, width - 24, 10.5, mono=True, lines=1)
        body.append(f'<text x="12" y="{y}" class="k">{esc(line)}</text>')
    y += 8
    for n, paragraph in enumerate(s["pick_legend"]):
        for line in wrap(f"pick_legend[{n}]", paragraph, width - 24, 11):
            y += 15
            body.append(f'<text x="12" y="{y}" class="l">{esc(line)}</text>')
    height = y + 14

    head = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(picker_description(picker, lang))}">',
        f"<style>"
        f".t{{font:600 15px {MONO};fill:{c['fg']}}}"
        f".k{{font:10.5px {MONO};fill:{c['faint']}}}"
        f".q{{font:12.5px {SANS};fill:{c['fg']}}}"
        f".n{{font:600 13px {SANS};fill:{c['fg']}}}"
        f".g{{fill:{c['ok']}}}"
        f".d{{font:11.5px {SANS};fill:{c['dim']}}}"
        f".c{{font:600 11px {MONO};fill:{c['fg']}}}"
        f".a{{font:italic 11px {SANS};fill:{c['dim']}}}"
        f".l{{font:11px {SANS};fill:{c['faint']}}}"
        f"</style>",
        f'<text x="12" y="22" class="t">{esc(s["pick_title"])}</text>',
        f'<text x="12" y="40" class="k">{esc(s["pick_sub"])}</text>',
    ]
    return "\n".join([*head, *body, "</svg>"])


def main() -> int:
    catalog = json.loads(CATALOG.read_text())
    counts: dict[str, int] = {}
    for entry in catalog:
        for pattern in entry["patterns"]:
            counts[pattern] = counts.get(pattern, 0) + 1

    known = {key for key, _, _ in PATTERNS}
    unknown = set(counts) - known
    if unknown:
        print(
            f"error: catalog uses pattern(s) with no figure label: {sorted(unknown)}. "
            "Add them to PATTERNS in build_assets.py.",
            file=sys.stderr,
        )
        return 1

    today = max((e.get("checked", "") for e in catalog), default="") or ""
    layers = _stats.primitive_layers(catalog)
    picker = picker_rules.load()
    patterns = json.loads(PATTERNS_FILE.read_text())["patterns"]
    by_pattern = _stats.primitive_layers_by_pattern(catalog, patterns)
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    for lang in ("en", "zh"):
        for theme in ("light", "dark"):
            (OUT / f"coverage-{lang}-{theme}.svg").write_text(
                coverage_svg(counts, lang, theme, len(catalog), today)
            )
            (OUT / f"primitives-{lang}-{theme}.svg").write_text(
                primitives_svg(lang, theme, layers)
            )
            (OUT / picker_file(lang, theme)).write_text(picker_svg(lang, theme, picker, by_pattern))
            written += 3
    steps, _ = picker_rules.walk(picker)
    counted = [leaf for _, leaf in steps if picker_rules.layers(leaf, by_pattern) is not None]
    print(f"wrote {written} SVG figures to docs/assets/")
    print(
        f"primitive picker: {len(steps)} questions from picker.json, "
        f"{len(picker_rules.sources(picker))} docs.typesafe.ai sources, counts beside "
        + ", ".join(f"{leaf['primitive']} under {leaf['pattern_key']}" for leaf in counted)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
