import test from "node:test";
import assert from "node:assert/strict";
import {
  compareEntries, evidenceKind, evidenceUrl, matchesEntry, verification, isIndependentReport, EVIDENCE_KINDS,
  queryFromState, shareUrl, stateFromQuery, TOGGLES, VIEWS, SUMMARY_SOURCES, MARKED_SOURCES, summaryMarks,
} from "../site/catalog-core.mjs";
import { readFileSync } from "node:fs";

const row = (slug, extra = {}) => ({ slug, title: slug, patterns: ["context-compaction"], ...extra });

test("an HTTP success and dated call-site citation never imply an execution", () => {
  const result = verification(row("source", {checked: "2026-09-24", link_status: 200, evidence: {read_on: "2026-09-22"}}));
  assert.equal(result.linkOk, true);
  assert.equal(result.codeRead, "2026-09-22");
  assert.equal(result.runtime, "not-tested");
  assert.equal(result.performance, "not-reproduced");
  assert.equal(verification(row("undated", {link_status: 200})).linkOk, false);
  assert.equal(verification(row("failed", {checked: "2026-09-24", link_status: 404})).linkOk, false);
});

test("a summary in the project's own words is marked, and Chinese says when a model translated it", () => {
  const schema = JSON.parse(readFileSync(new URL("../schema/entry.schema.json", import.meta.url)));
  assert.deepEqual(SUMMARY_SOURCES, schema.properties.summary_source.enum);
  const taxonomy = JSON.parse(readFileSync(new URL("../taxonomy.json", import.meta.url)));
  assert.deepEqual(taxonomy.summary_sources.map(x => x.key), SUMMARY_SOURCES, "every mark has a label");
  const upstream = row("up", {summary_source: "upstream-description", zh_machine: true});
  assert.deepEqual(summaryMarks(upstream, "en"), ["upstream-description"]);
  assert.deepEqual(summaryMarks(upstream, "zh"), ["upstream-description", "zh-machine"]);
  assert.deepEqual(summaryMarks(row("stale", {summary_source: "upstream-description-stale"}), "en"), ["upstream-description-stale"]);
  // A person's text, or no record, carries no source mark; zh_machine only describes the Chinese.
  assert.deepEqual(summaryMarks(row("curated", {summary_source: "curated", zh_machine: true}), "en"), []);
  assert.deepEqual(summaryMarks(row("curated", {summary_source: "curated", zh_machine: true}), "zh"), ["zh-machine"]);
  assert.deepEqual(summaryMarks(row("bare"), "zh"), []);
  assert.deepEqual(summaryMarks(row("odd", {summary_source: "toString", zh_machine: "yes"}), "zh"), []);
  assert.deepEqual(MARKED_SOURCES, SUMMARY_SOURCES.slice(1));
});

test("an evidence record without a kind is a call site, and a row without one has none", () => {
  assert.deepEqual(EVIDENCE_KINDS, ["call-site", "wire-shape", "example-only"]);
  assert.equal(evidenceKind(row("none")), null);
  assert.equal(evidenceKind(row("bare", {evidence: {path: "a.py", matched: ["jev"]}})), "call-site");
  for (const kind of EVIDENCE_KINDS) {
    assert.equal(evidenceKind(row(kind, {evidence: {path: "a.py", matched: ["jev"], kind}})), kind);
  }
  // A value the schema does not know reads as the default, like a missing one.
  assert.equal(evidenceKind(row("odd", {evidence: {path: "a.py", matched: ["jev"], kind: "toString"}})), "call-site");
});

test("evidence links preserve repository overrides and encoded file paths", () => {
  assert.equal(evidenceUrl(row("x", {url: "https://github.com/owner/repo/pull/42", evidence: {path: "src/a b.ts"}})), "https://github.com/owner/repo/blob/HEAD/src/a%20b.ts");
  assert.equal(evidenceUrl(row("x", {repo: "https://github.com/other/repo", url: "https://example.com", evidence: {path: "src/main.py"}})), "https://github.com/other/repo/blob/HEAD/src/main.py");
  assert.equal(evidenceUrl(row("x", {url: "https://github.com.evil.example/o/r", evidence: {path: "x"}})), null);
});

test("editorial ranking can surface a useful small project ahead of stars", () => {
  const rows = [row("popular", {stars: 200000}), row("selected", {stars: 1})];
  assert.equal(rows.toSorted(compareEntries("curated", new Map([["selected", 0]])))[0].slug, "selected");
  assert.equal(rows.toSorted(compareEntries("stars"))[0].slug, "popular");
});

test("newest and last link check are separate clocks; missing dates sort last", () => {
  const rows = [row("old", {first_seen: "2026-09-20", checked: "2026-09-24"}), row("new", {first_seen: "2026-09-23", checked: "2026-09-22"}), row("undated")];
  assert.deepEqual(rows.toSorted(compareEntries("newest")).map(x => x.slug), ["new", "old", "undated"]);
  assert.deepEqual(rows.toSorted(compareEntries("checked")).map(x => x.slug), ["old", "new", "undated"]);
});

