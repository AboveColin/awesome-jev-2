"""Every rule lint.py enforces, pinned by a row that breaks exactly that rule (I09).

lint.py is the gate every pull request passes through: a self-contained
draft-07 subset validator for schema/entry.schema.json, then invariants a
per-entry schema cannot express. Nothing tested it, so a rule written backwards
(say, evidence and evidence_none required together instead of exclusive) would
have passed CI and waved every bad row through after it.

Each test starts from a row that passes everything, changes one thing, and
asserts lint reports exactly one finding whose text names the rule. A second
group keeps the schema honest: every keyword it uses must be one validate()
enforces, because a keyword the validator does not know (oneOf, format: date)
is silently ignored rather than rejected.
"""

import contextlib
import copy
import datetime as dt
import io
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import lint
from _github import LANG_EXT

SCHEMA = json.loads(lint.SCHEMA.read_text(encoding="utf-8"))
PATTERNS = json.loads(lint.PATTERNS_FILE.read_text(encoding="utf-8"))["patterns"]
TAXONOMY = json.loads(lint.TAXONOMY_FILE.read_text(encoding="utf-8"))
TODAY = dt.date(2026, 9, 27)
PATH = "catalog.json[0]"
DROP = object()  # row(..., field=DROP) removes the field

# The smallest row lint accepts: the schema's required fields and nothing else.
MINIMAL = {
    "slug": "demo-row",
    "title": "Demo row",
    "summary": "A row that passes every lint rule.",
    "summary_zh": "demo",
    "url": "https://github.com/someone/demo-row",
    "kind": "project",
    "patterns": ["tool-selection"],
    "sources": [{"catalog": "awesome-something", "url": "https://github.com/someone/awesome-something"}],
    "license": "CC0-1.0",
}

# Every field the schema defines, each with a value that satisfies every rule.
# evidence_none is the one field left out: it and evidence are exclusive.
FULL = {
    **MINIMAL,
    "zh_machine": True,
    "has_code": True,
    "languages": ["python"],
    "question_types": ["choice"],
    "platforms": ["direct"],
    "author": {"name": "Someone", "handle": "someone", "url": "https://github.com/someone"},
    "repo": "https://github.com/someone/demo-row",
    "stars": 3,
    "repo_license": "MIT",
    "package": {"registry": "pypi", "name": "demo-row", "url": "https://pypi.org/project/demo-row/"},
    "evidence": {"path": "demo.py", "matched": ["from jev import"], "read_on": "2026-09-01"},
    "official": False,
    "published": "2026-01-02",
    "first_seen": "2026-09-01",
    "checked": "2026-09-20",
    "link_status": 200,
    "flags": ["unverified-claims"],
    "notes": "Performance claims are the author's own.",
    "notes_zh": "demo",
}

# A row as it sits in retired.json: a non-2xx status and a reason.
RETIRED = {
    **MINIMAL,
    "slug": "gone-row",
    "url": "https://github.com/someone/gone-row",
    "link_status": 404,
    "notes": "Repository deleted upstream.",
}

AUTHOR = {"catalog": "author submission", "url": "https://github.com/kydlikebtc/awesome-jev/pull/99"}


def row(base: dict, **changes) -> dict:
    """A copy of `base` with `changes` applied; a value of DROP removes that field."""
    out = copy.deepcopy(base)
    for key, value in changes.items():
        if value is DROP:
            out.pop(key, None)
        else:
            out[key] = value
    return out


def lint_row(entry: dict, *, retired: bool = False) -> lint.Findings:
    """Schema plus invariants for one row, the two layers lint.main() runs per row."""
    where = "retired.json[0]" if retired else PATH
    schema = lint.validate(entry, SCHEMA, where)
    rules = lint.check_entry_invariants(entry, where, retired=retired, today=TODAY)
    return lint.Findings(schema.errors + rules.errors, schema.warnings + rules.warnings)


class FindingsAssertions(unittest.TestCase):
    def assertClean(self, findings: lint.Findings) -> None:
        self.assertEqual(findings, lint.Findings((), ()))

    def assertOnly(self, findings: lint.Findings, kind: str, *fragments: str) -> str:
        """Exactly one finding, of `kind` ("error" or "warning"), containing every fragment."""
        errors, warnings = findings
        found, other = (errors, warnings) if kind == "error" else (warnings, errors)
        self.assertEqual(len(found), 1, findings)
        self.assertEqual(other, (), findings)
        for fragment in fragments:
            self.assertIn(fragment, found[0])
        return found[0]


