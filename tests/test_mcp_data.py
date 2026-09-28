"""Where the MCP server's data comes from, tested rung by rung (I33).

src/awesome_jev_mcp/data.py walks a ladder — AWESOME_JEV_CATALOG, a checkout
above the package, GitHub with the cached ETags, the cache, the snapshot in the
wheel — and says which rung answered in every result. These tests run inside a
checkout, which would always answer, so they start the checkout search in a
temporary directory (`load(checkout_from=...)`), point the cache and the
bundled snapshot at temporary directories, and stand a fake in for urlopen that
plays raw.githubusercontent.com: 200 with an ETag, 304 when the ETag matches,
or a failure. Standard library only; nothing reaches the network.
"""

from __future__ import annotations

import email.message
import json
import os
import pathlib
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from awesome_jev_mcp import data  # noqa: E402


def payload(*slugs: str, checked: tuple[str, ...] = ()) -> dict[str, object]:
    """The five files' contents; `slugs` tells which rung answered."""
    rows = [{"slug": s} for s in slugs]
    for row, date in zip(rows, checked):
        row["checked"] = date
    return {
        "catalog.json": rows,
        "compat.json": {"platforms": [], "tag": slugs[0] if slugs else ""},
        "patterns.json": {"patterns": [{"key": "overview"}]},
        "taxonomy.json": {"flags": [{"key": "not-jev", "blurb_en": "Never calls it."}]},
        "collections.json": {"collections": [{"id": "first-call", "entries": []}]},
    }


def write(directory: pathlib.Path, files: dict[str, object], *, skip: str = "") -> pathlib.Path:
    directory.mkdir(parents=True, exist_ok=True)
    for name, body in files.items():
        if name != skip:
            (directory / name).write_text(json.dumps(body))
    return directory


class _Response:
    def __init__(self, body: bytes, etag: str | None):
        self.body = body
        self.headers = email.message.Message()
        if etag:
            self.headers["ETag"] = etag

    def read(self) -> bytes:
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> bool:
        return False


class FakeGitHub:
    """raw.githubusercontent.com for the files data.py fetches. `files` maps a name to
    its current body; `fail` maps a name to the exception raised instead."""

    def __init__(self, files: dict[str, object], fail: dict[str, BaseException] | None = None, raw: dict | None = None):
        self.files = files
        self.fail = fail or {}
        self.raw = raw or {}
        self.requests: list[tuple[str, str | None, float | None]] = []
        self.errors: list[urllib.error.HTTPError] = []

    def http_error(self, url: str, code: int, msg: str) -> urllib.error.HTTPError:
        """An HTTPError like urllib's, closed when the test ends (Python 3.14
        warns about one garbage-collected open)."""
        error = urllib.error.HTTPError(url, code, msg, email.message.Message(), None)
        self.errors.append(error)
        return error

    def close(self) -> None:
        for error in self.errors:
            error.close()

    @staticmethod
    def etag(name: str, body: object) -> str:
        return f'W/"{name}-{abs(hash(json.dumps(body))) % 10**8}"'

    def __call__(self, request, timeout=None):
        name = request.full_url.removeprefix(data.RAW)
        condition = request.get_header("If-none-match")
        self.requests.append((request.full_url, condition, timeout))
        if name in self.fail:
            raise self.fail[name]
        body = self.files[name]
        tag = self.etag(name, body)
        if condition == tag:
            raise self.http_error(request.full_url, 304, "Not Modified")
        return _Response(self.raw.get(name, json.dumps(body).encode()), tag)


class LadderTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self.outside = self.tmp / "installed" / "site-packages" / "awesome_jev_mcp"
        self.outside.mkdir(parents=True)
        self.assertIsNone(data._find_checkout(self.outside), "the temporary directory sits inside a checkout")
        self.cache = self.tmp / "cache"
        self.bundled = self.tmp / "bundled"
        env = mock.patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop("AWESOME_JEV_CATALOG", None)
        for patcher in (mock.patch.object(data, "cache_dir", return_value=self.cache),
                        mock.patch.object(data, "BUNDLED", self.bundled)):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.github = FakeGitHub(payload("net-a", "net-b", checked=("2026-09-01", "2026-09-20")))
        self.addCleanup(self.github.close)
        net = mock.patch.object(data.urllib.request, "urlopen", self.github)
        net.start()
        self.addCleanup(net.stop)

    def load(self, start: pathlib.Path | None = None):
        loaded = data.load(checkout_from=start or self.outside)
        return [row["slug"] for row in loaded.catalog], loaded.provenance

    def checkout(self, slugs=("co",), *, skip: str = "") -> pathlib.Path:
        repo = self.tmp / "repo"
        write(repo, payload(*slugs), skip=skip)
        (repo / ".git").mkdir(exist_ok=True)
        return repo

    # --- 1 and 2: local sources ------------------------------------------------

    def test_the_override_beats_a_checkout_and_the_network(self):
        override = write(self.tmp / "override", payload("ov"))
        repo = self.checkout()
        os.environ["AWESOME_JEV_CATALOG"] = str(override)
        slugs, provenance = self.load(repo / "src")
        self.assertEqual(slugs, ["ov"])
        self.assertEqual((provenance.source, provenance.detail), ("override", f"from AWESOME_JEV_CATALOG={override}"))
        self.assertEqual(self.github.requests, [])

    def test_an_incomplete_or_broken_override_is_skipped_whole(self):
        repo = self.checkout()
        for broken in ("missing", "corrupt"):
            with self.subTest(broken=broken):
                override = write(self.tmp / broken, payload("ov"), skip="patterns.json" if broken == "missing" else "")
                if broken == "corrupt":
                    (override / "compat.json").write_text("{not json")
                os.environ["AWESOME_JEV_CATALOG"] = str(override)
                self.assertEqual(self.load(repo / "src")[1].source, "checkout")

    def test_a_source_missing_any_one_of_the_five_files_is_skipped_whole(self):
        # taxonomy.json and collections.json joined the ladder on 2026-09-28
        # (I35): a source without either is as incomplete as one without the
        # catalogue.
        repo = self.checkout()
        self.assertEqual(len(data.FILES), 5)
        for name in data.FILES:
            with self.subTest(missing=name):
                override = write(self.tmp / f"no-{name}", payload("ov"), skip=name)
                os.environ["AWESOME_JEV_CATALOG"] = str(override)
                self.assertEqual(self.load(repo / "src")[1].source, "checkout")

    def test_a_checkout_is_found_from_below_and_the_network_is_not_asked(self):
        repo = self.checkout()
        deep = repo / "src" / "awesome_jev_mcp"
        deep.mkdir(parents=True)
        slugs, provenance = self.load(deep)
        self.assertEqual(slugs, ["co"])
        self.assertEqual((provenance.source, provenance.detail), ("checkout", f"from the repository at {repo.resolve()}"))
        self.assertEqual(self.github.requests, [])

    def test_a_worktree_checkout_has_a_git_file(self):
        repo = self.tmp / "worktree"
        write(repo, payload("wt"))
        (repo / ".git").write_text("gitdir: /elsewhere\n")
        self.assertEqual(self.load(repo)[0], ["wt"])

    def test_a_directory_is_a_checkout_only_with_git_and_the_catalogue(self):
        plain = write(self.tmp / "plain", payload("plain"))
        self.assertEqual(self.load(plain)[1].source, "network")
        bare = self.tmp / "bare"
        (bare / ".git").mkdir(parents=True)
        self.assertEqual(self.load(bare)[1].source, "network")

    def test_a_checkout_missing_a_file_is_skipped_for_the_network(self):
        repo = self.checkout(skip="compat.json")
        slugs, provenance = self.load(repo)
        self.assertEqual((slugs, provenance.source), (["net-a", "net-b"], "network"))

    def test_by_default_the_search_starts_at_the_package_itself(self):
        # Why load() takes checkout_from: these tests run inside a checkout.
        self.assertEqual(data._find_checkout(), ROOT)

    # --- 3: the network --------------------------------------------------------

    def test_a_first_fetch_is_unconditional_and_fills_the_cache(self):
        slugs, provenance = self.load()
        self.assertEqual(slugs, ["net-a", "net-b"])
        self.assertEqual((provenance.source, provenance.detail), ("network", "fetched from GitHub"))
        self.assertEqual(self.github.requests, [(data.RAW + n, None, data.TIMEOUT) for n in data.FILES])
        for name in data.FILES:
            self.assertEqual(json.loads((self.cache / name).read_text()), self.github.files[name])
        self.assertEqual(json.loads((self.cache / "etags.json").read_text()),
                         {n: FakeGitHub.etag(n, self.github.files[n]) for n in data.FILES})

    def test_a_revalidated_fetch_is_served_from_the_cache_and_leaves_it_alone(self):
        self.load()
        stamps = {n: (self.cache / n).stat().st_mtime_ns for n in (*data.FILES, "etags.json")}
        self.github.requests.clear()
        slugs, provenance = self.load()
        self.assertEqual(slugs, ["net-a", "net-b"])
        self.assertEqual((provenance.source, provenance.detail), ("network", "revalidated against GitHub"))
        self.assertEqual([c for _, c, _ in self.github.requests],
                         [FakeGitHub.etag(n, self.github.files[n]) for n in data.FILES])
        self.assertEqual({n: (self.cache / n).stat().st_mtime_ns for n in stamps}, stamps)

    def test_one_changed_file_is_fetched_and_the_others_revalidated(self):
        self.load()
        old = json.loads((self.cache / "etags.json").read_text())
        self.github.files = {**self.github.files, "compat.json": {"platforms": [], "tag": "new"}}
        slugs, provenance = self.load()
        self.assertEqual(provenance.detail, "fetched from GitHub")
        self.assertEqual(json.loads((self.cache / "compat.json").read_text())["tag"], "new")
        etags = json.loads((self.cache / "etags.json").read_text())
        self.assertNotEqual(etags["compat.json"], old["compat.json"])
        self.assertEqual({n: etags[n] for n in ("catalog.json", "patterns.json")},
                         {n: old[n] for n in ("catalog.json", "patterns.json")})

    def test_an_etag_without_its_cached_file_asks_unconditionally(self):
        self.load()
        (self.cache / "patterns.json").unlink()
        self.github.requests.clear()
        self.load()
        conditions = {url.rsplit("/", 1)[1]: c for url, c, _ in self.github.requests}
        self.assertIsNone(conditions["patterns.json"])
        self.assertIsNotNone(conditions["catalog.json"])

    def test_an_unwritable_cache_still_serves_what_was_fetched(self):
        blocker = self.tmp / "a-file"
        blocker.write_text("")
        with mock.patch.object(data, "cache_dir", return_value=blocker / "cache"):
            slugs, provenance = self.load()
        self.assertEqual((slugs, provenance.source), (["net-a", "net-b"], "network"))

    # --- 4 and 5: degraded, and loud about it ----------------------------------

    def test_any_file_failing_discards_the_whole_fetch(self):
        self.load()
        cached = {n: (self.cache / n).read_text() for n in data.FILES}
        self.github.files = payload("newer")
        failures = {
            "no route": urllib.error.URLError("no route to host"),
            "timeout": TimeoutError("timed out"),
            "server error": self.github.http_error(data.RAW, 503, "Unavailable"),
        }
        for label, failure in failures.items():
            with self.subTest(failure=label):
                self.github.fail = {"compat.json": failure}
                self.assertIsNone(data._fetch())
                slugs, provenance = self.load()
                self.assertEqual((slugs, provenance.source), (["net-a", "net-b"], "cache"))
                # catalog.json was fetched before compat.json failed; nothing of it is kept.
                self.assertEqual({n: (self.cache / n).read_text() for n in data.FILES}, cached)

    def test_a_body_that_is_not_json_discards_the_fetch(self):
        self.github.raw = {"patterns.json": b"<html>rate limited</html>"}
        self.assertIsNone(data._fetch())
        self.assertFalse((self.cache / "catalog.json").exists())

    def test_a_304_with_an_unreadable_cached_copy_is_no_answer(self):
        self.load()
        (self.cache / "catalog.json").write_text("{half a file")
        self.assertIsNone(data._fetch())

    def test_the_cache_answers_when_the_network_does_not(self):
        self.load()
        self.github.fail = {n: urllib.error.URLError("offline") for n in data.FILES}
        slugs, provenance = self.load()
        self.assertEqual(slugs, ["net-a", "net-b"])
        self.assertEqual(provenance.source, "cache")
        self.assertTrue(provenance.line().startswith(
            "STALE — network unreachable, serving the last copy fetched to this machine · 2 rows · "))

    def test_the_bundled_snapshot_is_the_last_resort_and_says_so(self):
        write(self.bundled, payload("snap"))
        self.github.fail = {n: urllib.error.URLError("offline") for n in data.FILES}
        slugs, provenance = self.load()
        self.assertEqual((slugs, provenance.source), (["snap"], "bundled"))
        self.assertTrue(provenance.line().startswith("STALE — network unreachable and nothing cached, serving the "
                                                     "snapshot shipped inside this package"))

    def test_with_nothing_at_all_it_says_how_to_fix_it(self):
        self.github.fail = {n: urllib.error.URLError("offline") for n in data.FILES}
        with self.assertRaises(RuntimeError) as caught:
            data.load(checkout_from=self.outside)
        self.assertIn("AWESOME_JEV_CATALOG", str(caught.exception))
        for name in data.FILES:
            self.assertIn(name, str(caught.exception))


    # --- the examples index, on the same ladder but on its own -------------------

    INDEX = {"examples": [{"name": "01-x", "patterns": ["overview"], "code": "print(1)\n"}]}

    def write_index(self, directory: pathlib.Path, index: dict) -> pathlib.Path:
        (directory / "examples").mkdir(parents=True, exist_ok=True)
        (directory / data.EXAMPLES).write_text(json.dumps(index))
        return directory

    def test_the_catalogue_never_asks_for_the_index(self):
        self.github.files[data.EXAMPLES] = self.INDEX
        self.load()
        self.assertNotIn(data.RAW + data.EXAMPLES, [url for url, _, _ in self.github.requests])

    def test_the_index_comes_from_the_first_rung_that_has_it(self):
        repo = self.checkout()
        override = write(self.tmp / "override", payload("ov"))
        os.environ["AWESOME_JEV_CATALOG"] = str(override)
        self.github.files[data.EXAMPLES] = {"examples": ["net"]}
        # The override has the catalogue but no index, so the checkout's index answers,
        # while the catalogue itself still comes from the override.
        self.write_index(repo, self.INDEX)
        self.assertEqual(data.load_examples(repo), (self.INDEX, f"from the repository at {repo.resolve()}"))
        self.assertEqual(self.load(repo)[1].source, "override")
        self.write_index(override, {"examples": ["ov"]})
        self.assertEqual(data.load_examples(repo), ({"examples": ["ov"]}, f"from AWESOME_JEV_CATALOG={override}"))
        self.assertEqual(self.github.requests, [])

    def test_the_network_fetches_the_index_alone_and_caches_it_beside_the_catalogue(self):
        self.load()
        tags = json.loads((self.cache / "etags.json").read_text())
        self.github.requests.clear()
        self.github.files[data.EXAMPLES] = self.INDEX
        self.assertEqual(data.load_examples(self.outside), (self.INDEX, "fetched from GitHub"))
        self.assertEqual(self.github.requests, [(data.RAW + data.EXAMPLES, None, data.TIMEOUT)])
        self.assertEqual(json.loads((self.cache / data.EXAMPLES).read_text()), self.INDEX)
        etags = json.loads((self.cache / "etags.json").read_text())
        self.assertEqual({n: etags[n] for n in data.FILES}, {n: tags[n] for n in data.FILES})
        self.assertIn(data.EXAMPLES, etags)
        self.assertEqual(data.load_examples(self.outside), (self.INDEX, "revalidated against GitHub"))
        self.assertEqual(self.github.requests[-1][1], etags[data.EXAMPLES])

    def test_a_degraded_index_says_so(self):
        self.github.files[data.EXAMPLES] = self.INDEX
        data.load_examples(self.outside)
        self.github.fail = {data.EXAMPLES: urllib.error.URLError("offline")}
        index, line = data.load_examples(self.outside)
        self.assertEqual(index, self.INDEX)
        self.assertEqual(line, "STALE — network unreachable, serving the last copy fetched to this machine")
        (self.cache / data.EXAMPLES).unlink()
        self.write_index(self.bundled, {"examples": ["snap"]})
        index, line = data.load_examples(self.outside)
        self.assertEqual(index, {"examples": ["snap"]})
        self.assertTrue(line.startswith("STALE — network unreachable and nothing cached"), line)

    def test_no_index_anywhere_is_an_answer_not_an_error(self):
        self.github.fail = {data.EXAMPLES: urllib.error.URLError("offline")}
        self.assertEqual(data.load_examples(self.outside), (None, "no source had examples/index.json"))


