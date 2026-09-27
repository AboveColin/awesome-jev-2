<!-- Written by scripts/build_review_queue.py from catalog.json. Edit those, not this file. -->

# Review queue · 复核队列

<sub>The Chinese on this page is model-written and has not been reviewed by a person. · 本页中文由模型撰写（机翻），未经人工审校。</sub>

Rows a script has singled out for a person to read. Each entry is a machine signal (a path or a string matched a rule), not a finding about the row, and nothing on this page is written into `catalog.json`. Whoever reads a row records the decision in it, as each section says, and the row leaves this page when it is next regenerated. [status.md](status.md) publishes the counts.

脚本挑出、需要人来读的行。每一项都是机器信号（某个路径或字符串命中了规则），不是对该行的结论，本页内容也不会写回 `catalog.json`。读过某一行的人按各节所说把判断记进该行，下次重新生成时它就会离开本页。数量见 [status.md](status.md)。

| Signal · 信号 | Rows · 行数 |
| --- | --- |
| [Evidence read from an examples directory · 证据取自 examples 目录](#examples-dir) | 22 |
| [Evidence resting on one model name or the API host · 证据只靠一个模型名或 API 主机](#single-model-name) | 76 |

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