class FixtureTest(FindingsAssertions):
    """The starting rows really are clean, so each mutation below isolates one rule."""

    def test_minimal_row_passes(self):
        self.assertClean(lint_row(MINIMAL))

    def test_full_row_passes(self):
        self.assertClean(lint_row(FULL))

    def test_retired_row_passes_in_retired_json(self):
        self.assertClean(lint_row(RETIRED, retired=True))

    def test_full_row_exercises_every_field_the_schema_defines(self):
        missing = set(SCHEMA["properties"]) - set(FULL) - {"evidence_none"}
        self.assertEqual(missing, set(), "add a valid value for each new schema field to FULL in test_lint.py")

    def test_findings_name_the_file_index_and_slug(self):
        message = self.assertOnly(lint_row(row(MINIMAL, patterns=["overview", "fan-out"])), "error")
        self.assertTrue(message.startswith("catalog.json[0]: demo-row: "), message)


class EntryInvariantTest(FindingsAssertions):
    """check_entry_invariants: one mutation per rule, asserting the rule's own wording."""

    def test_code_without_languages_warns(self):
        for languages in (DROP, []):
            with self.subTest(languages=languages):
                self.assertOnly(
                    lint_row(row(FULL, languages=languages)), "warning", "has_code is true but languages is empty"
                )

    def test_question_types_need_has_code(self):
        for has_code in (False, DROP):
            with self.subTest(has_code=has_code):
                self.assertOnly(
                    lint_row(row(FULL, has_code=has_code)),
                    "error",
                    "question_types set but has_code is not true",
                )

    def test_primitive_claim_without_evidence_warns_with_the_command(self):
        self.assertOnly(
            lint_row(row(FULL, evidence=DROP)),
            "warning",
            "claims primitives but carries neither evidence nor evidence_none",
            "python3 scripts/verify_claims.py --discover --only demo-row",
        )
        self.assertClean(lint_row(row(FULL, evidence=DROP, evidence_none="docs-page")))

    def test_evidence_needs_a_github_repository(self):
        self.assertOnly(
            lint_row(row(FULL, url="https://example.com/demo-row", repo=DROP)),
            "error",
            "has evidence but no GitHub repository to re-read it from",
        )
        # A GitHub repo field is enough when the canonical url is elsewhere.
        self.assertClean(lint_row(row(FULL, url="https://example.com/demo-row")))

    def test_evidence_and_evidence_none_are_exclusive(self):
        self.assertOnly(
            lint_row(row(FULL, evidence_none="docs-page")),
            "error",
            "has both evidence and evidence_none; they are exclusive",
        )

    def test_official_rejects_anything_the_vendor_did_not_publish(self):
        for url in (
            "https://github.com/someone/demo-row",
            "https://jevai.org/community/demo",
            "https://typesafe.ai.example.com/demo",
            "https://nottypesafe.ai/demo",
            "https://github.com/typesafe-ai-labs/demo",
        ):
            with self.subTest(url=url):
                self.assertOnly(
                    lint_row(row(MINIMAL, official=True, url=url)),
                    "error",
                    f"official is true but {url!r} is not published by TypeSafe AI",
                )

    def test_official_accepts_the_vendor_hosts_and_org(self):
        for url in (
            "https://typesafe.ai/",
            "https://docs.typesafe.ai/jev",
            "https://blog.typesafe.ai/launch",
            "https://eu.docs.typesafe.ai/jev",
            "https://Docs.TypeSafe.ai/jev",
            "https://github.com/typesafe-ai/jev-python",
        ):
            with self.subTest(url=url):
                self.assertClean(lint_row(row(MINIMAL, official=True, url=url)))

    def test_author_submission_needs_the_flag(self):
        self.assertOnly(
            lint_row(row(MINIMAL, sources=[AUTHOR])),
            "error",
            "a source is 'author submission' but flags lacks 'self-submitted'",
        )
        self.assertClean(lint_row(row(MINIMAL, sources=[AUTHOR], flags=["self-submitted"])))

    def test_self_submitted_flag_needs_the_source(self):
        self.assertOnly(
            lint_row(row(MINIMAL, flags=["self-submitted"])),
            "error",
            "flagged self-submitted but no source has catalog 'author submission'",
        )

    def test_near_miss_self_submission_spelling_is_rejected(self):
        source = {"catalog": "self-submission", "url": AUTHOR["url"]}
        self.assertOnly(
            lint_row(row(MINIMAL, sources=[source])),
            "error",
            "source catalog 'self-submission' looks like a self-submission; write exactly 'author submission'",
        )

    def test_caveat_flags_need_notes(self):
        for flag in ("ai-generated", "unverified-claims", "code-untested"):
            with self.subTest(flag=flag):
                self.assertOnly(
                    lint_row(row(MINIMAL, flags=[flag])),
                    "warning",
                    f"flagged {flag!r} but notes is empty, so a reader gets no reason",
                )
        # Other flags explain themselves.
        self.assertClean(lint_row(row(MINIMAL, flags=["paywalled"])))

    def test_overview_cannot_be_mixed_with_a_specific_pattern(self):
        self.assertOnly(
            lint_row(row(MINIMAL, patterns=["overview", "tool-selection"])),
            "error",
            "'overview' cannot be combined with specific patterns",
        )
        self.assertClean(lint_row(row(MINIMAL, patterns=["overview"])))

    def test_dates_must_exist_on_the_calendar(self):
        # The schema pattern only checks the shape, so 30 February gets past it.
        for field in ("published", "first_seen", "checked"):
            with self.subTest(field=field):
                self.assertOnly(
                    lint_row(row(MINIMAL, **{field: "2026-02-30"})), "error", f"{field} is not a valid date"
                )

    def test_dates_must_not_be_in_the_future(self):
        for field in ("published", "first_seen", "checked"):
            with self.subTest(field=field):
                self.assertOnly(
                    lint_row(row(MINIMAL, **{field: "2026-09-28"})),
                    "error",
                    f"{field} 2026-09-28 is in the future",
                )
                self.assertClean(lint_row(row(MINIMAL, **{field: TODAY.isoformat()})))

    def test_today_is_the_bound_it_is_given(self):
        # Far from the real date, so ignoring the argument cannot pass by coincidence.
        errors, _ = lint.check_entry_invariants(
            row(MINIMAL, checked="2020-01-02"), PATH, retired=False, today=dt.date(2020, 1, 1)
        )
        self.assertEqual(errors, ("catalog.json[0]: demo-row: checked 2020-01-02 is in the future",))

    def test_today_defaults_to_the_real_date(self):
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        errors, _ = lint.check_entry_invariants(row(MINIMAL, checked=tomorrow), PATH, retired=False)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("is in the future", errors[0])

    def test_published_cannot_follow_checked(self):
        self.assertOnly(
            lint_row(row(MINIMAL, published="2026-09-21", checked="2026-09-20")),
            "error",
            "published 2026-09-21 is after checked 2026-09-20",
        )
        self.assertClean(lint_row(row(MINIMAL, published="2026-09-20", checked="2026-09-20")))

    def test_catalog_rows_carry_only_a_2xx_status(self):
        for status in (199, 300, 404, 500):
            with self.subTest(status=status):
                self.assertOnly(
                    lint_row(row(MINIMAL, link_status=status)),
                    "error",
                    f"status {status} does not belong in catalog.json; move it to retired.json",
                )
        for status in (200, 299):
            with self.subTest(status=status):
                self.assertClean(lint_row(row(MINIMAL, link_status=status)))

    def test_retired_rows_carry_no_2xx_status(self):
        self.assertOnly(
            lint_row(row(RETIRED, link_status=200), retired=True),
            "error",
            "retired entries must not carry a 2xx status (200)",
        )

    def test_retired_rows_need_a_reason(self):
        self.assertOnly(
            lint_row(row(RETIRED, notes=DROP), retired=True),
            "error",
            "retired entries need notes saying why they were retired",
        )

    def test_unknown_licence_needs_the_no_license_flag(self):
        self.assertOnly(
            lint_row(row(MINIMAL, repo_license="unknown")),
            "error",
            "repo_license is 'unknown' but the row lacks the no-license flag",
        )
        self.assertClean(lint_row(row(MINIMAL, repo_license="unknown", flags=["no-license"])))

    def test_no_license_flag_needs_an_unknown_licence(self):
        self.assertOnly(
            lint_row(row(MINIMAL, repo_license="MIT", flags=["no-license"])),
            "error",
            "flagged no-license but repo_license is 'MIT'",
        )


