"""Every row that cites a file links it, in the READMEs and on the pattern pages (I28).

The site linked a row's cited file (`evidence.path`, at HEAD of its GitHub
repository) and the generated lists did not, so a README row whose summary is
the project's own words ("An AI Hedge Fund Team") said nothing about what the
project does with Jev while the catalogue knew the exact file. Now each row
prints a link named for what `evidence.kind` says the file shows, with the day
a person last read it: a dated reading, never "verified". The READMEs print
the link alone; the pattern pages add the path.

The link is built by scripts/evidence_url.py, a copy of the site's
evidenceUrl(); scripts/tests/evidence_url_cases.json is read by this suite and
by scripts/test_catalog_core.mjs, and SiteParityTest runs the site's function
itself beside the copy over the whole catalogue and thousands of made-up
addresses, so the two cannot drift apart unnoticed.

Two text signals about what a row says came with it: a summary naming nothing
about Jev (listed in docs/review-queue.md; over a hundred rows) and a cited
path naming a shadow or dry run without the flag (a lint warning; one row).
"""

from __future__ import annotations

import json
import pathlib
import random
import re
import shutil
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import build_docs  # noqa: E402
import build_readme  # noqa: E402
import build_review_queue as queue  # noqa: E402
from evidence_url import evidence_url  # noqa: E402
from readme import pages, rows, sections, strings  # noqa: E402

CASES = ROOT / "scripts" / "tests" / "evidence_url_cases.json"
CATALOG = json.loads((ROOT / "catalog.json").read_text())
RETIRED = json.loads((ROOT / "retired.json").read_text())


def row(slug: str = "demo", **fields) -> dict:
    base = {
        "slug": slug, "title": slug, "summary": "Routes tickets with a choice.", "summary_zh": "用 choice 分流工单。",
        "url": f"https://github.com/someone/{slug}", "kind": "project", "patterns": ["support-triage"],
        "has_code": True, "languages": ["python"],
        "evidence": {"path": "src/triage.py", "matched": ["from jev import"], "read_on": "2026-09-22"},
    }
    return {**base, **fields}


def sub_line(entry: dict, pack: dict, *, readme_layout: bool) -> str:
    """The dim signal line under a row."""
    lines = rows.entry_list([entry], pack, readme_layout=readme_layout)
    return next(line for line in lines if line.startswith("  <sub>"))


class SharedCasesTest(unittest.TestCase):
    def test_every_shared_case(self):
        cases = json.loads(CASES.read_text())
        self.assertGreaterEqual(len(cases), 40)
        for case in cases:
            with self.subTest(case=case["about"]):
                self.assertEqual(evidence_url(case["entry"]), case["url"])

    def test_the_node_suite_reads_the_same_cases(self):
        text = (ROOT / "scripts" / "test_catalog_core.mjs").read_text()
        self.assertIn('"./tests/evidence_url_cases.json"', text)
        self.assertIn("assert.equal(evidenceUrl(entry), url, about)", text)


def made_up(count: int, seed: int = 28) -> list[dict]:
    """Rows whose addresses and paths mix every shape the two parsers treat
    specially: schemes, slashes, userinfo, ports, percent-encoding, dots,
    backslashes, spaces, tabs, non-ASCII, queries and fragments."""
    rnd = random.Random(seed)
    schemes = ["https://", "HTTPS://", "hTtPs://", "https:", "https:///", "https:\\\\", "http://", "ftp://", "", "https//"]
    hosts = [
        "github.com", "GitHub.COM", "github.com.", "www.github.com", "gist.github.com", "github.com.evil.example",
        "git%68ub.com", "GIT%68UB.COM", "github%2Ecom", "github.com%2Fo", "github.com:443", "github.com:",
        "github.com:65535", "github.com:65536", "github.com:8a", "github.com:+1", "someone@github.com",
        "a@b@github.com", "u:p@github.com:0", "", "example.com", "[::1]", "github.com\t", " github.com", "git hub.com",
    ]
    segments = [
        "o", "r", "Owner", "repo.git", "ö", "a b", "a^b", "a`b", "{x}", "<y>", '"q"', "%2e", "%2E%2e", ".%2e", "..",
        ".", "", "tree", "main", "日本", "a|b", "a[b]", "a(b", "~u", "%41", "%zz", "a\\b", "\x01", "\x7f", "a\tb", "😀",
    ]
    tails = ["", "", "/", "?q=1", "#frag", "?x#y", "/?", "#", "?/o/r"]
    paths = [
        "src/main.py", "a b/c d.ts", "日本/é.md", "a#b?c&d=e+f%g", "/lead", "x/../y", "", "!*'()~", "a(b.py", "sp ace/",
        "a\\b", "😀.py", "\x00", "q\ud800",
    ]

    def address() -> str:
        path = "/".join(rnd.choice(segments) for _ in range(rnd.randint(0, 4)))
        text = rnd.choice(schemes) + rnd.choice(hosts)
        if path or rnd.random() < 0.5:
            text += rnd.choice(["/", "/", "\\"]) + path
        text += rnd.choice(tails)
        return f" \t{text}\n " if rnd.random() < 0.1 else text

    made = []
    for _ in range(count):
        entry = {"url": address(), "evidence": {"path": rnd.choice(paths), "matched": ["jev"]}}
        if rnd.random() < 0.4:
            entry["repo"] = rnd.choice([address(), None, ""])
        made.append(entry)
    return made


