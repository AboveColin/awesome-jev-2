# Content scoring

<sub>[awesome-jev](../../README.md) · [中文](content-scoring.zh-CN.md)</sub>

_Score quality, risk or relevance on an ordered scale._

Every catalogued example of this decision — 164 of them. The same rows, with caveats, are in [the index](../../README.md#content-scoring); [the site](https://kydlikebtc.github.io/awesome-jev/?p=content-scoring&lang=en) can filter them further by language, primitive and kind.

★ gives a repository's GitHub stars as a band — ★10+, ★100+, ★1k+, ★10k+ and ★100k+; rows with no repository or under 10 stars show no band. Rows run official first, then with code, then by band, then by title. A band is a popularity signal, not a quality verdict; the exact count, as last read from GitHub, is in [`catalog.json`](../../catalog.json) and on [the site](https://kydlikebtc.github.io/awesome-jev/?lang=en).

- **[Cookbook: Self-consistency with choices](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook)** ⭐ — Adds an explicit "uncertain" outcome to moderation decisions and measures label agreement against the share of actions taken automatically.
  <sub>`Official docs` · `Py` · `choice`</sub>

- **[Pattern: Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring)** ⭐ — Break one broad judgement into atomic scores and combine them with weights that live in your code, not in the prompt.
  <sub>`Official docs` · `Py` · `score`</sub>

- **[AutoGPT TypeSafe blocks](https://github.com/Significant-Gravitas/AutoGPT/tree/master/autogpt_platform/backend/backend/blocks/typesafe)** — Seven production blocks — choice, score, yes/no, ask-many, route, pick-best, filter — with a UTF-8 byte budget, verbatim wire capture and eleven test files.
  <sub>`Project` · ★100k+ · `Py` · `choice` · `score` · `noul`</sub>

- **[worldmonitor: news threat classification](https://github.com/koala73/worldmonitor)** — Two Choice questions over threat level and category, held in shadow mode after a blind evaluation found Jev merely tied the incumbent model.
  <sub>`Benchmark` · ★10k+ · `TS` · `choice` · ⚠ `shadow mode`</sub>

- **[ai-cookbook: Jev track](https://github.com/daveebbelaar/ai-cookbook)** — A graded course from a first call through each primitive, state shapes and criteria, to ticket triage and a multi-step workflow, mirroring all four official patterns.
  <sub>`Tutorial` · ★1k+ · `Py` · `choice` · `score` · `noul`</sub>

- **[gptcache](https://github.com/zilliztech/GPTCache)** — Semantic cache for LLMs. Fully integrated with LangChain and llama_index. <sub>(upstream description)</sub>
  <sub>`Project` · ★1k+ · zilliztech · `Py`</sub>

- **[jev-chat-jarvis](https://github.com/jev-chat/jev-chat-jarvis)** — An Android reply co-pilot that judges intent, timing and risk from on-screen text, while separate models handle OCR and drafting.
  <sub>`Project` · ★1k+ · `Java` · `choice` · `score` · `noul`</sub>

- **[jev-review](https://github.com/NiazMorshed2007/jev-review)** — A local-first MCP plugin for continuous code-quality review by coding agents.
  <sub>`Plugin` · ★100+ · niazmorshed2007 · `TS`</sub>

- **[jev-review](https://github.com/devagrawal09/jev-review)** — Pre-screens code review with Jev to surface high-risk changes for a more expensive model or a person, with a local dashboard.
  <sub>`Project` · ★100+ · `TS` · `choice` · `score` · `noul`</sub>

- **[jev-semgrep](https://github.com/uehaj/jev-semgrep)** — grep by meaning, across languages. TypeSafe Jev scores every line against a meaning; combine meanings with AND/OR/NOT. 意味で探す grep。日本語で英語を、英語で日本語を検索できる <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · uehaj · `JS`</sub>

- **[killmyidea](https://github.com/monteduro/killmyidea)** — Scores a startup idea across several dimensions and returns a verdict of kill, fix or ship.
  <sub>`Project` · ★100+ · `TS` · `score` · `choice` · ⚠ `no licence`</sub>

- **[llm2jev](https://github.com/Yinsongxu/LLM2Jev)** — Adapt local language models into Jev-compatible structured decision engines with Choice, Score, and Noul outputs powered by prefill-only binary inference.
  <sub>`Project` · ★100+ · yinsongxu · `Py`</sub>

- **[neurolink](https://github.com/juspay/neurolink)** — The pipe layer of an AI nervous system: one interface connecting provider neurons to an application, across three inference types — generate, stream, and decide. Decide returns typed, calibrated judgments (boolean/choice/score) via TypeSafe Jev, not text.
  <sub>`Plugin` · ★100+ · juspay · `TS`</sub>

- **[perch: semantic code linting](https://github.com/lakeday-org/perch)** — Tree-sitter finds and ranks methods, then user-authored YAML rules compile into nouls, with severity read as the rubric's expected value rather than the top band.
  <sub>`Project` · ★100+ · `JS` · `choice` · `score` · `noul`</sub>

- **[pg-jev](https://github.com/realZachi/pg-jev)** — A real PostgreSQL extension exposing the primitives as SQL functions, so a semantic decision can appear in a WHERE clause over any row type.
  <sub>`Project` · ★100+ · `Py` · `sh` · `choice` · `score` · `noul`</sub>

- **[supercov](https://github.com/supercorp-ai/supercov)** — Code quality and coverage judgements for coding agents, in Rust.
  <sub>`Project` · ★100+ · supercorp-ai · `Rs`</sub>

- **[hookmeter-jev](https://github.com/ehui1226/hookmeter-jev)** — ⚡ Millisecond-level Viral Hook Telemetry & Co-pilot for Social Media (Chrome Extension + JEV System 1) <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · ehui1226 · `Py`</sub>

- **[jev-as-a-judge](https://github.com/danielgshea/jev-as-a-judge)** — Using Jev as an evaluator. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · danielgshea · `Py` · ⚠ `no licence`</sub>

- **[jev-calibrate](https://github.com/smkrv/jev-calibrate)** — Calibrate Jev questions against your own labels: tune criteria on labelled examples, confirm on a held-out set, get a verdict per question. Unofficial. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · smkrv · `TS`</sub>

- **[jev-code](https://github.com/FrancoisChastel/jev-code)** — Jev, TypeSafe's System One classifier, as a tool inside Claude Code, Codex, Pi, and OpenCode: typed classify, check, score, rank, and ask, plus one-command setup. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · francoischastel · `TS`</sub>

- **[jev-curate](https://github.com/AkashPriyadarshii/jev-curate)** — Curates training data: JSONL and Parquet rows are judged on quality, relevance and risk before deciding what reaches downstream training.
  <sub>`Project` · ★10+ · `Rs` · `score` · `noul`</sub>

- **[jev-dataops](https://github.com/RenaGao/jev-dataops)** — An open-source JEV-powered workbench for streaming data selection, quality evaluation, automatic LoRA training and held-out model evaluation. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · renagao · `Py`</sub>

- **[jev-feels](https://github.com/Qew7/jev-feels)** — Semantic decisions as ordinary Ruby — feels?, decide, score, Rails validations and pattern matching powered by Jev
  <sub>`Project` · ★10+ · qew7 · `Rb`</sub>

- **[jev-forge](https://github.com/zwliJay/jev-forge)** — An open training and inference stack for Jev-style decision models. Train models to score dynamic candidate branches from a shared prefix, with support for high-cardinality choice, calibration, and fast batched inference. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · zwlijay · `Py` · ⚠ `not Jev itself`</sub>

- **[jev-lint](https://github.com/mizchi/jev-lint)** — lint text in code by jev scorerer <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · mizchi · `TS`</sub>

- **[jev-mcp](https://github.com/blakestone-x/jev-mcp)** — An MCP server exposing classify, score, check, match and screen to any agent.
  <sub>`Plugin` · ★10+ · blakestone-x · `Py`</sub>

- **[Jev-Moderation-Bot](https://github.com/brainstormity/Jev-Moderation-Bot)** — A Discord moderation bot: a Choice tiers each message while a Noul carries ban urgency, and an admin pardon is fed back as a safe precedent in later requests.
  <sub>`Project` · ★10+ · brainstormity · `Py` · `choice` · `noul`</sub>

- **[jev-seo](https://github.com/AgriciDaniel/jev-seo)** — Live SEO audit for any website from one homepage URL, judged by Jev. PDF, XLSX and Markdown reports. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · agricidaniel · `Py`</sub>

- **[jev-superpowers](https://github.com/AkashPriyadarshii/jev-superpowers)** — Systematic software development framework for AI coding agents upgraded with TypeSafe Jev System One typed decisions <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · akashpriyadarshii · `TS`</sub>

- **[jev-test-filter](https://github.com/mizchi/jev-test-filter)** — Score every test against a git diff with Jev, and emit the filter arguments vitest, node:test, Playwright, cargo test and go test already understand <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · mizchi · `TS`</sub>

- **[jev-yaba-wechat](https://github.com/wuxie888/jev-yaba-wechat)** — A macOS floating assistant for replying in WeChat: it reads a message's intent and communication risk, GPT drafts several replies, Jev rates the candidates, and one click fills the chosen one in. You still decide what to send.
  <sub>`Project` · ★10+ · wuxie888 · `Py`</sub>

- **[jevalyn](https://github.com/Ray-Hughes/jevalyn)** — The decision layer for your Rails app. A Rails-native wrapper around TypeSafe's Jev System One API: typed, calibrated decisions in your control flow. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · ray-hughes · `Rb`</sub>

- **[jevframe](https://github.com/ktaletsk/jevframe)** — Semantic AI for pandas and Polars: classify text, analyze sentiment, and score DataFrame rows with natural-language questions and full probabilities using TypeSafe Jev. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · ktaletsk · `Py`</sub>

- **[jevgpt](https://github.com/Bewinxed/jevgpt)** — A chatbot built on a model that cannot generate text (TypeSafe AI's Jev, driven autoregressively) <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · bewinxed · `TS`</sub>

- **[jevlint](https://github.com/iamtoomas/JevLint)** — Configurable semantic linting powered by Jev, with file-level NOUL judgments and a magic-strings plugin. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · huntedman · `TS`</sub>

- **[jevlogs](https://github.com/reachjalil/jevlogs)** — Open-source Jev log triage for OpenTelemetry. Score the signal before expensive LLM analysis. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · reachjalil · `JS`</sub>

- **[jevmeter](https://github.com/ChetasLua/jevmeter)** — Scores every sentence of a video and renders the result as a live meter.
  <sub>`Project` · ★10+ · chetaslua · `Py`</sub>

- **[JevScout](https://github.com/hqman/JevScout)** — A coding-agent skill that hunts jobs on real company sites: Chrome sees and acts, Jev scores every link and posting, and the host LLM never picks what to click.
  <sub>`Plugin` · ★10+ · hqman · `Py` · ⚠ `no licence`</sub>

- **[jsort](https://github.com/keltokhy/jsort)** — sort by meaning: order lines along a plain-English dimension, from pairwise comparisons judged by TypeSafe's Jev model <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · keltokhy · `Py`</sub>

- **[MetaCog](https://github.com/ItIsCuthNotCup/MetaCog)** — Inference-time metacognition: a small, fast judge scores a bigger model's answers and steers its reasoning; Jev is one of the judges it can use.
  <sub>`Project` · ★10+ · itiscuthnotcup · `Py`</sub>

- **[plugins](https://github.com/cline/plugins)** — Official curated plugins for Cline CLI and extensions <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · cline · `TS`</sub>

- **[SemDecide](https://github.com/sharziki/semdecide)** — Jev as a command-line tool: classify, score and filter straight from a shell, for crawlers, CI and data pipelines.
  <sub>`Plugin` · ★10+ · `Py` · `sh` · `choice` · `score` · `noul`</sub>

- **[slop-grader](https://github.com/lukstei/slop-grader)** — Jev-powered, rule-based grader for text files. Runs every rule against every line in parallel. No skimming, no missed lines. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · lukstei · `TS`</sub>

- **[smartmoney-cub](https://github.com/myc0576/SmartMoney-Cub)** — Read-only trading journal and review harness: Jev typed judgments, agent integration, and a reproducible finance benchmark. No orders, no advice. <sub>(upstream description)</sub>
  <sub>`Benchmark` · ★10+ · myc0576 · `Py`</sub>

- **[snifftest](https://github.com/DanRWilloughby/snifftest)** — A prose linter that sniffs out AI writing tells. Zero dependencies, countable rules plus one judgment model. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · danrwilloughby · `TS`</sub>

- **[typed-decision-bert](https://github.com/hawkymisc/typed-decision-bert)** — Unofficial PoC: a BERT-style encoder decision engine behind a typed-decision (noul / choice / score) HTTP API. Not affiliated with TypeSafe. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · hawkymisc · `Py`</sub>

- **[Working-Memory-Jev](https://github.com/AustinAWay/Working-Memory-Jev)** — Passage: helps educators see where instructional text may ask a learner to hold too many ideas at once, using the real Jev API to trace active groups and changes in demand.
  <sub>`Project` · ★10+ · austinaway · `Py`</sub>

- **[x-scanner](https://github.com/oso95/x-scanner)** — Chrome extension that labels every post you scroll past on X with typed Jev judgments and a live cost counter <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · oso95 · `TS`</sub>

- **[yoshi](https://github.com/compozy/yoshi)** — Context-pruning proxy for Claude Code and Codex: Jev judges which history is still needed, measured not claimed. POC here now, heading soon into https://github.com/compozy/compozy <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · compozy · `TS`</sub>

- **[A deep dive into Jev, TypeSafe's System One model](https://flaviocopes.com/jev/)** — The densest independent explainer: code in JS, Python and the AI SDK, all three answer shapes, the advanced patterns, and an honest list of where the model fails.
  <sub>`Tutorial` · Flavio Copes · `JS` · `Py` · `TS` · `choice` · `score` · `noul`</sub>

- **[a0-typesafe-ai](https://github.com/3clyp50/a0-typesafe-ai)** — TypeSafe AI Jev judgments for Agent Zero, with typed tools and probability cards. <sub>(upstream description)</sub>
  <sub>`Project` · 3clyp50 · `Py`</sub>

- **[ai-provider-for-jev](https://github.com/soderlind/ai-provider-for-jev)** — Connect WordPress to TypeSafe's Jev System One model for structured decisions (choice, score, noul). <sub>(upstream description)</sub>
  <sub>`Integration` · soderlind · `PHP` · ⚠ `no licence`</sub>

- **[anydecisionmodel](https://github.com/mattt/AnyDecisionModel)** — A Swift package for typed decisions from language models (probabilities, choices, and scores), with support for local MLX models and the TypeSafe Jev API. <sub>(upstream description)</sub>
  <sub>`Project` · mattt · `Swift`</sub>

- **[aside-jev](https://github.com/himomohi/aside-jev)** — Aside agents decide with TypeSafe Jev (System One: Choice/Score/Noul). Not a Cua binding — Jev is the model, Aside is the browser runtime. <sub>(upstream description)</sub>
  <sub>`SDK` · himomohi · `Py`</sub>

- **[ask-jev-ai](https://github.com/waynesutton/ask-jev-ai)** — A public wall where anyone asks a question in three to fifteen words and Jev, TypeSafe's judgment model, answers yes, no, or it depends in about 100 milliseconds. Every judged ask lands on the wall in realtime, with a running count toward one million, showing cost. <sub>(upstream description)</sub>
  <sub>`Project` · waynesutton · `JS` · ⚠ `no licence`</sub>

- **[book-aurora](https://github.com/dani1005/book-aurora)** — Jev reads a whole novel in seconds. Every passage becomes a row of colour. <sub>(upstream description)</sub>
  <sub>`Project` · dani1005 · `TS`</sub>

- **[citation-verifier](https://github.com/MarissaFamularo/citation-verifier)** — Check whether each cited paper supports the sentence citing it. Claude proves the quote, TypeSafe's Jev scores it, a human decides. <sub>(upstream description)</sub>
  <sub>`Project` · marissafamularo · `JS`</sub>

- **[clarity-judge](https://github.com/TypeSafeAI/clarity-judge)** — Multi-axis writing quality checker powered by TypeSafe AI's Jev model. Separate named checks, each with its own verdict and confidence. <sub>(upstream description)</sub>
  <sub>`Project` · bunsdev · `TS` · ⚠ `no licence`</sub>

- **[claude-jev](https://github.com/buchmark/claude-jev)** — Claude Code plugin that scores review findings, debug hypotheses and design options with TypeSafe's Jev — calibrated probabilities instead of one more opinion. <sub>(upstream description)</sub>
  <sub>`Plugin` · buchmark · `TS`</sub>

- **[clear-head](https://github.com/VladyslavHontar/clear-head)** — Claude Code Stop hook that checks an AI assistant's claims against what it actually read this session, using TypeSafe's Jev as the judge <sub>(upstream description)</sub>
  <sub>`Plugin` · vladyslavhontar · `Py`</sub>

- **[decide-mcp](https://github.com/dakdevs/decide-mcp)** — Configurable decision MCP server with AI SDK, Jev, percentage scores, and bias profile routing <sub>(upstream description)</sub>
  <sub>`SDK` · dakdevs · `TS`</sub>

- **[decision-first](https://github.com/harrymunro/decision-first)** — Agent skill that spots bounded-judgment steps, tries a typed decision model (TypeSafe's Jev) first, and documents every attempt <sub>(upstream description)</sub>
  <sub>`Plugin` · harrymunro · `Py`</sub>

- **[deslop](https://github.com/yoichiojima-2/deslop)** — Score web pages for ads, slop, SEO and second-hand content. An agent skill built on TypeSafe Jev: four probabilities per page, no verdict, the caller sets the thresholds. <sub>(upstream description)</sub>
  <sub>`Plugin` · yoichiojima-2 · `Py`</sub>

- **[draftpulse](https://github.com/pekth/draftpulse)** — Experimental: live X draft viral scorer powered by TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Project` · pekth · `TS` · ⚠ `no licence`</sub>

- **[dsh-jev](https://github.com/noetion/dsh-jev)** — DSH bundle that registers jev_ask for TypeSafe Jev noul, choice, and score answers. <sub>(upstream description)</sub>
  <sub>`Project` · noetion · `TS`</sub>

- **[dsh-jev-decide](https://github.com/nanami-0713/dsh-jev-decide)** — DSH plugin: register TypeSafe Jev (System One decision model) as an agent tool — jev_decide returns calibrated probabilities (noul/choice/score) for routing/triage/guardrail judgments, no text generation. 把 TypeSafe Jev 决策模型注册为 DSH agent 工具 <sub>(upstream description)</sub>
  <sub>`Plugin` · nanami-0713 · `JS`</sub>

- **[dsh-jev-prune](https://github.com/yangyu666/dsh-jev-prune)** — Jev-judged context compaction for DeepSeek Harness: semantic tool-result pruning + deterministic receipt compaction <sub>(upstream description)</sub>
  <sub>`Project` · yangyu666 · `JS`</sub>

- **[dsh-jev-verify](https://github.com/xienda/dsh-jev-verify)** — Jev (TypeSafe System One) decision tools + live verification benchmark for DeepSeek Harness: jev_decision (choice/score/noul) and jev_verify, honest by design. <sub>(upstream description)</sub>
  <sub>`Benchmark` · xienda · `JS`</sub>

- **[github-issue-classification-using-jev](https://github.com/KalyanM45/GitHub-Issue-Classification-Using-Jev)** — This repository contains a GitHub issue classifier built on Jev, TypeSafe AI's System One model. It labels every new issue with typed values and calibrated confidence in milliseconds, labelling what it is sure about and escalating what it is not. Three guardrail layers guard every write, and a
  <sub>`Project` · kalyanm45 · `Py`</sub>

- **[gpt-vs-jev](https://github.com/TanayPadar/gpt-vs-jev)** — Compare GPT generated language with JEV structured Noul decisions on the same input. <sub>(upstream description)</sub>
  <sub>`Project` · tanaypadar · `TS`</sub>

- **[harnessjudge](https://github.com/ndolinschi/harnessjudge)** — Judge agent steps — ok / retry / escalate / stop via TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Project` · ndolinschi · `TS` · ⚠ `no licence`</sub>

- **[heist-one](https://github.com/AbdelStark/heist-one)** — Observable browser stealth game: Jev makes typed guard judgments while deterministic code owns the world. <sub>(upstream description)</sub>
  <sub>`Project` · abdelstark · `TS`</sub>

- **[hush](https://github.com/emreozyoruk/hush)** — Issue triage that stays quiet when it isn't sure. Calibrated labels, spam and duplicate detection — with abstention. <sub>(upstream description)</sub>
  <sub>`Project` · emreozyoruk · `JS`</sub>

- **[instruct-jev](https://github.com/ctaxnagomi/instruct-jev)** — INSTRUCT_JEV - TypeSafe AI Jev / System One instruction corpus (choice/noul/score), compiled by DeckerGUI. 119 rows. Mirrored on HuggingFace. <sub>(upstream description)</sub>
  <sub>`Project` · ctaxnagomi · `Py`</sub>

- **[jev-as-quant](https://github.com/jiayylu/jev-as-quant)** — Typed System-1 decisions (Laya/Jev) as the judgment layer of a quant research stack, with Claude as System 2. Requirements → design → code → experiments. <sub>(upstream description)</sub>
  <sub>`Project` · jiayylu · `Py`</sub>

- **[jev-asks-until-sure](https://github.com/mintannn/jev-asks-until-sure)** — A twenty-questions guesser that keeps asking until Jev's calibrated confidence crosses a threshold — or gives up and says so <sub>(upstream description)</sub>
  <sub>`Project` · mintannn · `TS`</sub>

- **[jev-builder-loop](https://github.com/rainbowpuffpuff/jev-builder-loop)** — Grok skill: Jev as a judgment sensor in a builder-agent loop (priors × probabilities → next act) <sub>(upstream description)</sub>
  <sub>`Plugin` · rainbowpuffpuff · `Py`</sub>

- **[jev-carryforward](https://github.com/Dharundp6/jev-carryforward)** — What your last session knew, scored against what this one is doing. MCP server: a per-project ledger written as things happen, recalled per task with TypeSafe's Jev evaluation model via Vercel AI Gateway. <sub>(upstream description)</sub>
  <sub>`Plugin` · dharundp6 · `TS`</sub>

- **[jev-certify](https://github.com/nikkoxgonzales/jev-certify)** — Finite-sample guarantees for Jev (TypeSafe's System One). Conformal risk control turns calibrated probabilities into certified routing thresholds; prediction-powered inference audits them. 2,412 decisions on CLINC150 for $0.23 — including the shift and prevalence cases where the guarantee break
  <sub>`Benchmark` · nikkoxgonzales · `Py`</sub>

- **[jev-compaction](https://github.com/picaye/jev-compaction)** — Context compaction for Hermes sessions that never summarises: every tool call is scored by TypeSafe's Jev model, stale calls are dropped, everything kept stays verbatim. <sub>(upstream description)</sub>
  <sub>`Project` · picaye · `JS`</sub>

- **[jev-decision-lab](https://github.com/jlov7/jev-decision-lab)** — A local lab for seeing what TypeSafe's Jev judgment model does on realistic business cases: typed answers, probabilities, policy in code, receipts. <sub>(upstream description)</sub>
  <sub>`Project` · jlov7 · `Py`</sub>

- **[jev-dsl](https://github.com/inanna-malick/jev-dsl)** — Agent-first Haskell DSL for TypeSafe's Jev judgment model: typed packets, inferred types, answers under the same labels <sub>(upstream description)</sub>
  <sub>`Project` · inanna-malick · `Hs`</sub>

- **[jev-flash-router](https://github.com/Ravinder82/jev-flash-router)** — open-sourced jev-flash-router: an MCP server for TypeSafe's new Jev model. AI coding agents waste hundreds of reasoning tokens just deciding which file to edit, which route to pick, or whether a diff breaks tests. Jev evaluates state and outputs calibrated probabilities. Works with Cursor, Wind
  <sub>`Plugin` · ravinder82 · `TS`</sub>

- **[jev-gates](https://github.com/rashedInt32/jev-gates)** — Six calibrated gates for Claude Code, judged by TypeSafe Jev: rules, scope, intent, done, claims, and commit honesty. Each one escalates, none ever approves. <sub>(upstream description)</sub>
  <sub>`Plugin` · rashedint32 · `JS`</sub>

- **[jev-hooks](https://github.com/microchipgnu/jev-hooks)** — Compose typed Jev judgments as reactive semantic state in React and backend programs <sub>(upstream description)</sub>
  <sub>`Project` · microchipgnu · `TS` · ⚠ `no licence`</sub>

- **[jev-judgment](https://github.com/HyunjunJeon/jev-judgment)** — Agent Skill: send closed coding-agent judgments to TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Plugin` · hyunjunjeon · `Py`</sub>

- **[jev-llm-router-benchmark](https://github.com/erendikmenn/jev-llm-router-benchmark)** — Benchmark-driven Jev router and judge for cost-aware, reliable LLM coding workflows <sub>(upstream description)</sub>
  <sub>`Benchmark` · erendikmenn · `Py`</sub>

- **[jev-local](https://github.com/us/jev-local)** — Local Jev-compatible evaluation server: POST /v1/systemone with typed noul/choice/score, open weights, no waitlist <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · us · `Py` · ⚠ `not Jev itself` `no licence`</sub>

- **[jev-mcp-server](https://github.com/wangkuangkuang/jev-mcp-server)** — MCP server for Jev (TypeSafe System One): the three official question types — choice, score, noul — plus batch classify. Calibrated probabilities, ~0.5s, <$0.001/call. <sub>(upstream description)</sub>
  <sub>`Plugin` · wangkuangkuang · `Py`</sub>

- **[jev-mode](https://github.com/ddfeyes/jev-mode)** — I kept watching coding agents burn context on decisions that aren't hard - triage 400 tickets, tag 600 files, route to one of six teams. jev-mode moves those verdicts to a typed-judgment model. I A/B'd it: 78% fewer tokens, 16x less work-attributable input, accuracy 96.1% vs 93.7%. Python, no d
  <sub>`Project` · ddfeyes · `Py`</sub>

- **[jev-model-router](https://github.com/lucianfialho/jev-model-router)** — Cost-optimized OpenRouter model router using TypeSafe's Jev, with a live full-catalog scorer instead of a hardcoded model list <sub>(upstream description)</sub>
  <sub>`Project` · lucianfialho · `Py`</sub>

- **[jev-ood-calibration](https://github.com/scienthoon/jev-ood-calibration)** — Independent calibration test of TypeSafe's Jev on a task it cannot have seen: 900 rule-generated support tickets (choice / score / boolean) plus 3 public benchmarks via Vercel AI Gateway. Raw responses, ECE with noise floor, temperature refit, per-type sign of miscalibration. Reproducible for ~
  <sub>`Benchmark` · scienthoon · `Py`</sub>

- **[jev-orderby-bench](https://github.com/yodablocks/jev-orderby-bench)** — Does ORDER BY over a Jev probability put rows in a defensible order? Independent ranking, calibration and invariant measurements of TypeSafe AI's Jev: passes six pre-registered gates on 360 labeled rows, fails four of six on graded product relevance. <sub>(upstream description)</sub>
  <sub>`Benchmark` · yodablocks · `Py`</sub>

- **[jev-packs](https://github.com/dtduc-git/jev-packs)** — Evidence-gated registry of Jev question packs — curated questions, golden cases and measured evidence for Jev-compatible decision endpoints <sub>(upstream description)</sub>
  <sub>`Project` · dtduc-git · `Py`</sub>

- **[jev-paper-judge](https://github.com/JacobLinCool/jev-paper-judge)** — Feedback on your paper in seconds. <sub>(upstream description)</sub>
  <sub>`Project` · jacoblincool · `TS`</sub>

- **[JEV-Paper-Radar](https://github.com/Eliot5566/JEV-Paper-Radar)** — Let Jev read every new arXiv paper each morning and surface the few you should read. Plain-English interests, calibrated probabilities, ~$0.06/day, fork and go. <sub>(upstream description)</sub>
  <sub>`Project` · eliot5566 · `Py`</sub>

- **[jev-rl](https://github.com/Bring-AI/jev-rl)** — JEV Reinforcement Learning: four classic games trained with JEV-powered rewards, reproducible experiments and checkpoint replays. <sub>(upstream description)</sub>
  <sub>`Project` · bring-ai · `Py`</sub>

- **[jev-rs](https://github.com/yijunyu/jev-rs)** — System One judgments (noul/choice/score) from any LLM in one prefill — a Rust, Jev-compatible /v1/systemone engine <sub>(upstream description)</sub>
  <sub>`Project` · yijunyu · `Rs`</sub>

- **[jev-score](https://github.com/a-Fig/jev-score)** — Local-first document evaluation workspaces powered by Jev <sub>(upstream description)</sub>
  <sub>`Project` · a-fig · `JS`</sub>

- **[jev-scout](https://github.com/AkashPriyadarshii/jev-scout)** — Zero-hallucination open-source repo and crate scout powered by TypeSafe AI Jev System One scoring <sub>(upstream description)</sub>
  <sub>`Project` · akashpriyadarshii · `Rs`</sub>

- **[jev-shadcn-lint-eval](https://github.com/blas0/jev-shadcn-lint-eval)** — A small second eval for shadcn-ui/lint that uses TypeSafe's Jev to judge the linter's own output. <sub>(upstream description)</sub>
  <sub>`Project` · blas0 · `JS`</sub>

- **[jev-skill-gate](https://github.com/ShivamPansuriya/jev-skill-gate)** — Cut Claude Code's skill manifest by ~75% with TypeSafe Jev. Scores every installed skill for relevance and hides the rest via skillOverrides — 12,750 → 3,185 tokens on a 217-skill install, for $0.0009 a session. <sub>(upstream description)</sub>
  <sub>`Plugin` · shivampansuriya · `JS`</sub>

- **[jev-songwriter](https://github.com/beingcognitive/jev-songwriter)** — A decision model that cannot write a single note writes songs. Code computes, Jev judges, and every call is replayable. <sub>(upstream description)</sub>
  <sub>`Project` · beingcognitive · `JS`</sub>

- **[Jev-test](https://github.com/WeSecureYou/Jev-test)** — A CLI and REST API that asks Jev how exposed an occupation is to AI-driven layoffs, where it is heading, how much human accountability it needs, and how resilient it is.
  <sub>`Project` · wesecureyou · `TS` · ⚠ `no licence`</sub>

- **[jev-trace-classifier](https://github.com/sypherin/jev-trace-classifier)** — Application of TypeSafe Jev (noul judgment primitive) on the collusion.wiki corpus: agent vs human page authorship, head-to-head vs local Qwen3.8-Flash-Next <sub>(upstream description)</sub>
  <sub>`Benchmark` · sypherin · `Py`</sub>

- **[jev-ui](https://github.com/etweisberg/jev-ui)** — React components that resolve which component to render, how to order a list, and whether to show an affordance — from calibrated judgments returned by TypeSafe's Jev. <sub>(upstream description)</sub>
  <sub>`Project` · etweisberg · `TS` · ⚠ `no licence`</sub>

- **[jev-workbench](https://github.com/molis-ai/jev-workbench)** — Build versioned judgment functions on TypeSafe's Jev once, then call the same published version from your backend over HTTP and from coding agents over MCP. The vendor key stays on your machine. <sub>(upstream description)</sub>
  <sub>`Plugin` · molis-ai · `TS`</sub>

- **[jev-wrapped](https://github.com/gaborishka/jev-wrapped)** — Telegram channel X-ray: Jev judges a year of posts, you get a card. One Cloudflare Worker. <sub>(upstream description)</sub>
  <sub>`Project` · gaborishka · `JS`</sub>

- **[jevaluate](https://github.com/ElshinQ/jevaluate)** — Jevaluate: evaluate before you trust. Field notes, runnable scripts and an agent skill for TypeSafe Jev: gated evals, a browser loop, a product walk with DeepSeek vision, a UI text judge and a first-click tree test. Co-authored with Claude Fable 5.1. <sub>(upstream description)</sub>
  <sub>`Plugin` · elshinq · `JS`</sub>

- **[jevbus](https://github.com/zkjoie/jevbus)** — A streaming event bus whose routing, subscription and consumption are decided by a probabilistic judge. The reference judge is TypeSafe AI's Jev (System One) model: send it a payload and a set of typed questions, get back calibrated probabilities instead of prose. <sub>(upstream description)</sub>
  <sub>`Project` · zkjoie · `Rs`</sub>

- **[jevchess](https://github.com/choxos/jevchess)** — Jev, TypeSafe's System One model, plays chess against any OpenRouter LLM, Stockfish and you. One-page web app with live moves, Jev's move probabilities, saved games and win rates. <sub>(upstream description)</sub>
  <sub>`Project` · choxos · `JS`</sub>

- **[jevflow](https://github.com/Mawfyy/jevflow)** — Probabilistic AI decisions as composable backend primitives — typed judgments (noul/score/choice), deterministic thresholds, and explainable workflows. Powered by TypeSafe's Jev, provider-agnostic. <sub>(upstream description)</sub>
  <sub>`Integration` · mawfyy · `TS` · ⚠ `no licence`</sub>

- **[jevmetrics](https://github.com/ishantanu/jevmetrics)** — An experimental OpenTelemetry Collector processor that asks Jev how operationally valuable each metric instrument is, from its metadata, then applies deterministic policy to decide what to keep.
  <sub>`Project` · ishantanu · `Go`</sub>

- **[jevmoji](https://github.com/cheeaun/jevmoji)** — Type anything. Get related emojis scored 0–3 with Jev. <sub>(upstream description)</sub>
  <sub>`Project` · cheeaun · `JS`</sub>

- **[jevmory](https://github.com/romiluz13/jevmory)** — Coding-agent memory where every fact is a verbatim quote graded by TypeSafe Jev's calibrated confidence. Local-first, SQLite receipts, zero dependencies. <sub>(upstream description)</sub>
  <sub>`Project` · romiluz13 · `Py`</sub>

- **[jevplay](https://github.com/ndolinschi/jevplay)** — TypeSafe Jev playground — custom Choice/Score/Noul builder with live distributions <sub>(upstream description)</sub>
  <sub>`Project` · ndolinschi · `TS` · ⚠ `no licence`</sub>

- **[JevPromptCoach](https://github.com/CrowdLinker/JevPromptCoach)** — Claude Code plugin that scores how well you prompt a coding agent, and shows whether your habits are improving. Runs on TypeSafe's Jev model. Zero added latency. <sub>(upstream description)</sub>
  <sub>`Plugin` · crowdlinker · `TS`</sub>

- **[jevriel](https://github.com/thehan-co/jevriel)** — Give your AI JEV wings. A skill and plugin to build with TypeSafe Jev, upgrade LLM-only workflows and measure the result. <sub>(upstream description)</sub>
  <sub>`Plugin` · thehan-co · `JS`</sub>

- **[jevseek](https://github.com/morcoan/JMP)** — JMP — Joint Model Participation. A local coding workspace where Jev routes actions and OpenAI, DeepSeek, or local models generate arguments. <sub>(upstream description)</sub>
  <sub>`Project` · morcoan · `Py` · ⚠ `archived`</sub>

- **[jevseo](https://github.com/epergaboni/jevseo)** — Typed SEO, AEO and GEO judgments powered by Jev, a System One decision model. Code owns the rules, the model owns the meaning. <sub>(upstream description)</sub>
  <sub>`Project` · epergaboni · `TS`</sub>

- **[jevshield](https://github.com/lgy1027/jevshield)** — Sub-100ms security gate for AI agent tool calls, powered by TypeSafe's Jev (System-1) decision model. Single-request Choice/Noul/Score evaluation, dual-factor blocking matrix, calibrated-confidence routing, fail-closed parsing, zero-config local fallback. LangChain-ready. <sub>(upstream description)</sub>
  <sub>`Project` · lgy1027 · `Py`</sub>

- **[judging-with-typesafe](https://github.com/carlsonchik/judging-with-typesafe)** — Скилл для агентов Letta: суждения по критериям через TypeSafe System One (Jev) <sub>(upstream description)</sub>
  <sub>`Project` · carlsonchik · `Py` · ⚠ `no licence`</sub>

- **[leanest](https://github.com/baronunread/leanest)** — Local-first test selector using Jev judgments to determine which tests are affected by a code change <sub>(upstream description)</sub>
  <sub>`Project` · baronunread · `TS`</sub>

- **[limpet](https://github.com/noplan-inc/limpet)** — A Stop hook that stops your coding agent from stopping too early. Plain-language rules, judged by jev. <sub>(upstream description)</sub>
  <sub>`Plugin` · noplan-inc · `Py`</sub>

- **[llama-index-jev](https://github.com/WiktorB2004/llama-index-jev)** — LlamaIndex reranker + router powered by TypeSafe Jev — typed scores/choices, cheaper than LLM-as-judge.
  <sub>`Project` · wiktorb2004 · `Py`</sub>

- **[local-jev](https://github.com/amithgc/local-jev)** — A local, offline System One server compatible with TypeSafe's Jev API. It answers typed yes/no, category and score questions with small open models. <sub>(upstream description)</sub>
  <sub>`Project` · amithgc · `Py`</sub>

- **[luce](https://github.com/scienthoon/luce)** — Luce: a recipe for calibrated decision models — a sentence about your task in, a small model that answers typed questions with honest probabilities out (init → synth → train → eval → serve) <sub>(upstream description)</sub>
  <sub>`Project` · scienthoon · `Py`</sub>

- **[n8n-nodes-jev-classification](https://github.com/khmuhtadin/n8n-nodes-jev-classification)** — n8n community node for Jev by TypeSafe AI: classify, score and check text with calibrated probabilities. Parallel requests and multi-item batching. <sub>(upstream description)</sub>
  <sub>`Project` · khmuhtadin · `TS`</sub>

- **[n8n-nodes-typesafe-ai](https://github.com/DomMonte/n8n-nodes-typesafe-ai)** — n8n community node for the TypeSafe AI System One API — typed yes/no, choice and score questions with calibrated probabilities <sub>(upstream description)</sub>
  <sub>`Project` · dommonte · `TS`</sub>

- **[omp-jev-compaction](https://github.com/jerryfane/omp-jev-compaction)** — Verbatim Jev-scored context reduction for omp, over TypeSafe or OpenRouter <sub>(upstream description)</sub>
  <sub>`Project` · jerryfane · `TS`</sub>

- **[omp-jevens-classifier](https://github.com/STRML/omp-jevens-classifier)** — Jev-powered model-judged permission gate for OMP (TypeSafe System One) <sub>(upstream description)</sub>
  <sub>`Project` · strml · `TS` · ⚠ `archived`</sub>

- **[padflow-jev-evals](https://github.com/zsavage8/padflow-jev-evals)** — Typed-decision benchmark from PadFlow (land development SaaS): schemas, anonymized labeled rows, and a runner for confidence-calibrated models like TypeSafe Jev. <sub>(upstream description)</sub>
  <sub>`Benchmark` · zsavage8 · `Py`</sub>

- **[pagegrade](https://github.com/kitze/pagegrade)** — Grade page sections for clarity, writing and on-page SEO. WXT + TypeSafe AI Jev. <sub>(upstream description)</sub>
  <sub>`Project` · kitze · `TS`</sub>

- **[pi-jev-permit](https://github.com/kurihada/pi-jev-permit)** — A Jev (TypeSafe System One) permission gate for the Pi coding agent: judges every bash / write / edit call before it runs <sub>(upstream description)</sub>
  <sub>`Project` · kurihada · `TS`</sub>

- **[pi-typesafe-jev](https://github.com/legacybridge-tech/pi-typesafe-jev)** — A pi extension that exposes TypeSafe (Jev, System One) judgments as five pi tools, so a model can make narrow semantic judgments while your code and your users keep control of thresholds, weights, and actions. <sub>(upstream description)</sub>
  <sub>`Plugin` · legacybridge-tech · `TS`</sub>

- **[poorjev](https://github.com/rupeshpoojary9/poorjev)** — Open-source, local Jev alternative: a System One decision layer with provably calibrated confidence (ECE 0.170→0.071). Typed decisions, runs offline, no API key, no waitlist. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · rupeshpoojary9 · `Py` · ⚠ `not Jev itself`</sub>

- **[prompt2jev](https://github.com/sumleo/prompt2jev)** — Agent skill and CLI that turn natural language, an LLM prompt, or the code that runs one into a TypeSafe Jev decision: typed state, Choice/Score/Noul questions, and a runnable script <sub>(upstream description)</sub>
  <sub>`Plugin` · sumleo · `Py`</sub>

- **[pytest-jev](https://github.com/allebee/pytest-jev)** — Semantic assertions for pytest: test what your LLM app's output means, judged by TypeSafe's Jev.
  <sub>`Plugin` · allebee · `Py`</sub>

- **[qwen-rlcd](https://github.com/shamazharikh/qwen-rlcd)** — Jev-style calibrated decision model (Choice/Score/Noul) on Qwen3.5-0.8B <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · shamazharikh · `Py` · ⚠ `not Jev itself` `no licence`</sub>

- **[s1-rs](https://github.com/AbdelStark/s1-rs)** — Typed System One layer for Rust (Choice/Score/Noul). <sub>(upstream description)</sub>
  <sub>`Project` · abdelstark · `Rs`</sub>

- **[s1s](https://github.com/cpaczek/s1s)** — System One Search: navigate and trace code with TypeSafe judgments and repository evidence <sub>(upstream description)</sub>
  <sub>`Project` · cpaczek · `TS`</sub>

- **[shady-town](https://github.com/tpaulshippy/shady-town)** — Shady Town: social-deduction party game for the living room TV, moderated by TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Project` · tpaulshippy · `Rb` · ⚠ `no licence`</sub>

- **[sloppy-jevs-extension](https://github.com/neddes/sloppy-jevs-extension)** — Open-source Chrome extension that filters AI-generated prose and ads with Jev <sub>(upstream description)</sub>
  <sub>`Plugin` · neddes · `JS`</sub>

- **[spendbrake](https://github.com/ndolinschi/spendbrake)** — Agent budget brake — continue / downgrade_model / stop via TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Project` · ndolinschi · `TS` · ⚠ `no licence`</sub>

- **[system-one-gemma](https://github.com/akash-kamat/system-one-gemma)** — Open-source Jev-style System One decision model. Gemma 3 270M with a scoring head — fast, calibrated decisions in a single forward pass. No text generation. Inspired by TypeSafe.ai's Jev. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · akash-kamat · `Py` · ⚠ `not Jev itself` `no licence`</sub>

- **[tenbin](https://github.com/simota/tenbin)** — MCP server and agent skill for the TypeSafe AI System One API (Jev): decompose a judgment into Choice / Score / Noul questions, lint them, measure on labelled data, and put calibrated thresholds in code <sub>(upstream description)</sub>
  <sub>`Plugin` · simota · `TS`</sub>

- **[toolgate](https://github.com/RiskAverseTech/toolgate)** — Open auto mode for AI agents — a calibrated tool-call firewall powered by TypeSafe Jev. Ships as a Claude Code hook <sub>(upstream description)</sub>
  <sub>`Plugin` · riskaversetech · `TS`</sub>

- **[transcript-scorecard](https://github.com/brandonbryant12/transcript-scorecard)** — ACME live support-call scoring demo with TypeSafe AI, Effect, SQLite, React, Vite, and Turborepo <sub>(upstream description)</sub>
  <sub>`Project` · brandonbryant12 · `TS` · ⚠ `no licence`</sub>

- **[tripwire](https://github.com/noelzappy/tripwire)** — Judge every LLM response before the user sees it. AI SDK middleware and OpenAI-compatible proxy. <sub>(upstream description)</sub>
  <sub>`Integration` · noelzappy · `TS`</sub>

- **[typed-decisions](https://github.com/kotoba-lang/typed-decisions)** — Jev-shaped typed-decision model (state + Choice/Score/Noul questions -> calibrated probabilities, one pass) on ModernBERT / DeBERTa / LLaDA-MoE, with measured latency, accuracy, calibration and training cost <sub>(upstream description)</sub>
  <sub>`Project` · kotoba-lang · `Py`</sub>

- **[typesafe-as-a-judge](https://github.com/E-FL/typesafe-as-a-judge)** — Unofficial community MCP plugin for Codex and Claude Code using TypeSafe Jev for bounded routing, ranking, extraction, verification, and escalation <sub>(upstream description)</sub>
  <sub>`Plugin` · e-fl · `JS`</sub>

- **[typesafe-cli](https://github.com/y0usaf/typesafe-cli)** — Ask Jev typed questions from the shell: noul, choice, and score answers as numbers, not prose <sub>(upstream description)</sub>
  <sub>`Project` · y0usaf · `TS`</sub>

- **[typesafe-demo-mcp](https://github.com/bestagentkits/typesafe-demo-mcp)** — MCP server exposing TypeSafe System One judgments (noul, choice, score) as agent tools <sub>(upstream description)</sub>
  <sub>`Plugin` · bestagentkits · `TS` · ⚠ `no licence`</sub>

- **[typesafe-jev](https://github.com/gtaras7/typesafe-jev)** — Screen a folder of CVs with the TypeSafe Jev decision model: typed judgments, an editable policy, free re-scoring. <sub>(upstream description)</sub>
  <sub>`Project` · gtaras7 · `TS`</sub>

- **[typesafe-jev-bridge](https://github.com/RevocGG/typesafe-jev-bridge)** — Use the TypeSafe Jev decision model (System One) anywhere: zero-dependency OpenAI-compatible bridge for 9Router, Claude Code, Cursor, Cline & any OpenAI SDK. Typed yes/no, choice & score judgments via CLI or HTTP. <sub>(upstream description)</sub>
  <sub>`SDK` · revocgg · `JS`</sub>

- **[typesafe-local](https://github.com/aabolfazl/typesafe-local)** — Inspired by TypeSafe Ai, Ask a local LLM typed questions, get calibrated probabilities instead of text. Structured output without generation or parsing. MLX / Apple Silicon. <sub>(upstream description)</sub>
  <sub>`Project` · aabolfazl · `Py`</sub>

- **[typesafe-oracles](https://github.com/trophee-bot/typesafe-oracles)** — Evaluating TypeSafe's System One primitives (Choice/Score/Noul) — where a typed oracle beats an LLM call
  <sub>`Project` · trophee-bot · `JS` · ⚠ `no licence`</sub>

- **[typesafe-showcase](https://github.com/Ashadeepa/typesafe-showcase)** — Next.js UI showing off TypeSafe's System One model (Jev) — parallel Noul judgments and a Choice-based citation checker, deployable to Vercel <sub>(upstream description)</sub>
  <sub>`Project` · ashadeepa · `TS` · ⚠ `no licence`</sub>

- **[typesafe-triage-guard](https://github.com/shivam2003-dev/typesafe-triage-guard)** — Three composable judgment pipelines on TypeSafe's Jev: support-ticket triage, observability alert triage, and a deploy-risk gate. <sub>(upstream description)</sub>
  <sub>`Project` · shivam2003-dev · `Py`</sub>

- **[typesafeai-review](https://github.com/rbalch/typesafeai-review)** — Using Typesafe.AI to generate diff reviews. <sub>(upstream description)</sub>
  <sub>`Project` · rbalch · `Py` · ⚠ `no licence`</sub>

- **[vgi-typesafe](https://github.com/Query-farm/vgi-typesafe)** — A VGI worker exposing TypeSafe System One questions (choice, noul, score) to DuckDB/SQL as LATERAL-joinable table functions <sub>(upstream description)</sub>
  <sub>`Project` · query-farm · `Py`</sub>

- **[watfile](https://github.com/jexp/watfile)** — Text/PDF - File categorization and sorting with Typesafe AI Jev or local calibrated decision model <sub>(upstream description)</sub>
  <sub>`Project` · jexp · `Py` · ⚠ `no licence`</sub>

- **[zcode-jev](https://github.com/Zahrannnn/zcode-jev)** — Typed judgment layer for coding agents — gates from PRD to ship. Jev-ready, provider-agnostic. <sub>(upstream description)</sub>
  <sub>`Integration` · zahrannnn · `TS` · ⚠ `no licence`</sub>

- **[jevai.org community showcase cases](https://www.jevai.org/cases)** — Nine worked community scenarios: intent routing, invoice classification, news filtering, product tagging, moderation, claim verification, CSV validation and more.
  <sub>`Project` · ⚠ `unverified claims`</sub>

---

<sub>Generated from `catalog.json` by `scripts/build_readme.py`. Edit the catalogue, not this file.</sub>