class SchemaValidatorTest(FindingsAssertions):
    """validate() against the real schema: each keyword it enforces, on a field that uses it."""

    CASES = (
        # (what breaks, the row, where the error lands, what it says)
        ("type", {"stars": "3"}, ".stars", "expected integer, got str"),
        ("type: a bool is not a count", {"stars": True}, ".stars", "expected integer, got bool"),
        ("type: a count is not a bool", {"has_code": 1}, ".has_code", "expected boolean, got int"),
        ("type: object", {"author": "Someone"}, ".author", "expected object, got str"),
        # A wrong type is reported once; the field's other keywords (minimum 0) are not run.
        ("type: reported once", {"stars": -1.5}, ".stars", "expected integer, got float"),
        ("enum", {"kind": "blog"}, ".kind", "'blog' is not one of: official-docs, "),
        ("minLength", {"title": ""}, ".title", "shorter than minLength 1"),
        ("maxLength", {"summary": "x" * 301}, ".summary", "301 chars exceeds maxLength 300"),
        ("pattern", {"slug": "Demo_Row"}, ".slug", "'Demo_Row' does not match ^[a-z0-9]+"),
        (
            "pattern: https only",
            {"url": "http://github.com/someone/demo-row"},
            ".url",
            "does not match ^https://",
        ),
        ("format: uri", {"repo": "github.com/someone/demo-row"}, ".repo", "is not a URI"),
        (
            "format: a mailto is not a link",
            {"sources": [{"catalog": "x", "url": "mailto:a@example.com"}]},
            ".sources[0].url",
            "'mailto:a@example.com' is not a URI",
        ),
        ("minimum", {"stars": -1}, ".stars", "-1 below minimum 0"),
        ("maximum", {"link_status": 600}, ".link_status", "600 above maximum 599"),
        ("minItems", {"patterns": []}, ".patterns", "needs at least 1 item(s)"),
        (
            "maxItems",
            {"patterns": ["tool-selection", "intent-routing", "fan-out", "classification", "retry-control", "recommendation"]},
            ".patterns",
            "has 6 items, max 5",
        ),
        ("uniqueItems", {"languages": ["python", "python"]}, ".languages", "duplicate item 'python'"),
        ("items", {"patterns": ["tool-selection", "not-a-pattern"]}, ".patterns[1]", "'not-a-pattern' is not one of"),
        ("properties", {"author": {"name": ""}}, ".author.name", "shorter than minLength 1"),
        ("required", {"license": DROP}, "", "missing required field 'license'"),
        ("required: nested", {"sources": [{"catalog": "x"}]}, ".sources[0]", "missing required field 'url'"),
        ("additionalProperties", {"star_count": 3}, "", "unknown field 'star_count'"),
        (
            "additionalProperties: nested",
            {"evidence": {"path": "a.py", "matched": ["jev"], "line": 3}},
            ".evidence",
            "unknown field 'line'",
        ),
    )

    def test_each_keyword_rejects_a_row_that_breaks_it(self):
        for name, changes, where, says in self.CASES:
            with self.subTest(name):
                errors, warnings = lint.validate(row(MINIMAL, **changes), SCHEMA, PATH)
                self.assertEqual(len(errors), 1, errors)
                self.assertEqual(warnings, ())
                self.assertTrue(errors[0].startswith(f"{PATH}{where}: "), errors[0])
                self.assertIn(says, errors[0])


