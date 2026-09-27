#!/usr/bin/env python3
"""Refill every generated number and table inside the hand-written docs.

The README was always generated. The docs around it were not, and every one of
them froze at the first build: status.md said 148 entries and listed
`retry-control` as a pattern nobody had published, sources.md warned that
fourteen linked projects had no licence when the real number was 171, and the
site's link-preview text still said 148. None of that was ever wrong on the day
it was written. It became wrong silently, which is worse.

The site's link-preview tags are no longer here: since 2026-09-27 they are
written at deploy by `assemble_site.py --deploy`, and git keeps a placeholder.

The rule this enforces: a number describing the catalogue may appear only where
something re-derives it. Here that means one of

  * a block — `<!-- name:start -->` … `<!-- name:end -->` — whose whole body is
    generated (a table or a list), or
  * an inline value — `<!--n:key-->805<!--/n-->` — inside a hand-written sentence.

Both are invisible once rendered. The prose around them stays hand-written.
lint.py rejects a bare catalogue count anywhere else, so a new stale number
cannot creep back in. Dated history (docs/method.md) is exempt by design: a log
entry saying the first build had 148 entries is true forever.

Run: python3 scripts/build_docs.py
     python3 scripts/build_docs.py --check    # CI: fail if anything is stale
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import _stats  # noqa: E402
from _markers import normalise, replace_block, replace_inline  # noqa: E402

ROOT = _stats.ROOT

LICENCE_LABEL = {
    "unknown": "None declared",
    "NOASSERTION": "NOASSERTION (non-standard terms)",
}


def table(header: list[str], rows: list[list[str]]) -> str:
    out = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join(" --- " for _ in header) + "|",
    ]
    out += [
        "| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |"
        for row in rows
    ]
    return "\n".join(out)


# ---- status.md -------------------------------------------------------------


def shape_block(s: dict) -> str:
    return table(
        ["", ""],
        [
            ["Entries", s["entries"]],
            ["Carrying code", s["with_code"]],
            ["Official (TypeSafe AI's own)", s["official"]],
            ["Links with a dated 2xx response record", s["link_ok"]],
            ["Most recent successful link-check date (dates vary by row)", s["last_sweep"]],
            ["Rows whose latest successful check is on that date", f"{s['sweep_coverage']} of {s['entries']}"],
            ["Rows citing a file where the project calls Jev (`evidence`; not a CI pass count)", s["call_site_rows"]],
            ["Rows citing a file that speaks Jev's request shape rather than building on Jev (`evidence.kind` `wire-shape`)", s["wire_shape_rows"]],
            ["Rows citing only an example the project ships (`evidence.kind` `example-only`)", s["example_only_rows"]],
            ["Rows with code citing no file and giving no reason (neither `evidence` nor `evidence_none`)", s["has_code_unbacked"]],
            ["Rows naming the primitives a person read the code calling (`question_types`)", s["primitive_rows"]],
            ["Machine text signal: rows whose cited file contains a primitive's request or answer shape (`primitives_seen`; not a reading, never counted as `question_types`)", s["primitive_signal_rows"]],
            ["Of those, rows with no `question_types`: the text signal is all that is recorded about their primitives", s["primitive_signal_only_rows"]],
            ["Machine signal: evidence under an examples directory, not yet judged ([review queue](review-queue.md#examples-dir))", s["review_examples_dir"]],
            ["Machine signal: evidence resting on one model name or the API host ([review queue](review-queue.md#single-model-name))", s["review_single_model_name"]],
            ["Machine signal: `tool-selection` suggested only by keyword-rule words dropped on 2026-09-27 ([review queue](review-queue.md#tool-selection-broad-words))", s["review_tool_selection_broad"]],
            ["Patterns covered", f"{s['patterns_covered']} of {s['patterns_total']}"],
            ["Rows whose `patterns` are exactly what the keyword rules suggest for their summary (agreement with the rules, not a review: any review of these rows was not recorded)", f"{s['patterns_rule_identical']} of {s['entries']}"],
            ["Rows whose patterns a person recorded reading (`patterns_reviewed`)", s["patterns_reviewed"]],
            ["Overview rows that are projects or plugins with code, listed apart as not yet indexed by pattern ([review queue](review-queue.md#unsorted-overview))", s["overview_unindexed"]],
            ["Summaries that are the project's own GitHub description (`summary_source` `upstream-description`)", f"{s['summary_upstream']} of {s['entries']}"],
            ["Summaries taken from that description that no longer match it (`upstream-description-stale`)", s["summary_upstream_stale"]],
            ["Summaries marked as written for this catalogue (`curated`)", s["summary_curated"]],
            ["Chinese summaries hand-written", f"{s['zh_hand']} of {s['entries']}"],
            ["Rows recording GitHub's creation date, last push and default-branch commit count for their repository (`repo_created_at`, `repo_pushed_at`, `repo_commits`; GitHub's facts at the last weekly refresh, not a judgement of upkeep)", f"{s['repo_facts_rows']} of {s['entries']}"],
            ["Rows flagged `single-commit`: one commit on the default branch (the refresh sets and clears it from `repo_commits`)", s["single_commit_rows"]],
            ["Retired links", s["retired"]],
        ],
    )


def pushed_block(s: dict) -> str:
    """Rows per calendar month of their repository's last push, newest first.
    Absolute months, never an age: the table changes only when a push lands
    in a new month, and says nothing about whether anything is maintained."""
    months = s["pushed_by_month"]
    if not months:
        return "No row records a last push yet."
    return table(
        ["Month of the last push (UTC)", "Rows"],
        [[month, count] for month, count in months.items()],
    )


# Editorial commentary on a gap, keyed by the state it describes. A note is
# emitted only while that state holds: "nobody has published one" belongs to
# `empty` and must vanish the day the first example lands. Keying notes by
# pattern alone let that sentence survive into the `thin` list the day
# recommendation got its first entry, contradicting the count printed beside it.
GAP_NOTES = {
    ("recommendation", "empty"): (
        "The vendor lists it as a use case, and nothing has surfaced across every "
        "sibling directory harvested so far. This is a gap in this catalogue, "
        "not proof that no example has been published."
    ),
    ("recommendation", "thin"): (
        "The first example is a movie recommender: retrieval narrows the field, and "
        "Jev parses the request and chooses from the shortlist."
    ),
    ("retry-control", "thin"): (
        "Most apparent matches are false positives: an HTTP client advertising "
        "\"observable retries\" is not a retry decision. The first real one was a "
        "semantic circuit breaker asking whether an HTTP 200 is a silent failure."
    ),
    ("case-study", "empty"): (
        "The catalogue has no case study documenting both cost and observed outcomes."
    ),
}


def gaps_block(s: dict, patterns: list[dict]) -> str:
    counts = s["by_pattern"]
    # Thin is a share, not a count: ten rows meant something at 148 entries and
    # means much less at 800.
    thin_below = s["entries"] * _stats.THIN_SHARE
    empty = [p for p in patterns if counts[p["key"]] == 0]
    thin = sorted(
        (p for p in patterns if 0 < counts[p["key"]] < thin_below and p["key"] != "overview"),
        key=lambda p: counts[p["key"]],
    )
    def note(key: str, state: str, lead: str = " ") -> str:
        text = GAP_NOTES.get((key, state))
        return f"{lead}{text}" if text else ""

    lines = []
    if empty:
        lines += ["No entries yet:", ""]
        lines += [f"- **`{p['key']}`** — {p['blurb_en']}{note(p['key'], 'empty')}" for p in empty]
    else:
        lines.append("Every pattern has at least one entry.")
    if s["empty_kinds"]:
        lines += ["", "Empty kinds:", ""]
        lines += [f"- **`{k}`**.{note(k, 'empty')}" for k in s["empty_kinds"]]
    if thin:
        pct = f"{_stats.THIN_SHARE:.1%}".replace(".0%", "%")
        lines += [
            "",
            f"Thin — under {pct} of the catalogue:",
            "",
        ]
        lines += [
            f"- `{p['key']}` ({counts[p['key']]} of {s['entries']})"
            + note(p["key"], "thin", " — ")
            for p in thin
        ]
    return "\n".join(lines)


# ---- sources.md ------------------------------------------------------------


def sources_block(catalog: list[dict]) -> str:
    counts: Counter = Counter()
    urls: dict[str, set] = {}
    for entry in catalog:
        # A row citing one source twice still counts once for that source.
        for source in {s["catalog"]: s for s in entry["sources"]}.values():
            counts[source["catalog"]] += 1
            urls.setdefault(source["catalog"], set()).add(source["url"])
    rows = [
        [name, f"<{next(iter(urls[name]))}>" if len(urls[name]) == 1 else "various", n]
        for name, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].lower()))
    ]
    return table(["Source", "URL", "Rows"], rows)


def licences_block(catalog: list[dict]) -> str:
    counts = Counter(e["repo_license"] for e in catalog if e.get("repo_license"))
    rows = [
        [LICENCE_LABEL.get(lic, lic), n]
        for lic, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    return table(["Licence", "Repositories"], rows)


def row_licences_block(s: dict, catalog: list[dict]) -> str:
    """Whose words the summaries are, and what the per-row licence covers.

    Until 2026-09-27 this said every row being CC0 meant no descriptive text was
    inherited — while most summaries were the linked project's own GitHub
    description, copied. Now the split comes from summary_source, counted by
    _stats. Facts only: who wrote the words and what this repository claims.
    """
    quoted = s["summary_upstream"] + s["summary_upstream_stale"]
    labels = {
        item["key"]: item["en"]
        for item in json.loads((ROOT / "taxonomy.json").read_text())["summary_sources"]
    }
    parts = []
    if quoted:
        parts.append(
            f"{s['summary_upstream']} of the {s['entries']} summaries in `catalog.json` are the linked "
            "project's own GitHub description, word for word apart from letter case, spacing and a "
            "final full stop (`summary_source: upstream-description`), and "
            f"{s['summary_upstream_stale']} more were taken from such a description and no longer "
            "match it (`upstream-description-stale`). The projects' authors wrote those words and the "
            "copyright in them is theirs: this repository does not dedicate them under `CC0-1.0`. "
            f"{s['summary_upstream_zh_machine']} of their Chinese counterparts are machine translations "
            "of them (`zh_machine`); the Chinese of such a row translates the project's words, and this "
            "repository does not dedicate it under `CC0-1.0` either. The READMEs, the pattern pages and "
            "the site mark each such summary "
            f"*({labels['upstream-description']})* or *({labels['upstream-description-stale']})*."
        )
    parts.append(
        f"{s['summary_curated']} summaries are marked `curated`: written for this catalogue. The "
        f"other {s['summary_unlabelled']} carry no `summary_source`, so where their words come from "
        "is not recorded row by row."
    )
    by = Counter(e["license"] for e in catalog)
    scope = (
        "covers the row's structured metadata (slug, kind, patterns, flags, dates, counts, evidence "
        "records and the rest) and any text written for this catalogue, not a summary labelled as "
        "the project's own description or the Chinese translation of one."
    )
    if set(by) == {"CC0-1.0"}:
        parts.append(f"Every row's `license` field is `CC0-1.0`. It {scope}")
    else:
        parts.append(
            f"{by.get('CC0-1.0', 0)} rows are `CC0-1.0`; {by.get('CC-BY-4.0', 0)} are "
            "`CC-BY-4.0` because their descriptive text was inherited from a CC BY 4.0 "
            "source, and the attribution is that row's `sources` array. Either way the "
            f"field {scope}"
        )
    return "\n\n".join(parts)


# ---- driver ----------------------------------------------------------------


def inline_values(s: dict) -> dict[str, object]:
    return {
        "entries": s["entries"],
        "with_code": s["with_code"],
        "official": s["official"],
        "link_ok": s["link_ok"],
        "link_unstamped": s["link_unstamped"],
        "last_sweep": s["last_sweep"],
        "sweep_coverage": s["sweep_coverage"],
        "call_site_rows": s["call_site_rows"],
        "wire_shape_rows": s["wire_shape_rows"],
        "example_only_rows": s["example_only_rows"],
        "primitive_rows": s["primitive_rows"],
        "primitive_rows_cited": s["primitive_rows_cited"],
        "primitive_signal_rows": s["primitive_signal_rows"],
        "primitive_signal_only_rows": s["primitive_signal_only_rows"],
        "no_licence": s["no_licence"],
        "platforms": s["platforms"],
        "sibling_lists": s["sibling_lists"],
        "patterns_total": s["patterns_total"],
        "patterns_rule_identical": s["patterns_rule_identical"],
        "patterns_reviewed": s["patterns_reviewed"],
        "overview_unindexed": s["overview_unindexed"],
        "kinds": ", ".join(s["kinds"]),
        "pattern_keys": ", ".join(s["pattern_keys"]),
        "fields": ", ".join(s["fields"]),
    }


def render() -> dict[pathlib.Path, str]:
    catalog, _, patterns, _, _ = _stats.load()
    s = _stats.compute()
    values = inline_values(s)

    blocks = {
        "docs/status.md": {"shape": shape_block(s), "pushed": pushed_block(s), "gaps": gaps_block(s, patterns)},
        "docs/sources.md": {
            "sources": sources_block(catalog),
            "licences": licences_block(catalog),
            "row-licences": row_licences_block(s, catalog),
        },
        "llms.txt": {},
        "docs/patterns.md": {},
    }

    out = {}
    for rel, regions in blocks.items():
        path = ROOT / rel
        text = path.read_text()
        for name, body in regions.items():
            text = replace_block(text, name, body, where=rel)
        out[path] = replace_inline(text, values, where=rel)
    return out


def squash(text: str) -> str:
    """Whitespace-insensitive form. A formatter that re-wraps a long HTML
    attribute changes bytes, not data, and must not turn CI red."""
    return re.sub(r"\s+", " ", normalise(text)).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail instead of writing")
    args = parser.parse_args()

    stale = []
    for path, rendered in render().items():
        current = path.read_text()
        if rendered == current or squash(rendered) == squash(current):
            continue
        stale.append(path)
        if not args.check:
            path.write_text(rendered)

    rel = [str(p.relative_to(ROOT)) for p in stale]
    if args.check:
        if stale:
            print(
                "error: generated values are stale in: " + ", ".join(rel) + "\n"
                "Run 'python3 scripts/build_docs.py' and commit the result.",
                file=sys.stderr,
            )
            return 1
        print("generated values in docs/status.md, docs/sources.md, docs/patterns.md and llms.txt are up to date")
        return 0

    print(("rewrote " + ", ".join(rel)) if stale else "nothing to update")
    return 0


if __name__ == "__main__":
    sys.exit(main())
