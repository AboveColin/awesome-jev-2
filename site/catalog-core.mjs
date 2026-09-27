// Data-only catalogue behavior, shared by the page and its offline tests.
export const SORTS = ["curated", "newest", "checked", "stars", "pattern"];

export function verification(entry) {
  return {
    linkChecked: entry.checked || null,
    linkOk: Boolean(entry.checked && entry.link_status >= 200 && entry.link_status < 300),
    codeRead: entry.evidence?.read_on || null,
    // The catalogue records source inspection, not executions or replications.
    runtime: "not-tested",
    performance: "not-reproduced",
  };
}

// What a cited file shows, as evidence.kind records it (schema/entry.schema.json).
// A record without the field is a call site; a row without evidence has none.
export const EVIDENCE_KINDS = ["call-site", "wire-shape", "example-only"];

export function evidenceKind(entry) {
  if (!entry.evidence) return null;
  return EVIDENCE_KINDS.includes(entry.evidence.kind) ? entry.evidence.kind : "call-site";
}

// Whose words a summary is, as summary_source records it (schema/entry.schema.json).
// The two upstream values are the project's own description; they are marked
// wherever the summary is shown, as the READMEs mark them. `curated` is not.
export const SUMMARY_SOURCES = ["curated", "upstream-description", "upstream-description-stale"];
export const MARKED_SOURCES = ["upstream-description", "upstream-description-stale"];

// The provenance marks a card's summary carries in a language, in reading
// order: whose words it is, then, for the Chinese text only, that a model
// translated it (zh_machine describes summary_zh, never the English).
export function summaryMarks(entry, lang) {
  const marks = [];
  if (MARKED_SOURCES.includes(entry.summary_source)) marks.push(entry.summary_source);
  if (lang === "zh" && entry.zh_machine === true) marks.push("zh-machine");
  return marks;
}

// A project or plugin with code whose only pattern is `overview`, and no record
// of a person reading it against the patterns (`patterns_reviewed`), is not yet
// indexed by pattern: `overview` is also what the keyword rules suggest when
// nothing matches. The overview listing shows these rows last, under their own
// heading, as the READMEs do. scripts/_stats.py not_indexed_by_pattern() is the
// same rule for the generated pages.
export const UNINDEXED_KINDS = ["project", "plugin"];

export function notIndexedByPattern(entry) {
  return Array.isArray(entry.patterns) && entry.patterns.length === 1 && entry.patterns[0] === "overview"
    && Boolean(entry.has_code) && UNINDEXED_KINDS.includes(entry.kind) && !entry.patterns_reviewed;
}

// The Jev primitives in the schema's order, and the two records of which ones a
// row uses, never merged. question_types is a person's reading of the code
// calling them. primitives_seen is a script's text signal: the one file the
// row's evidence cites contains their request or answer shape, which is not a
// call. signalOnly is what the signal adds to the reading. scripts/_stats.py
// signal_only() is the same rule for the generated pages and the figures.
export const PRIMITIVES = ["choice", "score", "noul"];

export function primitiveLayers(entry) {
  const read = PRIMITIVES.filter(p => (entry.question_types || []).includes(p));
  const signalOnly = PRIMITIVES.filter(p => (entry.primitives_seen || []).includes(p) && !read.includes(p));
  return { read, signalOnly };
}

export function evidenceUrl(entry) {
  if (!entry.evidence?.path) return null;
  for (const candidate of [entry.repo, entry.url]) {
    if (!candidate) continue;
    try {
      const url = new URL(candidate);
      const parts = url.pathname.split("/").filter(Boolean);
      if (url.protocol !== "https:" || url.hostname !== "github.com" || parts.length < 2) continue;
      const path = entry.evidence.path.split("/").map(encodeURIComponent).join("/");
      return `https://github.com/${parts[0]}/${parts[1]}/blob/HEAD/${path}`;
    } catch (_) { /* A malformed source cannot become an executable link. */ }
  }
  return null;
}

export function isIndependentReport(entry) {
  return entry.kind === "benchmark" && !(entry.flags || []).includes("vendor-reported");
}

const originalOrder = (a, b) =>
  Number(Boolean(b.official)) - Number(Boolean(a.official)) ||
  Number(Boolean(b.has_code)) - Number(Boolean(a.has_code)) ||
  (b.stars || 0) - (a.stars || 0) ||
  a.title.localeCompare(b.title) || a.slug.localeCompare(b.slug);