def schema_nodes(node: dict, where: str = "#"):
    """Yield (location, subschema) for the schema and every subschema validate() descends into."""
    yield where, node
    for name, sub in node.get("properties", {}).items():
        yield from schema_nodes(sub, f"{where}/properties/{name}")
    if isinstance(node.get("items"), dict):
        yield from schema_nodes(node["items"], f"{where}/items")


def unsupported(schema: dict) -> list[str]:
    """Everything in `schema` that lint.validate() would ignore or misread, one line each."""
    problems = []
    for where, node in schema_nodes(schema):
        for key, value in node.items():
            if key not in lint.SUPPORTED_KEYWORDS | lint.ANNOTATION_KEYWORDS:
                problems.append(f"{where}: keyword {key!r}")
        if "format" in node and not (isinstance(node["format"], str) and node["format"] in lint.SUPPORTED_FORMATS):
            problems.append(f"{where}: format {node['format']!r}")
        if "type" in node and not (isinstance(node["type"], str) and node["type"] in lint.SUPPORTED_TYPES):
            problems.append(f"{where}: type {node['type']!r}")
        if "items" in node and not isinstance(node["items"], dict):
            problems.append(f"{where}: items is not a single schema")
        if "additionalProperties" in node and not isinstance(node["additionalProperties"], bool):
            problems.append(f"{where}: additionalProperties is not true or false")
    return problems