test("collections, bilingual search, and language filters intersect", () => {
  const entry = row("selected", {summary_zh: "上下文压缩插件", languages: ["typescript"], has_code: true});
  assert.equal(matchesEntry(entry, {q: "压缩", code: true, lang: "typescript"}, new Set(["selected"])), true);
  assert.equal(matchesEntry(entry, {q: "压缩", lang: "python"}, new Set(["selected"])), false);
  assert.equal(matchesEntry(entry, {}, new Set(["different"])), false);
  assert.equal(matchesEntry(entry, {q: "上下文"}, null, "上下文压缩"), true);
});

test("third-party benchmark is a report classification, not a replication certificate", () => {
  assert.equal(isIndependentReport(row("b", {kind: "benchmark", flags: ["unverified-claims"]})), true);
  assert.equal(isIndependentReport(row("b", {kind: "benchmark", flags: ["vendor-reported"]})), false);
  assert.equal(verification(row("b", {kind: "benchmark"})).performance, "not-reproduced");
});

test("short entry permalinks resolve exactly without changing ordinary text search", () => {
  const entries = [row("jev"), row("ai"), row("every"), row("typesafe"), row("jev-router", {summary: "An AI tool using TypeSafe Jev for every request"})];
  for (const slug of ["jev", "ai", "every", "typesafe"]) {
    assert.deepEqual(entries.filter(e => matchesEntry(e, {entry: slug})).map(e => e.slug), [slug]);
  }
  assert.ok(entries.filter(e => matchesEntry(e, {q: "jev"})).length > 1);
});

// ─── URL state: every view and filter is a shareable link ─────────────────
const DEFAULTS = {entry: "", collection: "", sort: "curated", pattern: "", kind: "", lang: "", q: "", code: false, off: false, indep: false, noflag: false};
const OPTIONS = {languages: ["en", "zh"], collections: ["first-call", "build", "measured"]};
const read = (search, hash = "") => stateFromQuery(search, hash, OPTIONS);

test("a default catalogue writes only the language", () => {
  assert.equal(queryFromState(DEFAULTS, "catalog", "en").toString(), "lang=en");
  assert.deepEqual(read("?lang=en"), {lang: "en", view: "catalog", state: DEFAULTS});
});

test("parameter names and order stay what already-shared links use", () => {
  const state = {...DEFAULTS, collection: "build", sort: "stars", pattern: "tool-selection", kind: "project", lang: "python", q: "retry budget", code: true, off: true, indep: true, noflag: true};
  assert.equal(
    queryFromState(state, "prims", "zh").toString(),
    "view=prims&collection=build&sort=stars&p=tool-selection&k=project&lang_f=python&q=retry+budget&code=1&off=1&indep=1&noflag=1&lang=zh",
  );
});

test("every view, sort, toggle and filter survives a round trip", () => {
  for (const view of VIEWS) {
    for (const sort of ["curated", "newest", "checked", "stars", "pattern"]) {
      for (const toggle of TOGGLES) {
        const state = {...DEFAULTS, sort, collection: "measured", pattern: "safety-gating", kind: "benchmark", lang: "go", q: "上下文 压缩", [toggle]: true};
        const back = read("?" + queryFromState(state, view, "zh").toString());
        assert.deepEqual(back, {lang: "zh", view, state});
      }
    }
  }
});

test("values the page cannot show fall back instead of reaching the state", () => {
  const back = read("?sort=random&collection=nope&lang=fr&view=graph&code=true&off=0");
  assert.equal(back.lang, null);
  assert.equal(back.view, "catalog");
  assert.deepEqual(back.state, DEFAULTS);
  // Inherited object keys are not languages (a lookup in the strings table would say they were).
  assert.equal(read("?lang=constructor").lang, null);
});

test("the hash names a view only when the query does not", () => {
  assert.equal(read("", "#compat").view, "compat");
  assert.equal(read("?view=prims", "#compat").view, "prims");
  // A bare #slug is an entry permalink: the catalogue, nothing filtered.
  assert.deepEqual(read("", "#jev-router"), {lang: null, view: "catalog", state: DEFAULTS});
});

test("reading the URL always clears the entry being revealed", () => {
  assert.equal(read("?entry=jev-router&q=x").state.entry, "");
});

test("a shared URL keeps the hash only while following its permalink", () => {
  const query = queryFromState({...DEFAULTS, q: "gate"}, "catalog", "en");
  assert.equal(shareUrl(query, {pathname: "/awesome-jev/", hash: "#jev-router"}), "?q=gate&lang=en");
  assert.equal(shareUrl(query, {pathname: "/awesome-jev/", hash: "#jev-router", keepHash: true}), "?q=gate&lang=en#jev-router");
  assert.equal(shareUrl(new URLSearchParams(), {pathname: "/awesome-jev/", hash: "#x", keepHash: true}), "/awesome-jev/#x");
});
