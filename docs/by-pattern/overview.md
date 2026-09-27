# Overview

<sub>[awesome-jev](../../README.md) · [中文](overview.zh-CN.md)</sub>

_Surveys the model or the space rather than one pattern._

Every catalogued example of this decision — 451 of them. The same rows, with caveats, are in [the index](../../README.md#overview); [the site](https://kydlikebtc.github.io/awesome-jev/?p=overview&lang=en) can filter them further by language, primitive and kind.

★ gives a repository's GitHub stars as a band — ★10+, ★100+, ★1k+, ★10k+ and ★100k+; rows with no repository or under 10 stars show no band. Rows run official first, then with code, then by band, then by title. A band is a popularity signal, not a quality verdict; the exact count, as last read from GitHub, is in [`catalog.json`](../../catalog.json) and on [the site](https://kydlikebtc.github.io/awesome-jev/?lang=en).

- **[Official agent skill for Claude Code](https://docs.typesafe.ai/agent-skill)** ⭐ — Installs a TypeSafe skill into Claude Code so an agent can write correct Jev calls without you pasting the API shape each time.
  <sub>`Official docs` · ★1k+ · `sh`</sub>

- **[typesafe-ai/skills](https://github.com/typesafe-ai/skills)** ⭐ — The official agent-skills repository behind the Claude Code plugin, holding the SKILL.md that teaches an agent the System One API.
  <sub>`Plugin` · ★1k+ · `sh`</sub>

- **[@typesafe-ai/sdk (TypeScript / JavaScript)](https://github.com/typesafe-ai/typesafe-sdk-js)** ⭐ — The official TypeScript client. Ships ESM, CJS and type declarations, with lowercase choice()/score()/noul() helper factories.
  <sub>`SDK` · ★100+ · `TS` · `JS` · `choice` · `score` · `noul`</sub>

- **[system-one-adapter-python](https://github.com/typesafe-ai/system-one-adapter-python)** ⭐ — A drop-in TypeSafeClient replacement backed by ordinary LLM APIs, so you can run Jev-shaped code without Jev access.
  <sub>`SDK` · ★100+ · `Py`</sub>

- **[typesafe-sdk (Python)](https://github.com/typesafe-ai/typesafe-sdk-python)** ⭐ — The official Python client. Sync and async clients, retry policy with retry-after support, and Choice/Score/Noul helper classes.
  <sub>`SDK` · ★100+ · `Py` · `choice` · `score` · `noul`</sub>

- **[API reference](https://docs.typesafe.ai/api)** ⭐ — The one endpoint, POST /v1/systemone, with the exact request and answer shapes for all three question types.
  <sub>`Official docs` · `sh` · `Py` · `TS`</sub>

- **[Models, pricing and limits](https://docs.typesafe.ai/models)** ⭐ — The authoritative sheet: jev-1.13.0, $0.042 per Mtok input with output free, 64k context, 32k for state plus the longest question, text input only.
  <sub>`Official docs` · `sh` · `Py` · `TS`</sub>

- **[Primitives: Choice, Score, Noul](https://docs.typesafe.ai/primitives)** ⭐ — What each primitive is for and how to write criteria, including the 255-option cap on Choice and the 2-10 level range on Score.
  <sub>`Official docs` · `Py` · `TS` · `choice` · `score` · `noul`</sub>

- **[Introducing System One models and Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)** ⭐ — The launch post: what a System One model is, why decisions were split from generation, and the vendor's latency and cost claims.
  <sub>`Article` · Diogo Almeida · ⚠ `vendor numbers`</sub>

- **[Jev 1.13 known limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13)** ⭐ — The vendor's own list of where the model fails: literal reading, arithmetic and counting, date comparison, indirection, large noisy states, adversarial content.
  <sub>`Official docs`</sub>

- **[Use case map](https://docs.typesafe.ai/concepts/use-case-map)** ⭐ — The vendor's own taxonomy: five headline categories, nineteen industry groups, and ten decision shapes from classification through to structured data extraction.
  <sub>`Official docs`</sub>

- **[langchain](https://github.com/langchain-ai/langchain)** — The agent engineering platform. <sub>(upstream description)</sub>
  <sub>`Project` · ★100k+ · langchain-ai · `Py`</sub>

- **[OpenCode Zen: Jev resale](https://github.com/anomalyco/opencode)** — A coding agent whose hosted gateway resells Jev, including a free tier model id.
  <sub>`Integration` · ★100k+ · `TS`</sub>

- **[@effect/ai-typesafe](https://github.com/Effect-TS/effect)** — Implements Effect's DecisionModel interface over Jev, with an unusually candid caveat about unverified rounding behaviour.
  <sub>`Integration` · ★10k+ · `TS` · `choice` · `score` · `noul`</sub>

- **[ai](https://github.com/vercel/ai)** — The AI Toolkit for TypeScript. From the creators of Next.js, the AI SDK is a free open-source library for building AI-powered applications and agents <sub>(upstream description)</sub>
  <sub>`SDK` · ★10k+ · vercel · `TS`</sub>

- **[eliza](https://github.com/elizaOS/eliza)** — Open source agentic operating system <sub>(upstream description)</sub>
  <sub>`Project` · ★10k+ · elizaos · `TS`</sub>

- **[laya](https://github.com/NandhaKishorM/laya)** — Non-autoregressive System 1 decision engine. Typed choice, score and yes/no decisions over any text in a single forward pass, in 100+ languages, with a router that picks the right checkpoint per request. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10k+ · nandhakishorm · `Py` · ⚠ `not Jev itself`</sub>

- **[litellm](https://github.com/BerriAI/litellm)** — The fastest, litest AI Gateway. Rust core with Python SDK. Call 100+ LLM APIs in OpenAI (or native) format with cost tracking, guardrails, load balancing, and logging [Bedrock, Azure, OpenAI, Anthropic, OpenAI, VertexAI, vLLM, Nvidia NIM] <sub>(upstream description)</sub>
  <sub>`Integration` · ★10k+ · berriai · `Py`</sub>

- **[oh-my-pi](https://github.com/can1357/oh-my-pi)** — ⌥ Coding agent with the IDE wired in
  <sub>`Project` · ★10k+ · can1357 · `TS`</sub>

- **[openwork](https://github.com/different-ai/openwork)** — The open-source alternative to Claude Cowork (powered by opencode) <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10k+ · different-ai · `TS` · ⚠ `not Jev itself`</sub>

- **[Opik TypeSafe tracker](https://github.com/comet-ml/opik/blob/main/sdks/python/src/opik/integrations/typesafe/opik_tracker.py)** — Wraps the sync and async clients so every system_one call is recorded as a traced span.
  <sub>`Project` · ★10k+ · `Py`</sub>

- **[pydantic-ai](https://github.com/pydantic/pydantic-ai)** — How Python does AI. Agents, realtime voice, image generation, embeddings. Every model, every interface, typed end to end. <sub>(upstream description)</sub>
  <sub>`Project` · ★10k+ · pydantic · `Py`</sub>

- **[ax](https://github.com/ax-llm/ax)** — The pretty much "official" DSPy framework for Typescript <sub>(upstream description)</sub>
  <sub>`Project` · ★1k+ · ax-llm · `TS`</sub>

- **[Bifrost TypeSafe gateway route](https://github.com/maximhq/bifrost/tree/dev/core/providers/typesafe)** — A Go gateway provider that passes the native API through one-to-one, so the official SDKs work by changing only the base URL.
  <sub>`Project` · ★1k+ · `Go`</sub>

- **[deep-searcher](https://github.com/zilliztech/deep-searcher)** — Open Source Deep Research Alternative to Reason and Search on Private Data. Written in Python. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★1k+ · zilliztech · `Py` · ⚠ `not Jev itself`</sub>

- **[jevlike](https://github.com/vinnylarouge/jevlike)** — An independent, trainable model with the same input and output shape as Jev: text plus N options in, one probability per option out, in a single pass.
  <sub>`Jev-like alternative` · ★1k+ · vinnylarouge · `Py` · ⚠ `not Jev itself`</sub>

- **[kev](https://github.com/jaredpalmer/kev)** — A trainable, self-hostable family of Jev-like decision models with a System One compatible API, so the official SDK can point at your own server.
  <sub>`Jev-like alternative` · ★1k+ · Jared Palmer · `Py` · `choice` · `score` · `noul` · ⚠ `not Jev itself`</sub>

- **[Kiln: Jev adapter](https://github.com/Kiln-AI/Kiln)** — A JSON-Schema-to-question compiler wired into the adapter registry, with an honest note on what it cannot serve.
  <sub>`Integration` · ★1k+ · `Py` · `choice` · `score` · `noul`</sub>

- **[laya-mlx](https://github.com/mizorewww/laya-mlx)** — Native MLX runtime for Laya typed decision models — 7–14 ms short decisions on M3 Max. No text generation, PyTorch, or cloud API. <sub>(upstream description)</sub>
  <sub>`Project` · ★1k+ · mizorewww · `Py`</sub>

- **[memsearch](https://github.com/zilliztech/memsearch)** — A persistent, unified memory layer for all your AI agents (e.g. Claude Code, Codex, DSH), backed by Markdown and Milvus. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★1k+ · zilliztech · `Py`</sub>

- **[NanoJev](https://github.com/TianyuCodings/NanoJev)** — A self-described nano replica of Jev, for reading rather than for production.
  <sub>`Jev-like alternative` · ★1k+ · `Py` · ⚠ `not Jev itself`</sub>

- **[rig-typesafeai](https://github.com/0xPlaygrounds/rig)** — A Rust integration with compile-time-checked option counts, so an over-255 Choice fails to build rather than at runtime.
  <sub>`Integration` · ★1k+ · `Rs` · `choice` · `score` · `noul`</sub>

- **[ruby_llm: TypeSafe provider](https://github.com/crmne/ruby_llm)** — A Ruby provider with a dedicated System One protocol, the main route into Jev from Ruby.
  <sub>`Integration` · ★1k+ · `Rb` · `choice` · `score` · `noul`</sub>

- **[SemIf](https://github.com/TheoLeeCJ/SemIf-OpenJev)** — An independent semantic-if implementation that states up front it is unaffiliated with Jev or TypeSafe.
  <sub>`Jev-like alternative` · ★1k+ · `Py` · ⚠ `not Jev itself`</sub>

- **[vellum-assistant](https://github.com/vellum-ai/vellum-assistant)** — An AI Assistant that’s easy to setup, does your work 24/7, knows your preferences and gets better over time. <sub>(upstream description)</sub>
  <sub>`Project` · ★1k+ · vellum-ai · `TS`</sub>

- **[aiavatarkit](https://github.com/uezo/aiavatarkit)** — 🥰 Building AI-based conversational avatars lightning fast ⚡️💬 <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · uezo · `Py`</sub>

- **[awesome-jev (fatwang2)](https://github.com/fatwang2/awesome-jev)** — A sibling directory whose submissions are reviewed by Jev itself, with a notably thorough list of multi-language community clients.
  <sub>`Project` · ★100+ · fatwang2 · `JS`</sub>

- **[celesto](https://github.com/CelestoAI/celesto)** — Secure and persistent computer for AI agents -- build your own Grokbot, and Muse.
  <sub>`Project` · ★100+ · celestoai · `Py`</sub>

- **[crush-monitor](https://github.com/FerryCorleone/crush-monitor)** — Crush 好感监控器：用 Jev 分析微信聊天的情绪、意图和回复表现。本机部署，使用自己的 API Key。 <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · ferrycorleone · `TS`</sub>

- **[dasheng](https://github.com/wquguru/dasheng)** — 大声读 — R2T2 流式 ASR 听，Jev 逐词判，英文朗读评分 <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · wquguru · `JS` · ⚠ `no licence`</sub>

- **[decider](https://github.com/Mapika/decider)** — A family of System One-style models fine-tuned from an open base for one-pass typed decisions.
  <sub>`Jev-like alternative` · ★100+ · mapika · `Py` · ⚠ `not Jev itself`</sub>

- **[distill](https://github.com/samuelfaj/distill)** — Get FAR MORE done with FAR FEWER tokens 🔥 <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · samuelfaj · `Rs`</sub>

- **[djev-spark](https://github.com/mmastrac/djev-spark)** — DiffusionGemma NVFP4 structured decisions on a DGX Spark: container recipe <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · mmastrac · `TS` · ⚠ `no licence`</sub>

- **[jeff](https://github.com/logan-markewich/jeff)** — A self-hosted drop-in replacement for TypeSafe's jev, powered by GliFormer. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★100+ · logan-markewich · `Py` · ⚠ `not Jev itself`</sub>

- **[jev-chat-jarvis-mac](https://github.com/jev-chat/jev-chat-jarvis-mac)** — 微信消息意图识别悬浮窗（macOS）：看屏 + 本地小模型判断意图和风险，再按话术生成回复候选。纯只读、不注入微信。
  <sub>`Project` · ★100+ · jev-chat · `Py`</sub>

- **[jev-chat-windows](https://github.com/jev-chat/jev-chat-windows)** — 微信（Windows 4.x）旁挂的回复辅助：窗口截图 + 本地离线 OCR 读对方消息 → Jev 判断意图 → 3 条候选一键填入，发送永远手动
  <sub>`Project` · ★100+ · jev-chat · `Py`</sub>

- **[jev-experiments](https://github.com/dabit3/jev-experiments)** — Nader Dabit's collection of small Jev experiments, one per folder: a commit reviewer, a shell guard, a send guard, a log sentinel, instant search, reranking, a voice-turn detector and more.
  <sub>`Project` · ★100+ · dabit3 · `TS` · ⚠ `no licence`</sub>

- **[jev-skill](https://github.com/wuyoscar/jev-skill)** — An agent skill plus CLI that validates all three primitives, requires explicit consent before a billed call, and forbids inventing output when simulating.
  <sub>`Plugin` · ★100+ · `Py` · `choice` · `score` · `noul`</sub>

- **[jevbench](https://github.com/fstandhartinger/jevbench)** — JevBench v1 - a benchmark for Jev-class typed decision models: smart, cheap, fast, reliable, open. <sub>(upstream description)</sub>
  <sub>`Benchmark` · ★100+ · fstandhartinger · `Py`</sub>

- **[Jevmind](https://github.com/dealerdefi/Jevmind)** — An agent's decisions pulled out of its prose into one place: typed answers with a confidence, behind a gate written in code, sealed in a ledger, graded and learned from. Runs offline on a local rules brain; Jev can be swapped in with one flag.
  <sub>`Project` · ★100+ · dealerdefi · `Py`</sub>

- **[kody](https://github.com/kentcdodds/kody)** — 🐨 Your assistant's home — the memory, keys, code, and automations your AI agent keeps, portable across every MCP host. Built on Cloudflare Workers. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★100+ · kentcdodds · `TS`</sub>

- **[laya](https://github.com/receptron/laya)** — Run Laya, the open-source Jev-compatible System-1 decision model, from Node.js / TypeScript via ONNX Runtime <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · receptron · `TS`</sub>

- **[laya-ultrafast](https://github.com/ipenywis/laya-ultrafast)** — Same as jev-ultrafast but using Laya <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · ipenywis · `Py`</sub>

- **[localjev](https://github.com/githubnext/localjev)** — GitHub Next's local, Jev-compatible POST /v1/systemone API in TypeScript, reading probabilities from a DiffusionGemma model through a one-step structured read on a patched vLLM. It reimplements the wire, not the model.
  <sub>`Jev-like alternative` · ★100+ · githubnext · `TS` · ⚠ `not Jev itself`</sub>

- **[open-jev](https://github.com/daseinlabs/open-jev)** — Open Jev implementation with custom finetuning <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★100+ · daseinlabs · `Py` · ⚠ `not Jev itself`</sub>

- **[Open-Jev](https://github.com/Zefan-Cai/Open-Jev)** — Open-Jev-27B, an open-weight model that returns typed probabilities for a context, questions and candidates without generating an answer — a Jev-style decision model you can run yourself.
  <sub>`Jev-like alternative` · ★100+ · zefan-cai · `Py` · ⚠ `not Jev itself`</sub>

- **[openjev](https://github.com/razorback16/openjev)** — A Jev-compatible decision server on an open diffusion model.
  <sub>`Jev-like alternative` · ★100+ · razorback16 · `Py` · ⚠ `not Jev itself`</sub>

- **[OpenJev](https://github.com/SiliconLabAI/OpenJev)** — OpenSource Jev <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★100+ · siliconlabai · `TS` · ⚠ `not Jev itself`</sub>

- **[openjev-sglang](https://github.com/ekzhang/openjev-sglang)** — A Jev-compatible endpoint served from open models, prefill only.
  <sub>`Jev-like alternative` · ★100+ · ekzhang · `Py` · ⚠ `not Jev itself` `no licence`</sub>

- **[openwhisper](https://github.com/Knuckles92/OpenWhisper)** — Local speech-to-text, dictation, and meetings with Whisper and OpenAI API. Optional Windows x64 engines: Parakeet, Qwen3-ASR, Nemotron Streaming, and Moonshine.
  <sub>`Project` · ★100+ · knuckles92 · `Py`</sub>

- **[orchestkit](https://github.com/yonatangross/orchestkit)** — The Complete AI Development Toolkit for Claude Code. 106 skills, 36 agents, 171 hooks. Install `ork` for stable (v9.x), or `ork-alpha` for the v10 line, which ships daily. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★100+ · yonatangross · `TS`</sub>

- **[pi-fabric](https://github.com/monotykamary/pi-fabric)** — A programmable tool and agent runtime for Pi <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · monotykamary · `TS`</sub>

- **[req_llm](https://github.com/agentjido/req_llm)** — Composable Elixir library for LLM interactions built on Req and Finch <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · agentjido · `Ex`</sub>

- **[rizzo-flow](https://github.com/Rizzo-AI-Academy/rizzo-flow)** — The open, local take on Jev: typed decisions from an LLM, without generating a single token <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★100+ · rizzo-ai-academy · `Py` · ⚠ `not Jev itself`</sub>

- **[runline](https://github.com/Michaelliv/runline)** — ⚡ Code mode for agents <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · michaelliv · `TS` · ⚠ `no licence`</sub>

- **[simple-jev](https://github.com/featherless-ai/simple-jev)** — Turns any open-weights model into a Jev-shaped endpoint by reading next-token logits, with the server constructing the JSON rather than the model generating it.
  <sub>`Jev-like alternative` · ★100+ · `Py` · ⚠ `not Jev itself`</sub>

- **[smithers](https://github.com/smithersai/smithers)** — Smithers is an agentic workflow framework for defining workflows in simple TypeScript configuration files and executing them quickly, durably, and reliably <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · smithersai · `TS`</sub>

- **[stanley-code](https://github.com/devagrawal09/stanley-code)** — Bounded TypeSafe Jev workflows for coding agents. <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · devagrawal09 · `TS`</sub>

- **[third-hand](https://github.com/shhivv/third-hand)** — computer-use assistant w/ decision models <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · shhivv · `Swift`</sub>

- **[typesafe-mcp](https://github.com/itsmostafa/typesafe-mcp)** — The easiest first step once you have a key: registers Jev into Claude Code, Claude Desktop, Codex and Pi with one command.
  <sub>`Plugin` · ★100+ · `Go` · `choice` · `score` · `noul`</sub>

- **[von](https://github.com/wfzyx/von)** — The open-source System One decision model. Sub-15ms, non-autoregressive, local drop-in alternative to TypeSafe Jev. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★100+ · wfzyx · `Py` · ⚠ `not Jev itself`</sub>

- **[webctl](https://github.com/dorkitude/webctl)** — Smart web search CLI for agents, backed by Jev. Saves a lot of tokens. <sub>(upstream description)</sub>
  <sub>`Project` · ★100+ · dorkitude · `Go`</sub>

- **[advocaat](https://github.com/pithings/advocaat)** — A small typed client for asking questions about your own data.
  <sub>`SDK` · ★10+ · pithings · `TS`</sub>

- **[agent-router](https://github.com/nidhi-singh02/agent-router)** — CLI that picks Cursor, Claude Code, Codex, or OpenCode + model/effort for a task, then launches it. Powered by Jev and Herdr <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · nidhi-singh02 · `TS`</sub>

- **[ask-jev-skill](https://github.com/shantanugoel/ask-jev-skill)** — Skill for Hermes, and other agents, to ask typesafe's jev <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · shantanugoel · `Py`</sub>

- **[call-coach-ai](https://github.com/ZeroGold/call-coach-ai)** — Jev powered call coach <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · zerogold · `TS`</sub>

- **[captaincore](https://github.com/CaptainCore/captaincore)** — 👨🏽‍💻 CaptainCore is a command line application for automating WordPress maintenance. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · captaincore · `Go`</sub>

- **[clash-jev](https://github.com/bytelabs-oss/clash-jev)** — A Clash Royale bot with no trained policy: Jev (TypeSafe System One) makes every decision from the live game state <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · bytelabs-oss · `Py`</sub>

- **[cultivar](https://github.com/pinecone-io/cultivar)** — Use cultivar to test your Agent Skills and Docs by running them in sandboxes, and across different agents. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · pinecone-io · `Py`</sub>

- **[djev](https://github.com/mmastrac/djev)** — Jev-style structured decisions on DiffusionGemma: the example server from vLLM PR 57250 <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · mmastrac · `Py` · ⚠ `not Jev itself`</sub>

- **[dspy-typesafeify](https://github.com/typesafeainate/dspy-typesafeify)** — Add a decorator for dspy Signatures that automatically uses TypeSafe where relevant <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · typesafeainate · `Py`</sub>

- **[duckdb-jev](https://github.com/colliber/duckdb-jev)** — DuckDB extension: typed Jev answers as real SQL types <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · colliber · `C++`</sub>

- **[fastjev](https://github.com/chengyongru/fastjev)** — SDK-first, independently maintained SemIf fork for fast, self-hosted semantic decisions. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · chengyongru · `Py` · ⚠ `not Jev itself`</sub>

- **[go-jev](https://github.com/mattn/go-jev)** — Go SDK and CLI for TypeSafe Jev: typed decisions (yes/no, choice, score) from a model <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · mattn · `Go`</sub>

- **[hunch](https://github.com/carldaws/hunch)** — Probabilistic control flow for Ruby and Rails - powered by TypeSafe's Jev <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · carldaws · `Rb`</sub>

- **[is-jeven](https://github.com/wobsoriano/is-jeven)** — Is it even? Ask Jev. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · wobsoriano · `JS`</sub>

- **[james_library](https://github.com/topherchris420/james_library)** — R.A.I.N. Lab is an experimental scientific-agent architecture that separates fast local judgment, independent probabilistic evaluation, multi-agent deliberation, evidence, and authorization into distinct computational layers.🐙(Predates Karpathy's AutoResearch) <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · topherchris420 · `Rs`</sub>

- **[jev](https://github.com/BorisLeMeec/jev)** — A claude code plugin for jev <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · borislemeec · `Go`</sub>

- **[Jev](https://github.com/mayank953/Jev)** — Six live, side-by-side demos of Jev deciding while an LLM writes the words and code owns the control flow; the LLM side switches between Claude and Kimi models.
  <sub>`Project` · ★10+ · mayank953 · `JS`</sub>

- **[jev](https://github.com/okooo5km/jev)** — Typed decisions from the shell: an unofficial stdlib-Python CLI and Agent Skill for TypeSafe's Jev model, via the TypeSafe API (default) or OpenRouter. Yes/no, choice and ordinal scores with calibrated probabilities, semantic grep and batch mode. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · okooo5km · `Py`</sub>

- **[jev (Elixir/OTP)](https://github.com/dannote/jev)** — Jev as an OTP process: reply from a GenServer and pattern match on the answer.
  <sub>`SDK` · ★10+ · dannote · `Ex`</sub>

- **[jev-chat-for-twitch](https://github.com/ethanplusai/jev-chat-for-twitch)** — Filter any live Twitch chat with Jev: a bring-your-own-key Chrome extension <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · ethanplusai · `JS`</sub>

- **[jev-cli](https://github.com/tumf/jev-cli)** — Small dependency-free CLI for TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · tumf · `Py`</sub>

- **[jev-cli](https://github.com/shaharia-lab/jev-cli)** — Command-line tool for TypeSafe AI's Jev model. Ask yes/no, multiple-choice and rubric questions about any text and get calibrated probabilities back. Answers become exit codes for shells and CI, JSON for scripts, and MCP tools for AI agents. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · shaharia-lab · `Rs`</sub>

- **[jev-explained](https://github.com/davila7/jev-explained)** — Jev Explained <sub>(upstream description)</sub>
  <sub>`Tutorial` · ★10+ · davila7 · `TS`</sub>

- **[jev-foundation-models](https://github.com/peterfriese/jev-foundation-models)** — A lightweight, native Swift 6 bridge integrating TypeSafe AI's Jev System One decision model into Apple's Foundation Models framework. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · peterfriese · `Swift`</sub>

- **[jev-judge-mcp](https://github.com/PyModel/jev-judge-mcp)** — Typed judgment tools for MCP agents. TypeSafe's Jev model as verify, screen, find, classify, rerank, decide, compare, extract, review, gate, and score: the model judges, policy decides auto, review, or escalate. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · pymodel · `Py`</sub>

- **[jev-leftpad](https://github.com/f/jev-leftpad)** — Left-pad strings with TypeSafe AI's Jev. For reasons. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · f · `JS`</sub>

- **[jev-mcp](https://github.com/burnigtm/jev-mcp)** — MCP server that puts TypeSafe Jev on the coding loop in Cursor, Codex, and any MCP client <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · burnigtm · `TS`</sub>

- **[jev-paint](https://github.com/achimala/jev-paint)** — Use Jev to make art! <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · achimala · `JS`</sub>

- **[jev-playground](https://github.com/mizchi/jev-playground)** — A playground for calling Jev from MoonBit, with a CLI per question type (score, choice, noul) and measured reports on which composition patterns win.
  <sub>`Project` · ★10+ · mizchi · `TS` · ⚠ `no licence`</sub>

- **[Jev-Quantum](https://github.com/karminski/Jev-Quantum)** — A Jev-protocol random baseline: it speaks noul, choice and score but reads no prompt, answering from a fast pseudo-random generator — a mock, and a lower bound for routing evaluations.
  <sub>`Jev-like alternative` · ★10+ · karminski · `Rs` · ⚠ `not Jev itself`</sub>

- **[jev-recipes](https://github.com/agencyenterprise/jev-recipes)** — 80+ composable TypeScript recipes powered by Jev for AI agents, retrieval, answer verification, and conversation workflows.
  <sub>`Project` · ★10+ · agencyenterprise · `TS`</sub>

- **[jev-register-tool](https://github.com/2951461586/Jev-Register-Tool)** — TypeSafe（Jev / System One）申请 → 确认邮件 → 获批 → 注册 → 建 API Key 全链路工具，纯 HTTP 无浏览器 <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · 2951461586 · `Py` · ⚠ `no licence`</sub>

- **[jev-rules](https://github.com/EliaAlberti/jev-rules)** — Jev picks which of your rules apply to each prompt, so Claude only sees the ones that matter. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · eliaalberti · `JS`</sub>

- **[jev-seo](https://github.com/AkashPriyadarshii/jev-seo)** — 100% free ₹0 agent-first SEO & GEO CLI suite and MCP server in Rust replacing Semrush and OpenSEO via DuckDuckGo and TypeSafe Jev System One https://akashpriyadarshii.github.io/jev-seo/
  <sub>`Plugin` · ★10+ · akashpriyadarshii · `Rs`</sub>

- **[jev-skill-suggester](https://github.com/win4r/jev-skill-suggester)** — 用 TypeSafe Jev 推荐已安装 Skill / Bounded installed-skill recommendations with TypeSafe Jev. Python CLI, Codex skill, bilingual docs and live examples. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · win4r · `Py`</sub>

- **[jev-spring-boot-starter](https://github.com/danvega/jev-spring-boot-starter)** — A simple Spring Boot 4 starter for TypeSafe Jev using Spring MVC and RestClient <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · danvega · `Java` · ⚠ `no licence`</sub>

- **[jev-studio](https://github.com/utk2103/jev-studio)** — if you're experimenting with jev it will be easier from here <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · utk2103 · `Py`</sub>

- **[jev-tetris](https://github.com/trungdq88/jev-tetris)** — Jev play Tetris in real-time against other AI models <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · trungdq88 · `JS` · ⚠ `no licence`</sub>

- **[jev-to-answer](https://github.com/csskrtao/jev-to-answer)** — A Book of Answers toy: ask a question and Jev picks the answer.
  <sub>`Project` · ★10+ · csskrtao · `JS` · ⚠ `no licence`</sub>

- **[jev-trades](https://github.com/zadescoxp/Jev-Trades)** — Trading bot with the all new TypeSafe AI's first system one model named as Jev <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · zadescoxp · `Py`</sub>

- **[jev-tree](https://github.com/Chuf-H/jev-tree)** — Jev-native probability tree and graph runtime for verifiable multi-step decision making. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · chuf-h · `Py`</sub>

- **[jev-voice](https://github.com/kevinbadi/jev-voice)** — Talk to your Mac. Local whisper.cpp + one Jev (TypeSafe) call per command + macOS automation. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · kevinbadi · `Py`</sub>

- **[jev-vs-ml](https://github.com/QuicqDev/Jev-vs-ML)** — Jev-vs-ML <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · quicqdev · `Py` · ⚠ `no licence`</sub>

- **[jev_local](https://github.com/Argos1111/jev_local)** — Replicating Jev with a local LLM <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · argos1111 · `Py` · ⚠ `not Jev itself` `no licence`</sub>

- **[jev_stock](https://github.com/sosopop/jev_stock)** — An experimental JEV-powered framework for forecasting short-term stock price direction from structured market data. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · sosopop · `Py` · ⚠ `no licence`</sub>

- **[JevAny](https://github.com/weitianxin/JevAny)** — JevAny: a calibrated decision layer for RL, agents and model harnesses that returns typed answers and option probabilities in one prefill pass — an open 27B model on a Qwen backbone, not Jev.
  <sub>`Jev-like alternative` · ★10+ · weitianxin · `Py` · ⚠ `not Jev itself`</sub>

- **[jevchat](https://github.com/kyle-pena-nlp/jevchat)** — Turns Jev into a chatbot <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · kyle-pena-nlp · `Py` · ⚠ `no licence`</sub>

- **[jevcore](https://github.com/PerryLink/jevcore)** — TypeSafe Jev for DeepSeek Harness, the Model Context Protocol, and plain Node: typed judgments instead of prose, offline by default. <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · perrylink · `TS`</sub>

- **[jevernetes](https://github.com/sunil-sadasivan/jevernetes)** — Live Kubernetes log analysis, contextual investigation, and agent handoff powered by Jev. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · sunil-sadasivan · `Py`</sub>

- **[jevgraph](https://github.com/chenmingtang830/jevgraph)** — Evidence-backed knowledge graph construction with typed Jev relation decisions <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · chenmingtang830 · `Py`</sub>

- **[jeview](https://github.com/andududu/jeview)** — An unofficial local visualizer for Jev (TypeSafe): a live view of every call your code makes. Not affiliated with TypeSafe AI. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · andududu · `JS`</sub>

- **[jevify](https://github.com/altryne/jevify)** — An agent skill to discover TypeSafe Jev opportunities, design typed questions, and learn from recent community experiments. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · altryne · `Py`</sub>

- **[jevify](https://github.com/fidecastro/jevify)** — Supersimple way to serve LLMs as a Jev-like endpoint <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · fidecastro · `Py` · ⚠ `not Jev itself`</sub>

- **[jevk5](https://github.com/allebee/jevk5)** — JevK5: open-weight alternative to TypeSafe Jev. Typed decisions with probabilities in one forward pass; Apache-2.0 weights and code. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · allebee · `Py` · ⚠ `not Jev itself`</sub>

- **[jevloop](https://github.com/zjunlp/JevLoop)** — The agent loop where decisions don't cost a large language model call. Zero deps, runs offline, no API key needed. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · zjunlp · `TS`</sub>

- **[jevocks](https://github.com/unicodeveloper/jevocks)** — Everyday Stocks Status with Jev <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · unicodeveloper · `TS` · ⚠ `no licence`</sub>

- **[jevper](https://github.com/zhulinchng/jevper)** — Jev-shaped (TypeSafe System One) classification wrapper over OpenAI-like clients: probabilities and confidence instead of prose
  <sub>`Jev-like alternative` · ★10+ · zhulinchng · `Py` · ⚠ `not Jev itself`</sub>

- **[jevthoven](https://github.com/cocktailpeanut/jevthoven)** — AI Music (MIDI) generator powered by Jev <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · cocktailpeanut · `TS`</sub>

- **[jevvy](https://github.com/PanAchy/jevvy)** — Jev-powered plugins for coding agents <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · panachy · `TS`</sub>

- **[jot](https://github.com/runta-dev/jot)** — The first general-purpose System One agent for Jev <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · runta-dev · `TS` · ⚠ `no licence`</sub>

- **[laya-server](https://github.com/1Panel-dev/laya-server)** — A self-hosted API and web interface for Laya’s structured decision models, compatible with the TypeSafe Jev API format. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · 1panel-dev · `TS` · ⚠ `not Jev itself`</sub>

- **[laya-vs-jev](https://github.com/virajbhartiya/laya-vs-jev)** — Laya vs Jev: local MLX and hosted AI decisions playing T-Rex side by side, with live metrics and replay recording <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · virajbhartiya · `Py`</sub>

- **[laya-vs-jev-arena](https://github.com/PromptEngineer48/laya-vs-jev-arena)** — Laya (open source, local) vs TypeSafe Jev (API): two AI models race in Snake and fight in a Mortal-Kombat-style arena. Every move is a real model decision. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · promptengineer48 · `JS`</sub>

- **[litjev](https://github.com/zhengxuyu/litjev)** — Turn any off-the-shelf LLM into a Jev -like decision layer <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · zhengxuyu · `Py` · ⚠ `not Jev itself`</sub>

- **[llm-typesafe](https://github.com/simonw/llm-typesafe)** — LLM plugin for accessing Jev and other TypeSafe AI models <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · simonw · `Py`</sub>

- **[loki](https://github.com/wundercorp/loki)** — The agent that evolves with you 𖤍 <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · wundercorp · `Py`</sub>

- **[notjev](https://github.com/9pings/notjev)** — Super fast Jev like server, model agnostic, working with any OpenAI compatible endpoint <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · 9pings · `JS` · ⚠ `not Jev itself`</sub>

- **[open-spark-jev](https://github.com/abhishek085/open-spark-jev)** — Open-source, local decision models inspired by TypeSafe’s Jev and System One - built on Qwen3 for NVIDIA DGX Spark. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · abhishek085 · `Py`</sub>

- **[OpenDecision](https://github.com/deepanwadhwa/OpenDecision)** — An open-source semantic decision engine running a local zero-shot model, with a FastAPI server proven wire-compatible with the official SDK.
  <sub>`Jev-like alternative` · ★10+ · deepanwadhwa · `Py` · `choice` · `score` · `noul` · ⚠ `not Jev itself`</sub>

- **[OpenJev](https://github.com/zhangcy122/OpenJev)** — OpenJev: Open-source alternative to TypeSafe Jev. Typed probabilistic decision API (Choice, Noul, Score) powered by open LLMs & constrained logprob calibration.
  <sub>`Jev-like alternative` · ★10+ · zhangcy122 · `Py` · ⚠ `not Jev itself`</sub>

- **[OpenSourceJev](https://github.com/sabeel111/OpenSourceJev)** — Turning an LLM model into a Jev like System. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · sabeel111 · `Py` · ⚠ `not Jev itself`</sub>

- **[openthai-systemone](https://github.com/iapp-technology/openthai-systemone)** — OpenThai-SystemOne: open Thai + English System One decision model (0.8B, 256-way slot head, Apache-2.0) <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · iapp-technology · `Py`</sub>

- **[pi-quiet-ask](https://github.com/HyunjunJeon/pi-quiet-ask)** — TypeSafe Jev as the pi coding agent's quiet decision layer <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · hyunjunjeon · `TS`</sub>

- **[pijev](https://github.com/TypeLLM/pijev)** — Averages Jev's answers over option orderings — all permutations in one request — with Brier score and log loss guaranteed no worse than the average across the orderings included. A one-line import change.
  <sub>`SDK` · ★10+ · typellm · `Py`</sub>

- **[refgarden](https://github.com/AlbionaHoti/refgarden)** — A spatial reference explorer for creators. Local Jev query choices, metadata highlights and source-linked collections. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · albionahoti · `TS` · ⚠ `not Jev itself`</sub>

- **[ruby_decision_model](https://github.com/obie/ruby_decision_model)** — Ruby client for decision models such as Typesafe Jev <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · obie · `Rb`</sub>

- **[ruby_llm-typesafe](https://github.com/kieranklaassen/ruby_llm-typesafe)** — A structured-output provider for a Ruby LLM library.
  <sub>`Integration` · ★10+ · kieranklaassen · `Rb`</sub>

- **[snap](https://github.com/emnlmn/snap)** — Typed decisions from unstructured state: one forward pass, zero generated text. Local, deterministic, Jev-compatible. Not affiliated with typesafe.ai. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · emnlmn · `Rs` · ⚠ `not Jev itself` `no licence`</sub>

- **[snapjudge](https://github.com/Micha0827/snapjudge)** — Typed decisions (choice / score / yes-no) from local Qwen models on Apple Silicon. Probabilities come straight from the logits, no text generation. TypeSafe-compatible HTTP API, runs on MLX. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ★10+ · micha0827 · `Py` · ⚠ `not Jev itself`</sub>

- **[solar-mini4-jev](https://github.com/hunkim/solar-mini4-jev)** — A drop-in wrapper that exposes Upstage's Solar models through the Jev System One API shape — noul, choice and score with the same schema — with a hosted bring-your-own-key endpoint.
  <sub>`Jev-like alternative` · ★10+ · hunkim · `Py` · ⚠ `not Jev itself` `no licence`</sub>

- **[st-jeved](https://github.com/mossyfield/ST-jeved)** — SillyTavern extension that measures each reply and instructs the narrator only when a rule matches. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · mossyfield · `JS`</sub>

- **[swift-jev](https://github.com/d-date/swift-jev)** — A Swift client for TypeSafe AI's Jev — typed judgements, not text <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · d-date · `Swift`</sub>

- **[swift-typesafe](https://github.com/ainame/swift-typesafe)** — Unofficial Swift SDK for TypeSafe <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · ainame · `Swift`</sub>

- **[sys1](https://github.com/alvarobartt/sys1)** — System One compatible API for open decision models, e.g. Laya, written in Rust.
  <sub>`Jev-like alternative` · ★10+ · alvarobartt · `Rs` · ⚠ `not Jev itself`</sub>

- **[system-one](https://github.com/iamaamir/system-one)** — Provider-neutral System One runtime for TypeScript and Pi <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · iamaamir · `TS` · ⚠ `no licence`</sub>

- **[typesafe](https://github.com/krzyzanowskim/TypeSafe)** — TypeSafe SDK in Swift <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · krzyzanowskim · `Swift`</sub>

- **[typesafe-ai](https://github.com/Twister915/typesafe-ai)** — Typed TypeSafe AI clients for Rust, with async and blocking backends and observable retries. <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · twister915 · `Rs`</sub>

- **[typesafe-ai-benchmark](https://github.com/iammrduncan/typesafe-ai-benchmark)** — A gateway that mimics the structured-output shape, used to benchmark against it.
  <sub>`Benchmark` · ★10+ · iammrduncan · `TS`</sub>

- **[typesafe-playground](https://github.com/kavehmz/typesafe-playground)** — Interactive experiments with TypeSafe Jev, from support routing to 3D driving simulations with real AI decisions and visible sensor inputs. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · kavehmz · `JS` · ⚠ `no licence`</sub>

- **[typesafe-playground](https://github.com/TypeSafeAI/typesafe-playground)** — Community TypeSafe AI playground: 110 use cases, games, dilemmas and model challenges, with editable prompts, A/B comparisons and a mobile-friendly UI. <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · typesafeai · `TS`</sub>

- **[typesafe-sdk-go](https://github.com/atharvamhaske/typesafe-sdk-go)** — unofficial go sdk for typesafe ai. not affiliated with or endorsed by typesafe ai. a side project built to fill the missing go sdk gap, for the community to use. <sub>(upstream description)</sub>
  <sub>`SDK` · ★10+ · atharvamhaske · `Go`</sub>

- **[typesafe-skill-router](https://github.com/DECRUX9812/typesafe-skill-router)** — TypeSafe (Jev) skill routing for Hermes Agent: names the one skill worth loading, before the model call. Opt-in, stdlib only, ~$0.001 per routed turn. <sub>(upstream description)</sub>
  <sub>`Plugin` · ★10+ · decrux9812 · `Py`</sub>

- **[xtags](https://github.com/manifoldor/xtags)** — 在 X 的时间线上，给每条帖子标出它想让你干什么。判断来自 Jev，一个只返回概率、不生成文本的模型。 <sub>(upstream description)</sub>
  <sub>`Project` · ★10+ · manifoldor · `JS`</sub>

- **[@ai-sdk/typesafe-ai provider](https://ai-sdk.dev/providers/ai-sdk-providers/typesafe-ai)** — The AI SDK provider package for calling TypeSafe directly, with a sample covering all three question types and nested criteria shapes.
  <sub>`SDK` · `TS` · `JS` · `choice` · `score` · `noul`</sub>

- **[aegis: TypeSafe as a first-class provider](https://github.com/dvjn/aegis)** — A personal Rust AI gateway with a TypeSafe provider, usage extraction and alias resolution tested against real response bodies.
  <sub>`Project` · dvjn · `Rs` · ⚠ `code untested` `no licence`</sub>

- **[agent-jev-tetris](https://github.com/Yasserbhb/Agent-JEV-Tetris)** — using the new model JEV to play the game tetris <sub>(upstream description)</sub>
  <sub>`Project` · yasserbhb · `TS` · ⚠ `no licence`</sub>

- **[ai-elo-ranker](https://github.com/opaielsheikh/ai-elo-ranker)** — High-speed recursive AI Elo tournament engine powered by Jev and Swiss matchmaking <sub>(upstream description)</sub>
  <sub>`Project` · opaielsheikh · `Py` · ⚠ `no licence`</sub>

- **[ailerix](https://github.com/tylerjharden/ailerix)** — Type-safe model router. Jev (System One) banks each request to a typed catalog route. <sub>(upstream description)</sub>
  <sub>`Project` · tylerjharden · `TS` · ⚠ `no licence`</sub>

- **[alphaoptimizer](https://github.com/alpha-tales/alphaoptimizer)** — Jev-powered output optimization for Codex, built to keep large tool results concise and usable. <sub>(upstream description)</sub>
  <sub>`Plugin` · alpha-tales · `TS`</sub>

- **[antigravity-mcp-semantic-search-with-typesafeai](https://github.com/greenyamao/Antigravity-mcp-semantic-search-with-TypeSafeAi)** — Fast semantic code search & diff sanity auditor for AI coding assistants (Antigravity, Cursor, Claude Code) powered by TypeSafe System One. <sub>(upstream description)</sub>
  <sub>`Benchmark` · greenyamao · `Py` · ⚠ `no licence`</sub>

- **[askjev](https://github.com/pZacca/askjev)** — Unofficial MCP server for Jev (Typesafe AI) <sub>(upstream description)</sub>
  <sub>`Plugin` · pzacca · `TS`</sub>

- **[AskJev-MCP](https://github.com/cbruyndoncx/AskJev-MCP)** — MCP server for TypeSafe's System One API (Jev): typed choice/noul/score judgments with calibrated probabilities and confidence <sub>(upstream description)</sub>
  <sub>`Plugin` · cbruyndoncx · `JS` · ⚠ `no licence`</sub>

- **[audio-jevlike](https://github.com/alperiox/audio-jevlike)** — Prosodia: an audio-native Jev-shaped decision model — typed calibrated decisions from speech, no ASR <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · alperiox · `Py` · ⚠ `not Jev itself` `no licence`</sub>

- **[auto-mode-for-paseo](https://github.com/obetomuniz/auto-mode-for-paseo)** — A Paseo provider that uses TypeSafe Jev to route each Codex turn.
  <sub>`Plugin` · obetomuniz · `TS`</sub>

- **[awesome-jev](https://github.com/daftAI2026/awesome-jev)** — TypeSafe System One / Jev community directory — GitHub projects & posts around typed decisions (typesafe.ai)
  <sub>`Project` · daftai2026 · `TS` · ⚠ `no licence`</sub>

- **[awesome-jev-use-cases](https://github.com/SeeAPI/awesome-jev-use-cases)** — Explore real-world use cases and projects built with TypeSafe AI's Jev: content moderation, AI agents, model routing, and semantic search. Curated by SeeAPI. <sub>(upstream description)</sub>
  <sub>`Project` · seeapi · `Py`</sub>

- **[barrunto](https://github.com/elpumberto/barrunto)** — A Chrome extension that brings TypeSafe's Jev to X.com to analyze posts as you browse <sub>(upstream description)</sub>
  <sub>`Plugin` · elpumberto · `TS`</sub>

- **[beatjev](https://github.com/lambertsj/beatjev)** — try to beat jev <sub>(upstream description)</sub>
  <sub>`Project` · lambertsj · `JS` · ⚠ `no licence`</sub>

- **[bes-kelime-jev](https://github.com/mahmut-gundogdu/bes-kelime-jev)** — Ne yazarsanız yazın, beş kelimeden biriyle cevap veren sohbet botu. Kelimeyi TypeSafe AI'ın Jev evaluation modeli seçer. <sub>(upstream description)</sub>
  <sub>`Project` · mahmut-gundogdu · `TS`</sub>

- **[btc-jev-signal](https://github.com/WebGrga/btc-jev-signal)** — Experimental multi-horizon BTC signal generator using TypeSafe Jev probabilities and Binance market data. <sub>(upstream description)</sub>
  <sub>`Project` · webgrga · `TS` · ⚠ `no licence`</sub>

- **[Build Your Own JEV Locally: Run a 100% Private AI Agent on Your Machine](https://medium.com/coding-nexus/build-your-own-jev-locally-run-a-100-private-ai-agent-on-your-machine-bb98126d394a)** — Despite the title, this does not run Jev. It builds a Jev-like decision engine from an open LLM using constrained next-token scoring.
  <sub>`Jev-like alternative` · DataScience Nexus · `Py` · ⚠ `not Jev itself` `code untested` `paywall`</sub>

- **[cairn-jev-lab](https://github.com/Cairn-ink/cairn-jev-lab)** — Test what your AI should remember. An experimental, source-aware memory admission evaluator powered by Jev, with editable cases and inspectable results. <sub>(upstream description)</sub>
  <sub>`Project` · cairn-ink · `JS`</sub>

- **[can-jev-bayes](https://github.com/TomRichner/can-jev-bayes)** — Jev Bayes, No? Testing TypeSafe AI's Jev against Bayesian-optimal strategies, and testing if Jev can effectivly use Bayesian priors. <sub>(upstream description)</sub>
  <sub>`Benchmark` · tomrichner · `Py`</sub>

- **[cartshield](https://github.com/ndolinschi/cartshield)** — CartShield — SMB checkout fraud disposition via TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Project` · ndolinschi · `TS` · ⚠ `no licence`</sub>

- **[chat2jev](https://github.com/Chandler-Sun/chat2jev)** — Convert legacy chat completion API request to Typesafe jev API <sub>(upstream description)</sub>
  <sub>`SDK` · chandler-sun · `TS`</sub>

- **[codex-jev-preflight](https://github.com/wellkilo/codex-jev-preflight)** — Fail-open Codex UserPromptSubmit hook that injects TypeSafe Jev pre-task routing metadata. <sub>(upstream description)</sub>
  <sub>`Plugin` · wellkilo · `Py`</sub>

- **[commentcop](https://github.com/ntedvs/commentcop)** — Put your code comments on trial. Powered by Jev. <sub>(upstream description)</sub>
  <sub>`Project` · ntedvs · `TS`</sub>

- **[cu-Jev](https://github.com/dtunai/cu-Jev)** — cuda-Jev — a CUDA-native Jev System One decision inference engine. Jev compatible API, examples, and reproducible benchmarks. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · dtunai · `C` · ⚠ `not Jev itself`</sub>

- **[cyber-breach-jev](https://github.com/rchovatiya88/cyber-breach-jev)** — Cyber-Breach: The Jev Protocol - A tactical cyberpunk arena combat game powered by TypeSafe AI Jev System One decision model <sub>(upstream description)</sub>
  <sub>`Project` · rchovatiya88 · `JS` · ⚠ `no licence`</sub>

- **[dbt_jev](https://github.com/smithclay/dbt_jev)** — use jev in dbt <sub>(upstream description)</sub>
  <sub>`Plugin` · smithclay · `Py`</sub>

- **[decido](https://github.com/yairshy/decido)** — Probabilistic decisions for Python. Use Jev or bring your own provider; crawl with Playwright. <sub>(upstream description)</sub>
  <sub>`Integration` · yairshy · `Py`</sub>

- **[decision-bench](https://github.com/Hanno-Labs/decision-bench)** — Open benchmark runtime for document-grounded decision models <sub>(upstream description)</sub>
  <sub>`Benchmark` · hanno-labs · `Py`</sub>

- **[decision-circuits](https://github.com/Barneyjm/decision-circuits)** — Decision circuits: typed questions to a System One model, calibrated probabilities back, gates in code. Zero-dependency Python SDK with LangChain, OpenAI Agents, and Claude Agent SDK integrations. <sub>(upstream description)</sub>
  <sub>`SDK` · barneyjm · `Py`</sub>

- **[decisions-judge-mcp](https://github.com/clouatre-labs/decisions-judge-mcp)** — Typed decisions for AI agents as an MCP tool: yes/no probability (noul), choice, and score in one fast request. Backed by the TypeSafe System One model. <sub>(upstream description)</sub>
  <sub>`Plugin` · clouatre-labs · `JS`</sub>

- **[dgp](https://github.com/numerous-com/dgp)** — Decision Graph Protocol (DGP) by Numerous ApS: open-source contracts for decision-based AI agents, TypeSafe Jev orchestration, guarded actions, and assessment batching. <sub>(upstream description)</sub>
  <sub>`Project` · numerous-com · `Py`</sub>

- **[diffusion-jev-sglang](https://github.com/Hangzhi/diffusion-jev-sglang)** — A Jev-like decision engine powered by DiffusionGemma and SGLang. Jev with eyes. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · hangzhi · `Py` · ⚠ `not Jev itself`</sub>

- **[dohnuts.cpp](https://github.com/DreamBlooms/dohnuts.cpp)** — The same decisions, on CPU. System One model that can run on your Personal Computer. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · dreamblooms · `C++` · ⚠ `not Jev itself`</sub>

- **[edgejev](https://github.com/yzfly/edgejev)** — 离线可用的本地类型化决策：4 核 CPU 单题 15.6ms。Local & offline Jev / System One inference on CPU — ONNX + INT8, no torch at runtime. 支持 laya / kev / PlayJev <sub>(upstream description)</sub>
  <sub>`Project` · yzfly · `Py`</sub>

- **[emoji-jev](https://github.com/colinmcdermott/emoji-jev)** — Emoji autocomplete at the speed of typing. TypeSafe AI Jev on a Whop-hosted TanStack Start app. <sub>(upstream description)</sub>
  <sub>`Project` · colinmcdermott · `TS` · ⚠ `no licence`</sub>

- **[everything-about-jev](https://github.com/qingshungLI/everything-about-jev)** — tell you everything about jev,TypeSafe AI's System One model for typed decisions. <sub>(upstream description)</sub>
  <sub>`Project` · qingshungli · `Py`</sub>

- **[extremely-specific-council](https://github.com/cbetz/extremely-specific-council)** — Twelve members. Zero qualifications. A playful TypeSafe AI council with animated votes, inspectable decisions, and shareable verdicts. <sub>(upstream description)</sub>
  <sub>`Project` · cbetz · `TS`</sub>

- **[financialpredictionjev](https://github.com/thodoh1/FinancialPredictionJev)** — Using Jev to test how well it predicts financial markets(just like most llms as of september 2026, it doesnt do that good) <sub>(upstream description)</sub>
  <sub>`Project` · thodoh1 · `Py` · ⚠ `no licence`</sub>

- **[frost](https://github.com/marcus/frost)** — A flexible and configurable CLI model router using TypeSafe Jev. <sub>(upstream description)</sub>
  <sub>`Project` · marcus · `Go`</sub>

- **[functions](https://github.com/TrainLCD/Functions)** — 👷 Cloudflare Workers for the TrainLCD mobile app. <sub>(upstream description)</sub>
  <sub>`Project` · trainlcd · `TS` · ⚠ `no licence`</sub>

- **[git-jev-stage](https://github.com/ibrahemid/git-jev-stage)** — Select Git changes for staging with a plain-language description. <sub>(upstream description)</sub>
  <sub>`Project` · ibrahemid · `TS`</sub>

- **[go-system-one](https://github.com/rcarmo/go-system-one)** — when a gopher met Jev <sub>(upstream description)</sub>
  <sub>`SDK` · rcarmo · `Go`</sub>

- **[got-jev](https://github.com/phureewat29/jev-got)** — Jev (TypeSafe AI) PoC through Game of Thrones <sub>(upstream description)</sub>
  <sub>`Project` · phureewat29 · `TS` · ⚠ `no licence`</sub>

- **[ha-conversation-jev](https://github.com/luxus/ha-conversation-jev)** — Home Assistant custom component: Conversation agent with Jev fast-path + Grok fallback <sub>(upstream description)</sub>
  <sub>`Project` · luxus · `Py` · ⚠ `no licence`</sub>

- **[harden-jev-decides](https://github.com/tylerjharden/harden-jev-decides)** — JEV picks which stream idea becomes the live MVP. TypeSafe System One decision board. <sub>(upstream description)</sub>
  <sub>`Project` · tylerjharden · `TS` · ⚠ `no licence`</sub>

- **[hermes-jev-curator](https://github.com/anpicasso/hermes-jev-curator)** — Typed Jev relation governance and safe archive plans for Hermes Curator <sub>(upstream description)</sub>
  <sub>`Project` · anpicasso · `Py`</sub>

- **[hiresignal](https://github.com/ndolinschi/hiresignal)** — HireSignal — resume first-pass fit+interview via TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Project` · ndolinschi · `TS` · ⚠ `no licence`</sub>

- **[hunch-js](https://github.com/steven-shoemaker/hunch-js)** — Jev judgments as TypeScript functions over arrays: classify, score, check, where, extract, pick, rank, verify. LLMs propose, Jev decides. <sub>(upstream description)</sub>
  <sub>`SDK` · steven-shoemaker · `TS`</sub>

- **[jcm-router](https://github.com/adarshmishra07/jcm-router)** — Local proxy that picks the Claude model and effort per message using TypeSafe Jev. Routes subagents, leaves your cached main chat alone. <sub>(upstream description)</sub>
  <sub>`Project` · adarshmishra07 · `TS`</sub>

- **[jear](https://github.com/iJ03l/jear)** — Jev-routed client for NEAR AI Cloud inference and IronClaw agents. <sub>(upstream description)</sub>
  <sub>`SDK` · ij03l · `Rs`</sub>

- **[jeff-cli](https://github.com/saembit/jeff-cli)** — jeff, a Go CLI for Jev: from a shell script, give it state and a question with fixed answers and get calibrated probabilities back, with a rank command and meaningful exit codes.
  <sub>`Project` · saembit · `Go`</sub>

- **[jeq](https://github.com/cristianoliveira/jeq)** — What happens when jev meets jq? Intelligence you can pipe for quick experimentation and scripts <sub>(upstream description)</sub>
  <sub>`Project` · cristianoliveira · `Go`</sub>

- **[jev](https://github.com/anilsenay/jev)** — Unofficial Go client for TypeSafe's System One API and its model, Jev. <sub>(upstream description)</sub>
  <sub>`SDK` · anilsenay · `Go`</sub>

- **[Jev](https://github.com/cobusgreyling/Jev)** — Unofficial TypeSafe Jev showcase — System One decisions, not chat. <sub>(upstream description)</sub>
  <sub>`Project` · cobusgreyling · `Py`</sub>

- **[jev](https://github.com/kataras/jev)** — A Go client for the TypeSafe AI's System One API and its model, Jev. <sub>(upstream description)</sub>
  <sub>`SDK` · kataras · `Go`</sub>

- **[Jev Explained: How to Add Fast, Typed Decisions to an AI Agent](https://aihubmix.com/blog/jev-explained-how-to-add-fast-typed-decisions-to-an-ai-agent)** — A third-party explainer with a useful architecture sketch and an unusually honest list of cases where you should not use a decision model.
  <sub>`Article` · `Py` · ⚠ `code untested`</sub>

- **[jev-2048](https://github.com/ARCJ137442/jev-2048)** — An instrumented 2048 web lab where every move is a Jev (TypeSafe AI System One) Choice, with no heuristic fallback \| 用 Jev 决策模型驱动每一步的 2048 网页实验台，概率、置信度、延迟与成本全部摊开可见，且刻意不做启发式兜底 <sub>(upstream description)</sub>
  <sub>`Project` · arcj137442 · `TS`</sub>

- **[jev-acento](https://github.com/marcosmartinez/jev-acento)** — ¿Jev entiende tu acento? Pre-registered audit of TypeSafe AI's Jev on Spanish — accuracy, calibration and token cost — plus a CLI to run the same comparison on your own labelled data. <sub>(upstream description)</sub>
  <sub>`Benchmark` · marcosmartinez · `Py`</sub>

- **[jev-acp](https://github.com/formulahendry/jev-acp)** — Use Jev typed decisions from any ACP (Agent Client Protocol) client or IDE <sub>(upstream description)</sub>
  <sub>`Project` · formulahendry · `TS`</sub>

- **[jev-agent-failure-benchmark](https://github.com/TokenTrim/jev-agent-failure-benchmark)** — Benchmarking Jev (Typesafe.ai) against a strong LLM on the Who&When Pro agent-failure-attribution benchmark (text subset). <sub>(upstream description)</sub>
  <sub>`Benchmark` · tokentrim · `Py`</sub>

- **[jev-android](https://github.com/dougsong/jev-android)** — A Kotlin Android SDK for UI automation powered by TypeSafe Jev, with an accessibility runtime and sample app. <sub>(upstream description)</sub>
  <sub>`SDK` · dougsong · `Kt`</sub>

- **[jev-anotacao-sentencas](https://github.com/lab-dados/jev-anotacao-sentencas)** — Jev (TypeSafe) vs. Gemini 3.8 Flash vs. GPT-5.6 Luna na anotação estruturada de sentenças do TJSP: qualidade, tempo e custo <sub>(upstream description)</sub>
  <sub>`Project` · lab-dados · `Py` · ⚠ `no licence`</sub>

- **[jev-arena-nanojev](https://github.com/liao96312/jev-arena-nanojev)** — 完全本地的 NanoJev 网格决策游戏实验场，支持中文 Pygame、多关卡与 GTX 1660S 训练 <sub>(upstream description)</sub>
  <sub>`Project` · liao96312 · `Py` · ⚠ `no licence`</sub>

- **[jev-benchmark](https://github.com/wondertwins/jev-benchmark)** — Benchmarks and a playground for TypeSafe's Jev (System One) model: chess, and who-is-the-player-talking-to for speech-to-text game NPCs <sub>(upstream description)</sub>
  <sub>`Benchmark` · wondertwins · `Py`</sub>

- **[jev-blindspot](https://github.com/jsk4581/jev-blindspot)** — A side-panel assistant that finds the blind spots in your prompts. For Claude Code and Codex CLI. <sub>(upstream description)</sub>
  <sub>`Plugin` · jsk4581 · `TS`</sub>

- **[jev-bot](https://github.com/nssmd/jev-bot)** — Self-hosted Jev decision workbench and Feishu bot: automatic choices, probabilities, and experimental word/character writing. <sub>(upstream description)</sub>
  <sub>`Project` · nssmd · `JS`</sub>

- **[jev-broadcast-lab](https://github.com/4anti/jev-broadcast-lab)** — Testing Lab for Jev AI <sub>(upstream description)</sub>
  <sub>`Project` · 4anti · `JS` · ⚠ `no licence`</sub>

- **[jev-bun1](https://github.com/heiwa4126/jev-bun1)** — TypeSafe の Jev を TypeScript SDK で使ってみる最初の 1 歩 <sub>(upstream description)</sub>
  <sub>`SDK` · heiwa4126 · `TS` · ⚠ `no licence`</sub>

- **[jev-calculator](https://github.com/pc418/jev-calculator)** — A probabilistic AI calculator powered by Jev.
  <sub>`Project` · pc418 · `TS`</sub>

- **[jev-canvas](https://github.com/gaborishka/jev-canvas)** — Draw on a tldraw canvas with your voice and a pointing finger. Jev (TypeSafe System One) decides action, target and place in ~350 ms per spoken word. <sub>(upstream description)</sub>
  <sub>`Project` · gaborishka · `JS`</sub>

- **[jev-chat](https://github.com/adhyaay-karnwal/jev-chat)** — A chatbot from typed Jev decisions: hierarchical speculative decoding over System One probabilities. <sub>(upstream description)</sub>
  <sub>`Project` · adhyaay-karnwal · `Py`</sub>

- **[jev-chat-windows-deepseek-jev](https://github.com/Aimark-dai/jev-chat-windows-deepseek-jev)** — Windows 微信回复助手：DeepSeek 官方生成话术，TypeSafe JEV 官方判断排序，支持可取消的 3 秒自动发送。
  <sub>`Project` · aimark-dai · `Py`</sub>

- **[jev-ci-selector](https://github.com/guilhem/jev-ci-selector)** — CI task selection for GitHub Actions with Jev and a pure policy engine; current selection is applied by default, with an explicit shadow mode for observation.
  <sub>`Project` · guilhem · `TS`</sub>

- **[jev-cli](https://github.com/jtsang4/jev-cli)** — CLI for TypeSafe AI's Jev evaluation model — typed questions in, structured JSON answers out <sub>(upstream description)</sub>
  <sub>`Project` · jtsang4 · `TS`</sub>

- **[jev-cloud-quiz](https://github.com/minorun365/jev-cloud-quiz)** — A demo in which Jev judges, with probabilities, which of the three big clouds a feature name belongs to.
  <sub>`Project` · minorun365 · `TS`</sub>

- **[jev-codex-router-skill](https://github.com/455-dIAO/jev-codex-router-skill)** — Portable Codex Skill for Jev model and reasoning-effort routing, with safe installation and Chinese usage guides <sub>(upstream description)</sub>
  <sub>`Plugin` · 455-diao · `Py` · ⚠ `no licence`</sub>

- **[jev-connector](https://github.com/juanlentino/jev-connector)** — WordPress connector for TypeSafe Jev: typed, confidence-scored answers your code can branch on. <sub>(upstream description)</sub>
  <sub>`Plugin` · juanlentino · `PHP`</sub>

- **[jev-cookbook](https://github.com/paramjeetn/jev-cookbook)** — The complete cookbook for Jev by TypeSafe AI — 120+ use cases, 10 runnable examples, 4 composition patterns, and first-principles theory for the world's first System One AI model. <sub>(upstream description)</sub>
  <sub>`Tutorial` · paramjeetn · `Py`</sub>

- **[jev-cvss](https://github.com/Red5d/jev-cvss)** — Fast CVSS scoring from vulnerability descriptions using Typesafe Jev <sub>(upstream description)</sub>
  <sub>`Project` · red5d · `Py`</sub>

- **[jev-cyrillic-audit](https://github.com/AHTOOOXA/jev-cyrillic-audit)** — Does TypeSafe's Jev keep its accuracy and calibration on Russian? Independent RU vs EN audit (ECE, reliability diagrams, paired bootstrap) on parallel human-labelled data. <sub>(upstream description)</sub>
  <sub>`Benchmark` · ahtoooxa · `Py`</sub>

- **[jev-demo](https://github.com/sawzhang/jev-demo)** — Jev (TypeSafe System One) 学习与实测：概念文档 + 5 个可运行 demo + 可复现压测。实测 jev-1.13.0：扇出几乎免费，40 问与 1 问等延迟。 <sub>(upstream description)</sub>
  <sub>`Project` · sawzhang · `TS` · ⚠ `no licence`</sub>

- **[jev-demo](https://github.com/PenglongHuang/jev-demo)** — A zero-dependency web bench for TypeSafe Jev with three presets — browser actions, intent recognition and agent context pruning: send state and typed questions, get calibrated structured answers.
  <sub>`Project` · penglonghuang · `JS`</sub>

- **[jev-docs-zh](https://github.com/Bald0Wang/jev-docs-zh)** — Jev 模型（TypeSafe AI）官方使用文档的中文翻译 \| Unofficial Chinese translation of the official Jev (TypeSafe AI) docs — https://docs.typesafe.ai
  <sub>`Project` · bald0wang · `Py` · ⚠ `no licence`</sub>

- **[jev-does-not-play-dice](https://github.com/KantaHayashiAI/jev-does-not-play-dice)** — Experiments on Jev’s probability calibration, uncertainty reporting, and forecast probability preservation. <sub>(upstream description)</sub>
  <sub>`Benchmark` · kantahayashiai · `JS`</sub>

- **[jev-evaluation](https://github.com/willkelly/jev-evaluation)** — An adversarial evaluation of TypeSafe's jev decision model: nine experiments and 28 predictions fixed before any data was collected. 123,805 requests, $12.69. <sub>(upstream description)</sub>
  <sub>`Project` · willkelly · `Py`</sub>

- **[jev-eyes](https://github.com/LeddoEngano/jev-eyes)** — Give Jev eyes — honest, local image perception for TypeSafe's text-only System One model. OCR + spatial layout → Jev state. CLI, MCP server, agent skill. <sub>(upstream description)</sub>
  <sub>`Plugin` · leddoengano · `Py`</sub>

- **[jev-freeform](https://github.com/kesku/jev-freeform)** — An observable raw-character chat experiment powered entirely by TypeSafe Jev Choice <sub>(upstream description)</sub>
  <sub>`Project` · kesku · `JS` · ⚠ `no licence`</sub>

- **[jev-games](https://github.com/shantanugoel/jev-games)** — Visual Jev lab for multiple games and emulator platforms <sub>(upstream description)</sub>
  <sub>`Project` · shantanugoel · `Py` · ⚠ `no licence`</sub>

- **[jev-go](https://github.com/guillemus/jev-go)** — Unofficial Go SDK for TypeSafe AI's Jev API <sub>(upstream description)</sub>
  <sub>`SDK` · guillemus · `Go` · ⚠ `no licence`</sub>

- **[jev-go](https://github.com/Gaurav-Gosain/jev-go)** — Go client for TypeSafe's System One API and its model Jev: typed judgments and calibrated probabilities instead of generated text <sub>(upstream description)</sub>
  <sub>`SDK` · gaurav-gosain · `Go`</sub>

- **[jev-go-sdk](https://github.com/ajayk/jev-go-sdk)** — Dependency-free Go client for TypeSafe AI's System One API and the Jev model <sub>(upstream description)</sub>
  <sub>`SDK` · ajayk · `Go`</sub>

- **[jev-gomoku](https://github.com/XieChengYuan/jev-gomoku)** — 弈瞬：双 Jev 五子棋九宫格输入实验台，逐手查看模型决策，支持真实对局回放与实时对战。 <sub>(upstream description)</sub>
  <sub>`Project` · xiechengyuan · `JS` · ⚠ `no licence`</sub>

- **[jev-grand-prix](https://github.com/enoyola/jev-grand-prix)** — An F1 racing game where TypeSafe's Jev picks the racing line and the pedals, and learns each corner's limit between laps <sub>(upstream description)</sub>
  <sub>`Project` · enoyola · `JS`</sub>

- **[jev-grug](https://github.com/mkotlikov/jev-grug)** — Helping JEV speak <3 <sub>(upstream description)</sub>
  <sub>`Project` · mkotlikov · `TS`</sub>

- **[jev-java](https://github.com/Olti1947/jev-java)** — Idiomatic Java SDK for TypeSafe AI Jev System One decision engine <sub>(upstream description)</sub>
  <sub>`SDK` · olti1947 · `Java` · ⚠ `no licence`</sub>

- **[jev-java](https://github.com/gudcks0305/jev-java)** — Unofficial Java SDK for TypeSafe Jev and Vercel AI Gateway, with Spring Boot and WebClient support <sub>(upstream description)</sub>
  <sub>`SDK` · gudcks0305 · `Java`</sub>

- **[jev-jp-address](https://github.com/smasato/jev-jp-address)** — Jev (TypeSafe) 性能評価プロジェクト — 日本郵便 KEN_ALL をマスタに、AI SDK 経由の Jev が住所のあいまい一致にどこまで使えるかを検証 <sub>(upstream description)</sub>
  <sub>`SDK` · smasato · `TS` · ⚠ `no licence`</sub>

- **[jev-korean-benchmark](https://github.com/mahlernim/jev-korean-benchmark)** — Reproducible early-access evaluation of Jev on Korean understanding and medical text, with runtime and cost evidence <sub>(upstream description)</sub>
  <sub>`Benchmark` · mahlernim · `Py` · ⚠ `no licence`</sub>

- **[jev-lab](https://github.com/danielhirt/jev-lab)** — Experiments on TypeSafe Jev (System One decision model) via OpenRouter: repeatability, perturbation, and LLM baseline comparison <sub>(upstream description)</sub>
  <sub>`Benchmark` · danielhirt · `TS` · ⚠ `no licence`</sub>

- **[jev-lab](https://github.com/llt22/jev-lab)** — Hands-on research lab for TypeSafe's Jev (System One model): reproducible benchmarks of Noul/Choice/Score primitives, confidence gating, fan-out latency, agent control — plus a living audit of the Jev ecosystem. <sub>(upstream description)</sub>
  <sub>`Benchmark` · llt22 · `Py` · ⚠ `no licence`</sub>

- **[jev-lab](https://github.com/Menny1337/jev-lab)** — TypeScript experiments, evaluations, and latency benchmarks for TypeSafe's Jev model <sub>(upstream description)</sub>
  <sub>`Benchmark` · menny1337 · `TS` · ⚠ `no licence`</sub>

- **[jev-little-airways](https://github.com/lbotinelly/jev-little-airways)** — A show-and-tell capability study for Jev, TypeSafe's System One decision model. <sub>(upstream description)</sub>
  <sub>`Benchmark` · lbotinelly · `TS`</sub>

- **[jev-mcp](https://github.com/arunav25/jev-mcp)** — Connect JEV to MCP clients and compare its judgments against general-purpose LLMs using shared datasets and measurable accuracy. <sub>(upstream description)</sub>
  <sub>`Plugin` · arunav25 · `JS`</sub>

- **[jev-mcp](https://github.com/BYK/jev-mcp)** — An eval-first MCP server for TypeSafe's Jev, a System One model that returns typed judgments (noul, choice, score) with probabilities instead of generated text. <sub>(upstream description)</sub>
  <sub>`Plugin` · byk · `TS`</sub>

- **[jev-mcp](https://github.com/freepik-company/jev-mcp)** — MCP server for typed decisions with Jev / System One via OpenRouter or TypeSafe <sub>(upstream description)</sub>
  <sub>`Plugin` · freepik-company · `Go`</sub>

- **[jev-mcp](https://github.com/rajasekharponakala/jev-mcp)** — MCP server wrapping TypeSafe's Jev System One models — typed noul/choice/score judgments for AI agents <sub>(upstream description)</sub>
  <sub>`Plugin` · rajasekharponakala · `Py`</sub>

- **[jev-mcp](https://github.com/rashedInt32/jev-mcp)** — MCP server exposing TypeSafe Jev as typed, calibrated judgment tools: classify, score, check, batched ask. Ships as a Claude Code plugin. <sub>(upstream description)</sub>
  <sub>`Plugin` · rashedint32 · `TS`</sub>

- **[jev-mcp-spring](https://github.com/Ashfaqbs/jev-mcp-spring)** — Java/Spring Boot MCP server for TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Plugin` · ashfaqbs · `Java`</sub>

- **[jev-measured](https://github.com/WallerChen/jev-measured)** — Measured cost, latency and raw output from the live Jev API (TypeSafe AI System One model) across 8 use cases — reproducible <sub>(upstream description)</sub>
  <sub>`Project` · wallerchen · `Py`</sub>

- **[jev-minesweeper](https://github.com/comoc/jev-minesweeper)** — TypeSafe Jev (System One) にブラウザ上のマインスイーパーを解かせるデモ <sub>(upstream description)</sub>
  <sub>`Project` · comoc · `JS` · ⚠ `no licence`</sub>

- **[jev-no-enem](https://github.com/patryckalves/jev-no-enem)** — Reproducible benchmark evaluating TypeSafe AI's Jev (System One paradigm) on Brazil's ENEM 2025 standardized exam. Evaluates typed decision-making, domain-specific accuracy, and RLCD uncertainty calibration against open LLM baselines with an interactive GitHub Pages dashboard. <sub>(upstream description)</sub>
  <sub>`Benchmark` · patryckalves · `Py` · ⚠ `no licence`</sub>

- **[jev-php-sdk](https://github.com/mzainzulifqar/jev-php-sdk)** — PHP SDK for TypeSafe's Jev: send text and typed questions, get typed answers with calibrated confidence. PHP 8.1+, works with any PSR-18 client, Laravel 8–13. <sub>(upstream description)</sub>
  <sub>`SDK` · mzainzulifqar · `PHP`</sub>

- **[jev-pick-and-place-study](https://github.com/tryaksh/jev-pick-and-place-study)** — A small reproducible MuJoCo pilot comparing Jev, Claude Haiku, and reactive rules for pick-and-place. <sub>(upstream description)</sub>
  <sub>`Project` · tryaksh · `Py` · ⚠ `no licence`</sub>

- **[jev-pii-checker](https://github.com/coo-quack/jev-pii-checker)** — CLI that finds PII in text with TypeSafe Jev: presence, sensitivity, and located spans <sub>(upstream description)</sub>
  <sub>`Project` · coo-quack · `TS`</sub>

- **[jev-playground](https://github.com/wustep/jev-playground)** — Can a System One model steer music? Jev picks the plan (enums only); code renders sheet, audio and MIDI. <sub>(upstream description)</sub>
  <sub>`Project` · wustep · `TS` · ⚠ `no licence`</sub>

- **[jev-playground](https://github.com/Little-Planet-Labs/jev-playground)** — A small Next.js app for experimenting with TypeSafe AI's Jev model (System One) <sub>(upstream description)</sub>
  <sub>`Project` · little-planet-labs · `TS` · ⚠ `no licence`</sub>

- **[jev-plays-pokemon](https://github.com/milanboers/jev-plays-pokemon)** — Playing Pokemon Red using TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Project` · milanboers · `Py`</sub>

- **[jev-practice-speed](https://github.com/tubone24/jev-practice-speed)** — A WebGL demo where you play the card game Speed against a CPU whose brain is TypeSafe AI's Jev. The whole point of the app is to measure and show Jev's decision speed and decision accuracy in real time. <sub>(upstream description)</sub>
  <sub>`Project` · tubone24 · `JS` · ⚠ `no licence`</sub>

- **[jev-realtime-trading](https://github.com/rthomas24/jev-realtime-trading)** — Paper trading agents on a live tape, decided every second by TypeSafe's Jev (System One). Electron desktop app. <sub>(upstream description)</sub>
  <sub>`Project` · rthomas24 · `TS`</sub>

- **[jev-research](https://github.com/sherajdev/jev-research)** — Practical guide to using TypeSafe Jev with Herdr and Claude, Codex, Hermes, and browser agents. <sub>(upstream description)</sub>
  <sub>`Tutorial` · sherajdev · `TS`</sub>

- **[jev-resume-disqualifier](https://github.com/AiPersonacademy/jev-resume-disqualifier)** — Jev Resume Disqualifier: Sub-25ms automated resume knockout engine powered by TypeSafe Jev System One decision intelligence. Eliminates 80% of unqualified applicants with deterministic date math & EEOC-safe rejection notices. <sub>(upstream description)</sub>
  <sub>`Project` · aipersonacademy · `Py`</sub>

- **[jev-routing-experiment](https://github.com/TokenTrim/jev-routing-experiment)** — Benchmarking TypeSafe's Jev decision model as a cost-efficient LLM router on RouterArena <sub>(upstream description)</sub>
  <sub>`Benchmark` · tokentrim · `Py`</sub>

- **[jev-rs](https://github.com/abeldzan/jev-rs)** — Async-first Rust SDK for the TypeSafe AI API <sub>(upstream description)</sub>
  <sub>`SDK` · abeldzan · `Rs`</sub>

- **[jev-sdk-java](https://github.com/luigivis/jev-sdk-java)** — Type-safe Java 21 client for the TypeSafe AI Jev (System One) decision API <sub>(upstream description)</sub>
  <sub>`SDK` · luigivis · `Java`</sub>

- **[jev-search](https://github.com/larguesa/jev-search)** — Experimental semantic line search with TypeSafe Jev via OpenRouter. Python CLI with no runtime dependencies. <sub>(upstream description)</sub>
  <sub>`Project` · larguesa · `Py`</sub>

- **[jev-sim](https://github.com/dashbi1/jev-sim)** — Jev-compatible /v1/systemone server reading typed decisions from LLM logits, benchmarked against TypeSafe's Jev on the same items via JevBench <sub>(upstream description)</sub>
  <sub>`Benchmark` · dashbi1 · `Py`</sub>

- **[jev-skill-router](https://github.com/shimo4228/jev-skill-router)** — Claude Code plugin: asks TypeSafe Jev which installed skill fits each prompt and logs the answer (shadow-first). A working reference for the skill-suggestion cookbook on Claude Code — the README records why it is unlikely to help a strong model as a router. <sub>(upstream description)</sub>
  <sub>`Plugin` · shimo4228 · `Py`</sub>

- **[jev-skills](https://github.com/laguagu/jev-skills)** — Practical agent skills and examples for building with Jev. API setup, routing, ranking, and evidence checks. <sub>(upstream description)</sub>
  <sub>`Plugin` · laguagu · `JS`</sub>

- **[jev-skills](https://github.com/WanLanglin/jev-skills)** — Claude Code & Codex skills powered by Jev, TypeSafe's System One model. 256 calibrated judgements for $0.0005 in 0.72s — 360x cheaper than Claude Opus 5. Includes the first published Jev calibration curve, measured on 4,995 real agent decisions. <sub>(upstream description)</sub>
  <sub>`Plugin` · wanlanglin · `Py` · ⚠ `no licence`</sub>

- **[jev-snake](https://github.com/iammusham/jev-snake)** — An experimental Snake environment where the game engine owns deterministic rules and TypeSafe AI's Jev makes the movement decision from structured state on every tick. <sub>(upstream description)</sub>
  <sub>`Project` · iammusham · `Py` · ⚠ `no licence`</sub>

- **[jev-symfony-bundle](https://github.com/vbcherepanov/jev-symfony-bundle)** — Unofficial Symfony bundle for TypeSafe AI's Jev: typed client, validator constraints, Messenger, Workflow guards and profiler panel <sub>(upstream description)</sub>
  <sub>`SDK` · vbcherepanov · `PHP`</sub>

- **[jev-system-one](https://github.com/haseeb-heaven/jev-system-one)** — A polished OpenAI + TypeSafe Jev terminal interface for answers with transparent decision reports <sub>(upstream description)</sub>
  <sub>`Project` · haseeb-heaven · `Py`</sub>

- **[jev-t-rex-runner](https://github.com/joshlarsen/jev-t-rex-runner)** — Chrome dino game played by Typesafe AI Jev model <sub>(upstream description)</sub>
  <sub>`Project` · joshlarsen · `JS`</sub>

- **[jev-torneo-animales](https://github.com/hectorlcastro09/jev-torneo-animales)** — Winner-stays-on animal tournament refereed by Jev (TypeSafe System One): a local game to feel how fast typed decisions are. UI in Spanish. <sub>(upstream description)</sub>
  <sub>`Project` · hectorlcastro09 · `TS`</sub>

- **[jev-trip](https://github.com/liaoyuhua/jev-trip)** — Two Minds, One Trip. https://jev-trip.vercel.app/ <sub>(upstream description)</sub>
  <sub>`Project` · liaoyuhua · `TS`</sub>

- **[jev-wingman](https://github.com/1104480426-hash/jev-wingman)** — 基于 Jev 的聊天决策辅助，不挑 App（QQ / 微信 / 飞书皆可）· An on-device chat co-pilot that returns typed verdicts instead of prose, built on Jev
  <sub>`Project` · 1104480426-hash · `Java`</sub>

- **[jev-x-kit](https://github.com/Kadihx/jev-x-kit)** — Offline $0 decision layer for coding agents: Choice/Score/Noul primitives, BELKI confidence gatekeeper, ultra-planning, red-teaming, research and RLVR self-improvement -- as an MCP server + CLI + Claude Code skill. <sub>(upstream description)</sub>
  <sub>`Project` · kadihx · `TS`</sub>

- **[jev-yt-time-saver](https://github.com/jaibhasin/jev-yt-time-saver)** — A Chrome extension that covers distracting YouTube videos with Jev. Show anyway whenever you want. <sub>(upstream description)</sub>
  <sub>`Plugin` · jaibhasin · `JS` · ⚠ `no licence`</sub>

- **[jev2048](https://github.com/KyleKreuter/jev2048)** — Let Jev (TypeSafeAI) solve 2048 <sub>(upstream description)</sub>
  <sub>`Project` · kylekreuter · `TS` · ⚠ `no licence`</sub>

- **[jev4k](https://github.com/pambrose/jev4k)** — A Kotlin DSL and client for TypeSafe's Jev model <sub>(upstream description)</sub>
  <sub>`SDK` · pambrose · `Kt`</sub>

- **[jev4mellea](https://github.com/SoundBlaster/Jev4Mellea)** — Jev adapter for Mellea <sub>(upstream description)</sub>
  <sub>`Integration` · soundblaster · `Py`</sub>

- **[jev_jsonschema](https://github.com/Kiln-AI/jev_jsonschema)** — Run a JSON Schema through TypeSafe's Jev API, and get JSON back. <sub>(upstream description)</sub>
  <sub>`Project` · kiln-ai · `Py`</sub>

- **[Jev_Ontology](https://github.com/dagfinndybvig/Jev_Ontology)** — Trying to combine Jev with ontology <sub>(upstream description)</sub>
  <sub>`Project` · dagfinndybvig · `Py` · ⚠ `no licence`</sub>

- **[jev_project_context](https://github.com/poiuyjie/jev_project_context)** — Evidence-first long-term experiment memory skill for AI coding agents, with optional Jev decision-model layers <sub>(upstream description)</sub>
  <sub>`Plugin` · poiuyjie · `Py`</sub>

- **[jevals](https://github.com/dayhaysoos/jevals)** — Local evaluation workbench for TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Project` · dayhaysoos · `TS`</sub>

- **[jevclient](https://github.com/AboveColin/jevclient)** — Async Python client for TypeSafe Jev. Typed questions in, probabilities and choices out, no prose to parse. <sub>(upstream description)</sub>
  <sub>`SDK` · abovecolin · `Py`</sub>

- **[jevcode](https://github.com/miounet11/jevcode)** — JevCode: technical solutions and best practices for Jev (TypeSafe System One), with a companion website.
  <sub>`Project` · miounet11 · `TS` · ⚠ `no licence`</sub>

- **[jevgo](https://github.com/fgn/jevgo)** — Go client for TypeSafe AI's System One API (Jev), with optional Langfuse instrumentation <sub>(upstream description)</sub>
  <sub>`SDK` · fgn · `Go`</sub>

- **[jevgo](https://github.com/devbackend/jevgo)** — Unofficial Go client for the TypeSafe AI System One API (Jev) — typed questions in, calibrated answers out. <sub>(upstream description)</sub>
  <sub>`SDK` · devbackend · `Go`</sub>

- **[jevlang](https://github.com/sumanmichael/jevlang)** — The simplest way to write decision workflows in Python. Python with a smart if. <sub>(upstream description)</sub>
  <sub>`SDK` · sumanmichael · `Py`</sub>

- **[jevmem](https://github.com/Avinash-jetwani/jevmem)** — Automatic project memory for Claude Code. Also works with Cursor and Codex. <sub>(upstream description)</sub>
  <sub>`Plugin` · avinash-jetwani · `TS`</sub>

- **[Jevometry](https://github.com/Kunyanli230/Jevometry)** — an Information-Geometric Analysis Toolkit for any System-one (Jev, Jevlike) agent systems <sub>(upstream description)</sub>
  <sub>`Project` · kunyanli230 · `Py`</sub>

- **[jevopt](https://github.com/Ramneet-Singh/jevopt)** — Making intelligent compiler optimisation decisions with Jev <sub>(upstream description)</sub>
  <sub>`Project` · ramneet-singh · `Py`</sub>

- **[jevplayspokemon](https://github.com/anxkhn/JevPlaysPokemon)** — Jev plays Generation 3 Pokémon via Showdown and a real FireRed ROM. <sub>(upstream description)</sub>
  <sub>`Project` · anxkhn · `TS`</sub>

- **[jevsbistro](https://github.com/andrewsilber/JevsBistro)** — 3D restaurant service simulator for benchmarking low-latency decision models <sub>(upstream description)</sub>
  <sub>`Benchmark` · andrewsilber · `TS`</sub>

- **[jevscope](https://github.com/jeiel85/jevscope)** — Local-first visual decision debugger and regression testbench for TypeSafe AI Jev <sub>(upstream description)</sub>
  <sub>`Project` · jeiel85 · `TS`</sub>

- **[jevseek](https://github.com/blingdivinity/jevseek)** — DeepSeek proposes the next token, TypeSafe's Jev chooses it: a decision model used as a sampler <sub>(upstream description)</sub>
  <sub>`Project` · blingdivinity · `Py`</sub>

- **[jevslop](https://github.com/TKY-27/JevSlop)** — Jevによるnote記事のAI Slop判定サイト <sub>(upstream description)</sub>
  <sub>`Project` · tky-27 · `TS`</sub>

- **[JevTape](https://github.com/Hugo-DDT/JevTape)** — A record-and-replay tool for Jev decisions: a CLI, a local proxy and JSON tapes, with replay fully offline.
  <sub>`Project` · hugo-ddt · `Java`</sub>

- **[jevtest](https://github.com/joshhu/jevtest)** — 情緒測謊器：嘴上說「好」，心裡真的好嗎？用 TypeSafe Jev（System One 模型）透過 OpenRouter 即時判斷，並與一般 LLM 對照 <sub>(upstream description)</sub>
  <sub>`Project` · joshhu · `TS` · ⚠ `no licence`</sub>

- **[jevtok](https://github.com/LabGuy94/jevtok)** — Exact token counting and request-cost prediction for TypeSafe's Jev (tiktoken-style) <sub>(upstream description)</sub>
  <sub>`Project` · labguy94 · `Py`</sub>

- **[jevtown](https://github.com/gaborishka/jevtown)** — Jevtown: a social network where people write and 10,000 AI personas react <sub>(upstream description)</sub>
  <sub>`Project` · gaborishka · `JS`</sub>

- **[jpp](https://github.com/Towow-ai/jpp)** — J++: an experimental language with standalone source and a Rust runtime. Compose questions and methods. 独立源码，组合问题与方法。 <sub>(upstream description)</sub>
  <sub>`Project` · towow-ai · `Rs`</sub>

- **[kojev](https://github.com/ItisNoMatter/kojev)** — Kotlin Multiplatform client for Jev that returns your own enum/sealed types instead of string keys. <sub>(upstream description)</sub>
  <sub>`SDK` · itisnomatter · `Kt`</sub>

- **[kunobi-jev](https://github.com/kunobi-ninja/kunobi-jev)** — Rust client for the TypeSafe System One API (Jev) <sub>(upstream description)</sub>
  <sub>`SDK` · kunobi-ninja · `Rs`</sub>

- **[labs](https://github.com/kiarina/labs)** — Small, independent projects for experiments, research, and investigations. <sub>(upstream description)</sub>
  <sub>`Project` · kiarina · `Py`</sub>

- **[laya-jev-lab](https://github.com/yibie/laya-jev-lab)** — Independent measurements of typed-decision models: Jev (TypeSafe API) vs Laya (open weights), and a local-first cascade that matches Jev's accuracy at 1.8x the speed <sub>(upstream description)</sub>
  <sub>`Project` · yibie · `Py`</sub>

- **[learn-jev-end-to-end](https://github.com/harshithsunku/learn-jev-end-to-end)** — Learn Jev end to end: a free hands-on course. Build 13 AI agent use cases with a fast brain (Jev) and a slow brain (LLM). One OpenRouter key. <sub>(upstream description)</sub>
  <sub>`Tutorial` · harshithsunku · `Py`</sub>

- **[legalforecastbench](https://github.com/johnhughes3/LegalForecastBench)** — LegalForecast-MTD benchmark alpha and official evaluation workflows <sub>(upstream description)</sub>
  <sub>`Benchmark` · johnhughes3 · `Py`</sub>

- **[magic-jev-ball](https://github.com/mikecann/magic-jev-ball)** — A Magic 8 Ball that asks Jev instead of picking at random. Convex + AI Gateway + three.js. <sub>(upstream description)</sub>
  <sub>`Project` · mikecann · `TS`</sub>

- **[mcpmatch](https://github.com/ndolinschi/mcpmatch)** — Match user goals to MCP catalog (two-stage) via TypeSafe Jev <sub>(upstream description)</sub>
  <sub>`Plugin` · ndolinschi · `TS` · ⚠ `no licence`</sub>

- **[mcts-agent](https://github.com/lhemerly/mcts-agent)** — Discriminative Monte Carlo Tree Search using TypeSafe Jev System One Primitives and Gemini
  <sub>`Project` · lhemerly · `Py`</sub>

- **[midscene-jev-runner](https://github.com/KiritoKing/midscene-jev-runner)** — Community-maintained JEV runner integration for Midscene Test <sub>(upstream description)</sub>
  <sub>`Integration` · kiritoking · `TS`</sub>

- **[mimicry](https://github.com/jxucoder/mimicry)** — Rewrite AI drafts in your own voice with a bounded TypeSafe feedback loop. <sub>(upstream description)</sub>
  <sub>`Project` · jxucoder · `Py` · ⚠ `no licence`</sub>

- **[n8n-nodes-jev](https://github.com/vibe-with-me-tools/n8n-nodes-jev)** — Helper n8n community node for Jev by TypeSafe. Classify, route, and score text with questions you define, and get a probability for every answer so unsure items can go to review. <sub>(upstream description)</sub>
  <sub>`Plugin` · vibe-with-me-tools · `TS`</sub>

- **[n8n-nodes-typesafe](https://github.com/Biztactix/n8n-nodes-typesafe)** — Typesafe AI Node for N8N <sub>(upstream description)</sub>
  <sub>`Plugin` · biztactix · `TS`</sub>

- **[n8n-nodes-typesafe-jev](https://github.com/n3ndor/n8n-nodes-typesafe-jev)** — n8n community node for TypeSafe Jev structured AI decisions <sub>(upstream description)</sub>
  <sub>`Project` · n3ndor · `TS`</sub>

- **[new-api-plugin-typesafe](https://github.com/FFatTiger/new-api-plugin-typesafe)** — TypeSafe AI System One (Jev) task plugin for QuantumNous/new-api — native /v1/systemone, synchronous evaluation, token billing <sub>(upstream description)</sub>
  <sub>`Plugin` · ffattiger · `JS`</sub>

- **[open-jev-bridge](https://github.com/louis-szeto/open-jev-bridge)** — MCP plugin to connect jev-like system one API (local hosted or typesafe jev) to codex and claude code for decision tasks like compaction, verification judgement, etc. <sub>(upstream description)</sub>
  <sub>`Plugin` · louis-szeto · `JS`</sub>

- **[OpenJev](https://github.com/GPT-AGI/OpenJev)** — Jev-compatible System 开源Jev
  <sub>`Jev-like alternative` · gpt-agi · `Py` · ⚠ `not Jev itself`</sub>

- **[OpenJev](https://github.com/xingwudao/OpenJev)** — OpenJev: an independent Jev-inspired System One decision API based on TypeSafe.ai concepts. Choice, score and noul primitives, local mock server, Python and TypeScript SDKs. Real inference planned; not affiliated with TypeSafe AI. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · xingwudao · `Py` · ⚠ `not Jev itself` `no licence`</sub>

- **[openpoke-meets-jev](https://github.com/0xShin0221/openpoke-meets-jev)** — Open source implementation of Poke <sub>(upstream description)</sub>
  <sub>`Project` · 0xshin0221 · `Py`</sub>

- **[origin-civilization](https://github.com/JacquesGariepy/ORIGIN-CIVILIZATION)** — AI life-and-civilization simulation: TypeSafe Jev makes every decision (typed, probabilistic, auditable); LLMs plan — OpenAI-compatible APIs, local models (Ollama, LM Studio), Claude Code, Codex. <sub>(upstream description)</sub>
  <sub>`Benchmark` · jacquesgariepy · `TS`</sub>

- **[pi-agent-foreman](https://github.com/alexshpunt/pi-agent-foreman)** — Send Pi agents back to work when they stop before the job is done. <sub>(upstream description)</sub>
  <sub>`Project` · alexshpunt · `TS`</sub>

- **[pi-typesafe](https://github.com/twilwa/pi-typesafe)** — Pi coding-agent extension built on the TypeSafe AI System One API (Jev) <sub>(upstream description)</sub>
  <sub>`Plugin` · twilwa · `TS` · ⚠ `no licence`</sub>

- **[pong-jev](https://github.com/safzanpirani/pong-jev)** — TypeSafe's Jev plays Atari Pong. One typed Choice question per frame, no coordinates sent to the model. <sub>(upstream description)</sub>
  <sub>`Project` · safzanpirani · `TS` · ⚠ `no licence`</sub>

- **[pydantic-jev-examples](https://github.com/adtyavrdhn/pydantic-jev-examples)** — Pydantic AI capabilities made stronger with Jev: small runnable demos, one file each <sub>(upstream description)</sub>
  <sub>`Project` · adtyavrdhn · `Py` · ⚠ `no licence`</sub>

- **[r2r-jev](https://github.com/Thneoly/r2r-jev)** — Persistent governance for AI agents — turn Jev judgments into replayable relation state with R2R. <sub>(upstream description)</sub>
  <sub>`Project` · thneoly · `Rs`</sub>

- **[research_desk](https://github.com/0xnairb/research_desk)** — TypeSafe Jev demonstration for new analyzation — experimenting with Jev for fast analysis of news and tickers <sub>(upstream description)</sub>
  <sub>`Project` · 0xnairb · `Py` · ⚠ `no licence`</sub>

- **[risc-jev](https://github.com/i2cjak/RISC-jeV)** — I tortured Jev into being a RISC-V CPU. <sub>(upstream description)</sub>
  <sub>`Project` · i2cjak · `Py` · ⚠ `no licence`</sub>

- **[river-run-typesafe](https://github.com/ashaazami/river-run-typesafe)** — River shooter game in Python, inspired by Atari's River Raid, played by a TypeSafe AI pilot <sub>(upstream description)</sub>
  <sub>`Project` · ashaazami · `Py`</sub>

- **[rubikjev](https://github.com/0xtrou/rubikjev)** — Challenge the Jev's intelligence in Rubik Cube puzzles <sub>(upstream description)</sub>
  <sub>`Project` · 0xtrou · `TS` · ⚠ `no licence`</sub>

- **[ruling](https://github.com/bradAGI/ruling)** — Typed, calibrated decisions from a local model. No text generated. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · bradagi · `Py` · ⚠ `not Jev itself` `unverified claims`</sub>

- **[rust-sysone](https://github.com/zcoder-run/rust-sysone)** — System One TypeSafe AI Rust Client (unofficial) <sub>(upstream description)</sub>
  <sub>`Project` · zcoder-run · `Rs`</sub>

- **[s1_ruby](https://github.com/innocentdiaz/s1_ruby)** — Makes S1-model 'measurement' (and the collapse that follows it) a Ruby primitive. <sub>(upstream description)</sub>
  <sub>`SDK` · innocentdiaz · `Rb`</sub>

- **[scam-shield](https://github.com/ShupingR/scam-shield)** — Scam text message filter powered by TypeSafe's Jev model <sub>(upstream description)</sub>
  <sub>`Project` · shupingr · `TS` · ⚠ `no licence`</sub>

- **[search-function-test](https://github.com/Shifros/Search-Function-Test)** — A test project based on Jev AI, the goal is to build a search function for a blog/article website that has 100s of articles to search from, So the user can actually use the search as chat to question anything and find related answers/articles <sub>(upstream description)</sub>
  <sub>`Project` · shifros · `JS` · ⚠ `no licence`</sub>

- **[second-thought](https://github.com/KNambiarDJsc/second-thought)** — Learning infrastructure for typed probabilistic decisions from System One models (Laya, and typed-decision providers you bring yourself). <sub>(upstream description)</sub>
  <sub>`Project` · knambiardjsc · `Py`</sub>

- **[secondlayer](https://github.com/ryanwaits/secondlayer)** — Decoded Stacks data in your own database. Self-hosted. <sub>(upstream description)</sub>
  <sub>`Project` · ryanwaits · `TS`</sub>

- **[should-ai-kill-us-all](https://github.com/hellogumbo/should-ai-kill-us-all)** — We ask Jev, TypeSafe AI's System One model, whether AI should kill us all. Every ten minutes. Using the actual headlines. <sub>(upstream description)</sub>
  <sub>`Project` · hellogumbo · `JS`</sub>

- **[skill-router](https://github.com/lomeshdutta/skill-router)** — Tell Claude Code which installed skill a session needs, using Jev (TypeSafe AI) for the decision and skills.sh for discovery. <sub>(upstream description)</sub>
  <sub>`Plugin` · lomeshdutta · `Py`</sub>

- **[soupbase](https://github.com/spoonnotfound/soupbase)** — Jev x 海龟汤 <sub>(upstream description)</sub>
  <sub>`Project` · spoonnotfound · `TS`</sub>

- **[sqlite3-jev](https://github.com/mattn/sqlite3-jev)** — SQLite extension that calls TypeSafe Jev (or tensai serve) from SQL <sub>(upstream description)</sub>
  <sub>`Plugin` · mattn · `C`</sub>

- **[switchboard](https://github.com/ruban-24/switchboard)** — An open-source, model-agnostic decision router for Claude Code and Codex. <sub>(upstream description)</sub>
  <sub>`Plugin` · ruban-24 · `TS`</sub>

- **[sysone-bench](https://github.com/instax-dutta/sysone-bench)** — First independent head-to-head benchmark of System One decision models (Laya vs Jev) on byte-identical inputs <sub>(upstream description)</sub>
  <sub>`Benchmark` · instax-dutta · `Py`</sub>

- **[system-one-adapter-rust](https://github.com/codeitlikemiley/system-one-adapter-rust)** — Rust port of TypeSafe system-one-adapter (LLM-backed system_one evaluations) <sub>(upstream description)</sub>
  <sub>`Integration` · codeitlikemiley · `Rs`</sub>

- **[system-one-chess](https://github.com/dperezcabrera/system-one-chess)** — Chess against Jev, TypeSafe AI's System One model, through OpenRouter. Built with the pico framework. <sub>(upstream description)</sub>
  <sub>`Project` · dperezcabrera · `Py`</sub>

- **[systemone-lite](https://github.com/fritzprix/systemone-lite)** — Toy local System One–style decision API (Jev-shaped). Not affiliated with TypeSafe. <sub>(upstream description)</sub>
  <sub>`Project` · fritzprix · `Py`</sub>

- **[SystemOneDotNet](https://github.com/JabbaKadabra/SystemOneDotNet)** — .NET client for TypeSafe System One (Jev) — typed questions in, typed answers with probabilities and confidence out. No prompt engineering, no output parsing. <sub>(upstream description)</sub>
  <sub>`SDK` · jabbakadabra · `C#`</sub>

- **[tempo-jev-demo](https://github.com/mychaelangelo/tempo-jev-demo)** — A natural-language task workspace comparing performance across AI models (TypeSafe's Jev, GPT-5.6 Luna, and Gemini 3.8 Flash) <sub>(upstream description)</sub>
  <sub>`Project` · mychaelangelo · `TS`</sub>

- **[tinyjev](https://github.com/ankit-aglawe/tinyjev)** — A tiny jev-like model that answers Choice, Score and Noul questions in one forward pass and returns calibrated probabilities. MLX or PyTorch, fully offline, System One compatible. <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · ankit-aglawe · `Py` · ⚠ `not Jev itself`</sub>

- **[tinyjevclient](https://github.com/tinyhumansai/tinyjevclient)** — An integration with jev by typesafe.ai in Rust
  <sub>`Integration` · tinyhumansai · `Rs`</sub>

- **[Tracing Jev calls with Langfuse](https://langfuse.com/integrations/model-providers/typesafe)** — The only platform with dedicated Jev observability: an OpenInference instrumentor that traces every decision call over OpenTelemetry.
  <sub>`Integration` · `Py` · `choice` · `score` · `noul`</sub>

- **[trade-jev](https://github.com/justinhe16/trade-jev)** — Backtest Jev (TypeSafe) as a BUY/SELL/HOLD trader on NQ L10 order-book data <sub>(upstream description)</sub>
  <sub>`Project` · justinhe16 · `Py`</sub>

- **[typesafe](https://github.com/mattneel/typesafe)** — An idiomatic Elixir client for the TypeSafe AI API <sub>(upstream description)</sub>
  <sub>`SDK` · mattneel · `Ex`</sub>

- **[TypeSafe AI Jev now available on AI Gateway](https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway)** — Vercel's launch note for Jev on AI Gateway, with an experimental_evaluate sample using the model string typesafe-ai/jev.
  <sub>`Integration` · `TS` · `noul`</sub>

- **[TypeSafe models in Pydantic AI](https://pydantic.dev/docs/ai/models/typesafe/)** — First-party Pydantic AI support: an Agent with output_type=bool over the typesafe:jev-latest model string.
  <sub>`Integration` · `Py`</sub>

- **[TypeSafe pass-through on LiteLLM](https://docs.litellm.ai/docs/pass_through/typesafe)** — Proxy Jev through LiteLLM for unified keys and cost tracking, with any path under /typesafe/ passed straight through.
  <sub>`Integration` · `sh`</sub>

- **[typesafe-ai-go](https://github.com/kisshan13/typesafe-ai-go)** — Community-maintained Go SDK for the TypeSafe AI System One evaluation API, with typed questions, fluent builders, retries, and examples. <sub>(upstream description)</sub>
  <sub>`SDK` · kisshan13 · `Go`</sub>

- **[typesafe-ai-java](https://github.com/jamilxt/typesafe-ai-java)** — Community-maintained Java SDK for the TypeSafe AI System One (Jev) API. Not an official TypeSafe product. <sub>(upstream description)</sub>
  <sub>`SDK` · jamilxt · `Java` · ⚠ `no licence`</sub>

- **[typesafe-ai-playground](https://github.com/markjaquith/typesafe-ai-playground)** — A playground for experiments around Jev, TypeSafe's System One model. <sub>(upstream description)</sub>
  <sub>`Project` · markjaquith · `Rs`</sub>

- **[typesafe-ai-rails](https://github.com/GenieRobot/typesafe-ai-rails)** — Community Rails integration for TypeSafe AI's System One API on the community typesafe-sdk gem: Rails configuration, persisted usage and cost telemetry, and an opt-in confidence policy for Choice and Score answers.
  <sub>`SDK` · genierobot · `Rb`</sub>

- **[typesafe-ai-rs](https://github.com/gilljon/typesafe-ai-rs)** — Independent async and blocking Rust SDK for the TypeSafe AI System One API <sub>(upstream description)</sub>
  <sub>`SDK` · gilljon · `Rs`</sub>

- **[typesafe-ai-ruby](https://github.com/hnegishi/typesafe-ai-ruby)** — Ruby client for the TypeSafe AI(Jev) System One API <sub>(upstream description)</sub>
  <sub>`SDK` · hnegishi · `Rb`</sub>

- **[typesafe-assist](https://github.com/JanOstrowka/typesafe-assist)** — Home Assistant Assist conversation agent powered by TypeSafe's Jev (System One) model <sub>(upstream description)</sub>
  <sub>`Project` · janostrowka · `Py` · ⚠ `no licence`</sub>

- **[typesafe-chess](https://github.com/TholeG/typesafe-chess)** — Chess where both players are TypeSafe's Jev model: every move is a typed Choice decision <sub>(upstream description)</sub>
  <sub>`Project` · tholeg · `JS`</sub>

- **[typesafe-client](https://github.com/JedimEmO/typesafe-client)** — Unofficial typed async Rust client for the TypeSafe System One API <sub>(upstream description)</sub>
  <sub>`SDK` · jedimemo · `Rs`</sub>

- **[typesafe-comment](https://github.com/Hexdigest123/typesafe-comment)** — Small Python package that uses typesafe.ai to evaluate code comments on certain heuristics <sub>(upstream description)</sub>
  <sub>`Project` · hexdigest123 · `Py`</sub>

- **[TypeSafe-compatible API on Vercel AI Gateway](https://vercel.com/docs/ai-gateway/sdks-and-apis/typesafe)** — Point the official TypeSafe SDK at Vercel by changing one baseURL, or call the gateway's systemone endpoint directly with cURL.
  <sub>`Integration` · `TS` · `sh` · `noul`</sub>

- **[typesafe-go](https://github.com/zhirschtritt/typesafe-go)** — Idiomatic Go SDK for the TypeSafe AI API <sub>(upstream description)</sub>
  <sub>`SDK` · zhirschtritt · `Go`</sub>

- **[typesafe-go](https://github.com/cole-gillespie/typesafe-go)** — unofficial go SDK for typesafe AI, with typed answers, retries, and context support <sub>(upstream description)</sub>
  <sub>`SDK` · cole-gillespie · `Go`</sub>

- **[typesafe-go](https://github.com/Nibir1/typesafe-go)** — A zero-dependency community Go SDK, including a static analyser that flags poorly designed questions at compile time.
  <sub>`SDK` · Nibir1 · `Go` · `choice` · `score` · `noul` · ⚠ `code untested`</sub>

- **[typesafe-go](https://github.com/Shubham510/typesafe-go)** — Unofficial Go SDK for TypeSafe AI's System One API (Jev). <sub>(upstream description)</sub>
  <sub>`SDK` · shubham510 · `Go`</sub>

- **[typesafe-jev-examples](https://github.com/rajivkuriakose/typesafe-jev-examples)** — Worked examples for TypeSafe's Jev System One decision model, runnable today through OpenRouter <sub>(upstream description)</sub>
  <sub>`Project` · rajivkuriakose · `Py`</sub>

- **[typesafe-jev-mcp](https://github.com/anasbekheit/typesafe-jev-mcp)** — MCP server exposing TypeSafe's Jev model as a typed evaluate tool. <sub>(upstream description)</sub>
  <sub>`Plugin` · anasbekheit · `Rs`</sub>

- **[typesafe-jev-tools](https://github.com/wotai-dev/typesafe-jev-tools)** — A Claude Code hook that asks whether the decision you are writing needs a model at all. Includes a measured 149-row comparison of TypeSafe Jev against Claude Haiku 4.5. <sub>(upstream description)</sub>
  <sub>`Plugin` · wotai-dev · `TS`</sub>

- **[typesafe-rs](https://github.com/AbdelStark/typesafe-rs)** — Latency-first Rust SDK for TypeSafe System One. <sub>(upstream description)</sub>
  <sub>`SDK` · abdelstark · `Rs`</sub>

- **[typesafe-sdk](https://github.com/joshmn/typesafe-sdk)** — Ruby client for typesafe.ai <sub>(upstream description)</sub>
  <sub>`SDK` · joshmn · `Rb`</sub>

- **[typesafe-sdk](https://github.com/binnash/typesafe-sdk)** — PHP & Laravel SDK for TypeSafe AI's JEV Model series <sub>(upstream description)</sub>
  <sub>`SDK` · binnash · `PHP` · ⚠ `no licence`</sub>

- **[typesafe-sdk](https://github.com/typesafe-sdk-csharp/typesafe-sdk)** — An unofficial .NET SDK for TypeSafe AI, published on NuGet, with deterministic question building and high-throughput verification.
  <sub>`SDK` · typesafe-sdk-csharp · `C#`</sub>

- **[typesafe-sdk-dotnet](https://github.com/hardkoded/typesafe-sdk-dotnet)** — Unofficial .NET port of the TypeSafe AI client SDK (typed questions & answers) <sub>(upstream description)</sub>
  <sub>`SDK` · hardkoded · `C#`</sub>

- **[typesafe-sdk-go](https://github.com/Tangerg/typesafe-sdk-go)** — Go SDK for the TypeSafe AI API — typed questions in, probability distributions out. <sub>(upstream description)</sub>
  <sub>`SDK` · tangerg · `Go`</sub>

- **[typesafe-sdk-go](https://github.com/dwisiswant0/typesafe-sdk-go)** — Go SDK for TypeSafe AI. <sub>(upstream description)</sub>
  <sub>`SDK` · dwisiswant0 · `Go`</sub>

- **[typesafe-sdk-go](https://github.com/SergeAx/typesafe-sdk-go)** — TypeSafe.AI Go SDK <sub>(upstream description)</sub>
  <sub>`SDK` · sergeax · `Go`</sub>

- **[typesafe-sdk-go](https://github.com/valksor/typesafe-sdk-go)** — Unofficial Go SDK for the TypeSafe AI System One API — 1:1 parity with the official JS and Python SDKs. Not affiliated with TypeSafe AI. <sub>(upstream description)</sub>
  <sub>`SDK` · valksor · `Go`</sub>

- **[typesafe-sdk-java](https://github.com/Premo-Cloud/typesafe-sdk-java)** — Community Java client for the TypeSafe System One API (unofficial)
  <sub>`SDK` · premo-cloud · `Java`</sub>

- **[typesafe-sdk-kotlin](https://github.com/ufec/typesafe-sdk-kotlin)** — A Kotlin SDK for TypeSafe AI, ported from the official JavaScript SDK with its deviations documented; ask typed questions about text and get typed answers back.
  <sub>`SDK` · ufec · `Kt`</sub>

- **[typesafe-sdk-php](https://github.com/Fox-Islam/typesafe-sdk-php)** — Unofficial PHP library for the TypeSafe API <sub>(upstream description)</sub>
  <sub>`SDK` · fox-islam · `PHP`</sub>

- **[typesafe-sdk-php](https://github.com/valksor/typesafe-sdk-php)** — Unofficial PHP SDK for the TypeSafe AI System One API — 1:1 parity with the official JS and Python SDKs. Not affiliated with TypeSafe AI. <sub>(upstream description)</sub>
  <sub>`SDK` · valksor · `PHP`</sub>

- **[typesafe-sdk-ruby](https://github.com/afurm/typesafe-sdk-ruby)** — Unofficial Ruby SDK for the TypeSafe AI API (Jev model) - typed questions, retries, and typed errors. Community port of typesafe-sdk-js. <sub>(upstream description)</sub>
  <sub>`SDK` · afurm · `Rb`</sub>

- **[typesafe-sdk-rust](https://github.com/codeitlikemiley/typesafe-sdk-rust)** — Rust SDK for the TypeSafe AI API <sub>(upstream description)</sub>
  <sub>`SDK` · codeitlikemiley · `Rs`</sub>

- **[typesafe-sdk-swift](https://github.com/alterhq/typesafe-sdk-swift)** — Unofficial Swift library for the TypeSafe API <sub>(upstream description)</sub>
  <sub>`SDK` · alterhq · `Swift`</sub>

- **[typesafe-sdk-swift](https://github.com/InsaneArts/typesafe-sdk-swift)** — Swift SDK for TypeSafe AI <sub>(upstream description)</sub>
  <sub>`SDK` · insanearts · `Swift`</sub>

- **[typesafe-sdk-swift](https://github.com/marandaneto/typesafe-sdk-swift)** — typesafe-sdk-js and typesafe-sdk-python port for swift <sub>(upstream description)</sub>
  <sub>`SDK` · marandaneto · `Swift`</sub>

- **[typesafe-ui](https://github.com/TypeSafeAI/typesafe-ui)** — shadcn-style reusable components and blocks for using TypeSafe AI. <sub>(upstream description)</sub>
  <sub>`Project` · bunsdev · `TS` · ⚠ `no licence`</sub>

- **[typesafe_ai](https://github.com/hfiguera/typesafe_ai)** — An Elixir client for TypeSafe AI with typed responses and bounded concurrency <sub>(upstream description)</sub>
  <sub>`SDK` · hfiguera · `Ex`</sub>

- **[typesafe_ai](https://github.com/typesend/typesafe_ai)** — Typed Elixir client for TypeSafe AI and its Jev System One model, with offline test stubs, concurrent fan-out, and atom-keyed answers. <sub>(upstream description)</sub>
  <sub>`SDK` · typesend · `Ex`</sub>

- **[typesafe_chess_eval](https://github.com/AliceRoselia/Typesafe_chess_eval)** — An evaluation of typesafe AI chess. As it turns out, the AI isn't doing really well even though chess is not a particularly open-ended game. Still, it's only a prototype and this probably wasn't optimzied for games. <sub>(upstream description)</sub>
  <sub>`Project` · aliceroselia · `Py`</sub>

- **[typesafe_sdk (Elixir)](https://github.com/nshkrdotcom/typesafe_sdk)** — An Elixir port of the official SDK.
  <sub>`SDK` · nshkrdotcom · `Ex`</sub>

- **[typesafe_sdk_ex](https://github.com/vinnie357/typesafe_sdk_ex)** — Typesafe AI SDK in Elixir using Req <sub>(upstream description)</sub>
  <sub>`SDK` · vinnie357 · `Ex`</sub>

- **[typesafeai-cli](https://github.com/maddygoround/typesafeai-cli)** — Give your AI agent a CLI companion who has access to TypeSafe AI's Jev. <sub>(upstream description)</sub>
  <sub>`Project` · maddygoround · `Py`</sub>

- **[typesafeai-dotnet-sdk](https://github.com/saibimajdi/typesafeai-dotnet-sdk)** — Community .NET SDK for the TypeSafe AI System One API — typed noul, choice, and score questions with structured, confidence-scored answers. Not affiliated with TypeSafe AI. <sub>(upstream description)</sub>
  <sub>`SDK` · saibimajdi · `C#`</sub>

- **[typesafeai-go](https://github.com/chez-shanpu/typesafeai-go)** — Go SDK for TypeSafe AI API https://docs.typesafe.ai/api <sub>(upstream description)</sub>
  <sub>`SDK` · chez-shanpu · `Go`</sub>

- **[typesafeai.net](https://github.com/Hawxy/TypeSafeAI.Net)** — .NET SDK for the TypeSafe AI platform <sub>(upstream description)</sub>
  <sub>`SDK` · hawxy · `C#`</sub>

- **[wellposed](https://github.com/suraj-phanindra/wellposed)** — Lint your jev requests before they come back confidently wrong.
  <sub>`Project` · suraj-phanindra · `JS`</sub>

- **[werr](https://github.com/pCwOrM/werr)** — Zero-memory System-1 decision engine & TypeSafe Jev wire-compatible runtime powered by Mandelbrot wave dynamics (The Zero-VRAM Gauntlet). <sub>(upstream description)</sub>
  <sub>`Jev-like alternative` · pcworm · `Py` · ⚠ `not Jev itself`</sub>

- **[what-is-jev](https://github.com/g0runmezadam/what-is-jev)** — Independent, source-linked research on TypeSafe AI's Jev (System One), with 947 rubric-scored public repositories, recurring patterns, datasets, and bilingual documentation. <sub>(upstream description)</sub>
  <sub>`Benchmark` · g0runmezadam · `Py`</sub>

- **[your-signal](https://github.com/MithrilMan/your-signal)** — Open-source BYOK Chrome extension for personal, reversible X timeline filters. <sub>(upstream description)</sub>
  <sub>`Plugin` · mithrilman · `JS`</sub>

- **[awesome-jev (yibie)](https://github.com/yibie/awesome-jev)** — Currently the most-starred sibling directory in this space.
  <sub>`Project` · ★1k+ · ⚠ `no licence`</sub>

- **[awesome-jev (heyjunpenn)](https://github.com/heyjunpenn/awesome-jev)** — The broadest sibling directory: hundreds of projects in six languages, with a README that is itself the parsed data source.
  <sub>`Project` · ★100+ · heyjunpenn</sub>

- **[awesome-jev-projects](https://github.com/logicrw/awesome-jev-projects)** — A sibling directory aiming at ecosystem breadth with commit-pinned sources, four README languages and a generated site.
  <sub>`Project` · ★100+ · logicrw</sub>

- **[A new kind of AI model from a ChatGPT inventor is thrilling developers](https://techcrunch.com/2026/09/18/a-new-kind-of-ai-model-from-a-chatgpt-inventor-is-thrilling-developers/)** — The only launch coverage with first-hand developer quotes rather than vendor figures, including a caution that interpreting the thresholds is now your job.
  <sub>`Article` · Tim Fernholz</sub>

- **[AI model "Jev" to make machines decide faster](https://www.heise.de/en/news/AI-model-Jev-to-make-machines-decide-faster-11457071.html)** — Focuses on the missing explainability — the model returns no reasoning in language — and on every published benchmark coming from the vendor.
  <sub>`Article` · Tomislav Bezmalinović</sub>

- **[Hacker News: Introducing System One Models and Jev](https://news.ycombinator.com/item?id=49717558)** — The launch thread, and the densest single collection of scepticism: unsupported RLCD claims, apples-to-oranges latency comparisons, and the deliberate absence of public benchmarks.
  <sub>`Discussion`</sub>

- **[Jev (AI model) on Wikipedia](https://en.wikipedia.org/wiki/Jev_(AI_model))** — Most useful as an index: its reference list is a fast route to the coverage worth reading.
  <sub>`Article`</sub>

- **[Jev by TypeSafe: A Decision Model for AI Agents](https://beam.ai/agentic-insights/jev-typesafe-ai-agents)** — An agent-builder's framing of where a decision model sits in an agent stack.
  <sub>`Article` · ⚠ `marketing`</sub>

- **[Jev Cuts AI Decision Costs 100x And Vercel, Cloudflare Rushed To Add It](https://www.forbes.com/sites/josipamajic/2026/09/19/jev-cuts-ai-decision-costs-100x-and-vercel-cloudflare-rushed-to-add-it/)** — Mainstream coverage of the launch and the speed with which gateways added support.
  <sub>`Article` · Josipa Majic Predin · ⚠ `vendor numbers` `paywall`</sub>

- **[Jev From TypeSafe is a New Class of AI Model that is FAST and CHEAP - But There is a Caveat!](https://youtube.com/watch?v=qdji39XXgEY)** — A review that puts the limitation in the title rather than burying it.
  <sub>`Video` · Gary Explains</sub>

- **[Jev: System One models for Prod, not God](https://www.latent.space/p/jev)** — The only long-form founder interview: why RLHF was the wrong optimisation target, why public benchmarks were withheld, and the all-synthetic data approach.
  <sub>`Discussion` · Latent Space</sub>

- **[Jev: TypeSafe's System One Model Explained](https://www.datacamp.com/blog/system-one-models-jev)** — A neutral survey of the architecture, the claimed benchmarks and the pricing, which states plainly that no large independent reproduction had surfaced.
  <sub>`Article` · Matt Crabtree</sub>

- **[jevai.org community app gallery](https://www.jevai.org/apps)** — Thirty-six community builds curated from social posts: browser agents, spreadsheet tooling, inbox search by intent, ad blocking with judgement, games and robotics.
  <sub>`Project` · ⚠ `unverified claims`</sub>

- **[jevai.org community site](https://www.jevai.org/)** — An unaffiliated community site with a playground, a preset decision API, an MCP server, downloadable skills and a gallery of community apps.
  <sub>`Project` · ⚠ `3rd-party key` `unverified claims`</sub>

- **[RLCD explained: Reinforcement Learning for Calibrated Decisions](https://systemonemodels.org/guides/rlcd-explained/)** — An independent write-up whose most useful finding is a negative one: there is no paper, no reward function, no dataset description and no reproducible evaluation for RLCD.
  <sub>`Article`</sub>

- **[TypeSafe AI debuts model for machines that plays Doom](https://www.theregister.com/ai-and-ml/2026/09/16/typesafe-ai-debuts-model-for-machines-that-plays-doom/5296711)** — The most sceptical mainstream piece: it challenges the no-hallucination framing on the grounds that a well-formed answer is not the same as a correct one.
  <sub>`Article` · Thomas Claburn</sub>

- **[TypeSafe on OpenRouter](https://openrouter.ai/typesafe)** — OpenRouter's listing for Jev, with its own model ids and the unusual pricing shape of paid input and free output.
  <sub>`Integration`</sub>

---

<sub>Generated from `catalog.json` by `scripts/build_readme.py`. Edit the catalogue, not this file.</sub>