export function compareEntries(sort, ranks = new Map()) {
  return (a, b) => {
    if (sort === "curated") {
      const diff = (ranks.get(a.slug) ?? Infinity) - (ranks.get(b.slug) ?? Infinity);
      if (diff) return diff;
    }
    if (sort === "newest") {
      const diff = (b.first_seen || "").localeCompare(a.first_seen || "");
      if (diff) return diff;
    }
    if (sort === "checked") {
      const diff = (b.checked || "").localeCompare(a.checked || "");
      if (diff) return diff;
    }
    if (sort === "stars" && (b.stars || 0) !== (a.stars || 0)) return (b.stars || 0) - (a.stars || 0);
    return originalOrder(a, b);
  };
}

export function matchesEntry(entry, state, collectionSlugs = null, labels = "") {
  if (state.entry && entry.slug !== state.entry) return false;
  if (collectionSlugs && !collectionSlugs.has(entry.slug)) return false;
  if (state.pattern && !entry.patterns.includes(state.pattern)) return false;
  if (state.kind && entry.kind !== state.kind) return false;
  if (state.lang && !(entry.languages || []).includes(state.lang)) return false;
  if (state.code && !entry.has_code) return false;
  if (state.off && !entry.official) return false;
  if (state.noflag && (entry.flags || []).length) return false;
  if (state.indep && !isIndependentReport(entry)) return false;
  // question_types and not primitives_seen: a search for a primitive finds the
  // rows a person read calling it, never rows a text match alone suggests.
  const hay = [entry.title, entry.summary, entry.summary_zh, entry.notes, entry.notes_zh,
    entry.slug, ...(entry.platforms || []), ...(entry.languages || []), ...entry.patterns,
    ...(entry.question_types || []), entry.author?.name, entry.repo_license, entry.url, labels]
    .filter(Boolean).join(" ").toLowerCase();
  return (state.q || "").trim().toLowerCase().split(/\s+/).every(word => hay.includes(word));
}

// ─── URL state ────────────────────────────────────────────────
// Every view and filter round-trips through the query string, so any state
// is a shareable link. Pure: the page passes `location` in and applies what
// comes back. The parameter names are public — links in READMEs, pattern
// pages and elsewhere already use them — so rename none of them.
export const VIEWS = ["catalog", "prims", "compat"];
export const TOGGLES = ["code", "off", "indep", "noflag"];

export function queryFromState(state, view, lang) {
  const q = new URLSearchParams();
  if (view !== "catalog") q.set("view", view);
  if (state.collection) q.set("collection", state.collection);
  if (state.sort !== "curated") q.set("sort", state.sort);
  if (state.pattern) q.set("p", state.pattern);
  if (state.kind) q.set("k", state.kind);
  if (state.lang) q.set("lang_f", state.lang);
  if (state.q) q.set("q", state.q);
  for (const t of TOGGLES) if (state[t]) q.set(t, "1");
  q.set("lang", lang);
  return q;
}

// Only retain a hash while following its permalink. A later filter or view
// selection is new intent and must not restore the old entry.
export function shareUrl(query, { pathname, hash, keepHash = false }) {
  return (query.toString() ? "?" + query.toString() : pathname) + (keepHash ? hash : "");
}

// `lang` is null when the URL names no language the page has; the caller then
// keeps the one it chose. A bare #slug (no query) is an entry permalink: it
// yields the catalogue with every filter at its default, and the page reveals
// the entry itself.
export function stateFromQuery(search, hash, { languages, collections }) {
  const q = new URLSearchParams(search);
  const view = q.get("view") || (hash || "").replace("#", "");
  return {
    lang: languages.includes(q.get("lang")) ? q.get("lang") : null,
    view: VIEWS.includes(view) ? view : "catalog",
    state: {
      entry: "",
      collection: collections.includes(q.get("collection")) ? q.get("collection") : "",
      sort: SORTS.includes(q.get("sort")) ? q.get("sort") : "curated",
      pattern: q.get("p") || "",
      kind: q.get("k") || "",
      lang: q.get("lang_f") || "",
      q: q.get("q") || "",
      ...Object.fromEntries(TOGGLES.map(t => [t, q.get(t) === "1"])),
    },
  };
}
