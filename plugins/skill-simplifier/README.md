# skill-simplifier

> English version: [README.en.md](README.en.md)

一个 Claude Code plugin, 只含一个 skill, 用于审查一份 SKILL.md (含可选 `references/`) 或一份 CLAUDE.md, 找出其中与上游知识源 (系统提示词、Tool Description、其他 Skill、其他 CLAUDE.md) 重复的内容并去重。

## 为什么需要这个 skill

Claude 写 SKILL.md 和 CLAUDE.md 时倾向于把它认为重要的事一股脑都写上, 但分不清这些事是否已经由系统提示词、某个 Tool Description、其他 Skill、其他 CLAUDE.md 提供。重复内容既占 context token、挤压目标文档的独特价值, 又会在上游变化时悄悄过时漂移。本 skill 审查一个目标, 列出每一处重复, 自动删除那些"无论如何都该删"的重复 (上游 = 系统提示词 / Tool Description), 并让用户决定那些"两侧都由用户拥有"的重复该删哪一侧 (上游 = 其他 Skill / 其他 CLAUDE.md)。

## 安装

本 plugin 通过 [`fomalhaut647-plugins`](../..) marketplace 分发。两步安装:

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install skill-simplifier@fomalhaut647-plugins
```

本地开发、marketplace 没推到远端时, 把 GitHub 路径换成 marketplace 仓库的绝对路径:

```
/plugin marketplace add <marketplace 仓库绝对路径>
/plugin install skill-simplifier@fomalhaut647-plugins
```

## Skill 一览

| Skill | 触发者 | 做什么 |
|---|---|---|
| `skill-simplifier` | 用户, 在即将编写 / 修改 / 审查 SKILL.md 或 CLAUDE.md 时 | 枚举四类上游知识源, 把重复分到两 (或三) 个 zone, 自动删 Zone A, 让用户决定 Zone B (以及出现时的 Zone C) |

本 skill 通过 `ToolSearch` 加载 deferred tool 的 schema, 不在 SKILL.md 里重述 tool 内容。

## 工作流概览

1. **Stage 0** —— 确认目标 (每次调用只处理一个 skill 或一份 CLAUDE.md)
2. **Stage 1** —— 枚举四类上游知识源: 系统提示词、Tool Description、其他 Skill、其他 CLAUDE.md
3. **Stage 2** —— 按目标类型激活辅助 skill
4. **Stage 3** —— 完整读一遍目标
5. **Stage 4** —— 产出两 (或三) 区重复审查报告。**此时不要做 Edit。**
   - **Zone A**: 上游是系统提示词 / Tool Description → 自动从目标删除 (上游只读, 别无选择)
   - **Zone B**: 上游是其他 Skill / CLAUDE.md → 让用户决定哪侧删 (两侧都由用户拥有)
   - **Zone C** (仅当目标是带 `references/` 的 skill 时出现): SKILL.md 与 `references/` 之间的内部分层重复
6. **Stage 5** —— 按 Stage 4 决定, 用 `Edit` 应用

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

LICENSE 在 marketplace 仓库根目录, 适用于本 plugin 与所有其他 plugin。

## 为什么是 skill 而不是 subagent

本 plugin 故意做成 skill 形态, 而不是 `code-simplifier` 那样的 subagent。原因: Stage 4 要把每条 Zone B 的取舍交给用户决定, 而 subagent 是"派出去 - 跑完返回"的模型, 没法中途暂停问用户。在主 agent session 里跑审查的另一个好处: 主 agent 知道用户最近为什么这么写, 这帮 audit 在"具体胜过泛化"和"真重复"之间做更准的判断。

## 许可证

MIT —— 见 [marketplace 根目录的 LICENSE](../../LICENSE)。
