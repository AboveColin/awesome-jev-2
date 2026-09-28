# Retry control

<sub>[awesome-jev](../../README.md) · [中文](retry-control.zh-CN.md)</sub>

_Decide whether a failed step is worth retrying._

Every catalogued example of this decision — 6 of them. The same rows, with caveats, are in [the index](../../README.md#retry-control); [the site](https://kydlikebtc.github.io/awesome-jev/?p=retry-control&lang=en) can filter them further by language, primitive and kind.

Evidence recorded for this pattern's rows (reports counted, not a verdict; a row may count more than once): official documentation 0 · call site 6 · wire shape 0 · example only 0 · independent reports 0 · negative results 0 · no file cited 0. “Independent” = a benchmark not flagged vendor-reported, not reproduced by this repository. [Every pattern side by side](../shape.md#evidence-by-decision-pattern).

★ gives a repository's GitHub stars as a band — ★10+, ★100+, ★1k+, ★10k+ and ★100k+; rows with no repository or under 10 stars show no band. Rows run official first, then with code, then by band, then by title. A band is a popularity signal, not a quality verdict; the exact count, as last read from GitHub, is in [`catalog.json`](../../catalog.json) and on [the site](https://kydlikebtc.github.io/awesome-jev/?lang=en).

A *call site* link opens the one file a row cites (`evidence.path`) at `HEAD` of the repository's default branch; the date after it is the day a person last read that file (`evidence.read_on`): a reading, not a run of the code. A *cited file* link is the same for a file that shows the project speaking Jev's request shape rather than building on Jev, or only an example it ships (`evidence.kind`). Neither is pinned to a commit, so it opens the file as it is now, which may differ from what was read, and stops resolving once the file moves; the weekly claims check reports that.

- **[harnessjudge](https://github.com/ndolinschi/harnessjudge)** — Judge agent steps — ok / retry / escalate / stop via TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Project` · ndolinschi · `TS` · call site [`src/lib/jev.ts`](https://github.com/ndolinschi/harnessjudge/blob/HEAD/src/lib/jev.ts), read 2026-09-22 · ⚠ `one commit` `no licence`</sub>

- **[Jev by Example](https://github.com/ReallyArtificial/jev-by-example)** — Ten runnable JavaScript agent decisions, one file each: reconciling a new memory against a stored one, gating whether an HTTP 200 really satisfied the task, retry vs. reconcile after an uncertain write, scoring context against a budget, checking a handoff for dropped prohibitions.
  <sub>`Project` · Really Artificial · `JS` · `choice` · `score` · `noul` · call site [`src/client.mjs`](https://github.com/ReallyArtificial/jev-by-example/blob/HEAD/src/client.mjs), read 2026-09-22 · ⚠ `AI-written`</sub>

- **[jev-harness](https://github.com/ismaelsoilet/jev-harness)** — Zero-dependency System One decision harness: 5 semantic gates saving frontier AI agent tokens on trivial errors & doom loops. Python + TypeScript + Rust. MCP-compatible. <sub>(upstream description)</sub>
  <sub>`Plugin` · ismaelsoilet · `Py` · call site [`src/jev_harness/client.py`](https://github.com/ismaelsoilet/jev-harness/blob/HEAD/src/jev_harness/client.py), read 2026-09-24</sub>

- **[jev-reasoning-navigator](https://github.com/AndreuVM/jev-reasoning-navigator)** — JEV Reasoning Navigator: Cognitive supervision, loop prevention, and anti-hallucination engine for autonomous LLM agents using TypeSafe AI
  <sub>`Project` · andreuvm · `Py` · call site [`jev_navigator/core/typesafe_client.py`](https://github.com/AndreuVM/jev-reasoning-navigator/blob/HEAD/jev_navigator/core/typesafe_client.py), read 2026-09-24 · ⚠ `no licence`</sub>

- **[jev-resilience](https://github.com/Vicente-MD/jev-resilience)** — Non-blocking Spring Boot Starter for Spring WebFlux that implements a Semantic Circuit Breaker to detect silent HTTP 200 failures using TypeSafe Jev. <sub>(upstream description)</sub>
  <sub>`Plugin` · vicente-md · `Java` · call site [`src/main/java/ai/jev/resilience/client/dto/JevRequest.java`](https://github.com/Vicente-MD/jev-resilience/blob/HEAD/src/main/java/ai/jev/resilience/client/dto/JevRequest.java), read 2026-09-22 · ⚠ `no licence`</sub>

- **[jevswiftsdk](https://github.com/NSStudent/JevSwiftSDK)** — An independent, type-safe Swift SDK for TypeSafe Jev, with async/await, batching, retries, and SPM support. <sub>(upstream description)</sub>
  <sub>`SDK` · nsstudent · `Swift` · call site [`Sources/JevSwiftSDK/Configuration.swift`](https://github.com/NSStudent/JevSwiftSDK/blob/HEAD/Sources/JevSwiftSDK/Configuration.swift), read 2026-09-22</sub>

---

<sub>Generated from `catalog.json` by `scripts/build_readme.py`. Edit the catalogue, not this file.</sub>
