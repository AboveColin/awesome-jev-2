"""build_readme.py is a thin command over the scripts/readme/ package (I11).

The split must not change a byte of what is generated, and check.py's strict
generated-files step proves that on the real catalogue. These tests pin the
shape instead: every name another script reads from build_readme still
resolves, nothing patches the shell (a patch there never reaches the package),
render() takes no date, the reading map lists exactly the sections render()
writes, and no function grows back into the 310-line render() it replaced.
"""

from __future__ import annotations

import ast
import copy
import inspect
import json
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_readme  # noqa: E402
from readme import pages, rows, sections, strings  # noqa: E402

SHELL = ROOT / "scripts" / "build_readme.py"
PACKAGE = ROOT / "scripts" / "readme"
MODULES = (rows, strings, sections, pages)
MAX_FUNCTION_LINES = 80


def python_files() -> list[pathlib.Path]:
    """Every .py under scripts/ and tests/ whose text names build_readme.

    Both scans below look for the name build_readme, which a file cannot use
    without spelling it, so the filter drops nothing they could find. It also
    keeps them from parsing files that need a newer Python than the 3.11 floor
    CONTRIBUTING.md states (discover_candidates.py needed 3.12 for an f-string
    until I05), which made these tests error on 3.11 for a file that never
    mentions the shell.
    """
    return sorted(
        path
        for folder in (ROOT / "scripts", ROOT / "tests")
        for path in folder.rglob("*.py")
        if "__pycache__" not in path.parts and "build_readme" in path.read_text(encoding="utf-8")
    )


