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
import sys

import _stats

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
            written += 2
    print(f"wrote {written} SVG figures to docs/assets/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