SITE_SCRIPT = """
import { evidenceUrl } from %s;
let input = "";
for await (const chunk of process.stdin) input += chunk;
process.stdout.write(JSON.stringify(JSON.parse(input).map(entry => evidenceUrl(entry))));
"""


@unittest.skipUnless(shutil.which("node"), "node is not on PATH")
class SiteParityTest(unittest.TestCase):
    """The site's own function, run by node, beside the Python copy."""

    def site_urls(self, entries: list[dict]) -> list[str | None]:
        module = json.dumps((ROOT / "site" / "catalog-core.mjs").as_uri())
        done = subprocess.run(
            ["node", "--input-type=module", "-e", SITE_SCRIPT % module],
            input=json.dumps(entries), capture_output=True, text=True, check=True, timeout=60,
        )
        return json.loads(done.stdout)

    def assertAgree(self, entries: list[dict]) -> None:
        site = self.site_urls(entries)
        ours = [evidence_url(entry) for entry in entries]
        differ = [(entry, a, b) for entry, a, b in zip(entries, site, ours) if a != b]
        self.assertEqual(len(site), len(entries))
        self.assertEqual(differ[:5], [], f"{len(differ)} of {len(entries)} differ")

    def test_every_catalogue_row(self):
        self.assertAgree(CATALOG + RETIRED)

    def test_thousands_of_made_up_addresses(self):
        entries = made_up(4000)
        self.assertAgree(entries)
        # Not vacuous: plenty of the made-up rows do get a link, plenty do not.
        linked = sum(1 for entry in entries if evidence_url(entry))
        self.assertGreater(linked, 400)
        self.assertLess(linked, 3600)


class RowLinkTest(unittest.TestCase):
    def test_readme_rows_print_the_link_and_the_reading_date(self):
        url = "https://github.com/someone/demo/blob/HEAD/src/triage.py"
        self.assertIn(f"· [call site]({url}), read 2026-09-22</sub>", sub_line(row(), strings.EN, readme_layout=True))
        self.assertIn(f"· [调用点]({url})，2026-09-22 阅读</sub>", sub_line(row(), strings.ZH, readme_layout=True))

    def test_pattern_pages_also_print_the_path(self):
        url = "https://github.com/someone/demo/blob/HEAD/src/triage.py"
        self.assertIn(f"· call site [`src/triage.py`]({url}), read 2026-09-22</sub>",
                      sub_line(row(), strings.EN, readme_layout=False))
        self.assertIn(f"· 调用点 [`src/triage.py`]({url})，2026-09-22 阅读</sub>",
                      sub_line(row(), strings.ZH, readme_layout=False))

    def test_a_file_that_is_not_a_call_site_is_a_cited_file(self):
        for kind in ("wire-shape", "example-only"):
            entry = row(evidence={**row()["evidence"], "kind": kind})
            for pack, name, wrong in ((strings.EN, "[cited file](", "call site"), (strings.ZH, "[引用文件](", "调用点")):
                with self.subTest(kind=kind, lang=pack["lang_code"]):
                    line = sub_line(entry, pack, readme_layout=True)
                    self.assertIn(name, line)
                    self.assertNotIn(wrong, line)
        explicit = row(evidence={**row()["evidence"], "kind": "call-site"})
        self.assertIn("[call site](", sub_line(explicit, strings.EN, readme_layout=True))

    def test_an_undated_reading_prints_no_date(self):
        entry = row(evidence={"path": "src/triage.py", "matched": ["from jev import"]})
        line = sub_line(entry, strings.EN, readme_layout=True)
        self.assertIn("/src/triage.py)</sub>", line)
        self.assertNotIn("read", line)

    def test_no_link_without_a_file_or_a_github_repository(self):
        for entry in (row(evidence=None), row(url="https://example.com/demo"), row(evidence={"path": "", "matched": ["x"]})):
            with self.subTest(entry=entry.get("url")):
                for layout in (True, False):
                    line = sub_line({k: v for k, v in entry.items() if v is not None}, strings.EN, readme_layout=layout)
                    self.assertNotIn("call site", line)
                    self.assertNotIn("blob/HEAD", line)

    def test_the_label_is_a_reading_never_a_verdict(self):
        for pack in (strings.EN, strings.ZH):
            for layout in (True, False):
                bit = rows.call_site(row(), pack, with_path=not layout)
                with self.subTest(lang=pack["lang_code"], readme=layout):
                    self.assertNotRegex(bit.lower(), r"verif|pass|check|核实|验证|通过")
                    self.assertRegex(bit, r"\d{4}-\d{2}-\d{2}")

    def test_caveats_stay_the_last_word_on_a_page(self):
        entry = row(flags=["shadow-mode-only"])
        line = sub_line(entry, strings.EN, readme_layout=False)
        self.assertLess(line.index("call site"), line.index("⚠"))
        self.assertTrue(line.endswith("`shadow mode`</sub>"), line)

    def test_a_hostile_path_stays_one_inert_line(self):
        entry = row(evidence={"path": "we`ird/a(b\nc).py", "matched": ["x"], "read_on": "2026-09-22"})
        lines = rows.entry_list([entry], strings.EN)
        line = next(item for item in lines if item.startswith("  <sub>"))
        self.assertIn("call site [`we'ird/a(b c).py`](", line)
        # The destination keeps its parentheses escaped, so Markdown cannot end it early.
        self.assertIn("/blob/HEAD/we%60ird/a\\(b%0Ac\\).py)", line)
        self.assertEqual(sum(1 for item in lines if "we'ird" in item), 1)