def parse(path: pathlib.Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def is_patch(node: ast.AST) -> bool:
    """`patch`, `mock.patch` or `unittest.mock.patch`."""
    return (isinstance(node, ast.Name) and node.id == "patch") or (
        isinstance(node, ast.Attribute) and node.attr == "patch"
    )


def is_shell(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and node.id == "build_readme"


def rebinds_shell(node: ast.AST) -> bool:
    """Whether `node` replaces or removes a name on the build_readme module."""
    if isinstance(node, ast.Attribute) and isinstance(node.ctx, (ast.Store, ast.Del)):
        return is_shell(node.value)
    if not isinstance(node, ast.Call) or not node.args:
        return False
    first, func = node.args[0], node.func
    if isinstance(func, ast.Name) and func.id in ("setattr", "delattr"):
        return is_shell(first)
    if isinstance(func, ast.Attribute) and func.attr in ("object", "multiple") and is_patch(func.value):
        return is_shell(first)
    if is_patch(func):
        return (
            isinstance(first, ast.Constant)
            and isinstance(first.value, str)
            and first.value.startswith("build_readme.")
        )
    return False


class ShellTest(unittest.TestCase):
    def test_exported_names_are_the_package_objects(self):
        self.assertIn("main", build_readme.__all__)
        for name in build_readme.__all__:
            if name == "main":
                continue
            with self.subTest(name=name):
                value = getattr(build_readme, name)
                homes = [m.__name__ for m in MODULES if getattr(m, name, None) is value]
                self.assertTrue(homes, f"build_readme.{name} is not an object of scripts/readme/")

    def test_every_name_a_caller_reads_is_exported(self):
        used: dict[str, set[str]] = {}
        for path in python_files():
            if path == SHELL or PACKAGE in path.parents:
                continue
            for node in ast.walk(parse(path)):
                if (
                    isinstance(node, ast.Attribute)
                    and isinstance(node.value, ast.Name)
                    and node.value.id == "build_readme"
                    and not node.attr.startswith("__")
                ):
                    used.setdefault(node.attr, set()).add(str(path.relative_to(ROOT)))
        self.assertIn("render", used, "the scan should find the existing callers")
        missing = {name: sorted(where) for name, where in used.items() if name not in build_readme.__all__}
        self.assertEqual(missing, {}, "export these from build_readme.py, or import them from readme.*")

    def test_nothing_patches_the_shell(self):
        """patch.object(build_readme, "X", ...) rebinds the shell's copy of X.
        The package never reads that copy, so the patch would silently do
        nothing. Patch the module that uses the name (readme.sections, ...).

        Every spelling this repository's tests use counts: patch.object and
        mock.patch.object (or unittest.mock.patch.object), patch.multiple,
        a "build_readme.X" target string, setattr, and plain assignment."""
        offenders = []
        for path in python_files():
            for node in ast.walk(parse(path)):
                if rebinds_shell(node):
                    offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")
        self.assertEqual(offenders, [])

    def test_the_patch_scan_sees_every_spelling(self):
        """The scan above must not pass because it looks for one spelling only."""
        caught = [
            'patch.object(build_readme, "START_HERE", [])',
            'mock.patch.object(build_readme, "START_HERE", [])',
            'unittest.mock.patch.object(build_readme, "ROOT", None)',
            "patch.multiple(build_readme, START_HERE=[])",
            'patch("build_readme.START_HERE", [])',
            'mock.patch("build_readme.ROOT", None)',
            'setattr(build_readme, "ROOT", None)',
            "build_readme.START_HERE = []",
            "del build_readme.ROOT",
        ]
        allowed = [
            'patch.object(sections, "START_HERE", [])',
            'mock.patch.object(readme.sections, "ROOT", None)',
            'patch("readme.sections.START_HERE", [])',
            'patch.dict(build_readme.EN, {"lang_code": "en"})',
            "build_readme.render([], [], build_readme.EN)",
        ]
        for source in caught + allowed:
            with self.subTest(source=source):
                found = any(rebinds_shell(node) for node in ast.walk(ast.parse(source)))
                self.assertEqual(found, source in caught)

    def test_shell_defines_only_main(self):
        defined = [
            node.name
            for node in parse(SHELL).body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ]
        self.assertEqual(defined, ["main"])


class NoClockTest(unittest.TestCase):
    """Generated files never hold a time-relative value, so the README
    generator has no reason to read the date (the old `today` was unused)."""

    def test_render_takes_no_date(self):
        self.assertEqual(list(inspect.signature(build_readme.render).parameters), ["catalog", "retired", "strings"])

    def test_generator_imports_no_clock(self):
        for path in [SHELL, *sorted(PACKAGE.glob("*.py"))]:
            imported = set()
            for node in ast.walk(parse(path)):
                if isinstance(node, ast.Import):
                    imported |= {alias.name.split(".")[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                    imported.add(node.module.split(".")[0])
            with self.subTest(path=path.name):
                self.assertFalse(imported & {"datetime", "time"}, sorted(imported))


class ShapeTest(unittest.TestCase):
    def test_no_function_in_the_package_exceeds_the_limit(self):
        for path in sorted(PACKAGE.glob("*.py")):
            for node in ast.walk(parse(path)):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    length = node.end_lineno - node.lineno + 1
                    with self.subTest(function=f"{path.name}:{node.name}"):
                        self.assertLessEqual(
                            length, MAX_FUNCTION_LINES,
                            f"{path.name}:{node.lineno} {node.name}() is {length} lines; split it",
                        )

    def test_measured_means_a_benchmark_its_vendor_did_not_publish(self):
        # The same rule as the site's isIndependentReport (site/catalog-core.mjs).
        self.assertTrue(sections.is_measured({"kind": "benchmark"}))
        self.assertTrue(sections.is_measured({"kind": "benchmark", "flags": ["unverified-claims"]}))
        self.assertFalse(sections.is_measured({"kind": "benchmark", "flags": ["vendor-reported"]}))
        self.assertFalse(sections.is_measured({"kind": "project"}))

    def test_reading_map_lists_exactly_the_sections_render_writes(self):
        catalog = json.loads(build_readme.CATALOG.read_text(encoding="utf-8"))
        retired = json.loads(build_readme.RETIRED.read_text(encoding="utf-8"))
        for pack in (build_readme.EN, build_readme.ZH):
            with self.subTest(lang=pack["lang_code"]):
                readme = build_readme.render(copy.deepcopy(catalog), copy.deepcopy(retired), pack)
                headings = re.findall(r"^## (.+)$", readme, re.M)
                has_measured = any(sections.is_measured(entry) for entry in catalog)
                listed = [
                    re.match(r"\d\d \[(.+?)\]\(#", item).group(1)
                    for item in build_readme.section_nav(pack, has_measured=has_measured)
                ]
                self.assertEqual(headings, listed)


if __name__ == "__main__":
    unittest.main()
