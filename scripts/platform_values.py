"""Which catalogue rows stand for which compat.json surface, and the rules
that keep the two vocabularies joined.

A row records in `platforms` how it reaches Jev, in the catalogue's own words
(typesafe-api, vercel-ai-gateway, self-hosted, ...). compat.json describes
surfaces under ids of its own (typesafe-native, vercel-compat, cloudflare,
...). Until 2026-09-28 nothing joined the two, so a reader of
docs/compatibility.md could not tell whether any catalogued example used a
surface, and the MCP server matched `platform` as a fragment of a row's value.

Now each compat.json surface lists in `catalog_platforms` the values rows
record for it, and says `granularity: "coarse"` when such a value does not
tell it apart from another route. The rule itself — what a surface id or a
value matches, what a coarse match says — is the MCP package's query.py,
loaded here by its path as site_api.py loads it, so the generated
docs/compatibility.md, lint and the server count the same rows.
site/catalog-core.mjs applies the same rule on the site.

What lint holds (lint.check_platform_values):
* every surface has a `catalog_platforms` list of distinct values (possibly
  empty) and `granularity` is "coarse" or absent;
* a value two surfaces list is coarse on both;
* taxonomy.json's `platforms_without_surface` is a sorted list of distinct
  values no surface lists;
* every value a row records (catalog.json and retired.json) is listed by a
  surface or in platforms_without_surface.
A listed value no row records is allowed: the lists admit values, and the
counts and the site's choices come from the rows.

Stdlib only, like the rest of scripts/.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUERY = ROOT / "src" / "awesome_jev_mcp" / "query.py"
WITHOUT_SURFACE = "platforms_without_surface"


def load_query():
    """src/awesome_jev_mcp/query.py, by path, on first use. Not at import:
    lint.py imports this module, and review_pr.py imports lint.py from a
    copy of scripts/ alone. The same module name and guard as
    site_api.load_query(), so the two share one copy whichever loads first."""
    name = "awesome_jev_query"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, QUERY)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _distinct_strings(value: object) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(v, str) and v.strip() == v and v for v in value)
        and len(set(value)) == len(value)
    )


def compat_problems(compat: dict, without: object) -> list[tuple[str, str]]:
    """(file, message) for each way compat.json's catalog_platforms or
    taxonomy.json's platforms_without_surface breaks the rules above."""
    query = load_query()
    coarse = query.COARSE
    found: list[tuple[str, str]] = []
    for platform in compat.get("platforms") or []:
        name = platform.get("id", "?")
        if "catalog_platforms" not in platform:
            found.append(("compat.json", f"surface {name!r} has no catalog_platforms: list the values rows "
                          "record in `platforms` for it, or [] when none stands for it"))
        elif not _distinct_strings(platform["catalog_platforms"]):
            found.append(("compat.json", f"surface {name!r}: catalog_platforms must be a list of distinct, "
                          "non-empty strings without surrounding space"))
        if "granularity" in platform and platform["granularity"] != coarse:
            found.append(("compat.json", f"surface {name!r}: granularity is {platform['granularity']!r}; it is "
                          f"{coarse!r} or absent"))
    claims = query.claimed_by({"platforms": [p for p in compat.get("platforms") or []
                                             if _distinct_strings(p.get("catalog_platforms"))]})
    for value, surfaces in claims.items():
        fine = [p for p in surfaces if p.get("granularity") != coarse]
        if len(surfaces) > 1 and fine:
            found.append(("compat.json", f"{value!r} is in the catalog_platforms of "
                          f"{', '.join(repr(p.get('id')) for p in surfaces)}, so it does not tell them apart: "
                          f"set granularity {coarse!r} on {', '.join(repr(p.get('id')) for p in fine)}"))
    if not _distinct_strings(without) or without != sorted(without):
        found.append(("taxonomy.json", f"{WITHOUT_SURFACE} must be a sorted list of distinct, non-empty strings"))
    else:
        for value in without:
            if value in claims:
                found.append(("taxonomy.json", f"{WITHOUT_SURFACE} lists {value!r}, which compat.json surface "
                              f"{claims[value][0].get('id')!r} claims: keep it in one place"))
    return found


def row_problems(label: str, rows: list, compat: dict, without: object) -> list[tuple[str, str]]:
    """(where, message) for each value a row records in `platforms` that no
    surface lists and platforms_without_surface does not name."""
    listing = [p for p in compat.get("platforms") or [] if _distinct_strings(p.get("catalog_platforms"))]
    known = set(load_query().claimed_by({"platforms": listing})) | (set(without) if isinstance(without, list) else set())
    found = []
    for i, entry in enumerate(rows):
        if not isinstance(entry, dict) or not isinstance(entry.get("platforms"), list):
            continue
        for value in entry["platforms"]:
            if isinstance(value, str) and value not in known:
                found.append((
                    f"{label}[{i}]",
                    f"{entry.get('slug', '?')}: platforms value {value!r} is in no compat.json surface's "
                    f"catalog_platforms and not in taxonomy.json {WITHOUT_SURFACE}: fix the spelling, add it "
                    "to the catalog_platforms of the surface it reaches Jev through, or list it there",
                ))
    return found


def problems(catalog: list, retired: list, compat: dict, taxonomy: dict) -> list[tuple[str, str]]:
    """(where, message) for every break of the rules above, over both data
    files. Each is an error."""
    without = taxonomy.get(WITHOUT_SURFACE, [])
    found = compat_problems(compat, without)
    for label, rows in (("catalog.json", catalog), ("retired.json", retired)):
        found += row_problems(label, rows, compat, without)
    return found


def surface_counts(compat: dict, rows: list[dict]) -> dict[str, int]:
    """{surface id: how many rows record one of its catalog_platforms}."""
    query = load_query()
    return {
        p["id"]: len(query.platform_rows(rows, query.surface_values(p)))
        for p in compat.get("platforms") or []
    }