class RealCatalogueTest(unittest.TestCase):
    """Rendered in memory: CI runs the unit tests before it regenerates."""

    def test_every_cited_row_on_every_page_links_its_file(self):
        linked = {e["slug"]: evidence_url(e) for e in CATALOG if evidence_url(e)}
        self.assertTrue(linked)
        for key, members in rows.group_by_pattern(CATALOG).items():
            if not members:
                continue
            for pack in (strings.EN, strings.ZH):
                text = pages.render_page(key, members, pack)
                with self.subTest(page=key, lang=pack["lang_code"]):
                    for entry in members:
                        if entry["slug"] in linked:
                            self.assertIn(f"({rows.md_url(linked[entry['slug']])})", text)
                    self.assertEqual(text.count("/blob/HEAD/"), sum(1 for e in members if e["slug"] in linked))

    def test_both_readmes_link_without_the_path_and_explain_it(self):
        for pack, name, mark in ((strings.EN, "[call site](", ""), (strings.ZH, "[调用点](", " <sub>(机翻)</sub>")):
            text = build_readme.render(CATALOG, RETIRED, pack)
            with self.subTest(lang=pack["lang_code"]):
                self.assertIn(name, text)
                self.assertIn(pack["call_site_note"] + mark + "\n", text)
                self.assertNotRegex(text, r"(?:call site|调用点) \[`")
        self.assertIn("call_site_note", strings.ZH_MACHINE)

    def test_every_page_explains_the_link(self):
        members = rows.group_by_pattern(CATALOG)["tool-selection"]
        for pack in (strings.EN, strings.ZH):
            with self.subTest(lang=pack["lang_code"]):
                self.assertIn(rows.marked(pack, "call_site_note"), pages.render_page("tool-selection", members, pack))

    def test_the_review_queue_links_a_cited_file_the_same_way(self):
        for entry in CATALOG:
            if entry.get("evidence"):
                self.assertIn(f"({rows.md_url(evidence_url(entry))})", queue.file_link(entry))


class GenericSummaryTest(unittest.TestCase):
    def test_the_rule(self):
        generic = row(summary="An AI Hedge Fund Team")
        self.assertTrue(_stats.generic_summary(generic))
        for summary in ("Wraps Jev.", "A TypeSafe provider", "a System One client", "systemone harness",
                        "Scores leads", "picks a CHOICE", "noul gate", "Decisions at scale", "calibrated confidence"):
            with self.subTest(summary=summary):
                self.assertFalse(_stats.generic_summary(row(summary=summary)))
        self.assertFalse(_stats.generic_summary({**generic, "notes": "Asks Jev whether a trade clears risk."}))
        self.assertFalse(_stats.generic_summary({**generic, "official": True}))
        self.assertFalse(_stats.generic_summary({**generic, "has_code": False}))
        self.assertTrue(_stats.generic_summary({**generic, "notes_zh": "只有中文备注"}))

    def test_the_queue_lists_them_band_first_and_status_publishes_the_count(self):
        section = queue.generic_summary(CATALOG)
        stats = _stats.compute()
        self.assertEqual(len(section.rows), stats["review_generic_summary"])
        marked = [e for e in CATALOG if _stats.generic_summary(e)]
        bands = [rows.star_band(e.get("stars")) for e in queue.by_band(marked)]
        self.assertEqual(bands, sorted(bands, reverse=True))
        self.assertIn("review-queue.md#generic-summary", build_docs.shape_block(stats))
        self.assertIn(f"#generic-summary) | {stats['review_generic_summary']} |", queue.render(CATALOG))

    def test_a_summary_cell_cannot_break_the_table(self):
        entry = row("hostile", summary="a | b\nc", stars=None)
        (cells,) = queue.generic_summary([entry]).rows
        self.assertEqual(len(cells), len(queue.generic_summary([]).columns))
        self.assertEqual(cells[3], "a \\| b c")


if __name__ == "__main__":
    unittest.main()
