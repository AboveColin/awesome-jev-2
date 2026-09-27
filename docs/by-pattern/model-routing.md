# Model routing

<sub>[awesome-jev](../../README.md) · [中文](model-routing.zh-CN.md)</sub>

_Pick which downstream model or tier should handle a request._

Every catalogued example of this decision — 43 of them. The same rows, with caveats, are in [the index](../../README.md#model-routing); [the site](https://kydlikebtc.github.io/awesome-jev/?p=model-routing&lang=en) can filter them further by language, primitive and kind.

★ gives a repository's GitHub stars as a band — ★10+, ★100+, ★1k+, ★10k+ and ★100k+; rows with no repository or under 10 stars show no band. Rows run official first, then with code, then by band, then by title. A band is a popularity signal, not a quality verdict; the exact count, as last read from GitHub, is in [`catalog.json`](../../catalog.json) and on [the site](https://kydlikebtc.github.io/awesome-jev/?lang=en).

- **[Cookbook: Structured data extraction cascade](https://docs.typesafe.ai/cookbooks/sde_cascade)** ⭐ — A two-stage mini-then-verify-then-reasoning cascade that reaches most of a big reasoning model's quality at a fraction of the cost.
  <sub>`Official docs` · `Py`</sub>

- **[Pattern: Intent routing](https://docs.typesafe.ai/patterns/intent-routing)** ⭐ — Classify an incoming request and route it to the cheapest adequate handler: deterministic code, a specialist LLM, or a person.
  <sub>`Official docs` · `Py` · `choice`</sub>

- **[@langchain/typesafe](https://github.com/langchain-ai/langchainjs)** — The JavaScript counterpart of the LangChain integration, with the same classifier and middleware shapes.
  <sub>`Integration` · ★10k+ · `TS` · `choice` · `score` · `noul`</sub>

- **[claude-code-templates: three Jev plugins](https://github.com/davila7/claude-code-templates)** — Three independently installable Claude Code plugins — guardrails, model router and skill suggestion — each with its own hooks and tests.
  <sub>`Plugin` · ★10k+ · `Py` · `TS` · `choice` · `score` · `noul`</sub>

- **[Astra-Ares](https://github.com/miuuyy/Astra-Ares)** — Adaptive reasoning effort for GPT-6 during Codex tasks, powered by Jev to reduce token usage.
  <sub>`Plugin` · ★100+ · miuuyy · `JS`</sub>

- **[hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills)** — Nine agent skills plus a CLI covering model routing, memory filtering, turn retention, one-of-many skill selection and next-action choice.
  <sub>`Plugin` · ★100+ · `Py` · `choice` · `score` · `noul`</sub>

- **[jev-codex-router](https://github.com/0xNatoshi/jev-codex-router)** — Judges how hard a coding turn is, then picks the model tier, reasoning depth and speed mode to match.
  <sub>`Plugin` · ★100+ · `JS` · `choice` · `score`</sub>

- **[jev-eval-agent](https://github.com/vinilana/jev-eval-agent)** — An agent that routes evaluation work through typed decisions.
  <sub>`Project` · ★100+ · vinilana · `TS` · ⚠ `no licence`</sub>

- **[jev-review](https://github.com/devagrawal09/jev-review)** — Pre-screens code review with Jev to surface high-risk changes for a more expensive model or a person, with a local dashboard.
  <sub>`Project` · ★100+ · `TS` · `choice` · `score` · `noul`</sub>

- **[jevrouter](https://github.com/BillionsBobby/JevRouter)** — A router for models, tools and subagents.
  <sub>`Project` · ★100+ · billionsbobby · `TS`</sub>

- **[a3m-router](https://github.com/Das-rebel/a3m-router)** — ⚡ Adaptive multi-model LLM router — 80+ providers, Jev System One single-pass routing (model=jev-auto), pheromone-trail failover, parallel ensemble merge. npm: adaptive-memory-multi-model-router
  <sub>`Project` · ★10+ · das-rebel · `TS`</sub>

- **[jev-router](https://github.com/prismhq/jev-router)** — Open-source LLM router that uses TypeSafe's Jev to pick a model, on top of LiteLLM
  <sub>`Project` · ★10+ · prismhq · `Py`</sub>

- **[jev-use](https://github.com/shitianfang/jev-use)** — An agent plugin that hands steps needing no text output to Jev instead of the main model.
  <sub>`Plugin` · ★10+ · shitianfang · `JS`</sub>

- **[pi-jev-router](https://github.com/mejiasd3v/pi-jev-router)** — Automatic model routing for Pi using TypeSafe's Jev through Vercel AI Gateway
  <sub>`Project` · ★10+ · mejiasd3v · `JS`</sub>

- **[pi-jev-router](https://github.com/philippdubach/pi-jev-router)** — A minimal Pareto-optimal OpenRouter model router for pi, based on Jev
  <sub>`Plugin` · ★10+ · philippdubach · `TS`</sub>

- **[stuntd](https://github.com/bladedevoff/stuntd)** — Local proxy that learns your app's typed LLM decisions and answers them with a Laya head. Jev and OpenAI compatible.
  <sub>`Project` · ★10+ · bladedevoff · `Py`</sub>

- **[Building a Harness with Jev](https://www.langchain.com/blog/building-a-harness-with-jev)** — LangChain's explainer and integration walkthrough: the three question types, plus model routing and gating risky tool calls before they run.
  <sub>`Article` · Sydney Runkle, Hunter Lovell · `Py` · ⚠ `vendor numbers`</sub>

- **[Codex Jev Router](https://github.com/suenot/codex-jev-router)** — Uses Jev Choice and Noul judgments on short task summaries to select a Codex subagent model and reasoning effort with a Sol fallback.
  <sub>`Project` · suenot · `JS` · `choice` · `noul` · ⚠ `AI-written` `self-submitted`</sub>

- **[dsh-plugin-jev-effort-selector](https://github.com/justhalfbit/dsh-plugin-jev-effort-selector)** — A DeepSeek Harness plugin that picks the reasoning level automatically: Jev judges how much thought each message deserves, follow-ups inherit the topic's depth, low confidence rounds up, and any failure falls back silently.
  <sub>`Plugin` · justhalfbit · `JS`</sub>

- **[hermes-jev-router](https://github.com/ussyverse/hermes-jev-router)** — Experimental Hermes plugin: Jev-assisted model routing plans with budget and capability constraints. API access pending.
  <sub>`Plugin` · ussyverse · `Py`</sub>

- **[janus](https://github.com/FirasSX914/Janus)** — Measure when to use Jev and other models on your data, then route accordingly.
  <sub>`Project` · firassx914 · `Py`</sub>

- **[Jev AI Use Cases](https://medium.com/data-science-in-your-pocket/jev-ai-use-cases-9a87d57ac3b4)** — Walks through use case after use case — agent routing, an in-agent decision layer, ticket triage — each with a concrete option set and a sample response.
  <sub>`Tutorial` · Mehul Gupta · `Py` · `choice` · ⚠ `paywall`</sub>

- **[jev-auto-router](https://github.com/miniLV/Jev-Auto-Router)** — Jev Auto Router (Jev Router): experimental per-call GPT model routing for Codex via TypeSafe Jev and a local Responses proxy, with independent task verification.
  <sub>`Plugin` · minilv · `TS`</sub>

- **[jev-codex-bridge](https://github.com/ansidium/jev-codex-bridge)** — Model and reasoning routing for Codex Desktop and CLI, with a Windows service and validated updates
  <sub>`Plugin` · ansidium · `JS`</sub>

- **[jev-codex-pilot](https://github.com/Charlyhno-eng/jev-codex-pilot)** — Smart Codex overlay with JEV model routing, context optimization & Kanban automation. Reduce tokens, keep control
  <sub>`Plugin` · charlyhno-eng · `TS` · `choice` · `score` · `noul`</sub>

- **[jev-engineering](https://github.com/eugeniughelbur/jev-engineering)** — The decision layer for AI agents. Typed, calibrated decisions in ~400ms for two hundredths of a cent: gate tool calls, route models, rank options. With the 300-call injection test that found what breaks.
  <sub>`Project` · eugeniughelbur · `Py`</sub>

- **[jev-gate](https://github.com/MongLong0214/jev-gate)** — Not every coding task needs your best model. Experimental Jev-powered model routing for Claude Code — V3 prototype runs today, V4 routes at the task boundary.
  <sub>`Plugin` · monglong0214 · `TS` · ⚠ `no licence`</sub>

- **[jev-harness-router](https://github.com/JoacoMarc/jev-harness-router)** — Per-turn router for agent harnesses: one 350ms Jev call picks the model tier, effort, tools and skill, behind a hard deadline with a regex fallback. Claude Agent SDK adapter included.
  <sub>`SDK` · joacomarc · `TS`</sub>

- **[jev-model-router](https://github.com/az9713/jev-model-router)** — Jev (TypeSafe) model router on the Vercel AI Gateway
  <sub>`Project` · az9713 · `JS` · ⚠ `no licence`</sub>

- **[jev-model-router](https://github.com/Mandrilsquad1441/jev-model-router)** — Pick the best AI model and reasoning effort for any task in ~1s. Plugin for Claude Code, Claude Desktop and Codex, powered by TypeSafe's Jev decision model and live OpenRouter pricing. Balance intelligence, speed and cost, or choose your priority.
  <sub>`Plugin` · mandrilsquad1441 · `TS`</sub>

- **[jev-model-router](https://github.com/satviksinha/jev-model-router)** — Model router for Claude Code using Jev
  <sub>`Plugin` · satviksinha · `TS`</sub>

- **[jev-router](https://github.com/rajdhakad9826/jev-router)** — LLM router that picks the cheapest model capable of handling a query, using TypeSafe's Jev for fast classification instead of an LLM call.
  <sub>`Project` · rajdhakad9826 · `TS`</sub>

- **[jev-smart-router](https://github.com/rmosleydb/jev-smart-router)** — JEV Smart Router — a Databricks App that uses TypeSafe JEV to pick which model answers each message, then runs inference on the chosen Databricks Foundation Model API endpoint.
  <sub>`Project` · rmosleydb · `Py`</sub>

- **[jev-synthetic-survey](https://github.com/jjd-lab/jev-synthetic-survey)** — Jev vs GPT-4.1 as synthetic survey respondents on Twin-2K-500. How you ask mattered more than which model you used.
  <sub>`Project` · jjd-lab · `Py`</sub>

- **[jevonian](https://github.com/xinyao27/jevonian)** — A local endpoint between a coding agent and its providers that routes each turn to the most cost-effective capable model, manages quota and cache, and logs every routing decision to a local ledger.
  <sub>`Project` · xinyao27 · `TS`</sub>

- **[langchain-typesafe](https://docs.langchain.com/oss/python/integrations/providers/typesafe)** — The LangChain integration: a classifier plus experimental middleware for model routing and for gating risky tool calls before they run.
  <sub>`Integration` · `Py` · `choice` · `score` · `noul` · ⚠ `early access`</sub>

- **[pi-jev](https://github.com/iefnaf/pi-jev)** — Pi extension suite powered by Jev: selective context compaction and model routing
  <sub>`Plugin` · iefnaf · `TS`</sub>

- **[pi-typesafe-router](https://github.com/jekozyra/pi-typesafe-router)** — A Pi extension that has Jev classify each request and route it to the right model, off until you configure the mappings.
  <sub>`Plugin` · jekozyra · `TS`</sub>

- **[slo-router](https://github.com/zeeshan8281/slo-router)** — SLO-aware LLM inference router with Jev decisions, live queue metrics, counterfactual evaluation, and reproducible latency/cost benchmarks
  <sub>`Project` · zeeshan8281 · `Py` · ⚠ `no licence`</sub>

- **[smart-switch](https://github.com/reycn/smart-switch)** — Reimagined window switcher for macOS using frontier artificial intelligence. Predicted by TypeSafe's Jev model
  <sub>`Project` · reycn · `Swift`</sub>

- **[stuntdouble](https://github.com/ReallyArtificial/stuntdouble)** — A drop-in /v1/systemone proxy: the app keeps calling Jev while local decision models answer the same requests in the shadow, then it reports whether they would have decided the same — per question, per confidence band, at the app's own decide() — plus Brier, ECE, latency and cost.
  <sub>`Project` · Really Artificial · `JS` · `choice` · `score` · `noul` · ⚠ `AI-written`</sub>

- **[switchboard](https://github.com/aniruddh-krovvidi/switchboard)** — Guardrail + model router for LLM gateways on TypeSafe's Jev (System One model), with an independent accuracy/calibration/latency evaluation. Stdlib Python.
  <sub>`Project` · aniruddh-krovvidi · `Py` · ⚠ `no licence`</sub>

- **[tiershift](https://github.com/iamvatsalpatel/tiershift)** — Shift every LLM call to the cheapest model that can handle it. Routing decided by TypeSafe Jev in ~180 ms. No training data. Policy in plain YAML. TypeScript and Python.
  <sub>`Project` · iamvatsalpatel · `TS`</sub>

---

<sub>Generated from `catalog.json` by `scripts/build_readme.py`. Edit the catalogue, not this file.</sub>
