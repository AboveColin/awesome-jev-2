"""The READMEs and pattern pages print stars as a band, not as the count (I22).

The weekly refresh re-reads every repository's stars. Printed exactly and
sorted by exactly, one refresh rewrote over a thousand generated lines
(b8bae37: 220 rows changed, every one of them a star count only, 32 generated
files), for a precision no reader of a list needs. Now a count that moves
inside its band changes no line of either README or any pattern page, and no
row's position; only a row that crosses a band floor does. catalog.json, the
site and the MCP server keep the exact count.

The one generated line a star change still moves is the README screenshot's
cache-buster (`?v=`), which hashes catalog.json because the site in that
screenshot orders its cards by the exact count. The end-to-end test pins
that it is the only one.
"""

from __future__ import annotations

import copy
import json
import pathlib
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_readme  # noqa: E402
import regenerate  # noqa: E402
from readme import rows, strings  # noqa: E402

# Band floors as a reader sees them; the test's own copy, so a change to the
# bands has to be made here on purpose as well.
FLOORS = (10, 100, 1_000, 10_000, 100_000)
LABELS = ("★10+", "★100+", "★1k+", "★10k+", "★100k+")


def band_range(stars: int) -> tuple[int, int]:
    """The lowest and highest count in the band `stars` is in."""
    lows = (0, *FLOORS)
    band = sum(1 for floor in FLOORS if stars >= floor)
    low = lows[band]
    high = FLOORS[band] - 1 if band < len(FLOORS) else low * 10
    return low, high


def moved_within_bands(catalog: list[dict], how: str, seed: int = 22) -> list[dict]:
    """A copy of the catalogue with every star count moved inside its band."""
    rng = random.Random(seed)
    out = copy.deepcopy(catalog)
    for entry in out:
        stars = entry.get("stars")
        if stars is None:
            continue
        low, high = band_range(stars)
        entry["stars"] = {"low": low, "high": high, "random": rng.randint(low, high)}[how]
    return out


def row(slug: str, stars: int | None, title: str = "jev-mcp") -> dict:
    return {"slug": slug, "title": title, "stars": stars, "official": False, "has_code": True}


class BandTest(unittest.TestCase):
    def test_floors_and_labels(self):
        cases = [
            (None, 0, ""), (0, 0, ""), (9, 0, ""),
            (10, 1, "★10+"), (99, 1, "★10+"),
            (100, 2, "★100+"), (999, 2, "★100+"),
            (1_000, 3, "★1k+"), (9_999, 3, "★1k+"),
            (10_000, 4, "★10k+"), (99_999, 4, "★10k+"),
            (100_000, 5, "★100k+"), (248_479, 5, "★100k+"), (10**9, 5, "★100k+"),
        ]
        for stars, band, label in cases:
            with self.subTest(stars=stars):
                self.assertEqual(rows.star_band(stars), band)
                self.assertEqual(rows.star_label(stars), label)

    def test_the_package_table_is_the_one_readers_are_told_about(self):
        self.assertEqual(tuple(floor for floor, _ in rows.STAR_BANDS), FLOORS)
        self.assertEqual(tuple(label for _, label in rows.STAR_BANDS), LABELS)

    def test_order_is_band_then_title_then_slug(self):
        entries = [
            row("c-row", 99, title="beta"),
            row("b-row", 10, title="alpha"),
            row("a-row", 10, title="beta"),
            row("d-row", 100, title="zeta"),
            row("e-row", 9, title="aaa"),
            row("f-row", None, title="aab"),
        ]
        got = [e["slug"] for e in sorted(entries, key=rows.sort_key)]
        # ★100+ first; inside ★10+ by title, then slug; no band last, by title.
        self.assertEqual(got, ["d-row", "b-row", "a-row", "c-row", "e-row", "f-row"])

    def test_a_row_prints_its_band_and_nothing_under_the_lowest(self):
        for stars, shown in ((248_479, "★100k+"), (1_234, "★1k+"), (10, "★10+")):
            with self.subTest(stars=stars):
                entry = {**build_readme_row(), "stars": stars}
                for lang_strings in (strings.EN, strings.ZH):
                    text = "\n".join(rows.entry_list([entry], lang_strings))
                    self.assertEqual(re.findall(r"★[^ <]*", text), [shown])
        for stars in (0, 9, None):
            with self.subTest(stars=stars):
                text = "\n".join(rows.entry_list([{**build_readme_row(), "stars": stars}], strings.EN))
                self.assertNotIn("★", text)


def build_readme_row() -> dict:
    return {
        "slug": "some-row", "title": "Some row", "url": "https://example.invalid/some-row",
        "summary": "A row.", "summary_zh": "一行。", "kind": "project", "patterns": ["classification"],
    }


