# skill-simplifier

> [English version](README.en.md)

一个 Claude Code plugin，只含一个 skill，用于审查一份 SKILL.md（含可选 `references/`）或一份 CLAUDE.md，删除其中与上游知识源（系统提示词、Tool Description、其他 Skill、其他 CLAUDE.md）重复的内容，以及未污染模型本不会犯的假想防错。

## 为什么需要这个 skill

Claude 写 SKILL.md 和 CLAUDE.md 时倾向于把它认为重要的事一股脑都写上，但分不清哪些内容已经由上游提供，也可能把当前会话刚出现的错误固化成未来模型并不需要的防错。重复内容和假想防错都会占 context token；后者还会向全新会话中的模型植入原本不存在的错误认知。本 skill 自动删除上游只读的重复和假想防错，再让用户决定用户自有来源之间的重复该删哪一侧。

## 安装

本 plugin 通过 [`fomalhaut647-plugins`](../..) marketplace 分发。两步安装：

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install skill-simplifier@fomalhaut647-plugins
```

本地开发、marketplace 没推到远端时，把 GitHub 路径换成 marketplace 仓库的绝对路径：

```
/plugin marketplace add <marketplace 仓库绝对路径>
/plugin install skill-simplifier@fomalhaut647-plugins
```

## Skill 一览

| Skill | 触发者 | 做什么 |
|---|---|---|
| `skill-simplifier` | 用户，在即将编写 / 修改 / 审查 SKILL.md 或 CLAUDE.md 时 | 枚举四类上游知识源，用全新会话反事实检查假想防错，自动删除 Zone A/B，让用户决定 Zone C（以及出现时的 Zone D）|

本 skill 通过 `ToolSearch` 加载 deferred tool 的 schema，不在 SKILL.md 里重述 tool 内容。

## 工作流概览

1. **Stage 0** —— 确认目标（每次调用只处理一个 skill 或一份 CLAUDE.md）
2. **Stage 1** —— 枚举四类上游知识源：系统提示词、Tool Description、其他 Skill、其他 CLAUDE.md
3. **Stage 2** —— 按目标类型激活辅助 skill
4. **Stage 3** —— 完整读一遍目标
5. **Stage 4** —— 假想目标在全新、未受当前对话污染的会话中首次加载，检查模型是否真的会犯每条防错所预防的错误
6. **Stage 5** —— 产出两至四区审查报告。**此时不要做 Edit。**
   - **Zone A**：上游是系统提示词 / Tool Description → 自动从目标删除（上游只读，别无选择）
   - **Zone B**：全新会话中不会发生、也没有真实失败证据的假想防错 → 自动从目标删除
   - **Zone C**：上游是其他 Skill / CLAUDE.md → 让用户决定哪侧删（两侧都由用户拥有）
   - **Zone D**（仅当目标是带 `references/` 的 skill 时出现）：SKILL.md 与 `references/` 之间的内部分层重复
7. **Stage 6** —— 按 Stage 5 决定，用 `Edit` 应用

完整内容见 [`skills/skill-simplifier/SKILL.md`](skills/skill-simplifier/SKILL.md)。

## 目录结构

```
plugins/skill-simplifier/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── skill-simplifier/
│       ├── SKILL.md
│       └── references/      # 目前为空
├── CLAUDE.md                # 贡献者指南 (AI agent 提交 PR 前必读)
├── README.md                # 本文件 (中文)
├── README.en.md             # English
└── RELEASE-NOTES.md
```

LICENSE 在 marketplace 仓库根目录，适用于本 plugin 与所有其他 plugin。

## 为什么是 skill 而不是 subagent

本 plugin 故意做成 skill 形态，而不是 `code-simplifier` 那样的 subagent。原因：Stage 5 要把每条 Zone C 的取舍交给用户决定，而 subagent 是"派出去 - 跑完返回"的模型，没法中途暂停问用户。在主 agent session 里跑审查，既能利用最近的编辑背景判断"具体胜过泛化"，又能在 Stage 4 主动排除这段背景对全新会话模型认知的污染。

## 许可证

MIT —— 见 [marketplace 根目录的 LICENSE](../../LICENSE)。
