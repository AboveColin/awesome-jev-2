"""Self-submission is declared once and disclosed on every surface (I04).

A row's source string ``author submission`` records that the project's own
author or maintainer proposed it; the ``self-submitted`` flag is what the
READMEs, the pattern pages, the site and the MCP server render. lint keeps the
two in lock-step in both directions, and never guesses either one from a GitHub
handle or from the wording of a note.
"""

import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import lint

ROOT = pathlib.Path(__file__).resolve().parents[2]

AUTHOR = {"catalog": "author submission", "url": "https://github.com/kydlikebtc/awesome-jev/pull/99"}
MAINTAINER = {"catalog": "maintainer submission", "url": "https://github.com/kydlikebtc/awesome-jev"}
UPSTREAM = {"catalog": "awesome-something", "url": "https://github.com/someone/awesome-something"}


def entry(sources: list, flags: list | None = None, **extra) -> dict:
    row = {"slug": "demo", "url": "https://github.com/someone/demo", "sources": sources, **extra}
    if flags is not None:
        row["flags"] = flags
    return row


class SelfSubmittedInvariantTest(unittest.TestCase):
    def setUp(self):
        for name in ("errors", "warnings"):
            getattr(lint, name).clear()
            self.addCleanup(getattr(lint, name).clear)

    def check(self, row: dict) -> list[str]:
        lint.check_entry_invariants(row, "catalog.json[0]", retired=False)
        return list(lint.errors)

    def test_author_submission_without_the_flag_is_an_error(self):
        errors = self.check(entry([AUTHOR]))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("demo", errors[0])
        self.assertIn("'author submission'", errors[0])
        self.assertIn("self-submitted", errors[0])

    def test_the_flag_without_an_author_submission_source_is_an_error(self):
        for sources in ([MAINTAINER], [UPSTREAM]):
            with self.subTest(source=sources[0]["catalog"]):
                lint.errors.clear()
                errors = self.check(entry(sources, ["self-submitted"]))
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("flagged self-submitted", errors[0])
                self.assertIn("'author submission'", errors[0])

    def test_declared_and_flagged_rows_pass(self):
        self.assertEqual(self.check(entry([AUTHOR], ["self-submitted"])), [])
        # An upstream source beside the author's own submission is still a self-submission.
        self.assertEqual(self.check(entry([UPSTREAM, AUTHOR], ["unverified-claims", "self-submitted"])), [])

    def test_maintainer_submission_needs_no_flag(self):
        # "maintainer submission" means this list's maintainer added the row on
        # their own initiative. It says nothing about who wrote the project.
        self.assertEqual(self.check(entry([MAINTAINER])), [])

    def test_near_miss_spellings_are_rejected_rather_than_ignored(self):
        for spelling in (
            "Author submission",
            "author-submission",
            "author submission (PR #9)",
            "self-submission",
            "self submitted",
        ):
            with self.subTest(spelling=spelling):
                lint.errors.clear()
                source = {"catalog": spelling, "url": AUTHOR["url"]}
                errors = self.check(entry([source], ["self-submitted"]))
                spelled = [e for e in errors if "exactly" in e]
                self.assertEqual(len(spelled), 1, errors)
                self.assertIn(repr(spelling), spelled[0])

    def test_nothing_is_inferred_from_handles_or_notes(self):
        row = entry(
            [MAINTAINER],
            url="https://github.com/josharsh/demo",
            author={"name": "Josh", "handle": "josharsh"},
            notes="Submitted by its own author, who disclosed the affiliation.",
        )
        self.assertEqual(self.check(row), [])


class RealDataTest(unittest.TestCase):
    def test_schema_and_taxonomy_both_define_the_flag(self):
        schema = json.loads((ROOT / "schema" / "entry.schema.json").read_text())
        self.assertIn("self-submitted", schema["properties"]["flags"]["items"]["enum"])
        taxonomy = json.loads((ROOT / "taxonomy.json").read_text())
        (item,) = [f for f in taxonomy["flags"] if f["key"] == "self-submitted"]
        for field in ("en", "zh", "blurb_en", "blurb_zh"):
            self.assertTrue(item.get(field), field)
        # Model-written Chinese is labelled as such.
        self.assertIs(item.get("zh_machine"), True)

    def test_every_author_submission_row_is_flagged_and_no_other(self):
        for name in ("catalog.json", "retired.json"):
            with self.subTest(file=name):
                rows = json.loads((ROOT / name).read_text())
                declared = {
                    e["slug"]
                    for e in rows
                    if any(s.get("catalog") == "author submission" for s in e.get("sources", []))
                }
                flagged = {e["slug"] for e in rows if "self-submitted" in e.get("flags", [])}
                self.assertEqual(declared, flagged)
        catalog = json.loads((ROOT / "catalog.json").read_text())
        self.assertTrue(any("self-submitted" in e.get("flags", []) for e in catalog))


if __name__ == "__main__":
    unittest.main()
