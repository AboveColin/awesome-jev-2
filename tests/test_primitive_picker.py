"""The primitive picker as the README and the site show it (I25); no network.

picker.json is drawn by scripts/build_assets.py into
docs/assets/primitive-picker-{en,zh}-{light,dark}.svg, embedded under "What Jev
returns" in both READMEs with its sources as links, and fetched by the site's
primitives view. Like tests/test_readme_cover.py for the hero, these render in
memory (or into a temporary directory) and never read a committed generated
file: PR CI runs unit tests before it regenerates anything.
"""

from __future__ import annotations

import copy
import json
import pathlib
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import assemble_site  # noqa: E402
import build_assets  # noqa: E402
import build_readme  # noqa: E402
import picker  # noqa: E402
from readme import strings  # noqa: E402

SVG_NS = "{http://www.w3.org/2000/svg}"
PICKER = picker.load()
STEPS, LAST = picker.walk(PICKER)
LEAVES = [leaf for _, leaf in STEPS] + [LAST]
# Made-up counts, so a figure that printed anything else would show.
FAKE = {
    key: {name: {"read": 7000 + i * 10 + j, "signal_only": 8000 + i * 10 + j} for j, name in enumerate(_stats.PRIMITIVES)}
    for i, key in enumerate(key for key, _, _ in build_assets.PATTERNS)
}


def render(lang: str, theme: str, data: dict = PICKER, by_pattern: dict = FAKE) -> str:
    return build_assets.picker_svg(lang, theme, data, by_pattern)


