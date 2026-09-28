"""docs/patterns.zh-CN.md: the patterns page in Chinese, held to the English
page's rules (I24).

The Chinese README and the Chinese pattern pages linked docs/patterns.md, in
English. A model wrote a Chinese rendering from it; its first lines say so and
that the English page governs. lint_docs holds it to every pattern in
patterns.json, each section closing with its generated line, and checks its
model strings and limits against compat.json, for which the limit rules
learned the Chinese phrasings. The structure of the two pages is compared here
section by section, so a paragraph left out of the rendering shows.

Only the hand-written parts of the committed pages are read; the generated
lines render in memory (CI runs unit tests before it regenerates).
"""

from __future__ import annotations

import copy
import json
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import _stats  # noqa: E402
import build_docs  # noqa: E402
import build_readme  # noqa: E402
import lint_docs  # noqa: E402
from readme import pages, rows, strings  # noqa: E402

EN_DOC, ZH_DOC = "docs/patterns.md", "docs/patterns.zh-CN.md"
EN = (ROOT / EN_DOC).read_text(encoding="utf-8")
ZH = (ROOT / ZH_DOC).read_text(encoding="utf-8")
CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
RETIRED = json.loads((ROOT / "retired.json").read_text(encoding="utf-8"))
PATTERN_KEYS = [p["key"] for p in json.loads((ROOT / "patterns.json").read_text())["patterns"]]
# The paragraph labels of a pattern's section, English and as rendered.
LABELS = (
    ("**The decision:**", "**决策：**"),
    ("**Why here:**", "**为什么适合：**"),
    ("**Shape:**", "**形态：**"),
    ("**When not to", "**何时不该用"),
    ("**Note:**", "**注：**"),
)


def without_blocks(text: str) -> str:
    return lint_docs.BLOCK.sub("", text)


def paragraphs(text: str) -> list[str]:
    """Blank-line-separated chunks outside the generated blocks."""
    return [chunk for chunk in re.split(r"\n\s*\n", without_blocks(text)) if chunk.strip()]


def links(text: str) -> set[str]:
    """Link targets outside the generated blocks, less the two pages' links to each other."""
    found = set(re.findall(r"\]\(([^)\s]+)\)", without_blocks(text)))
    return {link for link in found if link not in ("patterns.md", "patterns.zh-CN.md")}


class ProvenanceTest(unittest.TestCase):
    def test_the_chinese_page_says_a_model_wrote_it_and_the_english_governs(self):
        head = "\n".join(ZH.splitlines()[:6])
        self.assertIn("由模型根据英文版 [docs/patterns.md](patterns.md) 译写", head)
        self.assertIn("以英文版为准", head)
        self.assertIn("<sub>[English](patterns.md)</sub>", head)

    def test_the_english_page_links_the_chinese_one(self):
        self.assertIn("<sub>[中文](patterns.zh-CN.md)</sub>", "\n".join(EN.splitlines()[:4]))


class StructureTest(unittest.TestCase):
    def test_the_same_patterns_in_the_same_order(self):
        self.assertEqual(list(lint_docs.pattern_sections(EN)), PATTERN_KEYS)
        self.assertEqual(list(lint_docs.pattern_sections(ZH)), PATTERN_KEYS)

    def test_each_section_has_the_same_paragraphs(self):
        en, zh = lint_docs.pattern_sections(EN), lint_docs.pattern_sections(ZH)
        for key in PATTERN_KEYS:
            with self.subTest(key=key):
                for english, chinese in LABELS:
                    self.assertEqual(en[key].count(english), zh[key].count(chinese), english)
                self.assertEqual(len(paragraphs(en[key])), len(paragraphs(zh[key])))

    def test_the_whole_page_has_as_many_paragraphs(self):
        # Headings, paragraphs, lists and tables alike; the English is wrapped, the Chinese is not.
        self.assertEqual(len(paragraphs(EN)), len(paragraphs(ZH)) - 1)  # the provenance note

    def test_the_same_links_tables_and_generated_values(self):
        self.assertEqual(links(EN), links(ZH))
        table = re.compile(r"^\|.*\|$", re.M)
        self.assertEqual(len(table.findall(EN)), len(table.findall(ZH)))
        inline = re.compile(r"<!--n:([a-z_]+)-->")
        self.assertEqual(inline.findall(EN), inline.findall(ZH))
        self.assertEqual(EN.count("\n---\n"), ZH.count("\n---\n"))

    def test_lint_docs_holds_the_chinese_page_to_every_pattern(self):
        self.assertIn(ZH_DOC, lint_docs.PATTERN_DOCS)
        cut = ZH.replace("\n## retry-control\n", "\n## retry-kontrol\n")
        problems = lint_docs.check_pattern_docs({EN_DOC: EN, ZH_DOC: cut})
        self.assertEqual(
            problems,
            [
                f"{ZH_DOC}: no `## retry-control` section for a pattern in patterns.json",
                f"{ZH_DOC}: `## retry-kontrol` is not a pattern in patterns.json",
            ],
        )
        unmarked = ZH.replace("<!-- catalogued-fan-out:start -->", "")
        (problem,) = lint_docs.check_pattern_docs({EN_DOC: EN, ZH_DOC: unmarked})
        self.assertTrue(problem.startswith(f"{ZH_DOC}: the `## fan-out` section has no"))

    def test_it_is_hand_written_around_generated_lines(self):
        import regenerate

        self.assertIn(ZH_DOC, regenerate.OUTPUTS)
        self.assertNotIn(ZH_DOC, lint_docs.GENERATED)
        self.assertIn(ZH_DOC, lint_docs.hand_written_files())