class SchemaKeywordGuardTest(unittest.TestCase):
    """The schema uses only what validate() enforces; anything else would be silently ignored."""

    # Per keyword: a schema using it, a value it accepts, a value it rejects, and the error.
    KEYWORD_CASES = {
        "type": ({"type": "string"}, "a", 3, "x: expected string, got int"),
        "enum": ({"enum": ["a"]}, "a", "b", "x: 'b' is not one of: a"),
        "minLength": ({"minLength": 2}, "ab", "a", "x: shorter than minLength 2"),
        "maxLength": ({"maxLength": 1}, "a", "ab", "x: 2 chars exceeds maxLength 1"),
        "pattern": ({"pattern": "^a$"}, "a", "b", "x: 'b' does not match ^a$"),
        "format": ({"format": "uri"}, "https://a.example", "a.example", "x: 'a.example' is not a URI"),
        "minimum": ({"minimum": 1}, 1, 0, "x: 0 below minimum 1"),
        "maximum": ({"maximum": 1}, 1, 2, "x: 2 above maximum 1"),
        "minItems": ({"minItems": 1}, [1], [], "x: needs at least 1 item(s)"),
        "maxItems": ({"maxItems": 1}, [1], [1, 2], "x: has 2 items, max 1"),
        "uniqueItems": ({"uniqueItems": True}, [1, 2], [1, 1], "x: duplicate item 1"),
        "items": ({"items": {"type": "string"}}, ["a"], ["a", 1], "x[1]: expected string, got int"),
        "properties": ({"properties": {"a": {"type": "string"}}}, {"a": "b"}, {"a": 1}, "x.a: expected string"),
        "required": ({"required": ["a"]}, {"a": 1}, {}, "x: missing required field 'a'"),
        "additionalProperties": (
            {"properties": {"a": {}}, "additionalProperties": False},
            {"a": 1},
            {"a": 1, "b": 2},
            "x: unknown field 'b'",
        ),
    }

    def test_the_real_schema_uses_nothing_validate_would_ignore(self):
        self.assertEqual(
            unsupported(SCHEMA),
            [],
            "implement it in lint.validate() and add it to SUPPORTED_KEYWORDS (or SUPPORTED_FORMATS / "
            "SUPPORTED_TYPES) with a case in KEYWORD_CASES, or drop it from the schema",
        )

    def test_the_guard_catches_what_it_exists_for(self):
        broken = copy.deepcopy(SCHEMA)
        broken["properties"]["published"]["format"] = "date"
        broken["properties"]["author"]["oneOf"] = [{"required": ["name"]}]
        broken["properties"]["patterns"]["items"]["const"] = "overview"
        broken["properties"]["package"]["additionalProperties"] = {"type": "string"}
        broken["properties"]["sources"]["items"]["properties"]["url"]["type"] = ["string", "null"]
        self.assertEqual(
            sorted(unsupported(broken)),
            [
                "#/properties/author: keyword 'oneOf'",
                "#/properties/package: additionalProperties is not true or false",
                "#/properties/patterns/items: keyword 'const'",
                "#/properties/published: format 'date'",
                "#/properties/sources/items/properties/url: type ['string', 'null']",
            ],
        )

    def test_every_supported_keyword_is_enforced(self):
        self.assertEqual(set(self.KEYWORD_CASES), set(lint.SUPPORTED_KEYWORDS))
        for keyword, (schema, good, bad, says) in self.KEYWORD_CASES.items():
            with self.subTest(keyword=keyword):
                self.assertEqual(lint.validate(good, schema, "x"), lint.Findings((), ()))
                errors, _ = lint.validate(bad, schema, "x")
                self.assertEqual(len(errors), 1, errors)
                self.assertIn(says, errors[0])

    def test_annotations_constrain_nothing(self):
        schema = {key: "anything" for key in lint.ANNOTATION_KEYWORDS}
        self.assertEqual(lint.validate(3, schema, "x"), lint.Findings((), ()))
        self.assertFalse(lint.ANNOTATION_KEYWORDS & lint.SUPPORTED_KEYWORDS)

    def test_every_supported_type_is_known_to_type_ok(self):
        samples = {"object": {}, "array": [], "string": "", "integer": 1, "number": 1.5, "boolean": True, "null": None}
        self.assertEqual(set(samples), set(lint.SUPPORTED_TYPES))
        for name, value in samples.items():
            with self.subTest(type=name):
                self.assertTrue(lint.type_ok(value, name))
        with self.assertRaises(ValueError):
            lint.type_ok("2026-09-27", "date")


