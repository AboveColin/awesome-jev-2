#!/usr/bin/env python3
"""Validate catalog.json and retired.json.

Two layers of checking:

1. A self-contained JSON Schema (draft-07 subset) validator. The repo ships no
   Python dependencies on purpose so CI is just `setup-python` with no install
   step, and a contributor can run this on a bare interpreter.
2. Cross-entry invariants a per-entry schema cannot express: slug and URL
   uniqueness across both files, both files in slug order (fix with
   scripts/sort_catalog.py), status codes matching the file an entry lives
   in, date sanity, and the honesty rules that keep flags meaningful.

Exit code is 0 when clean, 1 when any error was found. Warnings never fail the
build; they are advice for a reviewer.

Run: python3 scripts/lint.py
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"
RETIRED = ROOT / "retired.json"
SCHEMA = ROOT / "schema" / "entry.schema.json"
PATTERNS_FILE = ROOT / "patterns.json"

# Places we accept as TypeSafe AI speaking for itself. `official: true` anywhere
# else is a mistake: the community site at jevai.org is not the vendor, and a
# third-party integration is not official just because the vendor is mentioned.
OFFICIAL_HOSTS = (
    "typesafe.ai",
    "docs.typesafe.ai",
    "blog.typesafe.ai",
)

# The vendor's own GitHub org. A repo under any other owner is not official even
# when its code is a first-party integration published by that other vendor.
OFFICIAL_URL_PREFIXES = ("https://github.com/typesafe-ai/",)

# The one spelling of "the project's own author or maintainer proposed this row"
# in sources[].catalog, and the flag that discloses it on every surface. Each
# implies the other; see check_self_submission.
SELF_SUBMISSION_SOURCE = "author submission"
SELF_SUBMISSION_FLAG = "self-submitted"
# Spellings close enough that the writer clearly meant the declaration above.
# Rejected rather than accepted, so the rule cannot be evaded by a typo.
SELF_SUBMISSION_NEAR_MISS = re.compile(r"\b(?:author|self)[\s_-]*submi", re.IGNORECASE)

errors: list[str] = []
warnings: list[str] = []


def err(where: str, message: str) -> None:
    errors.append(f"{where}: {message}")


def warn(where: str, message: str) -> None:
    warnings.append(f"{where}: {message}")


# --------------------------------------------------------------------------
# Minimal draft-07 validator
# --------------------------------------------------------------------------

# Deliberately loose: we only need to catch a contributor pasting a bare word
# or a mailto: where a link belongs. check_links.py does the real verification.
URI_RE = re.compile(r"^[a-z][a-z0-9+.\-]*://[^\s]+$", re.IGNORECASE)


def type_ok(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        # bool is an int subclass in Python; a flag is not a count.
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"unhandled schema type {expected!r}")


def validate(value: Any, schema: dict, path: str) -> None:
    """Walk `schema` against `value`, appending to the module-level errors."""
    if "type" in schema and not type_ok(value, schema["type"]):
        err(path, f"expected {schema['type']}, got {type(value).__name__}")
        return

    if "enum" in schema and value not in schema["enum"]:
        allowed = ", ".join(map(str, schema["enum"]))
        err(path, f"{value!r} is not one of: {allowed}")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            err(path, f"shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            err(path, f"{len(value)} chars exceeds maxLength {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            err(path, f"{value!r} does not match {schema['pattern']}")
        if schema.get("format") == "uri" and not URI_RE.match(value):
            err(path, f"{value!r} is not a URI")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            err(path, f"{value} below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            err(path, f"{value} above maximum {schema['maximum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            err(path, f"needs at least {schema['minItems']} item(s)")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            err(path, f"has {len(value)} items, max {schema['maxItems']}")
        if schema.get("uniqueItems"):
            seen: list[Any] = []
            for item in value:
                if item in seen:
                    err(path, f"duplicate item {item!r}")
                seen.append(item)
        if "items" in schema:
            for i, item in enumerate(value):
                validate(item, schema["items"], f"{path}[{i}]")

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                err(path, f"missing required field {key!r}")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    err(path, f"unknown field {key!r}")
        for key, sub in props.items():
            if key in value:
                validate(value[key], sub, f"{path}.{key}")


# --------------------------------------------------------------------------
# Invariants across entries
# --------------------------------------------------------------------------


def parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def check_entry_invariants(entry: dict, path: str, *, retired: bool) -> None:
    slug = entry.get("slug", "?")
    today = dt.date.today()

    # An entry claiming code should say what language it is in, and a question
    # type is a claim about code. These keep `has_code` filters trustworthy.
    if entry.get("has_code") and not entry.get("languages"):
        warn(path, f"{slug}: has_code is true but languages is empty")
    if entry.get("question_types") and not entry.get("has_code"):
        err(path, f"{slug}: question_types set but has_code is not true")

    # A primitive claim should be re-checkable, or say why it is not. A warning
    # rather than an error so a new row is never blocked — but the count of
    # unbacked claims is what the README reports, so it stays visible.
    if entry.get("question_types") and not (
        entry.get("evidence") or entry.get("evidence_none")
    ):
        warn(
            path,
            f"{slug}: claims primitives but carries neither evidence nor evidence_none. "
            "Run 'python3 scripts/verify_claims.py --discover --only "
            + str(slug)
            + "'",
        )

    # Evidence without a repository to read it from cannot be verified.
    if entry.get("evidence"):
        url = entry.get("url", "")
        repo = entry.get("repo", "")
        if "github.com" not in url and "github.com" not in repo:
            err(
                path,
                f"{slug}: has evidence but no GitHub repository to re-read it from",
            )
    if entry.get("evidence") and entry.get("evidence_none"):
        err(path, f"{slug}: has both evidence and evidence_none; they are exclusive")

    # `official` is a factual claim about who published the thing, so it is
    # checked against the vendor's own hosts and GitHub org rather than trusted.
    if entry.get("official"):
        url = entry.get("url", "")
        host = re.sub(r"^https://([^/]+).*$", r"\1", url).lower()
        host_ok = any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS)
        path_ok = any(url.startswith(prefix) for prefix in OFFICIAL_URL_PREFIXES)
        if not (host_ok or path_ok):
            err(
                path,
                f"{slug}: official is true but {url!r} is not published by TypeSafe AI",
            )

    # A flag that needs explaining is worse than no flag at all.
    flags = entry.get("flags", [])
    check_self_submission(entry, path, flags)
    for flag in ("ai-generated", "unverified-claims", "code-untested"):
        if flag in flags and not entry.get("notes"):
            warn(
                path,
                f"{slug}: flagged {flag!r} but notes is empty, so a reader gets no reason",
            )

    # "overview" means the entry surveys the space rather than showing one
    # pattern. Mixing it with a specific pattern makes both filters lie.
    patterns = entry.get("patterns", [])
    if "overview" in patterns and len(patterns) > 1:
        err(path, f"{slug}: 'overview' cannot be combined with specific patterns")

    # Dates must be real and not from the future.
    for field in ("published", "first_seen", "checked"):
        if field in entry:
            parsed = parse_date(entry[field])
            if parsed is None:
                err(path, f"{slug}: {field} is not a valid date")
            elif parsed > today:
                err(path, f"{slug}: {field} {entry[field]} is in the future")

    published, checked = (
        parse_date(entry.get("published", "")),
        parse_date(entry.get("checked", "")),
    )
    if published and checked and published > checked:
        err(
            path,
            f"{slug}: published {entry['published']} is after checked {entry['checked']}",
        )

    # The status code has to agree with the file the entry lives in, otherwise
    # "everything in catalog.json was reachable" stops being true.
    status = entry.get("link_status")
    if status is not None:
        if retired and 200 <= status < 300:
            err(path, f"{slug}: retired entries must not carry a 2xx status ({status})")
        if not retired and not 200 <= status < 300:
            err(
                path,
                f"{slug}: status {status} does not belong in catalog.json; move it to retired.json",
            )

    if retired and not entry.get("notes"):
        err(path, f"{slug}: retired entries need notes saying why they were retired")

    # `no-license` and repo_license "unknown" state the same fact twice, so they
    # must agree. They drifted once: a project added a LICENSE upstream, the
    # weekly refresh noticed, and the row kept its flag because that refresh
    # was never merged — a row simultaneously claiming MIT and no licence.
    if "repo_license" in entry:
        unlicensed = entry["repo_license"] == "unknown"
        if unlicensed and "no-license" not in flags:
            err(
                path,
                f"{slug}: repo_license is 'unknown' but the row lacks the no-license flag",
            )
        if not unlicensed and "no-license" in flags:
            err(
                path,
                f"{slug}: flagged no-license but repo_license is {entry['repo_license']!r}",
            )


def check_self_submission(entry: dict, path: str, flags: list) -> None:
    """`author submission` in sources and the `self-submitted` flag go together.

    The source string is where a contributor declares the relationship; the
    flag is what the READMEs, the pattern pages, the site and the MCP server
    show a reader. Either one without the other means a surface is silent about
    it. Purely declarative on purpose: nothing is inferred from a GitHub handle
    (rarely filled, and an owner is often an org) or from the wording of a note.
    """
    slug = entry.get("slug", "?")
    sources = [s for s in entry.get("sources", []) if isinstance(s, dict)]
    names = [s.get("catalog") for s in sources if isinstance(s.get("catalog"), str)]
    for name in names:
        if name != SELF_SUBMISSION_SOURCE and SELF_SUBMISSION_NEAR_MISS.search(name):
            err(
                path,
                f"{slug}: source catalog {name!r} looks like a self-submission; write "
                f"exactly {SELF_SUBMISSION_SOURCE!r} so lint and every surface recognise it",
            )
    declared = SELF_SUBMISSION_SOURCE in names
    flagged = SELF_SUBMISSION_FLAG in flags
    if declared and not flagged:
        err(
            path,
            f"{slug}: a source is {SELF_SUBMISSION_SOURCE!r} but flags lacks "
            f"{SELF_SUBMISSION_FLAG!r}; add it so every surface discloses the relationship",
        )
    if flagged and not declared:
        err(
            path,
            f"{slug}: flagged {SELF_SUBMISSION_FLAG} but no source has catalog "
            f"{SELF_SUBMISSION_SOURCE!r}; add that source (url: the pull request or "
            "issue that proposed the row) or drop the flag",
        )


def check_slug_order(label: str, data: list) -> None:
    """Both data files stay in slug order.

    The order is meaningless to readers (every generator sorts for itself), but
    when each new row was appended at the end, every two pull requests adding
    rows edited the same lines and conflicted. In slug order they insert at
    different places. One error per file, with the fix, not one per row.
    """
    from sort_catalog import COMMAND, order_problem

    problem = order_problem(data)
    if problem:
        err(label, f"{problem}; run `{COMMAND}` and commit the result")


def main() -> int:
    for required_file in (CATALOG, RETIRED, SCHEMA):
        if not required_file.exists():
            print(
                f"error: {required_file.relative_to(ROOT)} is missing", file=sys.stderr
            )
            return 1

    schema = json.loads(SCHEMA.read_text())
    catalog = json.loads(CATALOG.read_text())
    retired = json.loads(RETIRED.read_text())

    # patterns.json feeds both README generators and the MCP server. If it
    # drifts from the schema enum, a pattern is either unlabelled in a figure
    # or unusable in the catalog, and both fail far from the cause.
    if PATTERNS_FILE.exists():
        taxonomy = {p["key"] for p in json.loads(PATTERNS_FILE.read_text())["patterns"]}
        enum = set(schema["properties"]["patterns"]["items"]["enum"])
        for key in sorted(enum - taxonomy):
            err(
                "patterns.json",
                f"schema allows {key!r} but patterns.json has no label for it",
            )
        for key in sorted(taxonomy - enum):
            err(
                "patterns.json",
                f"patterns.json labels {key!r} but the schema does not allow it",
            )
        # The site shows the short blurb, the README the long one. Both must
        # exist, or the site falls back to a raw slug without complaint.
        for p in json.loads(PATTERNS_FILE.read_text())["patterns"]:
            for field in ("en", "zh", "blurb_en", "blurb_zh", "short_en", "short_zh"):
                if not p.get(field):
                    err("patterns.json", f"{p['key']!r} has no {field}")

    # The scanners find code by extension. A language the schema accepts but
    # _github.LANG_EXT does not map is one discovery can never see: C and C++
    # were missing, so three database extensions looked test-only.
    sys.path.insert(0, str(ROOT / "scripts"))
    from _github import LANG_EXT

    langs = set(schema["properties"]["languages"]["items"]["enum"])
    for lang in sorted(langs - set(LANG_EXT)):
        err("scripts/_github.py", f"schema language {lang!r} has no file extensions in LANG_EXT")
    for lang in sorted(set(LANG_EXT) - langs):
        err("scripts/_github.py", f"LANG_EXT maps {lang!r}, which the schema does not allow")

    # taxonomy.json holds kind and flag labels for both the README and the site.
    # A key the schema allows but taxonomy.json lacks raises in build_readme but
    # renders as a raw slug on the site — loud in one place, silent in the other.
    taxonomy_file = ROOT / "taxonomy.json"
    if taxonomy_file.exists():
        labels = json.loads(taxonomy_file.read_text())
        for group, enum in (
            ("kinds", schema["properties"]["kind"]["enum"]),
            ("flags", schema["properties"]["flags"]["items"]["enum"]),
        ):
            have = [item["key"] for item in labels[group]]
            for key in sorted(set(enum) - set(have)):
                err(
                    "taxonomy.json",
                    f"schema allows {group[:-1]} {key!r} but it has no label",
                )
            for key in sorted(set(have) - set(enum)):
                err(
                    "taxonomy.json",
                    f"labels {group[:-1]} {key!r} but the schema does not allow it",
                )
            for item in labels[group]:
                for field in ("en", "zh", "blurb_en", "blurb_zh"):
                    if not item.get(field):
                        err(
                            "taxonomy.json",
                            f"{group[:-1]} {item['key']!r} has no {field}",
                        )

    for name, data in (("catalog.json", catalog), ("retired.json", retired)):
        if not isinstance(data, list):
            err(name, "top level must be an array of entries")
            print_report()
            return 1

    slugs: dict[str, str] = {}
    urls: dict[str, str] = {}

    for label, data, is_retired in (
        ("catalog.json", catalog, False),
        ("retired.json", retired, True),
    ):
        for i, entry in enumerate(data):
            path = f"{label}[{i}]"
            if not isinstance(entry, dict):
                err(path, "entry must be an object")
                continue
            validate(entry, schema, path)
            check_entry_invariants(entry, path, retired=is_retired)

            slug = entry.get("slug")
            if isinstance(slug, str):
                if slug in slugs:
                    err(path, f"duplicate slug {slug!r}, already used in {slugs[slug]}")
                else:
                    slugs[slug] = path

            url = entry.get("url")
            if isinstance(url, str):
                # Trailing slashes and casing are the usual way a duplicate sneaks in.
                key = url.rstrip("/").lower()
                if key in urls:
                    err(path, f"duplicate url {url!r}, already used in {urls[key]}")
                else:
                    urls[key] = path

        check_slug_order(label, data)

    print_report()
    print(
        f"checked {len(catalog)} catalog entr{'y' if len(catalog) == 1 else 'ies'} "
        f"and {len(retired)} retired"
    )
    return 1 if errors else 0


def print_report() -> None:
    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        print(f"\n{len(errors)} error(s)", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
