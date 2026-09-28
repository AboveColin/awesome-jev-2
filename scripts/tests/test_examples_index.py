"""examples/index.json: the repository's examples, indexed for the MCP
server's wire_pattern prompt (I35).

build_examples_index.py derives it from catalog.json (the rows whose
evidence.path is a file under examples/ of this repository) and the example
files themselves. These tests build it in memory or in a temporary tree; none
reads the committed, generated examples/index.json.
"""

from __future__ import annotations

import io
import json
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_examples_index as bei  # noqa: E402
import lint_docs  # noqa: E402
import regenerate  # noqa: E402

HERE = "https://github.com/kydlikebtc/awesome-jev/blob/main/"


def row(slug: str, path: str, **fields) -> dict:
    return {"slug": slug, "title": slug.title(), "url": HERE + path, "summary": "s", "kind": "snippet",
            "patterns": ["tool-selection"], "languages": ["python"], "evidence": {"path": path, "matched": ["x"]},
            **fields}


class BuildTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)
        for rel, body in {
            "examples/02-b/main.py": "print('b')\n",
            "examples/01-a/main.py": "print('a')\n",
            "examples/03-uncited/main.py": "print('c')\n",
            "examples/README.md": "# Examples\n",
            "examples/01-a/README.md": "about a\n",
        }.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(body)

    def test_rows_citing_this_repositorys_examples_in_path_order(self):
        catalog = [
            row("b", "examples/02-b/main.py", flags=["code-untested"], question_types=["noul"]),
            row("a", "examples/01-a/main.py", patterns=["fan-out", "tool-selection"]),
            row("elsewhere", "examples/01-a/main.py", url="https://github.com/someone/else"),
            row("docs", "docs/x.md"),
            row("no-evidence", "examples/01-a/main.py", evidence=None),
        ]
        index, log = bei.build(catalog, self.root)
        self.assertEqual(list(index), ["about", "examples"])
        self.assertEqual([e["slug"] for e in index["examples"]], ["a", "b"])
        a, b = index["examples"]
        self.assertEqual(list(b), ["name", "path", "slug", "title", "url", "patterns", "languages", "question_types",
                                   "flags", "status", "code"])
        self.assertEqual((b["name"], b["path"], b["code"], b["status"]),
                         ("02-b", "examples/02-b/main.py", "print('b')\n", "not-run"))
        self.assertEqual((a["patterns"], a["status"]), (["fan-out", "tool-selection"], "not-recorded"))
        self.assertNotIn("flags", a)
        self.assertEqual(log, ["  left out examples/03-uncited/main.py: no catalogue row cites it (evidence.path)"])

    def test_a_row_citing_a_missing_file_is_left_out_and_said(self):
        index, log = bei.build([row("gone", "examples/09-gone/main.py")], self.root)
        self.assertEqual(index["examples"], [])
        self.assertIn("  left out gone: examples/09-gone/main.py does not exist", log)

    def test_the_repository_is_recognised_however_its_url_is_spelled(self):
        spelled = row("a", "examples/01-a/main.py", url="https://GitHub.com/KydLikeBTC/Awesome-Jev/tree/main/x")
        self.assertEqual([e["slug"] for e in bei.build([spelled], self.root)[0]["examples"]], ["a"])
        by_repo = row("a", "examples/01-a/main.py", url="https://example.com", repo="https://github.com/kydlikebtc/awesome-jev")
        self.assertEqual(len(bei.build([by_repo], self.root)[0]["examples"]), 1)

    def test_the_text_is_deterministic_and_carries_no_date(self):
        catalog = [row("b", "examples/02-b/main.py"), row("a", "examples/01-a/main.py")]
        text = bei.render(bei.build(catalog, self.root)[0])
        self.assertEqual(text, bei.render(bei.build(catalog[::-1], self.root)[0]))
        self.assertTrue(text.endswith("}\n"))
        self.assertNotRegex(text, r"20\d\d-\d\d-\d\d")

    def test_check_and_write(self):
        (self.root / "catalog.json").write_text(json.dumps([row("a", "examples/01-a/main.py")]))
        out = io.StringIO()
        with mock.patch.object(bei, "ROOT", self.root), redirect_stdout(out), redirect_stderr(io.StringIO()) as err:
            self.assertEqual(bei.main(["--check"]), 1)
            self.assertIn("examples/index.json is stale", err.getvalue())
            self.assertEqual(bei.main([]), 0)
            self.assertEqual(bei.main(["--check"]), 0)
        self.assertIn("wrote examples/index.json (1 example(s): 01-a (tool-selection))", out.getvalue())
        self.assertIn("left out examples/02-b/main.py", out.getvalue())
        written = json.loads((self.root / "examples" / "index.json").read_text())
        self.assertEqual(written["examples"][0]["code"], "print('a')\n")


class RealTreeTest(unittest.TestCase):
    """The committed catalogue and example files, rendered in memory."""

    def test_every_example_this_repository_ships_is_indexed(self):
        catalog = json.loads((ROOT / "catalog.json").read_text())
        index, log = bei.build(catalog)
        self.assertEqual(log, [], "an example file no row cites, or a row citing a missing file")
        shipped = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "examples").glob("*/*.py"))
        self.assertEqual([e["path"] for e in index["examples"]], shipped)
        for example in index["examples"]:
            with self.subTest(example=example["name"]):
                self.assertEqual(example["code"], (ROOT / example["path"]).read_text())
                self.assertTrue(example["patterns"] and example["languages"])


class RegistrationTest(unittest.TestCase):
    def test_it_is_a_generator_and_its_output_is_generated(self):
        self.assertIn("build_examples_index.py", [script for script, _ in regenerate.GENERATORS])
        self.assertIn(bei.OUT, regenerate.OUTPUTS)
        self.assertIn(bei.OUT, lint_docs.GENERATED)


if __name__ == "__main__":
    unittest.main()
