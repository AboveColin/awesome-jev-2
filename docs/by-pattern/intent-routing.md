# Intent routing

<sub>[awesome-jev](../../README.md) · [中文](intent-routing.zh-CN.md)</sub>

_Classify what the user wants and send the request down the right branch._

Every catalogued example of this decision — 35 of them. The same rows, with caveats, are in [the index](../../README.md#intent-routing); [the site](https://kydlikebtc.github.io/awesome-jev/?p=intent-routing&lang=en) can filter them further by language, primitive and kind.

★ gives a repository's GitHub stars as a band — ★10+, ★100+, ★1k+, ★10k+ and ★100k+; rows with no repository or under 10 stars show none. Rows run official first, then with code, then by band, then by title. A band is a popularity signal, not a quality verdict; the exact count, as last read from GitHub, is in [`catalog.json`](../../catalog.json) and on [the site](https://kydlikebtc.github.io/awesome-jev/?lang=en).

- **[Demo: Smart home assistant](https://docs.typesafe.ai/demos/smart-home)** ⭐ — Runnable demo code for a smart home assistant that evaluates user requests with typed decisions.
  <sub>`Official docs` · `Py`</sub>

- **[Pattern: Confidence-gated routing](https://docs.typesafe.ai/patterns/confidence-routing)** ⭐ — Treat confidence as a second axis: the answer tells you what, the confidence tells you whether to act on it.
  <sub>`Official docs` · `Py`</sub>

- **[Pattern: Intent routing](https://docs.typesafe.ai/patterns/intent-routing)** ⭐ — Classify an incoming request and route it to the cheapest adequate handler: deterministic code, a specialist LLM, or a person.
  <sub>`Official docs` · `Py` · `choice`</sub>

- **[AutoGPT TypeSafe blocks](https://github.com/Significant-Gravitas/AutoGPT/tree/master/autogpt_platform/backend/backend/blocks/typesafe)** — Seven production blocks — choice, score, yes/no, ask-many, route, pick-best, filter — with a UTF-8 byte budget, verbatim wire capture and eleven test files.
  <sub>`Project` · ★100k+ · `Py` · `choice` · `score` · `noul`</sub>

- **[Airflow LLMBranchOperator with Jev](https://airflow.apache.org/docs/apache-airflow-providers-common-ai/stable/index.html)** — Turns downstream task ids into a choice option set, with a minimum-confidence gate that routes uncertain runs to a human.
  <sub>`Integration` · ★10k+ · `Py` · `choice`</sub>

- **[Inbox Zero: seven email decisions](https://github.com/elie222/inbox-zero)** — Seven distinct email decisions, each with its own separately chosen threshold, falling back to the normal LLM on any error.
  <sub>`Project` · ★10k+ · `TS` · `choice` · `noul`</sub>

- **[ai-cookbook: Jev track](https://github.com/daveebbelaar/ai-cookbook)** — A graded course from a first call through each primitive, state shapes and criteria, to ticket triage and a multi-step workflow, mirroring all four official patterns.
  <sub>`Tutorial` · ★1k+ · `Py` · `choice` · `score` · `noul`</sub>

- **[jev-chat-jarvis](https://github.com/jev-chat/jev-chat-jarvis)** — An Android reply co-pilot that judges intent, timing and risk from on-screen text, while separate models handle OCR and drafting.
  <sub>`Project` · ★1k+ · `Java` · `choice` · `score` · `noul`</sub>

- **[Real Python: hello-jev](https://github.com/realpython/materials/tree/master/hello-jev)** — A teaching example with a deliberate control group: the same station-enquiry task written in plain Python that only accepts Y/N, next to a Noul that reads intent.
  <sub>`Tutorial` · ★1k+ · Real Python · `Py` · `noul`</sub>

- **[foreman](https://github.com/thruwire/foreman)** — A software-factory foreman that uses Jev to decide what an agent pipeline should do next.
  <sub>`Project` · ★100+ · thruwire · `Py`</sub>

- **[hyperedit](https://github.com/kevinbadi/hyperedit)** — An AI video editor routing an editing instruction to an operation, a target clip and a track, with a keyword router as fallback.
  <sub>`Project` · ★100+ · `TS` · `choice` · `noul` · ⚠ `no licence`</sub>

- **[jev-search](https://github.com/superagents-lab/jev-search)** — Jev-driven web search: chooses the recency window and the best query rewrite, then reranks results in batches with one noul each.
  <sub>`Project` · ★100+ · `TS` · `choice` · `noul`</sub>

- **[jev-voice-browser](https://github.com/moritzkremb/jev-voice-browser)** — Voice-driven browser control where target criteria are rebuilt per request from the live element list, always including a none option.
  <sub>`Project` · ★100+ · `JS` · `choice` · `score` · `noul`</sub>

- **[shapeshift](https://github.com/anishfn/shapeshift)** — An input that becomes what you mean: one text box that morphs into the right UI as you type. Powered by TypeSafe Jev, works offline.
  <sub>`Project` · ★100+ · anishfn · `TS`</sub>

- **[taskuary](https://github.com/ldbumble/taskuary)** — Automate your job: local-first AI task hub. Email, Teams, Slack & reports -> one timeline -> AI triage -> your coding agents (Claude Code, Codex, Gemini) do the work, you approve.
  <sub>`Plugin` · ★100+ · ldbumble · `Py`</sub>

- **[ha-jev](https://github.com/AboveColin/HA-Jev)** — A Home Assistant integration: typed answers as sensors, with actions for automations.
  <sub>`Integration` · ★10+ · abovecolin · `Py`</sub>

- **[hono-jev-router](https://github.com/yusukebe/hono-jev-router)** — Routes HTTP requests by meaning — a semantic router for a web framework.
  <sub>`Project` · ★10+ · yusukebe · `TS`</sub>

- **[jev-chat: a tool-calling chatbot with no LLM](https://github.com/w3cj/jev-chat)** — A chat bot that does tool calling with no language model anywhere: one request asks the request kind, the tool, and every tool's arguments at once.
  <sub>`Project` · ★10+ · `TS` · `choice` · `noul`</sub>

- **[jev-mail-classifier](https://github.com/parth-kp/jev-mail-classifier)** — Classify your inbox with Jev (TypeSafe's System One model) — tag, move, flag, and notify, all config-driven.
  <sub>`Project` · ★10+ · parth-kp · `Py`</sub>

- **[jev-social](https://github.com/socai-io/jev-social)** — Read-only Instagram, TikTok and LinkedIn research: Jev routes the platform and selects each bounded socai CLI action from fresh browser evidence; code validates targets and preserves source links.
  <sub>`Project` · ★10+ · socai-io · `JS` · `choice` · ⚠ `3rd-party key`</sub>

- **[jevyoumean](https://github.com/syumai/jevyoumean)** — Semantic "Did you mean?" for any CLI — wraps commands and uses TypeSafe's Jev to match subcommand typos by intent, not edit distance.
  <sub>`Project` · ★10+ · syumai · `Go`</sub>

- **[A deep dive into Jev, TypeSafe's System One model](https://flaviocopes.com/jev/)** — The densest independent explainer: code in JS, Python and the AI SDK, all three answer shapes, the advanced patterns, and an honest list of where the model fails.
  <sub>`Tutorial` · Flavio Copes · `JS` · `Py` · `TS` · `choice` · `score` · `noul`</sub>

- **[Example: confidence-gated escalation](https://github.com/kydlikebtc/awesome-jev/blob/main/examples/02-confidence-gate/main.py)** — Routing with an act-or-escalate gate, where the policy function is deliberately left unimplemented because the thresholds are yours to choose.
  <sub>`Snippet` · `Py` · `choice` · ⚠ `code untested`</sub>

- **[Jev AI Use Cases](https://medium.com/data-science-in-your-pocket/jev-ai-use-cases-9a87d57ac3b4)** — Walks through use case after use case — agent routing, an in-agent decision layer, ticket triage — each with a concrete option set and a sample response.
  <sub>`Tutorial` · Mehul Gupta · `Py` · `choice` · ⚠ `paywall`</sub>

- **[Jev on Netlify AI Gateway](https://www.netlify.com/changelog/typesafe-jev-ai-gateway/)** — Zero-config access from a Netlify function: use the official SDK with no API key, base URL or provider setup, billed through Netlify credits.
  <sub>`Integration` · `TS` · `choice`</sub>

- **[jev-ai-sdk-form-router](https://github.com/vercel-labs/jev-ai-sdk-form-router)** — Route form submissions to the right people with Jev and AI SDK.
  <sub>`Project` · vercel-labs · `TS`</sub>

- **[jev-eval](https://github.com/Shogo-nfrealmusic/jev-eval)** — A third-party check of Jev against two LLMs under identical conditions: routing booking inquiries to a photo-shoot service for tourists in Japan, sixty synthetic messages in four languages.
  <sub>`Benchmark` · shogo-nfrealmusic · `TS` · ⚠ `no licence`</sub>

- **[jev-inbox-queue](https://github.com/tusharck/jev-inbox-queue)** — Turn an inbox into a short action queue with Jev (TypeSafe System One)
  <sub>`Project` · tusharck · `Py`</sub>

- **[jev-phishing-bench](https://github.com/anisselbd/jev-phishing-bench)** — Jev (TypeSafe) vs Claude Haiku 4.5 on 2 000 phishing emails: accuracy, calibration, latency, cost. Reproducible benchmark.
  <sub>`Benchmark` · anisselbd · `Py` · ⚠ `no licence`</sub>

- **[jevcache](https://github.com/kushals256/jevcache)** — Skip expensive LLM calls when TypeSafe Jev says same intent. OpenAI-compatible local cache proxy — npx @kushalicious/jevcache
  <sub>`Project` · kushals256 · `TS`</sub>

- **[lanebreak](https://github.com/ndolinschi/lanebreak)** — LaneBreak — support ticket priority+routing via TypeSafe Jev
  <sub>`Project` · ndolinschi · `TS` · ⚠ `no licence`</sub>

- **[langchain-typesafe](https://docs.langchain.com/oss/python/integrations/providers/typesafe)** — The LangChain integration: a classifier plus experimental middleware for model routing and for gating risky tool calls before they run.
  <sub>`Integration` · `Py` · `choice` · `score` · `noul` · ⚠ `early access`</sub>

- **[typesafe-jev-workflow](https://github.com/GiesN/typesafe-jev-workflow)** — A small async LangGraph workflow: each mocked email goes to Jev as a typed Choice (invoice or general) and the graph routes it to a demo handler. Classification makes real API calls; the handlers only set a destination.
  <sub>`Project` · giesn · `Py` · ⚠ `no licence`</sub>

- **[Using TypeSafe Jev with the AI SDK](https://vercel.com/kb/guide/typesafe-jev-and-ai-sdk)** — The richest Vercel walkthrough: single and multi-question calls, probability-threshold routing, and unit tests with a mock evaluation model.
  <sub>`Tutorial` · `TS` · `noul` · `choice` · `score`</sub>

- **[jevai.org community showcase cases](https://www.jevai.org/cases)** — Nine worked community scenarios: intent routing, invoice classification, news filtering, product tagging, moderation, claim verification, CSV validation and more.
  <sub>`Project` · ⚠ `unverified claims`</sub>

---

<sub>Generated from `catalog.json` by `scripts/build_readme.py`. Edit the catalogue, not this file.</sub>
