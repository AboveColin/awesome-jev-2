# Context compaction

<sub>[awesome-jev](../../README.md) · [中文](context-compaction.zh-CN.md)</sub>

_Decide which tool calls and results still matter so stale context can be dropped._

Every catalogued example of this decision — 34 of them. The same rows, with caveats, are in [the index](../../README.md#context-compaction); [the site](https://kydlikebtc.github.io/awesome-jev/?p=context-compaction&lang=en) can filter them further by language, primitive and kind.

★ gives a repository's GitHub stars as a band — ★10+, ★100+, ★1k+, ★10k+ and ★100k+; rows with no repository or under 10 stars show no band. Rows run official first, then with code, then by band, then by title. A band is a popularity signal, not a quality verdict; the exact count, as last read from GitHub, is in [`catalog.json`](../../catalog.json) and on [the site](https://kydlikebtc.github.io/awesome-jev/?lang=en).

- **[Hermes Agent: Jev compaction evaluation](https://github.com/NousResearch/hermes-agent)** — Ported the Jev compaction approach, measured it against their shipping summariser, and published the conclusion not to adopt it.
  <sub>`Benchmark` · ★100k+ · `Py` · `noul`</sub>

- **[jcode: memory recall without embeddings](https://github.com/1jehuang/jcode)** — Replaces the whole retrieval stack for memory recall — no embeddings, no BM25, no reranker — with one batched Noul per candidate memory.
  <sub>`Project` · ★10k+ · `Rs` · `noul`</sub>

- **[fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction)** — A Claude Code plugin that replaces the compaction summary with per-item decisions: stale tool calls are dropped or truncated, everything kept stays verbatim.
  <sub>`Plugin` · ★1k+ · tamaratran · `TS` · `noul`</sub>

- **[compact-adviser](https://github.com/kunchenguid/compact-adviser)** — "Work appears completed or recorded. Run /compact to save tokens." <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · kunchenguid · `TS`</sub>

- **[hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills)** — Nine agent skills plus a CLI covering model routing, memory filtering, turn retention, one-of-many skill selection and next-action choice.
  <sub>`Plugin` · ★100+ · `Py` · `choice` · `score` · `noul`</sub>

- **[jev-pruner](https://github.com/tamaratran/jev-pruner)** — Trims long shell output before the model sees it, asking one Noul per chunk.
  <sub>`Plugin` · ★100+ · tamaratran · `TS` · `noul`</sub>

- **[claude-jev](https://github.com/0x7067/claude-jev)** — Claude Code plugin: Jev for rule checks, verbatim compaction, and prompt routing <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · 0x7067 · `Py`</sub>

- **[save-token-jev-clean](https://github.com/IAmUnbounded/save-token-jev-clean)** — Portable, Jev-guided context compaction for coding agents: instead of an LLM rewriting old context into a lossy summary, Jev decides which tool calls and results still matter, and user and assistant text is kept verbatim.
  <sub>`Plugin` · ★10+ · iamunbounded · `TS`</sub>

- **[Winnow](https://github.com/GhalebDweikat/winnow)** — Context garbage collection for Claude Code: when Read, Bash or Grep dump a wall of output, each chunk is judged for relevance to the current task.
  <sub>`Plugin` · ★10+ · `Py` · `noul`</sub>

- **[yoshi](https://github.com/compozy/yoshi)** — Context-pruning proxy for Claude Code and Codex: Jev judges which history is still needed, measured not claimed. POC here now, heading soon into https://github.com/compozy/compozy <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · compozy · `TS`</sub>

- **[deepseek-harness-jev-pre-compaction](https://github.com/wjw66/deepseek-harness-jev-pre-compaction)** — A pre-compaction advisor for DeepSeek Harness. Runs before the standard `compaction-basic` backend, using TypeSafe JEV to safely prune low-value tool results from model context. Original session events stay in the append-only log; only the model-visible view is replaced with compact markers or
  <sub>`Project` · wjw66 · `TS`</sub>

- **[dsh-jev-prune](https://github.com/yangyu666/dsh-jev-prune)** — Jev-judged context compaction for DeepSeek Harness: semantic tool-result pruning + deterministic receipt compaction <sub>(upstream description)</sub>
  <sub>`Project` · yangyu666 · `JS`</sub>

- **[dsh-jev-tools](https://github.com/HorusJiang/dsh-jev-tools)** — Jev judgment, not generation: prune long tool output, screen fetched pages for injected instructions, and gate completion claims inside DeepSeek Harness. <sub>(upstream description)</sub>
  <sub>`Plugin` · horusjiang · `TS`</sub>

- **[fast-compaction-dsh](https://github.com/kolawong/fast-compaction-dsh)** — Verdict-based context compaction for DeepSeek Harness — replaces lossy LLM summaries with fast keep/truncate/drop decisions from jev-latest; everything kept stays verbatim. Port of tamaratran/fast-jev-compaction. <sub>(upstream description)</sub>
  <sub>`Project` · kolawong · `TS`</sub>

- **[fast-dev-compaction](https://github.com/leonaaardob/fast-dev-compaction)** — Codex plugin: verbatim Jev-guided context restoration around session compaction. Port of tamaratran/fast-jev-compaction to Codex lifecycle hooks. <sub>(upstream description)</sub>
  <sub>`Plugin` · leonaaardob · `TS`</sub>

- **[Jev by Example](https://github.com/ReallyArtificial/jev-by-example)** — Ten runnable JavaScript agent decisions, one file each: reconciling a new memory against a stored one, gating whether an HTTP 200 really satisfied the task, retry vs. reconcile after an uncertain write, scoring context against a budget, checking a handoff for dropped prohibitions.
  <sub>`Project` · Really Artificial · `JS` · `choice` · `score` · `noul` · ⚠ `AI-written`</sub>

- **[jev-compact](https://github.com/fatelei/jev-compact)** — Jev-scored context compaction for OpenAI Codex CLI — scores every tool call before compaction and restores critical tool outputs verbatim after it <sub>(upstream description)</sub>
  <sub>`Plugin` · fatelei · `TS`</sub>

- **[jev-compaction](https://github.com/picaye/jev-compaction)** — Context compaction for Hermes sessions that never summarises: every tool call is scored by TypeSafe's Jev model, stale calls are dropped, everything kept stays verbatim. <sub>(upstream description)</sub>
  <sub>`Project` · picaye · `JS`</sub>

- **[jev-compaction](https://github.com/Waxmell114514/jev-compaction)** — A context compactor that can only score, never write — so an agent's memory can't hold a fact the transcript never contained. Working demo, runs offline. <sub>(upstream description)</sub>
  <sub>`Project` · waxmell114514 · `Py`</sub>

- **[jev-docs](https://github.com/chenrui333/jev-docs)** — Community-maintained history of Jev / TypeSafe System One APIs, SDKs, agent guidance, and engineering best practices. <sub>(upstream description)</sub>
  <sub>`SDK` · chenrui333 · `Py`</sub>

- **[jevprune](https://github.com/ibrahemid/jevprune)** — Filter command output for coding agents using a task description. <sub>(upstream description)</sub>
  <sub>`Project` · ibrahemid · `TS`</sub>

- **[jit-context](https://github.com/wojciechwiesner/jit-context)** — Architectural Moat: JIT-JEV Context OS — Epistemic runtime & JEV System 1 context gate for AI agents (L0 SQLite WAL <3ms, Epistemic Invariants I1–I10, CERN Zenodo DOI: 10.5281/zenodo.22649542) <sub>(upstream description)</sub>
  <sub>`Project` · wojciechwiesner · `Py`</sub>

- **[jselect](https://github.com/keltokhy/jselect)** — Useful evidence for your AI, within a token budget. A fast, source-linked context selector for files, records, and agents. <sub>(upstream description)</sub>
  <sub>`Project` · keltokhy · `Py`</sub>

- **[lcc](https://github.com/lucasmartins-ai/lcc)** — Local Context Compiler (lcc): clean, dedupe and compact prompt context before it reaches the model, then report every block dropped, the cache tokens a pass invalidates and when pruning pays off. Runs offline with a local 1K decision model. MIT, no API key, zero telemetry. <sub>(upstream description)</sub>
  <sub>`Project` · lucasmartins-ai · `Py`</sub>

- **[omp-jev-compaction](https://github.com/jerryfane/omp-jev-compaction)** — Verbatim Jev-scored context reduction for omp, over TypeSafe or OpenRouter <sub>(upstream description)</sub>
  <sub>`Project` · jerryfane · `TS`</sub>

- **[pi-fast-jev-compaction](https://github.com/KamilPostrozny/pi-fast-jev-compaction)** — Fast JEV compaction extension for pi <sub>(upstream description)</sub>
  <sub>`Plugin` · kamilpostrozny · `TS`</sub>

- **[pi-fast-jev-compaction](https://github.com/QuentinDanblon/pi-fast-jev-compaction)** — Verbatim context pruning for the pi coding agent, scored by TypeSafe Jev: stale tool calls and results are dropped or truncated, everything kept stays verbatim. <sub>(upstream description)</sub>
  <sub>`Plugin` · quentindanblon · `TS`</sub>

- **[pi-jev](https://github.com/iefnaf/pi-jev)** — Pi extension suite powered by Jev: selective context compaction and model routing <sub>(upstream description)</sub>
  <sub>`Plugin` · iefnaf · `TS`</sub>

- **[pi-jev-compact](https://github.com/ilkerulusoy/pi-jev-compact)** — Selective, verbatim context compaction for Pi: Jev scores every tool call and result, unneeded calls are dropped and the rest stays verbatim, with no LLM-written summary.
  <sub>`Plugin` · ilkerulusoy · `TS` · ⚠ `no licence`</sub>

- **[pi-jev-compaction](https://github.com/nourhelmi/pi-jev-compaction)** — Automatic Jev context clearing for Pi. Keep the conversation, prune stale tool output, retrieve originals without rerunning commands. <sub>(upstream description)</sub>
  <sub>`Plugin` · nourhelmi · `TS`</sub>

- **[pi-jev-context](https://github.com/Nyarlathoteppppp/pi-jev-context)** — Model performance first. Token savings second. A Pi extension with freshness-aware read dedupe, Jev log filtering, and searchable verbatim recall. Keeps existing message history intact. <sub>(upstream description)</sub>
  <sub>`Plugin` · nyarlathoteppppp · `TS`</sub>

- **[pi-jev-context](https://github.com/kevinpita/pi-jev-context)** — Reversible context pruning for Pi, powered by TypeSafe Jev. Keep useful context without deleting session history. <sub>(upstream description)</sub>
  <sub>`Plugin` · kevinpita · `TS`</sub>

- **[pi-jev-context-curator](https://github.com/Shashank-H/pi-jev-context-curator)** — A Jev based context curator for pi <sub>(upstream description)</sub>
  <sub>`Plugin` · shashank-h · `TS`</sub>

- **[smoking-extraction-benchmark](https://github.com/vclic/smoking-extraction-benchmark)** — Synthetic smoking-history extraction benchmark comparing TypeSafe Jev and OpenAI structured outputs, with reproducible accuracy, cost, and latency results. <sub>(upstream description)</sub>
  <sub>`Benchmark` · vclic · `Py` · ⚠ `one commit` `no licence`</sub>

---

<sub>Generated from `catalog.json` by `scripts/build_readme.py`. Edit the catalogue, not this file.</sub>
