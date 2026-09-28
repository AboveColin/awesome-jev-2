# 重试控制

<sub>[awesome-jev](../../README.zh-CN.md) · [English](retry-control.md)</sub>

_判断失败的步骤是否值得重试。_

这个决策的全部已收录例子 —— 共 6 条。同样这些行及其警示也在[索引](../../README.zh-CN.md#重试控制)里；[站点](https://kydlikebtc.github.io/awesome-jev/?p=retry-control&lang=zh)还能按语言、原语和形态进一步筛选。

★ 以区间给出仓库的 GitHub star 数 —— ★10+、★100+、★1k+、★10k+、★100k+；没有仓库或不足 10 星的行不标区间。排序：官方优先，其次是含代码的，再按区间，最后按标题。区间只反映热度，不代表质量；最近一次从 GitHub 读到的精确数字在 [`catalog.json`](../../catalog.json) 和[站点](https://kydlikebtc.github.io/awesome-jev/?lang=zh)上。 <sub>(机翻)</sub>

*调用点*链接打开该行引用的那一个文件（`evidence.path`）在仓库默认分支 `HEAD` 上的版本；其后的日期是有人最近一次阅读该文件的日期（`evidence.read_on`）：这是阅读记录，不是运行过代码。*引用文件*链接同理，只是该文件表明项目采用了 Jev 的请求结构、并非基于 Jev 构建，或只是项目附带的示例（`evidence.kind`）。两种链接都没有固定到某个提交，打开的是文件的当前版本，可能与当时读到的不同；文件移动后链接就会失效，每周的 claims 检查会报告这种情况。 <sub>(机翻)</sub>

- **[harnessjudge](https://github.com/ndolinschi/harnessjudge)** — 评判智能体的每一步：通过／重试／升级／停止。 <sub>(项目自述)</sub> <sub>(机翻)</sub>
  <sub>`开源项目` · ndolinschi · `TS` · 调用点 [`src/lib/jev.ts`](https://github.com/ndolinschi/harnessjudge/blob/HEAD/src/lib/jev.ts)，2026-09-22 阅读 · ⚠ `仅一次提交` `无许可证`</sub>

- **[Jev by Example](https://github.com/ReallyArtificial/jev-by-example)** — 十个可运行的 JavaScript 智能体决策，一个文件一个：新记忆与旧记忆冲突时该改还是该留、工具返回 200 是否真的完成了任务、写入超时后该重试还是该对账、上下文分块在预算内如何取舍、压缩后的交接是否丢掉了某条禁令。Jev 只回答带类型的问题，阈值和最终提案由普通代码决定。
  <sub>`开源项目` · Really Artificial · `JS` · `choice` · `score` · `noul` · 调用点 [`src/client.mjs`](https://github.com/ReallyArtificial/jev-by-example/blob/HEAD/src/client.mjs)，2026-09-22 阅读 · ⚠ `疑似 AI 生成`</sub>

- **[jev-harness](https://github.com/ismaelsoilet/jev-harness)** — 零依赖的 System One 决策框架：用 5 道语义关卡，在琐碎错误和“死循环”上替前沿 AI 智能体省下 token。 <sub>(项目自述)</sub> <sub>(机翻)</sub>
  <sub>`插件` · ismaelsoilet · `Py` · 调用点 [`src/jev_harness/client.py`](https://github.com/ismaelsoilet/jev-harness/blob/HEAD/src/jev_harness/client.py)，2026-09-24 阅读</sub>

- **[jev-reasoning-navigator](https://github.com/AndreuVM/jev-reasoning-navigator)** — JEV 推理导航器：面向自主 LLM 智能体的认知监督、防止循环与反幻觉引擎。 <sub>(机翻)</sub>
  <sub>`开源项目` · andreuvm · `Py` · 调用点 [`jev_navigator/core/typesafe_client.py`](https://github.com/AndreuVM/jev-reasoning-navigator/blob/HEAD/jev_navigator/core/typesafe_client.py)，2026-09-24 阅读 · ⚠ `无许可证`</sub>

- **[jev-resilience](https://github.com/Vicente-MD/jev-resilience)** — 给 Spring WebFlux 的非阻塞 Starter，实现一个语义熔断器来检测静默故障。 <sub>(项目自述)</sub> <sub>(机翻)</sub>
  <sub>`插件` · vicente-md · `Java` · 调用点 [`src/main/java/ai/jev/resilience/client/dto/JevRequest.java`](https://github.com/Vicente-MD/jev-resilience/blob/HEAD/src/main/java/ai/jev/resilience/client/dto/JevRequest.java)，2026-09-22 阅读 · ⚠ `无许可证`</sub>

- **[jevswiftsdk](https://github.com/NSStudent/JevSwiftSDK)** — 独立的类型安全 Swift SDK，支持 async/await、批处理与重试。 <sub>(项目自述)</sub> <sub>(机翻)</sub>
  <sub>`SDK` · nsstudent · `Swift` · 调用点 [`Sources/JevSwiftSDK/Configuration.swift`](https://github.com/NSStudent/JevSwiftSDK/blob/HEAD/Sources/JevSwiftSDK/Configuration.swift)，2026-09-22 阅读</sub>

---

<sub>由 `scripts/build_readme.py` 从 `catalog.json` 生成。请修改目录，不要改这个文件。</sub>