class ProvenanceTest(unittest.TestCase):
    def test_only_the_cache_and_the_snapshot_are_stale(self):
        for source in ("override", "checkout", "network", "cache", "bundled"):
            with self.subTest(source=source):
                line = data.Provenance(source, "detail", "2026-09-20", 7).line()
                stale = source in ("cache", "bundled")
                self.assertEqual(data.Provenance(source, "d", "x", 1).degraded, stale)
                self.assertEqual(line, ("STALE — " if stale else "") + "detail · 7 rows · catalogue checked 2026-09-20")

    def test_the_date_is_the_catalogues_newest_check(self):
        # Newest, not last: the rows are in slug order, not date order.
        loaded = data._unpack(payload("a", "b", "c", checked=("2026-09-20", "2026-09-01")), "network", "d")
        provenance = loaded.provenance
        self.assertEqual((provenance.as_of, provenance.rows, loaded.patterns), ("2026-09-20", 3, [{"key": "overview"}]))
        self.assertEqual(data._unpack(payload("a"), "network", "d").provenance.as_of, "unknown")

    def test_every_file_is_handed_over(self):
        files = payload("a")
        loaded = data._unpack(files, "network", "d")
        self.assertEqual(loaded.catalog, files["catalog.json"])
        self.assertEqual(loaded.compat, files["compat.json"])
        self.assertEqual(loaded.taxonomy, files["taxonomy.json"])
        self.assertEqual(loaded.collections, files["collections.json"]["collections"])
        self.assertEqual(loaded._fields, ("catalog", "compat", "patterns", "taxonomy", "collections", "provenance"))