class GeneratedLinesTest(unittest.TestCase):
    def test_each_section_ends_with_its_count_in_chinese(self):
        docs = {str(path.relative_to(ROOT)): text for path, text in build_docs.render().items()}
        sections = lint_docs.pattern_sections(docs[ZH_DOC])
        counts = _stats.compute()["by_pattern"]
        for key in PATTERN_KEYS:
            with self.subTest(key=key):
                line = sections[key].split(f"<!-- catalogued-{key}:start -->\n", 1)[1].split("\n<!--", 1)[0]
                self.assertEqual(line, build_docs.catalogued_block(key, counts[key], "zh"))
                self.assertIn(f"目录中的**{rows.label(rows.PATTERN_LABELS, key, 'zh')}**", line)
                self.assertIn(f"({rows.site_link(key, 'zh')})", line)
                if counts[key]:
                    self.assertIn(f"共 {counts[key]} 条", line)
                    self.assertIn(f"(by-pattern/{key}.zh-CN.md)", line)


class VendorFactsTest(unittest.TestCase):
    FACTS = lint_docs.vendor_facts()

    def problems(self, text: str) -> list[str]:
        return lint_docs.check_vendor_facts("x.md", text, self.FACTS)

    def test_the_chinese_limits_are_read(self):
        self.assertEqual(self.problems("最多 255 个选项；2–10 级；2 到 10 个有序级别；64k token，32k token；64k 上下文"), [])
        for wrong in ("最多 256 个选项", "2–11 级", "3 到 10 个等级", "128k token", "96k 上下文"):
            with self.subTest(text=wrong):
                self.assertEqual(len(self.problems(wrong)), 1)

    def test_a_projects_own_numbers_are_not_limits(self):
        self.assertEqual(self.problems("每批最多 16 行、共享整页文本；1–3 次重试；20 个工具"), [])

    def test_a_model_string_next_to_chinese_is_read_whole(self):
        self.assertEqual(lint_docs.MODEL.search("用typesafe-ai/jev调用").group(0), "typesafe-ai/jev")
        self.assertEqual(lint_docs.MODEL.search("模型jev-1.13.0呢").group(0), "jev-1.13.0")
        self.assertEqual(len(self.problems("当前模型jev-9.9，不是别的")), 1)
        self.assertEqual(self.problems("当前模型jev-1.13.0，已记录"), [])

    def test_the_chinese_page_states_each_limit_where_a_rule_reads_it(self):
        read = {what for what, rx in lint_docs.LIMIT_RULES if rx.search(ZH)}
        self.assertEqual(read, {"choice options", "score levels", "context"})
        self.assertEqual(self.problems(ZH), [])
        self.assertEqual(len(self.problems(ZH.replace("255 个选项", "256 个选项", 1))), 1)


class LinksTest(unittest.TestCase):
    def test_chinese_pattern_pages_link_the_chinese_page_and_the_english_one_governs(self):
        self.assertEqual(pages.PATTERNS_DOC, {"en": "../patterns.md", "zh": "../patterns.zh-CN.md"})
        for key, members in rows.group_by_pattern(copy.deepcopy(CATALOG)).items():
            if not members:
                continue
            with self.subTest(key=key):
                zh = pages.render_page(key, members, strings.ZH)
                line = pages.design_line(key, strings.ZH)
                self.assertIn(line + "\n", zh)
                self.assertIn(f"](../patterns.zh-CN.md#{key})", line)
                self.assertIn(f"](../patterns.md#{key})", line)
                self.assertIn("以英文版为准", line)
                self.assertNotIn("patterns.zh-CN.md", pages.render_page(key, members, strings.EN))

    def test_the_overview_pages_unindexed_note_links_its_own_language(self):
        members = rows.group_by_pattern(copy.deepcopy(CATALOG))["overview"]
        self.assertIn(
            rows.marked(strings.ZH, "unindexed_page", n=sum(map(_stats.not_indexed_by_pattern, members)),
                        patterns="../patterns.zh-CN.md#overview", queue="../review-queue.md#unsorted-overview"),
            pages.render_page("overview", members, strings.ZH),
        )

    def test_the_chinese_readme_links_the_chinese_page(self):
        zh = build_readme.render(copy.deepcopy(CATALOG), copy.deepcopy(RETIRED), strings.ZH)
        en = build_readme.render(copy.deepcopy(CATALOG), copy.deepcopy(RETIRED), strings.EN)
        self.assertIn(f"[{strings.ZH['l_patterns']}](docs/patterns.zh-CN.md) · ", zh)
        self.assertIn("| [`docs/patterns.zh-CN.md`](docs/patterns.zh-CN.md) |", zh)
        self.assertNotIn("](docs/patterns.md)", zh)
        self.assertIn(f"[{strings.EN['l_patterns']}](docs/patterns.md) · ", en)
        self.assertNotIn("patterns.zh-CN.md", en)


if __name__ == "__main__":
    unittest.main()
