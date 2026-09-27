<!-- Written by scripts/build_review_queue.py from catalog.json. Edit those, not this file. -->

# Review queue · 复核队列

<sub>The Chinese on this page is model-written and has not been reviewed by a person. · 本页中文由模型撰写（机翻），未经人工审校。</sub>

Rows a script has singled out for a person to read. Each entry is a machine signal (a path, a string or a combination of fields matched a rule), not a finding about the row, and nothing on this page is written into `catalog.json`. Whoever reads a row records the decision in it, as each section says, and the row leaves this page when it is next regenerated. [status.md](status.md) publishes the counts.

脚本挑出、需要人来读的行。每一项都是机器信号（某个路径、字符串或字段组合命中了规则），不是对该行的结论，本页内容也不会写回 `catalog.json`。读过某一行的人按各节所说把判断记进该行，下次重新生成时它就会离开本页。数量见 [status.md](status.md)。

| Signal · 信号 | Rows · 行数 |
| --- | --- |
| [Evidence read from an examples directory · 证据取自 examples 目录](#examples-dir) | 22 |
| [Evidence resting on one model name or the API host · 证据只靠一个模型名或 API 主机](#single-model-name) | 76 |
| [Tool selection resting on words the keyword rules no longer count · 工具选择只靠关键词规则已不再计入的词](#tool-selection-broad-words) | 65 |
| [Overview rows with code, not yet indexed by pattern · 带代码、尚未按模式索引的 overview 行](#unsorted-overview) | 252 |

<a id="examples-dir"></a>

## Evidence read from an examples directory · 证据取自 examples 目录

The cited file sits under an `examples/` or `example/` directory and the row does not record `evidence.kind`. An SDK's examples are often its clearest call site; a project's examples can also be all it has, and say little about how it uses Jev itself. The path cannot tell which.

引用的文件位于 `examples/` 或 `example/` 目录下，而该行没有记录 `evidence.kind`。SDK 的示例往往就是最清楚的调用点；但一个项目的示例也可能是它仅有的调用，说明不了它自己如何使用 Jev。单凭路径无法判断是哪一种。

To take a row off, read the file and set `evidence.kind`: `call-site` when it is the project's own use of Jev, `example-only` when it is only an example. Citing a better file from the project's own code instead also takes it off.

移出方法：读这个文件，然后设置 `evidence.kind`——它就是项目自身对 Jev 的使用时设为 `call-site`，只是示例时设为 `example-only`。改为引用项目自身代码中更合适的文件，也会让它移出。

| Row · 行 | Kind · 类型 | Cited file · 引用的文件 | Matched · 匹配文本 |
| --- | --- | --- | --- |
| [agentgateway-guardrail](https://kydlikebtc.github.io/awesome-jev/?lang=en#agentgateway-guardrail) | `project` | [`examples/llm-guardrail-jev/guardrail.ts`](https://github.com/agentgateway/agentgateway/blob/HEAD/examples/llm-guardrail-jev/guardrail.ts) | `jev-latest` `choice` `score` |
| [ai](https://kydlikebtc.github.io/awesome-jev/?lang=en#ai) | `sdk` | [`examples/ai-functions/src/evaluate/typesafe-ai/basic.ts`](https://github.com/vercel/ai/blob/HEAD/examples/ai-functions/src/evaluate/typesafe-ai/basic.ts) | `jev-latest` |
| [celesto](https://kydlikebtc.github.io/awesome-jev/?lang=en#celesto) | `project` | [`examples/pr-review-jev/models.py`](https://github.com/CelestoAI/celesto/blob/HEAD/examples/pr-review-jev/models.py) | `api.typesafe.ai` `jev-latest` `/v1/systemone` |
| [cua-jev-use](https://kydlikebtc.github.io/awesome-jev/?lang=en#cua-jev-use) | `project` | [`libs/cua-driver/examples/jev-use/python/jev_adapter.py`](https://github.com/trycua/cua/blob/HEAD/libs/cua-driver/examples/jev-use/python/jev_adapter.py) | `typesafe_sdk` `system_one` `choice` `Choice` |
| [decision-circuits](https://kydlikebtc.github.io/awesome-jev/?lang=en#decision-circuits) | `sdk` | [`examples/02_jev_backend.py`](https://github.com/Barneyjm/decision-circuits/blob/HEAD/examples/02_jev_backend.py) | `jev-latest` |
| [discern](https://kydlikebtc.github.io/awesome-jev/?lang=en#discern) | `project` | [`examples/headline.ts`](https://github.com/doeixd/discern/blob/HEAD/examples/headline.ts) | `jev-latest` `TypeSafeClient` |
| [dspy-typesafeify](https://kydlikebtc.github.io/awesome-jev/?lang=en#dspy-typesafeify) | `project` | [`examples/typesafe_dspy_ticket_triage/run_demo.py`](https://github.com/typesafeainate/dspy-typesafeify/blob/HEAD/examples/typesafe_dspy_ticket_triage/run_demo.py) | `typesafe_sdk` `system_one` `TypeSafeClient` |
| [example-confidence-gate](https://kydlikebtc.github.io/awesome-jev/?lang=en#example-confidence-gate) | `snippet` | [`examples/02-confidence-gate/main.py`](https://github.com/kydlikebtc/awesome-jev/blob/HEAD/examples/02-confidence-gate/main.py) | `typesafe_sdk` `system_one` `Choice` |
| [example-fan-out](https://kydlikebtc.github.io/awesome-jev/?lang=en#example-fan-out) | `snippet` | [`examples/03-fan-out/main.py`](https://github.com/kydlikebtc/awesome-jev/blob/HEAD/examples/03-fan-out/main.py) | `typesafe_sdk` `system_one` `Choice` `Noul` |
| [example-three-primitives](https://kydlikebtc.github.io/awesome-jev/?lang=en#example-three-primitives) | `snippet` | [`examples/01-three-primitives/main.py`](https://github.com/kydlikebtc/awesome-jev/blob/HEAD/examples/01-three-primitives/main.py) | `typesafe_sdk` `system_one` `Choice` `Noul` |
| [example-tool-selection](https://kydlikebtc.github.io/awesome-jev/?lang=en#example-tool-selection) | `snippet` | [`examples/04-tool-selection/main.py`](https://github.com/kydlikebtc/awesome-jev/blob/HEAD/examples/04-tool-selection/main.py) | `typesafe_sdk` `system_one` `Choice` `Noul` |
| [jev-cookbook](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-cookbook) | `tutorial` | [`examples/01-customer-support-triage/triage.py`](https://github.com/paramjeetn/jev-cookbook/blob/HEAD/examples/01-customer-support-triage/triage.py) | `api.typesafe.ai` `typesafe/jev` `jev-latest` |
| [jev-harness-typesafeai](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-harness-typesafeai) | `project` | [`examples/host/jev-choice.ts`](https://github.com/TypeSafeAI/jev-harness/blob/HEAD/examples/host/jev-choice.ts) | `api.typesafe.ai` `/v1/systemone` |
| [jev-recipes](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-recipes) | `project` | [`examples/checkers/ai.mjs`](https://github.com/agencyenterprise/jev-recipes/blob/HEAD/examples/checkers/ai.mjs) | `@typesafe-ai/sdk` `TypeSafeClient` |
| [jev-skills-laguagu](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-skills-laguagu) | `plugin` | [`examples/decisions/run.mjs`](https://github.com/laguagu/jev-skills/blob/HEAD/examples/decisions/run.mjs) | `api.typesafe.ai` `@typesafe-ai/sdk` `systemOne` |
| [jevlang-timmikeladze](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevlang-timmikeladze) | `sdk` | [`examples/entity-alignment.js`](https://github.com/TimMikeladze/JevLang/blob/HEAD/examples/entity-alignment.js) | `jev-1.13` |
| [metacog](https://kydlikebtc.github.io/awesome-jev/?lang=en#metacog) | `project` | [`examples/jev_best_of_n.py`](https://github.com/ItIsCuthNotCup/MetaCog/blob/HEAD/examples/jev_best_of_n.py) | `api.typesafe.ai` |
| [openrouter-jev-mcp](https://kydlikebtc.github.io/awesome-jev/?lang=en#openrouter-jev-mcp) | `plugin` | [`examples/demo_typesafe_sdk.py`](https://github.com/ctmx/openrouter-jev-mcp/blob/HEAD/examples/demo_typesafe_sdk.py) | `typesafe_sdk` `system_one` `TypeSafeClient` |
| [public-browser](https://kydlikebtc.github.io/awesome-jev/?lang=en#public-browser) | `plugin` | [`examples/jev-loop.mjs`](https://github.com/Silbercue/public-browser/blob/HEAD/examples/jev-loop.mjs) | `typesafe-ai/jev` |
| [spring-ai-typesafe](https://kydlikebtc.github.io/awesome-jev/?lang=en#spring-ai-typesafe) | `integration` | [`examples/src/main/java/org/springaicommunity/typesafe/demo/JevQuickstart.java`](https://github.com/spring-ai-community/spring-ai-typesafe/blob/HEAD/examples/src/main/java/org/springaicommunity/typesafe/demo/JevQuickstart.java) | `systemOne` `TypeSafeClient` `Noul` `choice` |
| [typesafe-ai](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-ai) | `sdk` | [`examples/tsg/main.rs`](https://github.com/Twister915/typesafe-ai/blob/HEAD/examples/tsg/main.rs) | `api.typesafe.ai` `jev-latest` |
| [typesafeai-dotnet-sdk](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafeai-dotnet-sdk) | `sdk` | [`examples/TypeSafe.BureauOfBadIdeas/Program.cs`](https://github.com/saibimajdi/typesafeai-dotnet-sdk/blob/HEAD/examples/TypeSafe.BureauOfBadIdeas/Program.cs) | `TypeSafeClient` |

<a id="single-model-name"></a>

## Evidence resting on one model name or the API host · 证据只靠一个模型名或 API 主机

The only string in `evidence.matched` is one of `jev-latest`, `jev-1.13`, `typesafe-ai/jev`, `typesafe/jev`, `api.typesafe.ai`. Any file that configures Jev contains one of them (a settings file, a pricing table, a model list) whether or not it calls the API, so the weekly text check can keep passing after the call itself is gone.

`evidence.matched` 里唯一的字符串是 `jev-latest`, `jev-1.13`, `typesafe-ai/jev`, `typesafe/jev`, `api.typesafe.ai` 之一。任何配置 Jev 的文件都会包含它们（设置文件、价格表、模型列表），不论是否真的调用 API；所以即使调用本身已经删除，每周的文本检查也可能继续通过。

To take a row off, add a second string from the call itself (an import, the method called, a question type) to `evidence.matched`, then run `python3 scripts/verify_claims.py --only <slug>` to confirm the file holds every string.

移出方法：从调用本身再取一个字符串（import、被调用的方法、问题类型）加入 `evidence.matched`，然后运行 `python3 scripts/verify_claims.py --only <slug>`，确认文件含有每一个字符串。

| Row · 行 | Kind · 类型 | Cited file · 引用的文件 | Matched · 匹配文本 |
| --- | --- | --- | --- |
| [a3m-router](https://kydlikebtc.github.io/awesome-jev/?lang=en#a3m-router) | `project` | [`dist/routing/jev/remote.d.ts`](https://github.com/Das-rebel/a3m-router/blob/HEAD/dist/routing/jev/remote.d.ts) | `api.typesafe.ai` |
| [ai](https://kydlikebtc.github.io/awesome-jev/?lang=en#ai) | `sdk` | [`examples/ai-functions/src/evaluate/typesafe-ai/basic.ts`](https://github.com/vercel/ai/blob/HEAD/examples/ai-functions/src/evaluate/typesafe-ai/basic.ts) | `jev-latest` |
| [bes-kelime-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#bes-kelime-jev) | `project` | [`src/jev.ts`](https://github.com/mahmut-gundogdu/bes-kelime-jev/blob/HEAD/src/jev.ts) | `typesafe-ai/jev` |
| [cua-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#cua-jev) | `project` | [`src/cua_jev/cost.py`](https://github.com/ZJU-REAL/CUA-JEV/blob/HEAD/src/cua_jev/cost.py) | `jev-1.13` |
| [decide-mcp](https://kydlikebtc.github.io/awesome-jev/?lang=en#decide-mcp) | `sdk` | [`src/config.ts`](https://github.com/dakdevs/decide-mcp/blob/HEAD/src/config.ts) | `typesafe-ai/jev` |
| [decision-circuits](https://kydlikebtc.github.io/awesome-jev/?lang=en#decision-circuits) | `sdk` | [`examples/02_jev_backend.py`](https://github.com/Barneyjm/decision-circuits/blob/HEAD/examples/02_jev_backend.py) | `jev-latest` |
| [dinostomp](https://kydlikebtc.github.io/awesome-jev/?lang=en#dinostomp) | `project` | [`audits/xstest-refusal-guards/compare.py`](https://github.com/collapseindex/dinostomp/blob/HEAD/audits/xstest-refusal-guards/compare.py) | `jev-latest` |
| [dsh-jev-buberlo](https://kydlikebtc.github.io/awesome-jev/?lang=en#dsh-jev-buberlo) | `plugin` | [`packages/dsh-jev/src/config.ts`](https://github.com/buberlo/dsh-jev/blob/HEAD/packages/dsh-jev/src/config.ts) | `jev-latest` |
| [dsh-plugin-jev-effort-selector](https://kydlikebtc.github.io/awesome-jev/?lang=en#dsh-plugin-jev-effort-selector) | `plugin` | [`lib/client.js`](https://github.com/justhalfbit/dsh-plugin-jev-effort-selector/blob/HEAD/lib/client.js) | `jev-latest` |
| [eutrya](https://kydlikebtc.github.io/awesome-jev/?lang=en#eutrya) | `project` | [`bin/eutrya.mjs`](https://github.com/hellozenstrategist-lab/eutrya/blob/HEAD/bin/eutrya.mjs) | `typesafe-ai/jev` |
| [flue-jev-demo](https://kydlikebtc.github.io/awesome-jev/?lang=en#flue-jev-demo) | `project` | [`src/flue-jev.ts`](https://github.com/matthewp/flue-jev-demo/blob/HEAD/src/flue-jev.ts) | `typesafe/jev` |
| [go-system-one](https://kydlikebtc.github.io/awesome-jev/?lang=en#go-system-one) | `sdk` | [`docs/benchmarks/data/jevbench-public-20260923/protocol/aggregate.py`](https://github.com/rcarmo/go-system-one/blob/HEAD/docs/benchmarks/data/jevbench-public-20260923/protocol/aggregate.py) | `jev-1.13` |
| [instruct-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#instruct-jev) | `project` | [`DeckerGUI_JEV-CorpusDGUI/build_instruct_jev.py`](https://github.com/ctaxnagomi/instruct-jev/blob/HEAD/DeckerGUI_JEV-CorpusDGUI/build_instruct_jev.py) | `jev-latest` |
| [jev-ai-sdk-form-router](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-ai-sdk-form-router) | `project` | [`components/routing-result.tsx`](https://github.com/vercel-labs/jev-ai-sdk-form-router/blob/HEAD/components/routing-result.tsx) | `typesafe-ai/jev` |
| [jev-align-caiovicentino](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-align-caiovicentino) | `project` | [`src/jev.mjs`](https://github.com/caiovicentino/jev-align/blob/HEAD/src/jev.mjs) | `typesafe-ai/jev` |
| [jev-autopilot](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-autopilot) | `project` | [`server/pilot.ts`](https://github.com/arielweinberger/jev-autopilot/blob/HEAD/server/pilot.ts) | `jev-latest` |
| [jev-bot-bl888m](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-bot-bl888m) | `project` | [`jev_bot/jev.py`](https://github.com/bl888m/jev-bot/blob/HEAD/jev_bot/jev.py) | `api.typesafe.ai` |
| [jev-browser](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-browser) | `project` | [`src/index.ts`](https://github.com/jkudish/jev-browser/blob/HEAD/src/index.ts) | `jev-latest` |
| [jev-browser-openqa-cn](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-browser-openqa-cn) | `plugin` | [`src/jev.ts`](https://github.com/openqa-cn/jev-browser/blob/HEAD/src/jev.ts) | `jev-latest` |
| [jev-calculator](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-calculator) | `project` | [`shared/protocol.ts`](https://github.com/pc418/jev-calculator/blob/HEAD/shared/protocol.ts) | `jev-1.13` |
| [jev-carryforward](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-carryforward) | `plugin` | [`src/gateway.ts`](https://github.com/Dharundp6/jev-carryforward/blob/HEAD/src/gateway.ts) | `typesafe-ai/jev` |
| [jev-code](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-code) | `plugin` | [`integrations/opencode/jev.ts`](https://github.com/FrancoisChastel/jev-code/blob/HEAD/integrations/opencode/jev.ts) | `jev-latest` |
| [jev-compaction](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-compaction) | `project` | [`hermes-compact.mjs`](https://github.com/picaye/jev-compaction/blob/HEAD/hermes-compact.mjs) | `jev-latest` |
| [jev-dev](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-dev) | `project` | [`scripts/probe-jev.ts`](https://github.com/n-yokomachi/jev-dev/blob/HEAD/scripts/probe-jev.ts) | `typesafe-ai/jev` |
| [jev-document-classification](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-document-classification) | `project` | [`server/classification-cache.ts`](https://github.com/Charlyhno-eng/jev-document-classification/blob/HEAD/server/classification-cache.ts) | `typesafe-ai/jev` |
| [jev-does-not-play-dice](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-does-not-play-dice) | `benchmark` | [`src/run.mjs`](https://github.com/KantaHayashiAI/jev-does-not-play-dice/blob/HEAD/src/run.mjs) | `typesafe-ai/jev` |
| [jev-eval-shogo-nfrealmusic](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-eval-shogo-nfrealmusic) | `benchmark` | [`src/jev.ts`](https://github.com/Shogo-nfrealmusic/jev-eval/blob/HEAD/src/jev.ts) | `typesafe-ai/jev` |
| [jev-feels](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-feels) | `project` | [`lib/jev/client.rb`](https://github.com/Qew7/jev-feels/blob/HEAD/lib/jev/client.rb) | `jev-latest` |
| [jev-grug](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-grug) | `project` | [`lib/jev.ts`](https://github.com/mkotlikov/jev-grug/blob/HEAD/lib/jev.ts) | `jev-latest` |
| [jev-harness](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-harness) | `project` | [`demos/proof/row-filter/run.ts`](https://github.com/AntonioCoppe/jev-harness/blob/HEAD/demos/proof/row-filter/run.ts) | `jev-latest` |
| [jev-java-gudcks0305](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-java-gudcks0305) | `sdk` | [`jev-cloudflare/src/main/java/io/github/gudcks0305/jev/cloudflare/CloudflareJevClient.java`](https://github.com/gudcks0305/jev-java/blob/HEAD/jev-cloudflare/src/main/java/io/github/gudcks0305/jev/cloudflare/CloudflareJevClient.java) | `typesafe/jev` |
| [jev-jp-address](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-jp-address) | `sdk` | [`src/jev.ts`](https://github.com/smasato/jev-jp-address/blob/HEAD/src/jev.ts) | `jev-latest` |
| [jev-mail](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mail) | `plugin` | [`src/common/jev.js`](https://github.com/muhammedilyasy/jev-mail/blob/HEAD/src/common/jev.js) | `jev-1.13` |
| [jev-model-router-az9713](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-model-router-az9713) | `project` | [`probe.mjs`](https://github.com/az9713/jev-model-router/blob/HEAD/probe.mjs) | `typesafe-ai/jev` |
| [jev-ood-calibration](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-ood-calibration) | `benchmark` | [`scripts/jev_eval.mjs`](https://github.com/scienthoon/jev-ood-calibration/blob/HEAD/scripts/jev_eval.mjs) | `typesafe-ai/jev` |
| [jev-paint](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-paint) | `project` | [`web/jev.mjs`](https://github.com/achimala/jev-paint/blob/HEAD/web/jev.mjs) | `jev-latest` |
| [jev-playground-hegargarcia](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-playground-hegargarcia) | `benchmark` | [`src/app/api/connect-four/move/route.ts`](https://github.com/hegargarcia/jev-playground/blob/HEAD/src/app/api/connect-four/move/route.ts) | `typesafe-ai/jev` |
| [jev-pong](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-pong) | `project` | [`lib/compare/compare-models.ts`](https://github.com/ably-labs/jev-pong/blob/HEAD/lib/compare/compare-models.ts) | `typesafe-ai/jev` |
| [jev-report](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-report) | `project` | [`figs.py`](https://github.com/HackSing/jev-report/blob/HEAD/figs.py) | `jev-1.13` |
| [jev-tool-permissions](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-tool-permissions) | `sdk` | [`src/types.ts`](https://github.com/NicolasMontone/jev-tool-permissions/blob/HEAD/src/types.ts) | `typesafe-ai/jev` |
| [jev-tool-router](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-tool-router) | `plugin` | [`scripts/setup-codex.mjs`](https://github.com/jackbarunz/jev-tool-router/blob/HEAD/scripts/setup-codex.mjs) | `typesafe-ai/jev` |
| [jev-trader](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-trader) | `project` | [`src/config.ts`](https://github.com/jarrodwatts/jev-trader/blob/HEAD/src/config.ts) | `jev-latest` |
| [jev-tree](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-tree) | `project` | [`benchmarks/run.mjs`](https://github.com/reachjalil/jev-tree/blob/HEAD/benchmarks/run.mjs) | `typesafe-ai/jev` |
| [jevgate](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevgate) | `project` | [`src/auth/provider.rs`](https://github.com/Tech-Byte-Frontier/jevgate/blob/HEAD/src/auth/provider.rs) | `api.typesafe.ai` |
| [jevgraph](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevgraph) | `project` | [`src/jevgraph/benchmark.py`](https://github.com/chenmingtang830/jevgraph/blob/HEAD/src/jevgraph/benchmark.py) | `typesafe-ai/jev` |
| [jevlang-timmikeladze](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevlang-timmikeladze) | `sdk` | [`examples/entity-alignment.js`](https://github.com/TimMikeladze/JevLang/blob/HEAD/examples/entity-alignment.js) | `jev-1.13` |
| [jevlogs](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevlogs) | `project` | [`benchmarks/pager/run-jev-v2.mjs`](https://github.com/reachjalil/jevlogs/blob/HEAD/benchmarks/pager/run-jev-v2.mjs) | `typesafe-ai/jev` |
| [jevloop](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevloop) | `project` | [`bench/compare.ts`](https://github.com/zjunlp/JevLoop/blob/HEAD/bench/compare.ts) | `api.typesafe.ai` |
| [jevmory](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevmory) | `project` | [`jevmory/cli.py`](https://github.com/romiluz13/jevmory/blob/HEAD/jevmory/cli.py) | `api.typesafe.ai` |
| [jevocks](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevocks) | `project` | [`src/lib/classify.ts`](https://github.com/unicodeveloper/jevocks/blob/HEAD/src/lib/classify.ts) | `typesafe-ai/jev` |
| [jevtape](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevtape) | `project` | [`src/main/java/io/jevtape/cassette/RecordedRequest.java`](https://github.com/Hugo-DDT/JevTape/blob/HEAD/src/main/java/io/jevtape/cassette/RecordedRequest.java) | `jev-latest` |
| [json-render](https://kydlikebtc.github.io/awesome-jev/?lang=en#json-render) | `project` | [`apps/web/lib/jev/compose.ts`](https://github.com/vercel-labs/json-render/blob/HEAD/apps/web/lib/jev/compose.ts) | `typesafe-ai/jev` |
| [kody](https://kydlikebtc.github.io/awesome-jev/?lang=en#kody) | `plugin` | [`packages/worker/src/mcp/tools/search-jev-rerank.ts`](https://github.com/kentcdodds/kody/blob/HEAD/packages/worker/src/mcp/tools/search-jev-rerank.ts) | `typesafe/jev` |
| [metacog](https://kydlikebtc.github.io/awesome-jev/?lang=en#metacog) | `project` | [`examples/jev_best_of_n.py`](https://github.com/ItIsCuthNotCup/MetaCog/blob/HEAD/examples/jev_best_of_n.py) | `api.typesafe.ai` |
| [mobile-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#mobile-jev) | `project` | [`apps/jev-studio/app/components/use-studio.ts`](https://github.com/droidrun/mobile-jev/blob/HEAD/apps/jev-studio/app/components/use-studio.ts) | `jev-latest` |
| [oko](https://kydlikebtc.github.io/awesome-jev/?lang=en#oko) | `plugin` | [`scripts/benchmark-public/replay/replay.py`](https://github.com/bartlomein/oko/blob/HEAD/scripts/benchmark-public/replay/replay.py) | `jev-1.13` |
| [open-spark-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#open-spark-jev) | `project` | [`open_spark_jev/eval/speed_vs_generation.py`](https://github.com/abhishek085/open-spark-jev/blob/HEAD/open_spark_jev/eval/speed_vs_generation.py) | `jev-latest` |
| [openwork](https://kydlikebtc.github.io/awesome-jev/?lang=en#openwork) | `alternative` | [`.github/scripts/jev-test-coverage-review.mjs`](https://github.com/different-ai/openwork/blob/HEAD/.github/scripts/jev-test-coverage-review.mjs) | `typesafe-ai/jev` |
| [padflow-jev-evals](https://kydlikebtc.github.io/awesome-jev/?lang=en#padflow-jev-evals) | `benchmark` | [`scripts/run_baseline.py`](https://github.com/zsavage8/padflow-jev-evals/blob/HEAD/scripts/run_baseline.py) | `api.typesafe.ai` |
| [pagegrade](https://kydlikebtc.github.io/awesome-jev/?lang=en#pagegrade) | `project` | [`lib/jev.ts`](https://github.com/kitze/pagegrade/blob/HEAD/lib/jev.ts) | `typesafe-ai/jev` |
| [pg-typesafe](https://kydlikebtc.github.io/awesome-jev/?lang=en#pg-typesafe) | `plugin` | [`sql/typesafe.sql`](https://github.com/giuliosmall/pg_typesafe/blob/HEAD/sql/typesafe.sql) | `jev-latest` |
| [pi-jev-router](https://kydlikebtc.github.io/awesome-jev/?lang=en#pi-jev-router) | `project` | [`index.ts`](https://github.com/mejiasd3v/pi-jev-router/blob/HEAD/index.ts) | `typesafe-ai/jev` |
| [plugins](https://kydlikebtc.github.io/awesome-jev/?lang=en#plugins) | `plugin` | [`plugins/jev-browser/src/jev-model.ts`](https://github.com/cline/plugins/blob/HEAD/plugins/jev-browser/src/jev-model.ts) | `typesafe-ai/jev` |
| [profanity-checker](https://kydlikebtc.github.io/awesome-jev/?lang=en#profanity-checker) | `project` | [`src/endpoints/profanityCheck.ts`](https://github.com/4rays/profanity-checker/blob/HEAD/src/endpoints/profanityCheck.ts) | `typesafe/jev` |
| [public-browser](https://kydlikebtc.github.io/awesome-jev/?lang=en#public-browser) | `plugin` | [`examples/jev-loop.mjs`](https://github.com/Silbercue/public-browser/blob/HEAD/examples/jev-loop.mjs) | `typesafe-ai/jev` |
| [robo-harness](https://kydlikebtc.github.io/awesome-jev/?lang=en#robo-harness) | `project` | [`apps/server/src/decision/jev.ts`](https://github.com/grmkris/robo-harness/blob/HEAD/apps/server/src/decision/jev.ts) | `typesafe-ai/jev` |
| [search-function-test](https://kydlikebtc.github.io/awesome-jev/?lang=en#search-function-test) | `project` | [`htr-hero/src/lib/typesafeSearch.js`](https://github.com/Shifros/Search-Function-Test/blob/HEAD/htr-hero/src/lib/typesafeSearch.js) | `jev-latest` |
| [secondlayer](https://kydlikebtc.github.io/awesome-jev/?lang=en#secondlayer) | `project` | [`scripts/ops/jev-fault-triage.ts`](https://github.com/ryanwaits/secondlayer/blob/HEAD/scripts/ops/jev-fault-triage.ts) | `typesafe-ai/jev` |
| [shady-town](https://kydlikebtc.github.io/awesome-jev/?lang=en#shady-town) | `project` | [`lib/shady_town/evaluator.rb`](https://github.com/tpaulshippy/shady-town/blob/HEAD/lib/shady_town/evaluator.rb) | `jev-latest` |
| [smithers](https://kydlikebtc.github.io/awesome-jev/?lang=en#smithers) | `project` | [`apps/server/src/jev.ts`](https://github.com/smithersai/smithers/blob/HEAD/apps/server/src/jev.ts) | `typesafe-ai/jev` |
| [super-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#super-jev) | `project` | [`skills/super-jev/superjev.py`](https://github.com/Kevthetech143/super-jev/blob/HEAD/skills/super-jev/superjev.py) | `jev-1.13` |
| [tripwire](https://kydlikebtc.github.io/awesome-jev/?lang=en#tripwire) | `integration` | [`src/judge/jev.ts`](https://github.com/noelzappy/tripwire/blob/HEAD/src/judge/jev.ts) | `jev-latest` |
| [typesafe-playground-typesafeai](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-playground-typesafeai) | `project` | [`lib/callJev.ts`](https://github.com/TypeSafeAI/typesafe-playground/blob/HEAD/lib/callJev.ts) | `jev-latest` |
| [typesafe-ui](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-ui) | `project` | [`apps/web/components/demos.tsx`](https://github.com/TypeSafeAI/typesafe-ui/blob/HEAD/apps/web/components/demos.tsx) | `jev-latest` |
| [wakegate](https://kydlikebtc.github.io/awesome-jev/?lang=en#wakegate) | `project` | [`src/index.ts`](https://github.com/shitianfang/wakegate/blob/HEAD/src/index.ts) | `typesafe-ai/jev` |
| [yoshi](https://kydlikebtc.github.io/awesome-jev/?lang=en#yoshi) | `plugin` | [`benchmarks/jev-calibrate.ts`](https://github.com/compozy/yoshi/blob/HEAD/benchmarks/jev-calibrate.ts) | `typesafe-ai/jev` |

<a id="tool-selection-broad-words"></a>

## Tool selection resting on words the keyword rules no longer count · 工具选择只靠关键词规则已不再计入的词

The row carries `tool-selection`, and the keyword rules suggest it for the row's summary and title only as they stood until 2026-09-27. They then counted "control", "harness" and "screen" on their own, and "robot", "autonomous" and "drive" with no word for deciding or acting beside them; the rules in `scripts/classify.py` no longer do. The bulk passes took the rules' patterns, so a row here may never have been read against tool-selection, or a person may have agreed with it without recording so. The rules read a project's GitHub description at discovery; the summary stands in for it here.

该行带有 `tool-selection`，而关键词规则只有按 2026-09-27 之前的写法才会从它的摘要和标题建议这个模式。当时的规则单凭 "control"、"harness"、"screen" 就算数，"robot"、"autonomous"、"drive" 旁边没有表示决定或动作的词也算数；`scripts/classify.py` 里现在的规则不再这样。批量收录时直接采用了规则给出的模式，所以这里的行可能从未有人对照 tool-selection 读过，也可能有人读过并同意，只是没有记录。规则在发现阶段读的是项目的 GitHub 描述；这里以摘要代替。

To take a row off, read the project against [`tool-selection`](patterns.md#tool-selection). If nothing in it decides which tool or action comes next, replace `tool-selection` in `patterns` with the pattern it does show, or with `overview`. Either way, set `patterns_reviewed` to the date you read it; that alone takes off a row whose `tool-selection` was right.

移出方法：对照 [`tool-selection`](patterns.md#tool-selection) 阅读该项目。如果其中没有任何东西在决定下一步调用哪个工具或采取哪个动作，就把 `patterns` 里的 `tool-selection` 换成它实际体现的模式，或换成 `overview`。无论哪种情况，都把阅读日期写入 `patterns_reviewed`；`tool-selection` 本来就对的行，只写这个日期也会移出。

| Row · 行 | Stars · 星标 | Patterns in the row · 该行的模式 | Suggested until 2026-09-27 · 2026-09-27 之前的建议 | Suggested now · 现在的建议 |
| --- | --- | --- | --- | --- |
| [agent](https://kydlikebtc.github.io/awesome-jev/?lang=en#agent) | ★100+ | `tool-selection` | `tool-selection` | `overview` |
| [interlinked-cli](https://kydlikebtc.github.io/awesome-jev/?lang=en#interlinked-cli) | ★100+ | `tool-selection` | `tool-selection` | `overview` |
| [jev-dsh-decision](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-dsh-decision) | ★100+ | `tool-selection` | `tool-selection` | `overview` |
| [jevharness](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevharness) | ★100+ | `tool-selection` | `tool-selection` | `overview` |
| [omg-dev](https://kydlikebtc.github.io/awesome-jev/?lang=en#omg-dev) | ★100+ | `tool-selection` | `tool-selection` | `overview` |
| [systemoneharness](https://kydlikebtc.github.io/awesome-jev/?lang=en#systemoneharness) | ★100+ | `tool-selection` | `tool-selection` | `overview` |
| [azdaja](https://kydlikebtc.github.io/awesome-jev/?lang=en#azdaja) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [discern](https://kydlikebtc.github.io/awesome-jev/?lang=en#discern) | ★10+ | `tool-selection` `human-escalation` | `tool-selection` `human-escalation` | `human-escalation` |
| [dsh-jev-buberlo](https://kydlikebtc.github.io/awesome-jev/?lang=en#dsh-jev-buberlo) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [eutrya](https://kydlikebtc.github.io/awesome-jev/?lang=en#eutrya) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [jcr](https://kydlikebtc.github.io/awesome-jev/?lang=en#jcr) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [jev-agent-design-with-topk-logits-choices](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-agent-design-with-topk-logits-choices) | ★10+ | `tool-selection` | `tool-selection` `content-scoring` | `content-scoring` |
| [jev-autopilot](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-autopilot) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [jev-cua](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-cua) | ★10+ | `tool-selection` `output-validation` | `tool-selection` `output-validation` | `output-validation` |
| [jev-harness](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-harness) | ★10+ | `tool-selection` `safety-gating` `human-escalation` | `tool-selection` `safety-gating` `human-escalation` | `safety-gating` `human-escalation` |
| [jev-libero](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-libero) | ★10+ | `tool-selection` `output-validation` | `tool-selection` `output-validation` | `output-validation` |
| [jev-mem](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mem) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [jev-use-savka777](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-use-savka777) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [jevalyn](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevalyn) | ★10+ | `tool-selection` `content-scoring` `human-escalation` | `tool-selection` `content-scoring` `human-escalation` | `content-scoring` `human-escalation` |
| [jevgpt](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevgpt) | ★10+ | `tool-selection` `content-scoring` | `tool-selection` `content-scoring` | `content-scoring` |
| [live-jev-okinaaudio](https://kydlikebtc.github.io/awesome-jev/?lang=en#live-jev-okinaaudio) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [mario-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#mario-jev) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [robojev](https://kydlikebtc.github.io/awesome-jev/?lang=en#robojev) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [smartmoney-cub](https://kydlikebtc.github.io/awesome-jev/?lang=en#smartmoney-cub) | ★10+ | `tool-selection` `output-validation` `content-scoring` | `tool-selection` `output-validation` `content-scoring` | `output-validation` `content-scoring` |
| [super-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#super-jev) | ★10+ | `tool-selection` | `tool-selection` | `overview` |
| [agi-jev-containment](https://kydlikebtc.github.io/awesome-jev/?lang=en#agi-jev-containment) |  | `classification` `tool-selection` `safety-gating` | `classification` `tool-selection` `safety-gating` | `classification` `safety-gating` `human-escalation` |
| [casse-brique-typesafe](https://kydlikebtc.github.io/awesome-jev/?lang=en#casse-brique-typesafe) |  | `tool-selection` | `tool-selection` | `overview` |
| [datajev](https://kydlikebtc.github.io/awesome-jev/?lang=en#datajev) |  | `tool-selection` `output-validation` | `tool-selection` `output-validation` | `output-validation` |
| [deepseek-harness-jev-pre-compaction](https://kydlikebtc.github.io/awesome-jev/?lang=en#deepseek-harness-jev-pre-compaction) |  | `tool-selection` `context-compaction` | `tool-selection` `context-compaction` | `context-compaction` |
| [dsh-jev-zhangxaochen](https://kydlikebtc.github.io/awesome-jev/?lang=en#dsh-jev-zhangxaochen) |  | `tool-selection` | `tool-selection` | `overview` |
| [dsh-jev-prune](https://kydlikebtc.github.io/awesome-jev/?lang=en#dsh-jev-prune) |  | `tool-selection` `content-scoring` `context-compaction` | `tool-selection` `content-scoring` `context-compaction` | `content-scoring` `context-compaction` `document-triage` |
| [dsh-jev-verify](https://kydlikebtc.github.io/awesome-jev/?lang=en#dsh-jev-verify) |  | `tool-selection` `output-validation` `content-scoring` | `tool-selection` `output-validation` `content-scoring` | `output-validation` `content-scoring` |
| [fast-compaction-dsh](https://kydlikebtc.github.io/awesome-jev/?lang=en#fast-compaction-dsh) |  | `tool-selection` `context-compaction` | `tool-selection` `context-compaction` | `context-compaction` |
| [gg-friggin-ez](https://kydlikebtc.github.io/awesome-jev/?lang=en#gg-friggin-ez) |  | `tool-selection` | `tool-selection` | `overview` |
| [hearth-jev-rental-search](https://kydlikebtc.github.io/awesome-jev/?lang=en#hearth-jev-rental-search) |  | `tool-selection` | `tool-selection` | `overview` |
| [jev-agent-skill](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-agent-skill) |  | `classification` `tool-selection` `output-validation` | `classification` `tool-selection` `output-validation` | `classification` `output-validation` `content-scoring` |
| [jev-behavior-study](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-behavior-study) |  | `tool-selection` `output-validation` | `tool-selection` `output-validation` | `output-validation` |
| [jev-certify](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-certify) |  | `tool-selection` `safety-gating` `content-scoring` | `tool-selection` `safety-gating` `content-scoring` | `safety-gating` `content-scoring` `human-escalation` |
| [jev-codex-pilot](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-codex-pilot) |  | `model-routing` `tool-selection` | `model-routing` `tool-selection` | `model-routing` |
| [jev-for-engineers](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-for-engineers) |  | `classification` `tool-selection` `output-validation` | `classification` `tool-selection` `output-validation` | `classification` `output-validation` `data-extraction` |
| [jev-harness-typesafeai](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-harness-typesafeai) |  | `tool-selection` | `tool-selection` `document-triage` | `document-triage` |
| [jev-harness-router](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-harness-router) |  | `model-routing` `tool-selection` | `model-routing` `tool-selection` | `model-routing` |
| [jev-layer](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-layer) |  | `tool-selection` `document-triage` | `tool-selection` `document-triage` | `document-triage` |
| [jev-llm-router-benchmark](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-llm-router-benchmark) |  | `tool-selection` `content-scoring` | `tool-selection` `content-scoring` | `content-scoring` |
| [jev-mobile](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mobile) |  | `tool-selection` | `tool-selection` | `overview` |
| [jev-model-tokengate](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-model-tokengate) |  | `tool-selection` `safety-gating` | `tool-selection` `safety-gating` | `safety-gating` |
| [jev-physical-ai](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-physical-ai) |  | `tool-selection` | `tool-selection` | `overview` |
| [jev-plays](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-plays) |  | `tool-selection` | `tool-selection` | `overview` |
| [jev-robotics-demo](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-robotics-demo) |  | `tool-selection` | `tool-selection` | `overview` |
| [jev-routing](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-routing) |  | `tool-selection` | `tool-selection` | `overview` |
| [jev-usecases](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-usecases) |  | `tool-selection` `safety-gating` `human-escalation` | `tool-selection` `safety-gating` `human-escalation` | `safety-gating` `human-escalation` |
| [jev-voice-control](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-voice-control) |  | `tool-selection` | `tool-selection` | `overview` |
| [jev-windows-voice](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-windows-voice) |  | `tool-selection` | `tool-selection` | `overview` |
| [jevdroid](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevdroid) |  | `tool-selection` | `tool-selection` | `overview` |
| [jevloop-parkavenue9639](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevloop-parkavenue9639) |  | `tool-selection` | `tool-selection` | `overview` |
| [jevonly](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevonly) |  | `tool-selection` | `tool-selection` | `overview` |
| [jevscape](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevscape) |  | `tool-selection` | `tool-selection` | `overview` |
| [pi-typesafe-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#pi-typesafe-jev) |  | `tool-selection` `content-scoring` `human-escalation` | `tool-selection` `content-scoring` `human-escalation` | `content-scoring` `human-escalation` |
| [ps2-ai-agent](https://kydlikebtc.github.io/awesome-jev/?lang=en#ps2-ai-agent) |  | `tool-selection` | `tool-selection` | `overview` |
| [robo-harness](https://kydlikebtc.github.io/awesome-jev/?lang=en#robo-harness) |  | `tool-selection` | `tool-selection` | `overview` |
| [slidepilot](https://kydlikebtc.github.io/awesome-jev/?lang=en#slidepilot) |  | `tool-selection` | `tool-selection` | `overview` |
| [snake-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#snake-jev) |  | `tool-selection` `fan-out` | `tool-selection` `fan-out` | `fan-out` |
| [terrarium](https://kydlikebtc.github.io/awesome-jev/?lang=en#terrarium) |  | `tool-selection` | `tool-selection` | `overview` |
| [typesafe-minecraft-demo](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-minecraft-demo) |  | `tool-selection` | `tool-selection` | `overview` |
| [zerosweep](https://kydlikebtc.github.io/awesome-jev/?lang=en#zerosweep) |  | `classification` `tool-selection` `safety-gating` | `classification` `tool-selection` `safety-gating` | `classification` `safety-gating` |

<a id="unsorted-overview"></a>

## Overview rows with code, not yet indexed by pattern · 带代码、尚未按模式索引的 overview 行

The row is a project or a plugin with code, its only pattern is `overview`, and it records no `patterns_reviewed`. `overview` is for a row that surveys the model or the space ([patterns.md](patterns.md#overview)); it is also what the keyword rules suggest when nothing matches, and the bulk passes took the rules' patterns. The READMEs, the Overview page and the site list these rows apart, as not yet indexed by pattern. The last column is only a suggestion: what the keyword rules (`scripts/classify.py`) make of the row's summary and title, and a dash when none of them matches.

该行是带代码的项目或插件，唯一的模式是 `overview`，且没有记录 `patterns_reviewed`。`overview` 本是给介绍模型或整个领域的行用的（[patterns.md](patterns.md#overview)）；它也是关键词规则什么都没匹配到时给出的建议，而批量收录时直接采用了规则给出的模式。README、Overview 页面和站点把这些行单独列为“尚未按模式索引”。最后一列只是建议：关键词规则（`scripts/classify.py`）根据该行摘要和标题给出的结果，没有任何规则匹配时显示为破折号。

To take a row off, read the project against [the patterns](patterns.md). Put the patterns it shows in `patterns`, or keep `overview` if it surveys the space, and set `patterns_reviewed` to the date you read it.

移出方法：对照[决策模式](patterns.md)阅读该项目。把它体现的模式写进 `patterns`；如果它确实是在介绍整个领域，就保留 `overview`。然后把阅读日期写入 `patterns_reviewed`。

| Row · 行 | Kind · 类型 | Stars · 星标 | Keyword rules suggest (a suggestion) · 关键词规则的建议（仅供参考） |
| --- | --- | --- | --- |
| [langchain](https://kydlikebtc.github.io/awesome-jev/?lang=en#langchain) | `project` | ★100k+ | — |
| [eliza](https://kydlikebtc.github.io/awesome-jev/?lang=en#eliza) | `project` | ★10k+ | — |
| [oh-my-pi](https://kydlikebtc.github.io/awesome-jev/?lang=en#oh-my-pi) | `project` | ★10k+ | — |
| [opik-typesafe-tracker](https://kydlikebtc.github.io/awesome-jev/?lang=en#opik-typesafe-tracker) | `project` | ★10k+ | — |
| [pydantic-ai](https://kydlikebtc.github.io/awesome-jev/?lang=en#pydantic-ai) | `project` | ★10k+ | — |
| [ax](https://kydlikebtc.github.io/awesome-jev/?lang=en#ax) | `project` | ★1k+ | — |
| [bifrost-typesafe-gateway](https://kydlikebtc.github.io/awesome-jev/?lang=en#bifrost-typesafe-gateway) | `project` | ★1k+ | `safety-gating` |
| [laya-mlx](https://kydlikebtc.github.io/awesome-jev/?lang=en#laya-mlx) | `project` | ★1k+ | — |
| [memsearch](https://kydlikebtc.github.io/awesome-jev/?lang=en#memsearch) | `plugin` | ★1k+ | — |
| [typesafe-skills-repo](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-skills-repo) | `plugin` | ★1k+ | — |
| [vellum-assistant](https://kydlikebtc.github.io/awesome-jev/?lang=en#vellum-assistant) | `project` | ★1k+ | — |
| [aiavatarkit](https://kydlikebtc.github.io/awesome-jev/?lang=en#aiavatarkit) | `project` | ★100+ | — |
| [awesome-jev-fatwang2](https://kydlikebtc.github.io/awesome-jev/?lang=en#awesome-jev-fatwang2) | `project` | ★100+ | `output-validation` |
| [celesto](https://kydlikebtc.github.io/awesome-jev/?lang=en#celesto) | `project` | ★100+ | — |
| [crush-monitor](https://kydlikebtc.github.io/awesome-jev/?lang=en#crush-monitor) | `project` | ★100+ | — |
| [dasheng](https://kydlikebtc.github.io/awesome-jev/?lang=en#dasheng) | `project` | ★100+ | — |
| [distill](https://kydlikebtc.github.io/awesome-jev/?lang=en#distill) | `project` | ★100+ | — |
| [djev-spark](https://kydlikebtc.github.io/awesome-jev/?lang=en#djev-spark) | `project` | ★100+ | — |
| [jev-chat-jarvis-mac](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-chat-jarvis-mac) | `project` | ★100+ | — |
| [jev-chat-windows](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-chat-windows) | `project` | ★100+ | — |
| [jev-experiments](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-experiments) | `project` | ★100+ | `search-ranking` `safety-gating` `output-validation` |
| [jev-skill-wuyoscar](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-skill-wuyoscar) | `plugin` | ★100+ | `output-validation` |
| [jevmind](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevmind) | `project` | ★100+ | `safety-gating` `content-scoring` `human-escalation` |
| [kody](https://kydlikebtc.github.io/awesome-jev/?lang=en#kody) | `plugin` | ★100+ | — |
| [laya](https://kydlikebtc.github.io/awesome-jev/?lang=en#laya) | `project` | ★100+ | — |
| [laya-ultrafast](https://kydlikebtc.github.io/awesome-jev/?lang=en#laya-ultrafast) | `project` | ★100+ | — |
| [openwhisper](https://kydlikebtc.github.io/awesome-jev/?lang=en#openwhisper) | `project` | ★100+ | — |
| [orchestkit](https://kydlikebtc.github.io/awesome-jev/?lang=en#orchestkit) | `plugin` | ★100+ | — |
| [pi-fabric](https://kydlikebtc.github.io/awesome-jev/?lang=en#pi-fabric) | `project` | ★100+ | — |
| [req-llm](https://kydlikebtc.github.io/awesome-jev/?lang=en#req-llm) | `project` | ★100+ | — |
| [runline](https://kydlikebtc.github.io/awesome-jev/?lang=en#runline) | `project` | ★100+ | — |
| [smithers](https://kydlikebtc.github.io/awesome-jev/?lang=en#smithers) | `project` | ★100+ | — |
| [stanley-code](https://kydlikebtc.github.io/awesome-jev/?lang=en#stanley-code) | `project` | ★100+ | — |
| [third-hand](https://kydlikebtc.github.io/awesome-jev/?lang=en#third-hand) | `project` | ★100+ | — |
| [typesafe-mcp](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-mcp) | `plugin` | ★100+ | — |
| [webctl](https://kydlikebtc.github.io/awesome-jev/?lang=en#webctl) | `project` | ★100+ | — |
| [agent-router](https://kydlikebtc.github.io/awesome-jev/?lang=en#agent-router) | `plugin` | ★10+ | — |
| [ask-jev-skill](https://kydlikebtc.github.io/awesome-jev/?lang=en#ask-jev-skill) | `plugin` | ★10+ | — |
| [call-coach-ai](https://kydlikebtc.github.io/awesome-jev/?lang=en#call-coach-ai) | `project` | ★10+ | — |
| [captaincore](https://kydlikebtc.github.io/awesome-jev/?lang=en#captaincore) | `project` | ★10+ | — |
| [clash-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#clash-jev) | `project` | ★10+ | — |
| [cultivar](https://kydlikebtc.github.io/awesome-jev/?lang=en#cultivar) | `project` | ★10+ | — |
| [dspy-typesafeify](https://kydlikebtc.github.io/awesome-jev/?lang=en#dspy-typesafeify) | `project` | ★10+ | — |
| [duckdb-jev-colliber](https://kydlikebtc.github.io/awesome-jev/?lang=en#duckdb-jev-colliber) | `plugin` | ★10+ | — |
| [is-jeven](https://kydlikebtc.github.io/awesome-jev/?lang=en#is-jeven) | `project` | ★10+ | — |
| [james-library](https://kydlikebtc.github.io/awesome-jev/?lang=en#james-library) | `project` | ★10+ | `content-scoring` |
| [jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev) | `plugin` | ★10+ | — |
| [jev-mayank953](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mayank953) | `project` | ★10+ | — |
| [jev-okooo5km](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-okooo5km) | `plugin` | ★10+ | `search-ranking` `content-scoring` `human-escalation` |
| [jev-chat-for-twitch](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-chat-for-twitch) | `plugin` | ★10+ | — |
| [jev-cli-shaharia-lab](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-cli-shaharia-lab) | `project` | ★10+ | `content-scoring` `human-escalation` |
| [jev-foundation-models](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-foundation-models) | `project` | ★10+ | — |
| [jev-judge-mcp](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-judge-mcp) | `plugin` | ★10+ | `search-ranking` `classification` `tool-selection` |
| [jev-leftpad](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-leftpad) | `project` | ★10+ | — |
| [jev-mcp-burnigtm](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mcp-burnigtm) | `plugin` | ★10+ | — |
| [jev-paint](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-paint) | `project` | ★10+ | — |
| [jev-playground-mizchi](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-playground-mizchi) | `project` | ★10+ | `content-scoring` |
| [jev-recipes](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-recipes) | `project` | ★10+ | `search-ranking` `output-validation` |
| [jev-register-tool](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-register-tool) | `project` | ★10+ | — |
| [jev-rules](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-rules) | `project` | ★10+ | — |
| [jev-seo](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-seo) | `plugin` | ★10+ | — |
| [jev-skill-suggester](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-skill-suggester) | `plugin` | ★10+ | — |
| [jev-spring-boot-starter](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-spring-boot-starter) | `plugin` | ★10+ | — |
| [jev-studio](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-studio) | `project` | ★10+ | — |
| [jev-tetris](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-tetris) | `project` | ★10+ | — |
| [jev-to-answer](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-to-answer) | `project` | ★10+ | — |
| [jev-trades](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-trades) | `project` | ★10+ | — |
| [jev-tree-chuf-h](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-tree-chuf-h) | `project` | ★10+ | `output-validation` |
| [jev-voice](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-voice) | `project` | ★10+ | — |
| [jev-vs-ml](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-vs-ml) | `project` | ★10+ | — |
| [jev-stock](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-stock) | `project` | ★10+ | — |
| [jevchat](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevchat) | `project` | ★10+ | — |
| [jevernetes](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevernetes) | `project` | ★10+ | — |
| [jevgraph](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevgraph) | `project` | ★10+ | — |
| [jeview](https://kydlikebtc.github.io/awesome-jev/?lang=en#jeview) | `project` | ★10+ | — |
| [jevify](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevify) | `plugin` | ★10+ | — |
| [jevloop](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevloop) | `project` | ★10+ | — |
| [jevocks](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevocks) | `project` | ★10+ | — |
| [jevthoven](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevthoven) | `project` | ★10+ | — |
| [jevvy](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevvy) | `plugin` | ★10+ | — |
| [jot](https://kydlikebtc.github.io/awesome-jev/?lang=en#jot) | `project` | ★10+ | — |
| [laya-vs-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#laya-vs-jev) | `project` | ★10+ | — |
| [laya-vs-jev-arena](https://kydlikebtc.github.io/awesome-jev/?lang=en#laya-vs-jev-arena) | `project` | ★10+ | — |
| [llm-typesafe](https://kydlikebtc.github.io/awesome-jev/?lang=en#llm-typesafe) | `plugin` | ★10+ | — |
| [loki](https://kydlikebtc.github.io/awesome-jev/?lang=en#loki) | `project` | ★10+ | — |
| [open-spark-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#open-spark-jev) | `project` | ★10+ | — |
| [openthai-systemone](https://kydlikebtc.github.io/awesome-jev/?lang=en#openthai-systemone) | `project` | ★10+ | — |
| [pi-quiet-ask](https://kydlikebtc.github.io/awesome-jev/?lang=en#pi-quiet-ask) | `project` | ★10+ | — |
| [st-jeved](https://kydlikebtc.github.io/awesome-jev/?lang=en#st-jeved) | `plugin` | ★10+ | — |
| [typesafe-playground](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-playground) | `project` | ★10+ | — |
| [typesafe-playground-typesafeai](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-playground-typesafeai) | `project` | ★10+ | — |
| [typesafe-skill-router](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-skill-router) | `plugin` | ★10+ | — |
| [xtags](https://kydlikebtc.github.io/awesome-jev/?lang=en#xtags) | `project` | ★10+ | — |
| [aegis-typesafe-provider](https://kydlikebtc.github.io/awesome-jev/?lang=en#aegis-typesafe-provider) | `project` |  | `safety-gating` `data-extraction` |
| [agent-jev-tetris](https://kydlikebtc.github.io/awesome-jev/?lang=en#agent-jev-tetris) | `project` |  | — |
| [ai-elo-ranker](https://kydlikebtc.github.io/awesome-jev/?lang=en#ai-elo-ranker) | `project` |  | — |
| [ailerix](https://kydlikebtc.github.io/awesome-jev/?lang=en#ailerix) | `project` |  | — |
| [alphaoptimizer](https://kydlikebtc.github.io/awesome-jev/?lang=en#alphaoptimizer) | `plugin` |  | — |
| [askjev](https://kydlikebtc.github.io/awesome-jev/?lang=en#askjev) | `plugin` |  | — |
| [askjev-mcp](https://kydlikebtc.github.io/awesome-jev/?lang=en#askjev-mcp) | `plugin` |  | `content-scoring` `human-escalation` |
| [auto-mode-for-paseo](https://kydlikebtc.github.io/awesome-jev/?lang=en#auto-mode-for-paseo) | `plugin` |  | — |
| [awesome-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#awesome-jev) | `project` |  | — |
| [awesome-jev-use-cases](https://kydlikebtc.github.io/awesome-jev/?lang=en#awesome-jev-use-cases) | `project` |  | `search-ranking` `model-routing` `safety-gating` |
| [barrunto](https://kydlikebtc.github.io/awesome-jev/?lang=en#barrunto) | `plugin` |  | — |
| [beatjev](https://kydlikebtc.github.io/awesome-jev/?lang=en#beatjev) | `project` |  | — |
| [bes-kelime-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#bes-kelime-jev) | `project` |  | — |
| [btc-jev-signal](https://kydlikebtc.github.io/awesome-jev/?lang=en#btc-jev-signal) | `project` |  | — |
| [cairn-jev-lab](https://kydlikebtc.github.io/awesome-jev/?lang=en#cairn-jev-lab) | `project` |  | — |
| [cartshield](https://kydlikebtc.github.io/awesome-jev/?lang=en#cartshield) | `project` |  | — |
| [codex-jev-preflight](https://kydlikebtc.github.io/awesome-jev/?lang=en#codex-jev-preflight) | `plugin` |  | — |
| [commentcop](https://kydlikebtc.github.io/awesome-jev/?lang=en#commentcop) | `project` |  | — |
| [cyber-breach-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#cyber-breach-jev) | `project` |  | — |
| [dbt-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#dbt-jev) | `plugin` |  | — |
| [decisions-judge-mcp](https://kydlikebtc.github.io/awesome-jev/?lang=en#decisions-judge-mcp) | `plugin` |  | `content-scoring` |
| [dgp](https://kydlikebtc.github.io/awesome-jev/?lang=en#dgp) | `project` |  | `safety-gating` `fan-out` |
| [edgejev](https://kydlikebtc.github.io/awesome-jev/?lang=en#edgejev) | `project` |  | — |
| [emoji-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#emoji-jev) | `project` |  | — |
| [everything-about-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#everything-about-jev) | `project` |  | — |
| [extremely-specific-council](https://kydlikebtc.github.io/awesome-jev/?lang=en#extremely-specific-council) | `project` |  | — |
| [financialpredictionjev](https://kydlikebtc.github.io/awesome-jev/?lang=en#financialpredictionjev) | `project` |  | — |
| [frost](https://kydlikebtc.github.io/awesome-jev/?lang=en#frost) | `project` |  | — |
| [functions](https://kydlikebtc.github.io/awesome-jev/?lang=en#functions) | `project` |  | — |
| [git-jev-stage](https://kydlikebtc.github.io/awesome-jev/?lang=en#git-jev-stage) | `project` |  | — |
| [got-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#got-jev) | `project` |  | — |
| [ha-conversation-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#ha-conversation-jev) | `project` |  | — |
| [harden-jev-decides](https://kydlikebtc.github.io/awesome-jev/?lang=en#harden-jev-decides) | `project` |  | — |
| [hermes-jev-curator](https://kydlikebtc.github.io/awesome-jev/?lang=en#hermes-jev-curator) | `project` |  | — |
| [hiresignal](https://kydlikebtc.github.io/awesome-jev/?lang=en#hiresignal) | `project` |  | — |
| [jcm-router](https://kydlikebtc.github.io/awesome-jev/?lang=en#jcm-router) | `project` |  | — |
| [jeff-cli](https://kydlikebtc.github.io/awesome-jev/?lang=en#jeff-cli) | `project` |  | `search-ranking` `content-scoring` `human-escalation` |
| [jeq](https://kydlikebtc.github.io/awesome-jev/?lang=en#jeq) | `project` |  | — |
| [jev-cobusgreyling](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-cobusgreyling) | `project` |  | — |
| [jev-2048](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-2048) | `project` |  | — |
| [jev-acp](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-acp) | `project` |  | — |
| [jev-anotacao-sentencas](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-anotacao-sentencas) | `project` |  | — |
| [jev-arena-nanojev](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-arena-nanojev) | `project` |  | — |
| [jev-blindspot](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-blindspot) | `plugin` |  | — |
| [jev-bot](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-bot) | `project` |  | — |
| [jev-broadcast-lab](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-broadcast-lab) | `project` |  | — |
| [jev-calculator](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-calculator) | `project` |  | — |
| [jev-canvas](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-canvas) | `project` |  | — |
| [jev-chat](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-chat) | `project` |  | — |
| [jev-chat-windows-deepseek-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-chat-windows-deepseek-jev) | `project` |  | — |
| [jev-ci-selector](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-ci-selector) | `project` |  | — |
| [jev-cli-jtsang4](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-cli-jtsang4) | `project` |  | — |
| [jev-cloud-quiz](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-cloud-quiz) | `project` |  | `content-scoring` |
| [jev-codex-router-skill](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-codex-router-skill) | `plugin` |  | — |
| [jev-connector](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-connector) | `plugin` |  | `content-scoring` `human-escalation` |
| [jev-cvss](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-cvss) | `project` |  | — |
| [jev-demo](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-demo) | `project` |  | — |
| [jev-demo-penglonghuang](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-demo-penglonghuang) | `project` |  | `tool-selection` `content-scoring` `human-escalation` |
| [jev-docs-zh](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-docs-zh) | `project` |  | — |
| [jev-evaluation](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-evaluation) | `project` |  | — |
| [jev-eyes](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-eyes) | `plugin` |  | — |
| [jev-freeform](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-freeform) | `project` |  | — |
| [jev-games](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-games) | `project` |  | — |
| [jev-gomoku](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-gomoku) | `project` |  | — |
| [jev-grand-prix](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-grand-prix) | `project` |  | — |
| [jev-grug](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-grug) | `project` |  | — |
| [jev-mcp-arunav25](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mcp-arunav25) | `plugin` |  | `content-scoring` `feature-extraction` |
| [jev-mcp-byk](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mcp-byk) | `plugin` |  | `content-scoring` |
| [jev-mcp-freepik-company](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mcp-freepik-company) | `plugin` |  | — |
| [jev-mcp-rajasekharponakala](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mcp-rajasekharponakala) | `plugin` |  | `content-scoring` |
| [jev-mcp-rashedint32](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mcp-rashedint32) | `plugin` |  | `classification` `output-validation` `content-scoring` |
| [jev-mcp-spring](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-mcp-spring) | `plugin` |  | — |
| [jev-measured](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-measured) | `project` |  | — |
| [jev-minesweeper](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-minesweeper) | `project` |  | — |
| [jev-pick-and-place-study](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-pick-and-place-study) | `project` |  | — |
| [jev-pii-checker](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-pii-checker) | `project` |  | — |
| [jev-playground](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-playground) | `project` |  | — |
| [jev-playground-little-planet-labs](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-playground-little-planet-labs) | `project` |  | — |
| [jev-plays-pokemon](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-plays-pokemon) | `project` |  | — |
| [jev-practice-speed](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-practice-speed) | `project` |  | — |
| [jev-realtime-trading](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-realtime-trading) | `project` |  | — |
| [jev-resume-disqualifier](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-resume-disqualifier) | `project` |  | — |
| [jev-search](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-search) | `project` |  | — |
| [jev-skill-router](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-skill-router) | `plugin` |  | — |
| [jev-skills-laguagu](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-skills-laguagu) | `plugin` |  | `search-ranking` `output-validation` |
| [jev-skills-wanlanglin](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-skills-wanlanglin) | `plugin` |  | `content-scoring` `human-escalation` |
| [jev-snake](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-snake) | `project` |  | — |
| [jev-system-one](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-system-one) | `project` |  | — |
| [jev-t-rex-runner](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-t-rex-runner) | `project` |  | — |
| [jev-torneo-animales](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-torneo-animales) | `project` |  | — |
| [jev-trip](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-trip) | `project` |  | — |
| [jev-wingman](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-wingman) | `project` |  | — |
| [jev-x-kit](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-x-kit) | `project` |  | `safety-gating` `content-scoring` `human-escalation` |
| [jev-yt-time-saver](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-yt-time-saver) | `plugin` |  | — |
| [jev2048](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev2048) | `project` |  | — |
| [jev-jsonschema](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-jsonschema) | `project` |  | — |
| [jev-ontology](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-ontology) | `project` |  | — |
| [jev-project-context](https://kydlikebtc.github.io/awesome-jev/?lang=en#jev-project-context) | `plugin` |  | — |
| [jevals-dayhaysoos](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevals-dayhaysoos) | `project` |  | — |
| [jevcode](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevcode) | `project` |  | — |
| [jevmem](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevmem) | `plugin` |  | — |
| [jevometry](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevometry) | `project` |  | — |
| [jevopt](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevopt) | `project` |  | — |
| [jevplayspokemon](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevplayspokemon) | `project` |  | — |
| [jevscope](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevscope) | `project` |  | — |
| [jevseek-blingdivinity](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevseek-blingdivinity) | `project` |  | — |
| [jevslop](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevslop) | `project` |  | — |
| [jevtape](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevtape) | `project` |  | — |
| [jevtest](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevtest) | `project` |  | — |
| [jevtok](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevtok) | `project` |  | — |
| [jevtown](https://kydlikebtc.github.io/awesome-jev/?lang=en#jevtown) | `project` |  | — |
| [jpp](https://kydlikebtc.github.io/awesome-jev/?lang=en#jpp) | `project` |  | — |
| [labs](https://kydlikebtc.github.io/awesome-jev/?lang=en#labs) | `project` |  | — |
| [laya-jev-lab](https://kydlikebtc.github.io/awesome-jev/?lang=en#laya-jev-lab) | `project` |  | — |
| [magic-jev-ball](https://kydlikebtc.github.io/awesome-jev/?lang=en#magic-jev-ball) | `project` |  | `safety-gating` |
| [mcpmatch](https://kydlikebtc.github.io/awesome-jev/?lang=en#mcpmatch) | `plugin` |  | — |
| [mcts-agent](https://kydlikebtc.github.io/awesome-jev/?lang=en#mcts-agent) | `project` |  | — |
| [mimicry](https://kydlikebtc.github.io/awesome-jev/?lang=en#mimicry) | `project` |  | — |
| [n8n-nodes-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#n8n-nodes-jev) | `plugin` |  | `classification` `output-validation` `content-scoring` |
| [n8n-nodes-typesafe](https://kydlikebtc.github.io/awesome-jev/?lang=en#n8n-nodes-typesafe) | `plugin` |  | — |
| [n8n-nodes-typesafe-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#n8n-nodes-typesafe-jev) | `project` |  | — |
| [new-api-plugin-typesafe](https://kydlikebtc.github.io/awesome-jev/?lang=en#new-api-plugin-typesafe) | `plugin` |  | — |
| [open-jev-bridge](https://kydlikebtc.github.io/awesome-jev/?lang=en#open-jev-bridge) | `plugin` |  | `output-validation` `content-scoring` `context-compaction` |
| [openpoke-meets-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#openpoke-meets-jev) | `project` |  | — |
| [pi-agent-foreman](https://kydlikebtc.github.io/awesome-jev/?lang=en#pi-agent-foreman) | `project` |  | — |
| [pi-typesafe-twilwa](https://kydlikebtc.github.io/awesome-jev/?lang=en#pi-typesafe-twilwa) | `plugin` |  | — |
| [pong-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#pong-jev) | `project` |  | — |
| [pydantic-jev-examples](https://kydlikebtc.github.io/awesome-jev/?lang=en#pydantic-jev-examples) | `project` |  | — |
| [r2r-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#r2r-jev) | `project` |  | `content-scoring` |
| [research-desk](https://kydlikebtc.github.io/awesome-jev/?lang=en#research-desk) | `project` |  | — |
| [risc-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#risc-jev) | `project` |  | — |
| [river-run-typesafe](https://kydlikebtc.github.io/awesome-jev/?lang=en#river-run-typesafe) | `project` |  | — |
| [rubikjev](https://kydlikebtc.github.io/awesome-jev/?lang=en#rubikjev) | `project` |  | — |
| [rust-sysone](https://kydlikebtc.github.io/awesome-jev/?lang=en#rust-sysone) | `project` |  | — |
| [scam-shield](https://kydlikebtc.github.io/awesome-jev/?lang=en#scam-shield) | `project` |  | — |
| [search-function-test](https://kydlikebtc.github.io/awesome-jev/?lang=en#search-function-test) | `project` |  | — |
| [second-thought](https://kydlikebtc.github.io/awesome-jev/?lang=en#second-thought) | `project` |  | — |
| [secondlayer](https://kydlikebtc.github.io/awesome-jev/?lang=en#secondlayer) | `project` |  | — |
| [should-ai-kill-us-all](https://kydlikebtc.github.io/awesome-jev/?lang=en#should-ai-kill-us-all) | `project` |  | — |
| [skill-router](https://kydlikebtc.github.io/awesome-jev/?lang=en#skill-router) | `plugin` |  | — |
| [soupbase](https://kydlikebtc.github.io/awesome-jev/?lang=en#soupbase) | `project` |  | — |
| [sqlite3-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#sqlite3-jev) | `plugin` |  | — |
| [switchboard](https://kydlikebtc.github.io/awesome-jev/?lang=en#switchboard) | `plugin` |  | — |
| [system-one-chess](https://kydlikebtc.github.io/awesome-jev/?lang=en#system-one-chess) | `project` |  | — |
| [systemone-lite](https://kydlikebtc.github.io/awesome-jev/?lang=en#systemone-lite) | `project` |  | — |
| [tempo-jev-demo](https://kydlikebtc.github.io/awesome-jev/?lang=en#tempo-jev-demo) | `project` |  | — |
| [trade-jev](https://kydlikebtc.github.io/awesome-jev/?lang=en#trade-jev) | `project` |  | — |
| [typesafe-ai-playground](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-ai-playground) | `project` |  | — |
| [typesafe-assist](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-assist) | `project` |  | — |
| [typesafe-chess](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-chess) | `project` |  | — |
| [typesafe-comment](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-comment) | `project` |  | — |
| [typesafe-jev-examples](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-jev-examples) | `project` |  | — |
| [typesafe-jev-mcp](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-jev-mcp) | `plugin` |  | — |
| [typesafe-jev-tools](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-jev-tools) | `plugin` |  | — |
| [typesafe-ui](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-ui) | `project` |  | `safety-gating` |
| [typesafe-chess-eval](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafe-chess-eval) | `project` |  | — |
| [typesafeai-cli](https://kydlikebtc.github.io/awesome-jev/?lang=en#typesafeai-cli) | `project` |  | — |
| [wellposed](https://kydlikebtc.github.io/awesome-jev/?lang=en#wellposed) | `project` |  | `output-validation` |
| [your-signal](https://kydlikebtc.github.io/awesome-jev/?lang=en#your-signal) | `plugin` |  | — |