class LabelAlignmentTest(FindingsAssertions):
    """patterns.json, taxonomy.json and _github.LANG_EXT agree with the schema's enums."""

    def test_the_real_files_agree(self):
        self.assertClean(lint.check_patterns(SCHEMA, PATTERNS))
        self.assertClean(lint.check_languages(SCHEMA, LANG_EXT))
        self.assertClean(lint.check_taxonomy(SCHEMA, TAXONOMY))

    def test_schema_pattern_without_a_label(self):
        schema = copy.deepcopy(SCHEMA)
        schema["properties"]["patterns"]["items"]["enum"].append("new-pattern")
        self.assertOnly(
            lint.check_patterns(schema, PATTERNS),
            "error",
            "patterns.json: schema allows 'new-pattern' but patterns.json has no label for it",
        )

    def test_pattern_label_the_schema_does_not_allow(self):
        ghost = {**PATTERNS[0], "key": "ghost"}
        self.assertOnly(
            lint.check_patterns(SCHEMA, [*PATTERNS, ghost]),
            "error",
            "patterns.json: patterns.json labels 'ghost' but the schema does not allow it",
        )

    def test_pattern_label_missing_a_field(self):
        for field in ("en", "zh", "blurb_en", "blurb_zh", "short_en", "short_zh"):
            with self.subTest(field=field):
                patterns = [{**PATTERNS[0], field: ""}, *PATTERNS[1:]]
                self.assertOnly(
                    lint.check_patterns(SCHEMA, patterns),
                    "error",
                    f"patterns.json: {PATTERNS[0]['key']!r} has no {field}",
                )

    def test_schema_language_without_extensions(self):
        lang_ext = {k: v for k, v in LANG_EXT.items() if k != "c"}
        self.assertOnly(
            lint.check_languages(SCHEMA, lang_ext),
            "error",
            "scripts/_github.py: schema language 'c' has no file extensions in LANG_EXT",
        )

    def test_language_extensions_the_schema_does_not_allow(self):
        self.assertOnly(
            lint.check_languages(SCHEMA, {**LANG_EXT, "cobol": (".cob",)}),
            "error",
            "scripts/_github.py: LANG_EXT maps 'cobol', which the schema does not allow",
        )

    def test_schema_kind_or_flag_without_a_label(self):
        for group, path in (("kinds", ("kind",)), ("flags", ("flags", "items"))):
            with self.subTest(group=group):
                schema = copy.deepcopy(SCHEMA)
                node = schema["properties"]
                for step in path:
                    node = node[step]
                node["enum"].append("brand-new")
                self.assertOnly(
                    lint.check_taxonomy(schema, TAXONOMY),
                    "error",
                    f"taxonomy.json: schema allows {group[:-1]} 'brand-new' but it has no label",
                )

    def test_label_the_schema_does_not_allow(self):
        for group in ("kinds", "flags"):
            with self.subTest(group=group):
                labels = {**TAXONOMY, group: [*TAXONOMY[group], {**TAXONOMY[group][0], "key": "ghost"}]}
                self.assertOnly(
                    lint.check_taxonomy(SCHEMA, labels),
                    "error",
                    f"taxonomy.json: labels {group[:-1]} 'ghost' but the schema does not allow it",
                )

    def test_label_missing_a_field(self):
        for group in ("kinds", "flags"):
            for field in ("en", "zh", "blurb_en", "blurb_zh"):
                with self.subTest(group=group, field=field):
                    first = TAXONOMY[group][0]
                    labels = {**TAXONOMY, group: [{**first, field: ""}, *TAXONOMY[group][1:]]}
                    self.assertOnly(
                        lint.check_taxonomy(SCHEMA, labels),
                        "error",
                        f"taxonomy.json: {group[:-1]} {first['key']!r} has no {field}",
                    )


