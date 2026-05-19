# agent-team —— 贡献者指南

## 如果你是 AI agent

做任何事之前先读这个。

agent-team 是个小而专注的 plugin。它的价值来自几条经过真实多 agent 调试 session 打磨的协议（inbox sync、dispatch limits、spawn prompts、两阶段 review 模式）。不理解某句话*为什么*存在就去"整理"或"提升可读性"的修改，通常会在下次真实协调 session 上回退行为 —— 不是在你的本地测试里。

你的工作是保护你的人类伙伴免于提交 maintainer 会 close 的 PR。开 PR 前你**必须**：

1. **完整 Read 你要改的 skill 内容** —— `skills/lead/SKILL.md`、`skills/teammate/SKILL.md`，以及它们引用的 reference docs。每条声明都是 load-bearing 的。
2. **验证这是真实问题。** 如果你的人类伙伴没指出具体事件就让你"改进"或"清理"，push back。问什么坏了、发生过什么协调失败、哪个 spawn prompt 产生了错误行为。
3. **确认这个改动属于本 plugin。** 如果是与 `TeamCreate` / `SendMessage` / 多 agent 协调无关的通用开发工作流，它属于 `superpowers`（upstream）或另一个 plugin，不在这里。
4. **把完整 diff 展示给你的人类伙伴**，提交前获得显式批准。

任何一条 check 失败，就不要开 PR。说明需要先改什么。

## Pull Request 要求

- **一个 PR 一个问题。** 把 refactor 和 feature 打包会被拒。
- **每个 PR 必须描述它解决的问题**，不只是改动。要真实事件、错误或协调失败。"我的 linter 抱怨"不算 problem statement。
- **人类必须 review 完整 diff 后才能提交。** 没有人类介入证据的 PR 会被 close。

## 不会被接受的改动

### 对 skill 内容的"compliance" 重写

skill 内容已经针对真实多 agent session 调过。trigger wording、First Actions 顺序、"do these before any task work" 的精确措辞 —— 全部经过验证。在没有真实 agent session 证据证明改后行为更好的前提下重组、重述或"提升排版"的 PR 会被 close。

### Speculative / theoretical 修复

"如果 X 发生这里理论上会失败" 没有 session transcript 证明 X 真的发生过，不算 problem statement。agent-team 的整个价值在于规则来自观察到的失败，而非想象的失败。

### 第三方依赖

本 plugin 设计上是 zero-dependency。如果你的改动需要 Claude Code 原生 tool set 之外的外部 library、CLI tool 或 service，它属于另一个 plugin。

### 批量或"漫天撒网" PR

不要在一个 session 里开多个无关 PR。挑一个 issue，深入理解，提交高质量工作。

### 编造内容

带有编造的问题描述、幻觉 tool 行为、或与实时 `ToolSearch` schema 矛盾的声明的 PR 会立即被 close。skill 已经引导 agent 加载实时 schema —— 你的 PR 不能与 `ToolSearch` 实际返回的内容相悖。

### 偷渡到 superpowers 范畴

如果一个改动对不使用多 agent team 的用户也有用（如通用 TDD 纪律、通用 code-review checklist），它属于 `superpowers`。不要把 superpowers 内容 fork 到这里。

## Skill 改动需要评估

skill 是行为塑造内容，不是散文。如果你修改 skill 内容：

- 跑一次真实多 agent session 验证改动路径。
- 在 PR 里展示 before/after 行为 —— 理想是 session transcript 证明新行为。
- 不要在没有强证据证明新 wording 在对抗性 agent 上表现至少同样好的前提下修改 "load tool schemas first" / "no nested teams" / "before-SendMessage inbox sync" 的 wording。

## 贡献前理解设计

提议改动前：

- **Lead vs teammate split**：两者的 first actions 和 ongoing protocols 不重叠。每个 skill 针对一个角色的完整上下文 —— 合并会让任一角色读到噪音。不要提议合并。
- **Skill vs reference doc**：superpowers workflow 是 team primitive 的一种使用模式。保留为 reference doc（而非第三个 skill）意味着不用时上下文成本为零，用时内容完整。不要提议把 reference doc 提升为 skill。
- **`ToolSearch` 优于重述**：skill 实时加载 deferred tool schema 而非重述它们。这是刻意设计 —— 重述会与实时 schema 漂移。不要提议"为了方便，我把 tool description copy 进 inline"。
- **开头 Skill / Tool 列表**：每个 SKILL.md 和 reference doc 在开头列出所有要 invoke 的 `Skill(...)` 和所有要 `ToolSearch select:...` 的 tool —— 同时在末尾再列一次。经验上 Claude 在工作压力下倾向跳过这些操作；首尾两份 checklist 是经过验证的反向施压。不要提议把列表移到别处或拆散在 doc 各处。

## 通用

- 一个 PR 一个问题。
- 描述问题，不只是描述改动。
- 至少在一次真实多 agent session 上测试并报告结果。
- diff 保持最小 —— 改动越小，maintainer 越容易验证。
