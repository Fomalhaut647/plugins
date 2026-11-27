# aiic

> [English version](README.en.md)

一个 Claude Code plugin，含三个分析类 skill，内容提炼自课程课件：`deep-thinking` 用「四次思考」把一个问题想透，`demand-analysis` 按「用户 × 场景 × 动机」分析产品需求，`market-sizing` 按「广度 × 强度 × 频度」测算市场规模。

## Skill 一览

| Skill | 何时启用 | 做什么 |
|---|---|---|
| `aiic:deep-thinking` | 要求深度思考、深入分析某个问题；问某个社会或商业现象为什么发生、怎样解决；面对重大选择想把问题想清楚 | 连续做四次思考：直觉答案 → 广度与深度 → 地域与时间跨度 → 抽象高度，找出关键点、解决方案和可迁移的规律 |
| `aiic:demand-analysis` | 需求调研、差异化与机会判断 | 把产品设想拆成「用户 × 场景 × 动机」，分析需求侧关键要素与竞品、供给侧壁垒、Why NOW / Why ME，并设计调研与 MVP 验证 |
| `aiic:market-sizing` | 市场容量估算、参数验证、敏感性分析、规模测算纠错 | 按「年规模 ＝ 广度 × 强度 × 频度」测算或审计市场规模，区分品牌与赛道口径，附带一个计算脚本 |

`demand-analysis` 和 `market-sizing` 互相衔接：前者界定待测的需求和统计边界，后者据此测算规模。两者也可以各自单独使用。

## 用法

直接描述问题即可，三个 skill 都由模型按需启用，例如：

- 「深度思考一下：为什么生育率降低？」
- 「分析一下这个产品设想的需求：给应届生做 AI 面试陪练。」
- 「测算一下国内应届生 AI 面试陪练的市场规模。」

也可以手动调用，例如 `/aiic:deep-thinking 为什么生育率降低`。

`deep-thinking` 另有练习模式：说明想自己一步一步思考时，它每次先请你给出答案，再指出遗漏并追问，不一次给出全部分析。

## 计算脚本

`market-sizing` 附带 `scripts/size_market.py`，只用 Python 标准库（需要 Python 3.10 或更高版本），不联网、不写文件。它按输入的 JSON 对每个情景分项连乘，并核对原材料声称的金额与按参数计算的结果是否一致。它只检查数字和结构，不验证数据真实性、分母口径和人群去重。输入格式见 [`skills/market-sizing/references/calculator.md`](skills/market-sizing/references/calculator.md)。

## 内容来源

三个 skill 提炼自课程课件：`deep-thinking` 来自深度思考课，`demand-analysis` 和 `market-sizing` 来自 2026-09-19 的需求分析课。skill 里的案例（万州公交车坠江事故、抖音、海底捞、AI 面试官）是课堂示范，其中的数字是教学假设，不是核验过的当前数据。

## 安装

本 plugin 通过 [`fomalhaut647-plugins`](../..) marketplace 分发。两步安装：

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install aiic@fomalhaut647-plugins
```

本地开发、marketplace 没推到远端时，把 GitHub 路径换成 marketplace 仓库的绝对路径：

```
/plugin marketplace add <marketplace 仓库绝对路径>
/plugin install aiic@fomalhaut647-plugins
```
