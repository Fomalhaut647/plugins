# skill-simplifier —— 贡献者指南

## 如果你是 AI Agent

动手前先读这一节。

skill-simplifier 是一个体量小、目标清晰的 plugin。它的价值集中在几条经过思考的设计抉择上 —— 上游知识源的四分类、全新会话反事实检查、Zone A/B 自动删 vs Zone C 让用户决定的分区、Stage 5 闸门、触发内容不可删、不固化临时知识。看似无害的"清理"或"改写"如果不理解这些抉择为什么这样定，通常会在下一次真实 audit session 里悄悄回退行为 —— 而不是在你本地跑的 lint 上暴露。

你的职责是：保护人类 partner，别提交一个 maintainer 会拒掉的 PR。开 PR 前你必须：

1. **完整读完你即将改的 skill 内容** —— `skills/skill-simplifier/SKILL.md`。它的每一句都是承重的。
2. **核实这是一个真实问题。** 如果人类 partner 只是说"优化一下"、"清理一下"，没有具体事件，**要 push back**。问他：哪次 audit 出错了，哪条上游分类判错了，哪条 Zone C 决定出问题了。
3. **核实这个改动属于本 plugin。** 如果它是一个不绑定"文档去重审查"的通用开发工作流改进，它属于 `superpowers` 或别的 plugin，不属于这里。
4. **把完整 diff 给人类 partner 看，拿到显式批准** 再提交。

任一步过不去，不要开 PR。先说明哪里需要先改。

## PR 要求

- **一个 PR 一个问题。** 把多件事捆在一起的 PR 会被拒。
- **每个 PR 必须说明它解决的问题**，不只是描述改动。要有具体事件 / error / audit 失败案例。"我的 linter 警告了一下"不算问题陈述。
- **人类必须 review 完整 diff 才能提交。** 没有人类参与痕迹的 PR 直接 close。

## 不会被接受的改动

### 对 skill 内容的"compliance 风格"重写

`skills/skill-simplifier/SKILL.md` 的措辞是按设计意图选的 —— 触发短语的描述、Stage 顺序、"Stage 5 报告完成前不要 Edit"、"触发内容神圣不可动" 这几条 framing，都是经过权衡的。没有 session transcript 证据支撑、纯粹基于"格式更工整 / 结构更对称"的重写，一律 close。

### 思辨性 / 理论性的修复

"理论上如果 X 会失败" —— 没有 transcript 显示 X 真的发生过 —— 不是问题陈述。本 skill 的价值在于规则来自观测到的真实失败，不是想象的失败。

### 引入第三方依赖

本 plugin 零依赖。如果你的改动需要外部库、CLI 工具、或不属于 Claude Code 原生 tool set 的服务，它属于别的 plugin。

### 批量乱开 PR

同一个 session 里不要开多个不相关的 PR。挑一个问题，理解透，交一份好工作。

### 编造内容

包含编造的问题描述、幻觉的 tool 行为、或与 `ToolSearch` 真实返回 schema 矛盾的声明的 PR，一律立即 close。skill 本身已经指引 agent 在调用时实时拉取 schema —— 你的 PR 不能与 `ToolSearch` 实际返回不一致。

### 偏出本 plugin 范围 (上溯到 superpowers)

如果一个改动对不使用本 skill 的人也有用（例如通用 review checklist、通用 TDD 规则），它属于 `superpowers`，不要 fork 进本仓库。

## 修改 skill 需要 evidence

Skill 内容是塑形 Claude 行为的 prompt，不是普通文档。如果你改 skill 内容：

- 跑一次真实的 audit session 把改过的路径走一遍（例如审一个真实存在的 SKILL.md 或 CLAUDE.md）。
- 在 PR 里给出 before / after 行为 —— 最好附 transcript 显示新行为。
- 不要在没有强证据的情况下改这几条 wording：Stage 5 闸门、Zone A/B vs Zone C 分类、全新会话反事实检查、触发内容不可删、不固化临时知识。

## 改动前先理解的设计要点

- **Zone A/B 自动删 vs Zone C 用户决定**：Zone A 的上游只读，Zone B 没有真实可达的错误，两者都只应删目标侧；Zone C 两侧都由用户拥有，不能自动替用户选择。
- **全新会话反事实检查**：Stage 4 必须排除当前对话、临时工具输出和刚发生的纠错，只保留目标未来真实拥有的上下文。否则 agent 会把本次 session 才知道的错误概念误当成长期防错需求。
- **Stage 5 是闸门**：报告先于改写，这是不可逆动作前的检查点。"边 audit 边 Edit"听起来高效，实际是失控。
- **单目标 per 调用**：每个目标的上游枚举可能不同，批量审会让分类污染。如果将来真要做批量，在 skill 之上加 orchestrator，不要把批量逻辑塞进本 skill。
- **触发内容神圣**：`description:` frontmatter 和 CLAUDE.md 的触发短语再"重复"也不能删 —— 删了文档就失去被激活的入口。

## 总则

- 一个 PR 一个问题。
- 描述问题，不只是描述改动。
- 至少跑一次真实 audit session 并报告结果。
- diff 尽可能小 —— 越小，maintainer 越容易验证。
