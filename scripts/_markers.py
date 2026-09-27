"""Rewrite generated regions inside otherwise hand-written files.

Two shapes, both invisible once Markdown or HTML is rendered:

  Block — a whole region is generated (a table, a list, a group of tags):

      <!-- name:start -->
      ...generated...
      <!-- name:end -->

  Inline — one value inside a hand-written sentence:

      Fourteen became <!--n:no_licence-->171<!--/n--> linked projects.

Extracted from build_compat.py so that it and build_docs.py share one
implementation. Two copies of "find the markers, splice the body" would be two
chances for one of them to silently stop matching.
"""

from __future__ import annotations

import re

INLINE = re.compile(r"<!--n:([a-z_]+)-->(.*?)<!--/n-->", re.S)


def replace_block(text: str, name: str, body: str, *, where: str) -> str:
    """Replace everything between a block's markers. Missing markers are fatal:
    a generator that silently skips a region is how a stale table survives."""
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if start not in text or end not in text:
        raise SystemExit(f"error: {where} is missing the {start} / {end} markers")
    head, _, rest = text.partition(start)
    _, _, tail = rest.partition(end)
    # The end marker keeps the start marker's indentation, so a block nested
    # inside indented HTML closes where it opened.
    indent = head[len(head.rstrip(" \t")) :] if "\n" in head else ""
    return f"{head}{start}\n{body}\n{indent}{end}{tail}"


def read_block(text: str, name: str, *, where: str) -> str:
    """The body between a block's markers, as written. Missing markers are
    fatal for the same reason as in replace_block."""
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if start not in text or end not in text:
        raise SystemExit(f"error: {where} is missing the {start} / {end} markers")
    return text.partition(start)[2].partition(end)[0]


def replace_inline(text: str, values: dict[str, object], *, where: str) -> str:
    """Refill every inline marker. An unknown key is fatal for the same reason."""

    def fill(match: re.Match) -> str:
        key = match.group(1)
        if key not in values:
            raise SystemExit(f"error: {where} uses unknown inline value `{key}`")
        return f"<!--n:{key}-->{values[key]}<!--/n-->"

    return INLINE.sub(fill, text)


def normalise(text: str) -> str:
    """Collapse table cell padding so a check compares data, not formatting.

    A markdown formatter will happily pad every pipe to align columns, which is
    harmless but byte-different from what a generator emits. Without this, CI
    would fail for a contributor whose editor runs prettier — a false alarm that
    teaches people to ignore the check. Real data drift still fails.
    """
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            # A separator row is only dashes and colons; length is cosmetic.
            cells = ["-" if set(c) <= set("-: ") and c else c for c in cells]
            lines.append("|" + "|".join(cells) + "|")
        else:
            lines.append(stripped)
    return "\n".join(lines)