class FigureTest(unittest.TestCase):
    def test_main_writes_every_language_and_theme(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(build_assets, "OUT", pathlib.Path(directory)):
            with patch("sys.stdout"):
                self.assertEqual(build_assets.main(), 0)
            written = {path.name for path in pathlib.Path(directory).iterdir()}
        wanted = {build_assets.picker_file(lang, theme) for lang in ("en", "zh") for theme in ("light", "dark")}
        self.assertLessEqual(wanted, written)
        self.assertEqual(wanted, {"primitive-picker-en-light.svg", "primitive-picker-en-dark.svg",
                                  "primitive-picker-zh-light.svg", "primitive-picker-zh-dark.svg"})

    def test_figures_are_self_contained_and_well_formed(self):
        for lang in ("en", "zh"):
            for theme in ("light", "dark"):
                svg = render(lang, theme)
                with self.subTest(lang=lang, theme=theme):
                    root = ET.fromstring(svg)
                    self.assertEqual(root.tag, f"{SVG_NS}svg")
                    for banned in ("<image", "<script", "foreignObject", "@import", "@font-face", "href=", "url(http"):
                        self.assertNotIn(banned, svg)
                    self.assertEqual(root.get("width"), str(build_assets.PICK_WIDTH))

    def test_each_theme_is_drawn_in_its_own_palette(self):
        for lang in ("en", "zh"):
            light, dark = render(lang, "light"), render(lang, "dark")
            self.assertIn(build_assets.THEMES["light"]["fg"], light)
            self.assertNotIn(build_assets.THEMES["dark"]["fg"], light)
            self.assertIn(build_assets.THEMES["dark"]["fg"], dark)
            self.assertNotIn(build_assets.THEMES["light"]["fg"], dark)

    def test_every_question_leaf_and_source_is_drawn_from_picker_json(self):
        for lang in ("en", "zh"):
            svg = render(lang, "light")
            text = " ".join(t.text or "" for t in ET.fromstring(svg).iter(f"{SVG_NS}text"))
            flat = re.sub(r"\s+", "", text)
            with self.subTest(lang=lang):
                for n, (node, _) in enumerate(STEPS, 1):
                    self.assertIn(re.sub(r"\s+", "", node[f"question_{lang}"]), flat)
                for leaf in LEAVES:
                    self.assertIn(leaf[f"label_{lang}"], svg)
                    self.assertIn(re.sub(r"\s+", "", leaf[f"note_{lang}"]), flat)
                for n, url in enumerate(picker.sources(PICKER), 1):
                    self.assertIn(f"[{n}] {build_assets.short_url(url)}", svg)

    def test_counts_beside_a_leaf_come_from_the_layers_given(self):
        counted = [leaf for leaf in LEAVES if picker.layers(leaf, FAKE)]
        self.assertGreaterEqual(len(counted), 3)
        for lang in ("en", "zh"):
            svg = render(lang, "dark")
            lines = [t.text for t in ET.fromstring(svg).iter(f"{SVG_NS}text")]
            printed = [line for line in lines if line and re.search(r"\d{4}", line)]
            with self.subTest(lang=lang):
                wanted = [
                    build_assets.STRINGS[lang]["pick_counts"].format(
                        read=FAKE[leaf["pattern_key"]][leaf["primitive"]]["read"],
                        signal=FAKE[leaf["pattern_key"]][leaf["primitive"]]["signal_only"],
                    )
                    for leaf in counted
                ]
                # Exactly one counts line per counted leaf, in reading order,
                # and no other line carries a count.
                self.assertEqual(printed, wanted)

    def test_the_legend_keeps_the_two_layers_apart_and_disclaims_a_recommendation(self):
        en, zh = build_assets.STRINGS["en"]["pick_legend"], build_assets.STRINGS["zh"]["pick_legend"]
        self.assertIn("Never added together", en[0])
        self.assertIn("not a recommendation", en[1])
        self.assertIn("不是对任何收录条目的推荐", zh[1])
        self.assertTrue(zh[-1].endswith("(机翻)"))
        self.assertIsNone(re.search(r"verif|核实|验证", " ".join(en + zh), re.I))

    def test_text_that_would_overrun_its_box_fails_the_build(self):
        data = copy.deepcopy(PICKER)
        data["leaves"][0]["note_en"] = " ".join(["words"] * 120)
        with self.assertRaisesRegex(build_assets.PickerLayoutError, f"leaf '{data['leaves'][0]['id']}' note_en"):
            render("en", "light", data)
        data = copy.deepcopy(PICKER)
        data["nodes"][0]["question_en"] = "x" * 80
        with self.assertRaisesRegex(build_assets.PickerLayoutError, "no place to break"):
            render("en", "light", data)

    def test_wrapping_breaks_chinese_between_characters_but_not_before_closing_punctuation(self):
        lines = build_assets.wrap("t", "每个问题只问一个条件，并让高值表示「是」。" * 3, 120, 12, lines=10)
        self.assertGreater(len(lines), 1)
        for line in lines[1:]:
            self.assertNotRegex(line[0], r"[，。、；：？！）」』]")
        self.assertEqual("".join(lines), "每个问题只问一个条件，并让高值表示「是」。" * 3)

    def test_counts_can_grow_tenfold_without_overrunning(self):
        grown = {key: {name: {"read": 99999, "signal_only": 99999} for name in _stats.PRIMITIVES} for key in FAKE}
        for lang in ("en", "zh"):
            render(lang, "light", by_pattern=grown)

    def test_the_description_names_every_leaf_in_order(self):
        for lang in ("en", "zh"):
            text, at = build_assets.picker_description(PICKER, lang), 0
            for leaf in LEAVES:
                at = text.index(leaf[f"label_{lang}"], at) + 1
            self.assertIn(LAST[f"label_{lang}"], text.rsplit("：" if lang == "zh" else ": ", 1)[1])


class ReadmeTest(unittest.TestCase):
    def readme(self, pack: dict) -> str:
        catalog, retired, *_ = _stats.load()
        return build_readme.render(catalog, retired, pack)

    def section(self, pack: dict) -> str:
        text = self.readme(pack)
        return text.split(f"\n## {pack['prims_h']}\n", 1)[1].split("\n## ", 1)[0]

    def test_the_figure_sits_under_what_jev_returns_in_both_languages(self):
        for pack in (strings.EN, strings.ZH):
            lang = pack["lang_code"]
            section = self.section(pack)
            with self.subTest(lang=lang):
                found = re.findall(r'<source media="([^"]+)" srcset="docs/assets/([^"]+)">', section)
                self.assertIn(("(prefers-color-scheme: dark)", build_assets.picker_file(lang, "dark")), found)
                self.assertIn(f'<img src="docs/assets/{build_assets.picker_file(lang, "light")}"', section)
                # After the primitives figure, like every other figure: a dark
                # <source>, then the light <img> as the fallback.
                self.assertLess(section.index("primitives-"), section.index("primitive-picker-"))
                picture = section.split("primitive-picker-", 1)[0].rsplit("<picture>", 1)[1]
                self.assertNotIn("<img", picture)

    def test_alt_text_is_the_figures_own_description(self):
        for pack in (strings.EN, strings.ZH):
            lang = pack["lang_code"]
            described = build_assets.picker_description(PICKER, lang).replace('"', "&quot;")
            self.assertIn(f'alt="{described}"', self.section(pack))

    def test_every_source_is_a_link_numbered_as_in_the_figure(self):
        for pack in (strings.EN, strings.ZH):
            section = self.section(pack)
            for n, url in enumerate(picker.sources(PICKER), 1):
                self.assertIn(f"[{n}] [{build_assets.short_url(url)}]({url})", section)

    def test_the_intro_says_it_is_guidance_not_a_recommendation_and_zh_is_marked(self):
        self.assertIn("not a recommendation", strings.EN["picker_intro"])
        self.assertIn("不是对本目录任何条目的推荐", strings.ZH["picker_intro"])
        self.assertLessEqual({"picker_intro", "picker_sources"}, strings.ZH_MACHINE)
        section = self.section(strings.ZH)
        self.assertIn(strings.ZH["picker_intro"] + " <sub>(机翻)</sub>", section)

    def test_the_colour_scheme_is_spelled_as_github_detects_it(self):
        section = self.section(strings.EN)
        for condition in re.findall(r"\([^)]*color-scheme[^)]*\)", section):
            self.assertRegex(condition, r"^\(prefers-color-scheme: (light|dark)\)$")


class SiteTest(unittest.TestCase):
    PAGE = (ROOT / "site" / "index.html").read_text()

    def test_the_site_publishes_picker_json_apart_from_the_five_page_files(self):
        self.assertIn("picker.json", assemble_site.RUNTIME_FILES)
        self.assertNotIn("picker.json", assemble_site.PAGE_FILES)

    def test_the_primitives_view_walks_the_same_file(self):
        self.assertIn('fetch("picker.json")', self.PAGE)
        self.assertIn("pickerSteps, pickerCounts, isNegativeResult } from \"./catalog-core.mjs\"", self.PAGE)
        self.assertIn("pickerCounts(STATS, x)", self.PAGE)
        self.assertIn("${renderPicker()}", self.PAGE)

    def test_every_picker_string_exists_once_per_language(self):
        keys = set(re.findall(r"\b(pick_[a-z_]+):", self.PAGE))
        self.assertGreaterEqual(keys, {"pick_h", "pick_p", "pick_yes", "pick_no", "pick_source", "pick_counts", "pick_counts_about"})
        for key in keys:
            with self.subTest(key=key):
                self.assertEqual(len(re.findall(rf"\b{key}:", self.PAGE)), 2)
        self.assertIn("not a recommendation", self.PAGE.split("pick_p:", 1)[1].split("pick_yes", 1)[0])


if __name__ == "__main__":
    unittest.main()