class NoteTest(unittest.TestCase):
    """Readers are told what a band is, in both languages, where the rows are."""

    def test_note_lists_every_band_and_says_it_is_not_a_quality_verdict(self):
        # A row under the first floor is listed without a band, not left out;
        # the note once told Chinese readers such rows were not shown (不显示).
        cases = (
            (strings.EN, "not a quality verdict", "show no band"),
            (strings.ZH, "不代表质量", "不标区间"),
        )
        for pack, verdict, unbanded in cases:
            with self.subTest(lang=pack["lang_code"]):
                note = rows.stars_note(pack, catalog="catalog.json")
                for label in LABELS:
                    self.assertIn(label, note)
                self.assertIn(verdict, note)
                self.assertIn(unbanded, note)
                self.assertNotIn("不显示", note)
                self.assertNotIn("{", note)

    def test_model_written_chinese_is_marked(self):
        self.assertIn("stars_note", strings.ZH_MACHINE)
        self.assertTrue(set(strings.ZH_MACHINE) <= set(strings.ZH))
        self.assertIn("(机翻)", rows.stars_note(strings.ZH, catalog="catalog.json"))
        self.assertNotIn("机翻", rows.stars_note(strings.EN, catalog="catalog.json"))

    def test_note_is_on_both_readmes_and_every_pattern_page(self):
        catalog = json.loads(build_readme.CATALOG.read_text(encoding="utf-8"))
        retired = json.loads(build_readme.RETIRED.read_text(encoding="utf-8"))
        for pack in (strings.EN, strings.ZH):
            with self.subTest(readme=pack["lang_code"]):
                text = build_readme.render(copy.deepcopy(catalog), copy.deepcopy(retired), pack)
                self.assertIn(rows.stars_note(pack, catalog="catalog.json"), text)
            for key, members in build_readme.group_by_pattern(catalog).items():
                if not members:
                    continue
                with self.subTest(page=key, lang=pack["lang_code"]):
                    page = build_readme.render_page(key, members, pack)
                    self.assertIn(rows.stars_note(pack, catalog="../../catalog.json"), page)


class WithinBandTest(unittest.TestCase):
    """The real catalogue, every star count moved inside its band."""

    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(build_readme.CATALOG.read_text(encoding="utf-8"))
        cls.retired = json.loads(build_readme.RETIRED.read_text(encoding="utf-8"))

    def variants(self):
        for how in ("low", "high", "random"):
            moved = moved_within_bands(self.catalog, how)
            changed = sum(1 for a, b in zip(self.catalog, moved) if a.get("stars") != b.get("stars"))
            self.assertGreater(changed, 500, f"{how}: the test moved too few counts to mean anything")
            yield how, moved

    def test_readmes_do_not_change(self):
        for how, moved in self.variants():
            for pack in (strings.EN, strings.ZH):
                with self.subTest(how=how, lang=pack["lang_code"]):
                    self.assertEqual(
                        build_readme.render(copy.deepcopy(self.catalog), copy.deepcopy(self.retired), pack),
                        build_readme.render(moved, copy.deepcopy(self.retired), pack),
                    )

    def test_pattern_pages_do_not_change(self):
        before = build_readme.group_by_pattern(copy.deepcopy(self.catalog))
        for how, moved in self.variants():
            after = build_readme.group_by_pattern(moved)
            for key, members in before.items():
                if not members:
                    continue
                for pack in (strings.EN, strings.ZH):
                    with self.subTest(how=how, pattern=key, lang=pack["lang_code"]):
                        self.assertEqual(
                            build_readme.render_page(key, members, pack),
                            build_readme.render_page(key, after[key], pack),
                        )

    def test_crossing_a_floor_does_change_the_page(self):
        """Without this, a renderer that printed no stars at all would pass."""
        candidates = [e for e in self.catalog if (e.get("stars") or 0) >= FLOORS[1]]
        self.assertTrue(candidates)
        entry = candidates[0]
        key = entry["patterns"][0]
        moved = copy.deepcopy(self.catalog)
        for other in moved:
            if other["slug"] == entry["slug"]:
                other["stars"] = band_range(entry["stars"])[0] - 1
        before = build_readme.render_page(key, build_readme.group_by_pattern(self.catalog)[key], strings.EN)
        after = build_readme.render_page(key, build_readme.group_by_pattern(moved)[key], strings.EN)
        self.assertNotEqual(before, after)


def copy_tree(dest: pathlib.Path) -> None:
    """This repository's working files, tracked or new, without .git."""
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    for rel in filter(None, listed.split("\0")):
        source = ROOT / rel
        if source.is_file():
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)


def outputs(tree: pathlib.Path) -> dict[str, str]:
    files = {}
    for rel in regenerate.OUTPUTS:
        path = tree / rel
        for item in ([path] if path.is_file() else sorted(path.rglob("*")) if path.exists() else []):
            if item.is_file():
                files[str(item.relative_to(tree))] = item.read_text(encoding="utf-8")
    return files


class RegenerateTest(unittest.TestCase):
    """Every generator on a scratch copy: a within-band change touches only `?v=`."""

    CACHE_BUSTER = re.compile(r"\?v=[0-9a-f]+")

    def test_only_the_screenshot_cache_buster_moves(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp)
            copy_tree(tree)

            def run() -> dict[str, str]:
                subprocess.run(
                    [sys.executable, "scripts/regenerate.py"], cwd=tree, check=True, capture_output=True, text=True
                )
                return outputs(tree)

            # Generated once first: on a pull request the committed outputs need not be current.
            before = run()
            catalog = json.loads((tree / "catalog.json").read_text(encoding="utf-8"))
            moved = moved_within_bands(catalog, "random", seed=7)
            (tree / "catalog.json").write_text(json.dumps(moved, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            after = run()

        self.assertEqual(sorted(before), sorted(after))
        changed = sorted(rel for rel in before if before[rel] != after[rel])
        self.assertEqual(changed, ["README.md", "README.zh-CN.md"])
        for rel in changed:
            with self.subTest(file=rel):
                old, new = before[rel].splitlines(), after[rel].splitlines()
                self.assertEqual(len(old), len(new))
                differing = [(a, b) for a, b in zip(old, new) if a != b]
                self.assertEqual(len(differing), 1, differing[:3])
                a, b = differing[0]
                self.assertEqual(self.CACHE_BUSTER.sub("?v=", a), self.CACHE_BUSTER.sub("?v=", b))


if __name__ == "__main__":
    unittest.main()
