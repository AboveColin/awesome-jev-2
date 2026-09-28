"""Machine-translation signals and the translation queue (I19).

scripts/zh_audit.py compares each machine-translated Chinese summary
(`zh_machine: true`) with its English and writes docs/zh-queue.md, most-starred
band first. Its signals are text comparisons: they go to that page and, for a
row a change adds, to a lint warning, and nowhere else. No README row, pattern
page or site card shows them; those show only the (机翻) mark. These tests pin
the three rules, the page's order and cap, that only new rows are warned
about (counted from where the branch left its base), that check.py hands lint
that base, and that the READMEs and llms.txt give the split.

Everything renders in memory: CI runs the unit tests before regenerating, so a
test must not read a committed generated file.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

TESTS = pathlib.Path(__file__).resolve().parent
SCRIPTS = TESTS.parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TESTS))

import _stats  # noqa: E402
import build_docs  # noqa: E402
import build_readme  # noqa: E402
import check  # noqa: E402
import lint  # noqa: E402
import lint_docs  # noqa: E402
import regenerate  # noqa: E402
import zh_audit  # noqa: E402
from readme import strings  # noqa: E402
from readme.rows import STAR_BANDS, star_band  # noqa: E402
from test_check import FakeRun  # noqa: E402
from test_lint import MINIMAL, row  # noqa: E402

CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
RETIRED = json.loads((ROOT / "retired.json").read_text(encoding="utf-8"))
GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

# Summaries from the bulk pass, copied here so a person fixing the real rows
# (the queue's purpose) never breaks a test.
PHISHING_EN = "Jev (TypeSafe) vs Claude Haiku 4.5 on 2 000 phishing emails: accuracy, calibration, latency, cost."
PHISHING_ZH = "在 2000 封钓鱼邮件上对比 Jev 与一个轻量 LLM：准确率、校准度、延迟、成本。"
SEO_EN = (
    "100% free ₹0 agent-first SEO & GEO CLI suite and MCP server in Rust replacing Semrush and OpenSEO via "
    "DuckDuckGo and TypeSafe Jev System One https://akashpriyadarshii.github.io/jev-seo/"
)
SEO_ZH = "用 Rust 写的 agent 优先 SEO/GEO CLI 套件与 MCP server。"


def entry(slug: str, summary: str, summary_zh: str, *, machine: bool = True, stars=None) -> dict:
    found = {"slug": slug, "title": slug.replace("-", " ").title(), "summary": summary, "summary_zh": summary_zh}
    if machine:
        found["zh_machine"] = True
    if stars is not None:
        found["stars"] = stars
    return found


class NumbersTest(unittest.TestCase):
    def test_digit_groups_are_one_number(self):
        self.assertEqual(zh_audit.numbers("2 000 emails, 2,000 more, 2000 in all"), ["2000"])

    def test_full_width_digits_and_no_break_spaces_are_plain(self):
        self.assertEqual(zh_audit.numbers("２０００ 封，3 000 条"), ["2000", "3000"])

    def test_a_list_or_a_decimal_comma_is_not_a_group(self):
        self.assertEqual(zh_audit.numbers("1, 2 and 4,5 or 12,3456"), ["1", "2", "4", "5", "12", "3456"])

    def test_decimals_and_versions_stay_whole(self):
        self.assertEqual(zh_audit.numbers("Haiku 4.5, v1.2.3 and 4.5 again"), ["4.5", "1.2.3"])

    def test_lost_numbers_are_the_englishs_in_its_order(self):
        self.assertEqual(zh_audit.lost_numbers(PHISHING_EN, PHISHING_ZH), ("4.5",))
        self.assertEqual(zh_audit.lost_numbers(SEO_EN, SEO_ZH), ("100", "0"))
        self.assertEqual(zh_audit.lost_numbers("24/7 support", "全天候支持"), ("24", "7"))
        self.assertEqual(zh_audit.lost_numbers("no figures here", "没有数字"), ())


class AuditTest(unittest.TestCase):
    def test_short_is_strictly_below_the_ratio(self):
        self.assertEqual(zh_audit.audit(entry("a", "abcdefghij", "一二三")).signals, ())
        self.assertEqual(zh_audit.audit(entry("a", "abcdefghij", "一二")).signals, ("short",))

    def test_ascii_is_strictly_above_the_share(self):
        self.assertEqual(zh_audit.audit(entry("a", "abcde", "abc一二")).signals, ())
        self.assertEqual(zh_audit.audit(entry("a", "abcde", "abcd一")).signals, ("ascii",))

    def test_signals_come_in_one_order(self):
        found = zh_audit.audit(entry("seo", SEO_EN, SEO_ZH))
        self.assertEqual(found.signals, ("short", "numbers", "ascii"))
        self.assertEqual(found.lost, ("100", "0"))
        self.assertEqual(zh_audit.SIGNALS, ("short", "numbers", "ascii"))

    def test_a_share_prints_on_the_side_of_its_rule(self):
        self.assertEqual(zh_audit.two_places(0.2996, up=False), "0.29")
        self.assertEqual(zh_audit.two_places(0.6004, up=True), "0.61")
        self.assertEqual(zh_audit.two_places(0.25, up=False), "0.25")
        # Exact hundredths print as themselves, whatever floating point makes of them.
        self.assertEqual(zh_audit.two_places(29 / 100, up=False), "0.29")
        self.assertEqual(zh_audit.two_places(57 / 100, up=False), "0.57")
        self.assertEqual(zh_audit.two_places(7 / 100, up=True), "0.07")

    def test_every_share_on_the_real_page_is_the_exact_one(self):
        # floor/ceiling of the exact fraction, the way two_places means it.
        from fractions import Fraction

        for e in zh_audit.machine(CATALOG):
            found = zh_audit.audit(e)
            english, chinese = e.get("summary", ""), e.get("summary_zh", "")
            ratio = Fraction(len(chinese), max(len(english), 1)) * 100
            share = Fraction(sum(ord(ch) < 128 for ch in chinese), max(len(chinese), 1)) * 100
            floor, ceiling = ratio.numerator // ratio.denominator, -(-share.numerator // share.denominator)
            with self.subTest(slug=found.slug):
                if "short" in found.signals:
                    self.assertEqual(zh_audit.two_places(found.ratio, up=False), f"{floor / 100:.2f}")
                if "ascii" in found.signals:
                    self.assertEqual(zh_audit.two_places(found.ascii, up=True), f"{ceiling / 100:.2f}")

    def test_the_real_split_is_the_one_stats_publishes(self):
        s = _stats.compute()
        self.assertEqual(len(zh_audit.machine(CATALOG)), s["zh_machine"])
        self.assertEqual(len(zh_audit.hand(CATALOG)), s["zh_hand"])
        self.assertEqual(s["zh_hand"] + s["zh_machine"], s["entries"])


# ★1k+ with no signal; ★100+ short; a person's ★10k+ short; ★10+ numbers;
# no stars and mostly ASCII; ★10+ and nothing to flag.
QUEUE = [
    entry("alpha", "An English sentence of some length.", "一句相当长的中文句子，意思相同。", stars=1500),
    entry("bravo", "A long English sentence that the Chinese shortens a lot.", "短。", stars=150),
    entry("charlie", "A long English sentence a person translated briefly.", "短。", machine=False, stars=20000),
    entry("delta", "Beats Haiku 4.5 on 2 000 emails.", "在 2000 封邮件上胜过一个轻量模型。", stars=12),
    entry("echo", "Mostly code names here.", "agent CLI for MCP servers 用", stars=None),
    entry("foxtrot", "Nothing to flag in this one.", "这一条没有可标的地方。", stars=15),
]


class QueueTest(unittest.TestCase):
    def test_every_machine_translation_at_the_top_band_then_flagged_ones(self):
        top, rest = zh_audit.split(QUEUE)
        self.assertEqual([e["slug"] for e in top], ["alpha", "bravo"])
        self.assertEqual([e["slug"] for e in rest], ["delta", "echo"])

    def test_within_a_band_more_signals_come_first_then_the_title(self):
        rows = [
            entry("a-one", "Beats 2 models by far.", "胜过 2 个模型，差距很大。", stars=40),
            entry("b-three", SEO_EN, SEO_ZH, stars=11),
            entry("c-one", "Beats 3 models by far.", "胜过三个模型，差距很大。", stars=99),
            entry("d-two", PHISHING_EN, "对比 Jev 与一个轻量模型。", stars=10),
        ]
        self.assertEqual([e["slug"] for e in zh_audit.queue_order(rows)], ["b-three", "d-two", "c-one", "a-one"])

    def test_the_page_lists_rows_by_band_and_never_a_count(self):
        page = zh_audit.render(QUEUE)
        listed = re.findall(r"^\| \[([a-z-]+)\]", page, flags=re.M)
        self.assertEqual(listed, ["alpha", "bravo", "delta", "echo"])
        for exact in ("1500", "150 ", "12 ", "20000"):
            self.assertNotIn(exact, page)
        self.assertIn("| ★1k+ | — |", page)
        self.assertIn("`numbers` `4.5`", page)

    def test_the_page_says_what_a_signal_is_in_both_languages(self):
        page = zh_audit.render(QUEUE)
        self.assertTrue(page.startswith(zh_audit.HEADER))
        self.assertIn(zh_audit.PROVENANCE, page)
        self.assertIn("not a verdict on the translation", page)
        self.assertIn("不是对译文的结论", page)
        self.assertIn("../CONTRIBUTING.md#claim-a-translation", page)
        self.assertIn("| `short` | ", page)
        self.assertIn("| 1 of 5 | 1 of 1 |", page)  # short: bravo; and the person's charlie
        self.assertNotIn("verified", page.lower())

    def test_a_long_list_is_capped_and_says_how_many_more(self):
        with mock.patch.object(zh_audit, "SHOWN", 1):
            page = zh_audit.render(QUEUE)
        self.assertIn("…and 1 more, in the same order", page)
        self.assertIn("另有 1 行未列出", page)
        self.assertNotIn("[echo]", page)

    def test_an_empty_list_says_so(self):
        page = zh_audit.render([QUEUE[2]])
        self.assertEqual(page.count("Nothing is on this list. · 此列表为空。"), 2)

    def test_stars_moved_within_their_band_change_nothing(self):
        def floor(stars):
            band = star_band(stars)
            return stars if not band else STAR_BANDS[band - 1][0]

        def ceiling(stars):
            band = star_band(stars)
            if stars is None or band == len(STAR_BANDS):
                return stars
            return STAR_BANDS[band][0] - 1

        before = zh_audit.render(CATALOG)
        for move in (floor, ceiling):
            with self.subTest(move=move.__name__):
                moved = [{**e, "stars": move(e.get("stars"))} if "stars" in e else e for e in CATALOG]
                self.assertEqual(zh_audit.render(moved), before)

    def test_json_lists_every_machine_translation(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(zh_audit.main(["--json"]), 0)
        report = json.loads(out.getvalue())
        self.assertEqual(len(report["rows"]), report["machine"]["rows"])
        self.assertEqual(report["machine"]["rows"] + report["hand"]["rows"], len(CATALOG))
        self.assertEqual(set(report["rules"]), set(zh_audit.SIGNALS))

    def test_check_fails_on_a_stale_page_and_passes_once_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "docs").mkdir()
            (root / "catalog.json").write_text(json.dumps(QUEUE), encoding="utf-8")
            with mock.patch.object(zh_audit, "ROOT", root), mock.patch.object(zh_audit, "OUT", root / "docs" / "zh-queue.md"):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
                    self.assertEqual(zh_audit.main(["--check"]), 1)
                    self.assertIn("docs/zh-queue.md is stale; run python3 scripts/zh_audit.py", err.getvalue())
                    self.assertEqual(zh_audit.main([]), 0)
                    self.assertEqual(zh_audit.main(["--check"]), 0)
            self.assertEqual((root / "docs" / "zh-queue.md").read_text(encoding="utf-8"), zh_audit.render(QUEUE))


class NewRowWarningTest(unittest.TestCase):
    OLD = entry("old-row", PHISHING_EN, PHISHING_ZH)

    def test_only_a_new_machine_translation_that_drops_a_number(self):
        catalog = [
            self.OLD,
            entry("new-lossy", PHISHING_EN, PHISHING_ZH),
            entry("new-by-hand", PHISHING_EN, PHISHING_ZH, machine=False),
            entry("new-whole", "Beats 2 models.", "胜过 2 个模型。"),
        ]
        found = zh_audit.new_translation_warnings(catalog, [self.OLD])
        self.assertEqual(len(found), 1)
        where, message = found[0]
        self.assertEqual(where, "catalog.json[1]")
        self.assertTrue(message.startswith("new-lossy: new row whose machine-translated summary_zh leaves out 4.5"))
        self.assertIn("not a reading", message)

    def test_a_filed_row_is_never_warned_about(self):
        self.assertEqual(zh_audit.new_translation_warnings([self.OLD], [self.OLD]), [])


def git(root: pathlib.Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "init.defaultBranch=main", *args],
        cwd=root, capture_output=True, text=True, env={**os.environ, **GIT_ENV}, check=True,
    )
    return done.stdout.strip()


# A row lint accepts whose machine translation drops "4.5".
LOSSY = row(
    MINIMAL, slug="lossy-row", url="https://github.com/someone/lossy-row", zh_machine=True,
    summary="Beats Claude Haiku 4.5 on 2 000 phishing emails.", summary_zh="在 2000 封钓鱼邮件上胜过一个轻量 LLM。",
)


class LintBaseTest(unittest.TestCase):
    """lint.py --base REV in a scratch repository: warnings for rows the branch adds."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)
        for name in ("ROOT", "CATALOG", "RETIRED"):
            self.addCleanup(setattr, lint, name, getattr(lint, name))
        lint.ROOT, lint.CATALOG, lint.RETIRED = self.root, self.root / "catalog.json", self.root / "retired.json"
        patcher = mock.patch.dict(os.environ, GIT_ENV)
        patcher.start()
        self.addCleanup(patcher.stop)
        git(self.root, "init", "--quiet")

    def commit(self, rows: list[dict], message: str) -> None:
        lint.CATALOG.write_text(json.dumps(rows), encoding="utf-8")
        lint.RETIRED.write_text("[]", encoding="utf-8")
        git(self.root, "add", "catalog.json", "retired.json")
        git(self.root, "commit", "--quiet", "-m", message)

    def run_lint(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = lint.main(list(argv))
        return status, out.getvalue(), err.getvalue()

    def test_a_row_the_branch_adds_is_warned_about_and_nothing_fails(self):
        self.commit([MINIMAL], "base")
        git(self.root, "checkout", "--quiet", "-b", "feature")
        self.commit([MINIMAL, LOSSY], "add a row")
        status, out, err = self.run_lint("--base", "main")
        self.assertEqual((status, err), (0, ""))
        self.assertIn("note: 1 row(s) added since main (", out)
        self.assertIn("1 with a machine-translated summary_zh; 1 leave out a number the English gives", out)
        self.assertIn(
            "warning: catalog.json[1]: lossy-row: new row whose machine-translated summary_zh leaves out 4.5 "
            "from the English summary",
            out,
        )

    def test_uncommitted_rows_count_as_added(self):
        self.commit([MINIMAL], "base")
        lint.CATALOG.write_text(json.dumps([MINIMAL, LOSSY]), encoding="utf-8")
        self.assertIn("lossy-row: new row", self.run_lint("--base", "main")[1])

    def test_rows_are_counted_from_where_the_branch_left_the_base(self):
        # main later drops a row the branch still has: that row is not the branch's.
        self.commit([MINIMAL, LOSSY], "base")
        git(self.root, "checkout", "--quiet", "-b", "feature")
        git(self.root, "checkout", "--quiet", "main")
        self.commit([MINIMAL], "main retires a row")
        git(self.root, "checkout", "--quiet", "feature")
        status, out, _ = self.run_lint("--base", "main")
        self.assertEqual(status, 0)
        self.assertIn("note: 0 row(s) added since main", out)
        self.assertNotIn("warning:", out)

    def test_no_base_no_warning(self):
        self.commit([MINIMAL, LOSSY], "base")
        self.assertEqual(self.run_lint(), (0, "checked 2 catalog entries and 0 retired\n", ""))

    def test_an_unreadable_base_is_a_note_not_a_failure(self):
        self.commit([MINIMAL, LOSSY], "base")
        status, out, err = self.run_lint("--base", "no-such-ref")
        self.assertEqual((status, err), (0, ""))
        self.assertIn("note: no new-row translation warnings; catalog.json at no-such-ref cannot be read", out)
        self.assertNotIn("warning:", out)


class CheckBaseTest(unittest.TestCase):
    """check.py hands lint the base its mode compares with, and no base otherwise."""

    def test_the_base_for_each_mode(self):
        exists, absent = (lambda rev: True), (lambda rev: False)
        cases = [
            (check.Options(ci=True), "pull_request", exists, ["--base", "HEAD^1"]),
            (check.Options(ci=True), "push", exists, []),
            (check.Options(ci=True), "schedule", exists, []),
            (check.Options(), "", exists, []),
            (check.Options(fix=True), "", exists, ["--base", "origin/main"]),
            (check.Options(fix=True), "", absent, []),
            (check.Options(base="upstream/main"), "", exists, ["--base", "upstream/main"]),
        ]
        for opts, event, commit_exists, expected in cases:
            with self.subTest(opts=opts, event=event):
                self.assertEqual(check.base_args(opts, event, commit_exists)[0], expected)
        self.assertIn("not a commit", check.base_args(check.Options(fix=True), "", absent)[1])

    def test_only_lint_takes_the_base(self):
        self.assertEqual([s.name for s in check.STEPS if s.base], ["lint"])

    def test_the_runner_passes_it(self):
        pr = FakeRun(check.Options(ci=True), event="pull_request")
        self.assertIn([sys.executable, "scripts/lint.py", "--base", "HEAD^1"], pr.calls)
        self.assertIn("lint — rows the pull request adds are those not in HEAD^1", pr.out.getvalue())
        plain = FakeRun(check.Options())
        self.assertIn([sys.executable, "scripts/lint.py"], plain.calls)
        fix = FakeRun(check.Options(fix=True))
        self.assertIn([sys.executable, "scripts/lint.py", "--base", "origin/main"], fix.calls)


class WiringTest(unittest.TestCase):
    def test_the_page_is_generated_and_registered(self):
        self.assertIn("zh_audit.py", [name for name, _ in regenerate.GENERATORS])
        self.assertIn("docs/zh-queue.md", regenerate.OUTPUTS)
        self.assertIn("docs/zh-queue.md", lint_docs.GENERATED)

    def test_no_surface_but_the_queue_and_lint_reads_the_signals(self):
        importers = sorted(
            path.relative_to(SCRIPTS).as_posix()
            for path in [*SCRIPTS.glob("*.py"), *SCRIPTS.glob("readme/*.py"), *(ROOT / "src").rglob("*.py")]
            if re.search(r"^\s*(from zh_audit import|import zh_audit)", path.read_text(encoding="utf-8"), re.M)
        )
        self.assertEqual(importers, ["lint.py"])
        for path in (ROOT / "site").iterdir():
            if path.suffix in {".html", ".mjs", ".js", ".css"}:
                with self.subTest(path=path.name):
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("zh_audit", text)
                    self.assertNotIn("zh-queue", text)


class PublishedSplitTest(unittest.TestCase):
    STATS = {"zh_hand": 7, "zh_machine": 13, "entries": 20}

    @classmethod
    def setUpClass(cls):
        real = _stats.compute()
        with mock.patch.object(_stats, "compute", return_value={**real, **cls.STATS}):
            cls.readmes = {
                pack["lang_code"]: build_readme.render(copy.deepcopy(CATALOG), copy.deepcopy(RETIRED), pack)
                for pack in (strings.EN, strings.ZH)
            }
            cls.llms = build_docs.render()[ROOT / "llms.txt"]

    def test_the_readmes_give_the_split_and_link_the_queue(self):
        en, zh = self.readmes["en"], self.readmes["zh"]
        self.assertIn("**Who wrote the Chinese** — 7 of 20 rows have a Chinese summary a person wrote", en)
        self.assertIn("a model translated the other 13", en)
        self.assertIn("**中文是谁写的** —— 20 行中有 7 行的中文摘要由人撰写；其余 13 行由模型翻译", zh)
        for text in (en, zh):
            self.assertIn("(docs/zh-queue.md)", text)
            self.assertIn("(CONTRIBUTING.md#claim-a-translation)", text)

    def test_the_model_written_chinese_is_marked(self):
        self.assertIn("verified_translations", strings.ZH_MACHINE)
        line = next(l for l in self.readmes["zh"].splitlines() if l.startswith("- **中文是谁写的**"))
        self.assertTrue(line.endswith(" <sub>(机翻)</sub>"))
        line = next(l for l in self.readmes["en"].splitlines() if l.startswith("- **Who wrote the Chinese**"))
        self.assertNotIn("<sub>(机翻)</sub>", line)

    def test_llms_txt_gives_the_split(self):
        self.assertEqual(build_docs.inline_values(self.STATS | _stats.compute() | self.STATS)["zh_hand"], 7)
        self.assertIn("the Chinese summary of <!--n:zh_hand-->7<!--/n--> rows", self.llms)
        self.assertIn("the other <!--n:zh_machine-->13<!--/n-->", self.llms)
        self.assertIn("docs/zh-queue.md", self.llms)

    def test_the_public_pitch_is_unchanged(self):
        self.assertNotIn("zh_hand", json.dumps(_stats.pitch_public(_stats.compute())))


class ContributorDocsTest(unittest.TestCase):
    def test_contributing_explains_claiming_a_translation(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("\n## Claim a translation\n", text)
        section = text.split("\n## Claim a translation\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("keep `zh_machine: true`", section)
        self.assertIn("add a sentence to `notes`", section)
        self.assertIn("Only a translation you wrote yourself takes the flag off", section)
        self.assertIn("do not re-translate rows in bulk", section)

    def test_the_template_and_schema_say_who_clears_the_flag(self):
        template = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
        self.assertIn("docs/zh-queue.md", template)
        schema = json.loads((ROOT / "schema" / "entry.schema.json").read_text(encoding="utf-8"))
        self.assertIn("only a person's own translation clears it", schema["properties"]["zh_machine"]["description"])

    def test_method_records_the_change(self):
        self.assertIn(
            "Since 2026-09-27, the machine translations are compared with their English",
            (ROOT / "docs" / "method.md").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
