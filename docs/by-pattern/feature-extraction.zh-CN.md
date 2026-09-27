# 机器学习特征抽取

<sub>[awesome-jev](../../README.zh-CN.md) · [English](feature-extraction.md)</sub>

_把自由文本转成数值特征，喂给下游的传统模型。_

这个决策的全部已收录例子 —— 共 8 条。同样这些行及其警示也在[索引](../../README.zh-CN.md#机器学习特征抽取)里；[站点](https://kydlikebtc.github.io/awesome-jev/?p=feature-extraction&lang=zh)还能按语言、原语和形态进一步筛选。

★ 以区间给出仓库的 GitHub star 数 —— ★10+、★100+、★1k+、★10k+、★100k+；没有仓库或不足 10 星的行不标区间。排序：官方优先，其次是含代码的，再按区间，最后按标题。区间只反映热度，不代表质量；最近一次从 GitHub 读到的精确数字在 [`catalog.json`](../../catalog.json) 和[站点](https://kydlikebtc.github.io/awesome-jev/?lang=zh)上。 <sub>(机翻)</sub>

- **[Cookbook: Autoresearch feature discovery](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery)** ⭐ — 一个自动研究循环：自己提出问题、把自由文本转成数值特征、再用误差反过来改进下游的梯度提升回归模型。
  <sub>`官方文档` · `Py`</sub>

- **[nimble](https://github.com/bespokelabsai/nimble)** — 本地类型化决策、对比式数据筛选与模型评测。 <sub>(项目自述)</sub> <sub>(机翻)</sub>
  <sub>`开源项目` · ★1k+ · bespokelabsai · `Py` · ⚠ `无许可证`</sub>

- **[jev-align](https://github.com/sutro-sh/jev-align)** — 从人类反馈出发，构建经过校准的决策函数。
  <sub>`开源项目` · ★100+ · sutro-sh · `Py`</sub>

- **[jev-curate](https://github.com/AkashPriyadarshii/jev-curate)** — 拿 Jev 筛训练数据。JSONL / Parquet 先做质量、相关性和风险判断，再决定哪些进后面的训练。
  <sub>`开源项目` · ★10+ · `Rs` · `score` · `noul`</sub>

- **[Prism](https://github.com/irfndi/prism-liquidity-agent)** — 不直接让 Jev 下单。它判断 toxic flow、市场压力、均值回归之类的状态，再交给原来的策略。
  <sub>`开源项目` · ★10+ · `TS` · `choice` · `score`</sub>

- **[jev-board-lab](https://github.com/WebGrga/jev-board-lab)** — 面向 Jev Board 数据集的交互式浏览与问题工作区。 <sub>(项目自述)</sub> <sub>(机翻)</sub>
  <sub>`开源项目` · webgrga · `JS` · ⚠ `无许可证`</sub>

- **[jev-calibrated-narrative-coding](https://github.com/pozapas/jev-calibrated-narrative-coding)** — 用 System One 模型把警方的交通事故叙述，校准地转换为带概率的事故变量。包含完整流程。 <sub>(项目自述)</sub> <sub>(机翻)</sub>
  <sub>`开源项目` · pozapas · `Py`</sub>

- **[tiershift](https://github.com/iamvatsalpatel/tiershift)** — 把每次 LLM 调用下沉到能胜任的最便宜模型，路由由 Jev 在约 180 毫秒内决定，无需训练。 <sub>(项目自述)</sub> <sub>(机翻)</sub>
  <sub>`开源项目` · iamvatsalpatel · `TS`</sub>

---

<sub>由 `scripts/build_readme.py` 从 `catalog.json` 生成。请修改目录，不要改这个文件。</sub>
