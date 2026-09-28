#!/usr/bin/env python3
"""Generate the tables in docs/compatibility.md from compat.json.

The platform matrix is the repo's most-cited original asset, so it follows the
same rule as the catalog: one machine-readable source, generated presentation.
The site reads the same compat.json, which means the doc and the site cannot
drift apart — the failure mode that would quietly make the matrix useless.

Only the regions between the markers below are rewritten; the prose around
them is hand-written and left alone. One inline value, `<!--n:as_of-->`, is
compat.json's `as_of`: the day a person last read every platform's page. It is
written as that date, never as an age, which would be wrong a day later; the
weekly claims run reports how old it is.

Run: python3 scripts/build_compat.py
     python3 scripts/build_compat.py --check    # CI: fail if out of date
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _markers import normalise, replace_block, replace_inline  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
COMPAT = ROOT / "compat.json"
DOC = ROOT / "docs" / "compatibility.md"

# Each block is (marker-name, header row, row builder). A dash in the data
# means the surface does not expose that concept, and is printed as-is.
BLOCKS = {
    "models": (
        ["Surface", "Model string to send"],
        lambda p: [link(p), code_list(p["model"])],
    ),
    "yesno": (
        ["Surface", "Type name", "Read the answer from"],
        lambda p: [link(p), code(p["yesno"]), code(p["answer_field"])],
    ),
    "confidence": (
        ["Surface", "Where `choice` / `score` confidence lives"],
        lambda p: [link(p), p["confidence"]],
    ),
    "envelope": (
        ["Surface", "Request shape", "Endpoint"],
        lambda p: [link(p), p["envelope"], code(p["endpoint"])],
    ),
    "env": (
        ["Surface", "Environment variable"],
        lambda p: [link(p), code(p["env"])],
    ),
    "notes": (
        ["Surface", "Worth knowing"],
        lambda p: [link(p), p.get("notes", "—")],
    ),
}


def code(value: str) -> str:
    return "—" if value.strip() == "—" else f"`{value}`"


def code_list(value: str) -> str:
    """Wrap each of several dot-separated names in its own backticks."""
    if value.strip() == "—":
        return "—"
    return " · ".join(f"`{part.strip()}`" for part in value.split("·"))


def link(platform: dict) -> str:
    name = platform["name"]
    if platform.get("official"):
        name += " ⭐"
    url = platform.get("url")
    return f"[{name}]({url})" if url else name


def table(header: list[str], rows: list[list[str]]) -> list[str]:
    out = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join(" --- " for _ in header) + "|",
    ]
    out += [
        "| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |"
        for row in rows
    ]
    return out


def limits_table(limits: list[dict]) -> list[str]:
    rows = [[f"**{item['k']}**", item["v"], item["why"]] for item in limits]
    return table(["", "Limit", "Why it matters"], rows)


def build(data: dict | None = None, text: str | None = None) -> str:
    """docs/compatibility.md regenerated from compat.json (or from `data`,
    applied to `text`: lint_docs.py's release rehearsal renders a compat.json
    that does not exist yet)."""
    data = json.loads(COMPAT.read_text()) if data is None else data
    platforms = data["platforms"]
    text = DOC.read_text() if text is None else text

    for name, (header, row_of) in BLOCKS.items():
        body = "\n".join(table(header, [row_of(p) for p in platforms]))
        text = replace_block(text, name, body, where="docs/compatibility.md")

    if "<!-- limits:start -->" in text:
        body = "\n".join(limits_table(data["limits"]))
        text = replace_block(text, "limits", body, where="docs/compatibility.md")

    return replace_inline(text, {"as_of": data["as_of"]}, where="docs/compatibility.md")



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail instead of writing")
    args = parser.parse_args()

    rendered = build()
    current = DOC.read_text()

    if rendered == current:
        print("docs/compatibility.md is up to date")
        return 0
    if normalise(rendered) == normalise(current):
        print("docs/compatibility.md is up to date (formatting differs, data matches)")
        return 0
    if args.check:
        print(
            "error: docs/compatibility.md is out of sync with compat.json.\n"
            "Run 'python3 scripts/build_compat.py' and commit the result.",
            file=sys.stderr,
        )
        return 1

    DOC.write_text(rendered)
    data = json.loads(COMPAT.read_text())
    print(
        f"wrote docs/compatibility.md from {len(data['platforms'])} platforms "
        f"and {len(data['limits'])} limits"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
