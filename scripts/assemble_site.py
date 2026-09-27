#!/usr/bin/env python3
"""Assemble site/ for publishing: copy in the data, and write stats.json.

The same step for the Pages deploy and for a local preview, so the two cannot
differ. The list of runtime files lives here and nowhere else: pages.yml used to
spell out the copies while check_site_data.py kept its own list, which is how
site/compat.json once went unignored while site/catalog.json was.

stats.json is _stats.compute() — the definitions the README badges and the docs
use. The site's headline figures and the live social card both read it, rather
than each recounting "link-verified" in JavaScript.

`--deploy` also writes the link-preview tags (description, og:*, twitter:card)
into site/index.html, between its `meta` markers. They quote the catalogue
size, so until 2026-09-27 build_docs.py rewrote them in git and every pull
request adding a row had to carry a changed site/index.html. Git now keeps only
a placeholder there, and the tags exist only in the deployed artifact, built
from the same stats as everything else on the page. Only link unfurlers and
search engines read them, so a local preview does without, and running it
leaves the tracked file alone.

Run: python3 scripts/assemble_site.py
     python3 -m http.server --directory site      # then open localhost:8000
     python3 scripts/assemble_site.py --deploy    # pages.yml only
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import _stats  # noqa: E402
from _markers import read_block, replace_block  # noqa: E402

ROOT = _stats.ROOT
SITE = ROOT / "site"
SITE_URL = "https://kydlikebtc.github.io/awesome-jev/"
OG_IMAGE = f"{SITE_URL}img/og.png"

# Every data file the site fetches at runtime, copied verbatim.
RUNTIME_FILES = ("catalog.json", "compat.json", "patterns.json", "taxonomy.json", "collections.json")

# The whole body of site/index.html's `meta` block in git. check_site_data.py
# holds the committed file to it, so a number cannot be committed there again.
META_PLACEHOLDER = "<!-- written at deploy by scripts/assemble_site.py, see pages.yml -->"


def stats_payload() -> dict:
    return _stats.compute()


def meta_block(s: dict) -> str:
    """Link-preview tags. og:description is the same sentence as the GitHub
    repository description — both come from _stats.pitch_public, with the count
    floored to the hundred — so a link to the site and a link to the repo can
    no longer describe different catalogues. The image alt keeps the exact
    count, because the card it describes is rendered with live data."""
    text = html.escape(_stats.pitch_public(s), quote=True)
    alt = html.escape(
        "awesome-jev — "
        f"{s['entries']} public resources for TypeSafe AI's Jev, indexed by the "
        "decision each one makes.",
        quote=True,
    )
    tags = [
        f'<meta name="description" content="{text}" />',
        '<meta property="og:title" content="awesome-jev" />',
        f'<meta property="og:description" content="{text}" />',
        '<meta property="og:type" content="website" />',
        f'<meta property="og:url" content="{SITE_URL}" />',
        # Rendered from site/card.html with live data on every deploy, never
        # committed — so the preview image is exactly as current as the site.
        f'<meta property="og:image" content="{OG_IMAGE}" />',
        '<meta property="og:image:width" content="1280" />',
        '<meta property="og:image:height" content="640" />',
        f'<meta property="og:image:alt" content="{alt}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
    ]
    return "\n".join("    " + tag for tag in tags)


def meta_body(text: str) -> str:
    """The `meta` block's body with whitespace collapsed, for comparison."""
    return " ".join(read_block(text, "meta", where="site/index.html").split())


def fill_meta(text: str, stats: dict) -> str:
    return replace_block(text, "meta", meta_block(stats), where="site/index.html")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="also write the link-preview tags into site/index.html (pages.yml only)",
    )
    args = parser.parse_args(argv)

    for name in RUNTIME_FILES:
        shutil.copyfile(ROOT / name, SITE / name)
    stats = stats_payload()
    (SITE / "stats.json").write_text(json.dumps(stats, ensure_ascii=False))
    # Pages serves the artifact as-is; .nojekyll stops Jekyll touching it.
    (SITE / ".nojekyll").touch()
    print(f"assembled site/: {', '.join(RUNTIME_FILES)}, stats.json")

    if args.deploy:
        index = SITE / "index.html"
        index.write_text(fill_meta(index.read_text(), stats))
        print(
            f"wrote link-preview tags into site/index.html: {_stats.public_count(stats['entries'])} "
            f"in the description, {stats['entries']} in the image alt"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