class PackagingTest(unittest.TestCase):
    """The five files are the site's five, and the package carries each."""

    def test_the_server_serves_what_the_site_fetches(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import assemble_site  # noqa: PLC0415

        self.assertEqual(data.FILES, assemble_site.PAGE_FILES)
        self.assertEqual(assemble_site.RUNTIME_FILES[: len(data.FILES)], data.FILES)

    def test_the_sdist_and_the_wheels_snapshot_carry_every_file(self):
        import tomllib  # noqa: PLC0415 - Python 3.11+, like the rest of the tests

        hatch = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["hatch"]["build"]["targets"]
        for name in (*data.FILES, data.EXAMPLES):
            with self.subTest(name=name):
                self.assertIn(f"/{name}", hatch["sdist"]["include"])
                self.assertEqual(hatch["wheel"]["force-include"][name], f"awesome_jev_mcp/_bundled/{name}")

    def test_the_release_smoke_test_compares_every_file(self):
        workflow = (ROOT / ".github" / "workflows" / "publish.yml").read_text()
        self.assertIn("for name in data.FILES:", workflow)


class CacheDirTest(unittest.TestCase):
    def test_each_platform_keeps_it_where_that_platform_keeps_caches(self):
        home = pathlib.Path.home()
        with mock.patch.object(data.sys, "platform", "darwin"):
            self.assertEqual(data.cache_dir(), home / "Library" / "Caches" / "awesome-jev-mcp")
        if os.name != "nt":
            with mock.patch.object(data.sys, "platform", "linux"), \
                 mock.patch.dict(os.environ, {"XDG_CACHE_HOME": "/xdg"}):
                self.assertEqual(data.cache_dir(), pathlib.Path("/xdg/awesome-jev-mcp"))
            with mock.patch.object(data.sys, "platform", "linux"), mock.patch.dict(os.environ):
                os.environ.pop("XDG_CACHE_HOME", None)
                self.assertEqual(data.cache_dir(), home / ".cache" / "awesome-jev-mcp")


if __name__ == "__main__":
    unittest.main()