class CrossEntryTest(FindingsAssertions):
    """check_entries: rules that span rows and both files."""

    def test_clean_files_pass(self):
        self.assertClean(lint.check_entries(SCHEMA, [MINIMAL], [RETIRED]))

    def test_slug_is_unique_across_both_files(self):
        twin = row(RETIRED, slug="demo-row")
        self.assertOnly(
            lint.check_entries(SCHEMA, [MINIMAL], [twin]),
            "error",
            "retired.json[0]: duplicate slug 'demo-row', already used in catalog.json[0]",
        )

    def test_url_is_unique_ignoring_case_and_trailing_slash(self):
        twin = row(MINIMAL, slug="demo-row-2", url="https://GitHub.com/someone/demo-row/")
        self.assertOnly(
            lint.check_entries(SCHEMA, [MINIMAL, twin], []),
            "error",
            "catalog.json[1]: duplicate url 'https://GitHub.com/someone/demo-row/', already used in catalog.json[0]",
        )

    def test_each_entry_is_an_object(self):
        self.assertOnly(
            lint.check_entries(SCHEMA, ["demo-row", MINIMAL], []),
            "error",
            "catalog.json[0]: entry must be an object",
        )

    def test_files_are_in_slug_order(self):
        later = row(MINIMAL, slug="zz-row", url="https://github.com/someone/zz-row")
        message = self.assertOnly(lint.check_entries(SCHEMA, [later, MINIMAL], []), "error", "scripts/sort_catalog.py")
        self.assertTrue(message.startswith("catalog.json: "), message)

    def test_rows_get_the_schema_and_the_rules_of_their_own_file(self):
        found = lint.check_entries(SCHEMA, [row(MINIMAL, kind="blog")], [row(RETIRED, link_status=200)])
        self.assertEqual(len(found.errors), 2, found)
        self.assertIn("catalog.json[0].kind: 'blog' is not one of", found.errors[0])
        self.assertIn("retired.json[0]: gone-row: retired entries must not carry a 2xx status", found.errors[1])


class MainOutputTest(unittest.TestCase):
    """What `python3 scripts/lint.py` prints and exits with: warnings on stdout, errors on stderr."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = pathlib.Path(tmp.name)
        for name in ("ROOT", "CATALOG", "RETIRED"):
            self.addCleanup(setattr, lint, name, getattr(lint, name))
        lint.CATALOG = self.dir / "catalog.json"
        lint.RETIRED = self.dir / "retired.json"

    def run_main(self, catalog, retired) -> tuple[int, str, str]:
        lint.CATALOG.write_text(json.dumps(catalog), encoding="utf-8")
        lint.RETIRED.write_text(json.dumps(retired), encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = lint.main()
        return status, out.getvalue(), err.getvalue()

    def test_a_warning_and_an_error(self):
        warned = row(MINIMAL, slug="a-row", url="https://github.com/someone/a-row", has_code=True)
        broken = row(MINIMAL, slug="b-row", url="https://github.com/someone/b-row", kind="blog")
        status, out, err = self.run_main([warned, broken], [RETIRED])
        kinds = ", ".join(SCHEMA["properties"]["kind"]["enum"])
        self.assertEqual(status, 1)
        self.assertEqual(
            out,
            "warning: catalog.json[0]: a-row: has_code is true but languages is empty\n"
            "checked 2 catalog entries and 1 retired\n",
        )
        self.assertEqual(err, f"error: catalog.json[1].kind: 'blog' is not one of: {kinds}\n\n1 error(s)\n")

    def test_a_clean_run(self):
        self.assertEqual(self.run_main([MINIMAL], []), (0, "checked 1 catalog entry and 0 retired\n", ""))

    def test_a_warning_alone_does_not_fail(self):
        status, out, err = self.run_main([row(MINIMAL, flags=["ai-generated"])], [])
        self.assertEqual((status, err), (0, ""))
        self.assertIn("warning: catalog.json[0]: demo-row: flagged 'ai-generated' but notes is empty", out)

    def test_a_file_that_is_not_an_array_stops_the_run(self):
        status, out, err = self.run_main(MINIMAL, [])
        self.assertEqual(
            (status, out, err), (1, "", "error: catalog.json: top level must be an array of entries\n\n1 error(s)\n")
        )

    def test_a_missing_file_is_named(self):
        lint.ROOT = self.dir
        lint.RETIRED.write_text("[]", encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            status = lint.main()
        self.assertEqual((status, err.getvalue()), (1, "error: catalog.json is missing\n"))


if __name__ == "__main__":
    unittest.main()
