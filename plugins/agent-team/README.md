# agent-team

> [English version](README.en.md)

一个 Claude Code plugin：在桌面端让当前会话当主会话，把一件较大的工作拆给多个并行子会话分头完成。主会话负责拆分、派活、核实、审查判定和合并，实现代码由子会话写。

它基于 Claude Code 桌面端 2026 年 10 月的并行会话更新：主会话可以直接开子会话，子会话各有独立的工作树和分支，挂在主会话下面，结束时自动回报。它**不**使用官方实验性的 agent teams 功能（那个只在 CLI 里可用）。

## 要求

- Claude Code 桌面端（Code 标签页），会话里有 `start_session`、`list_events`、`SendMessage` 等子会话工具。CLI 里没有这些工具，本 plugin 不可用。
- 项目是 git 仓库：子会话靠 git 工作树隔离。

## 安装

本 plugin 通过 [`fomalhaut647-plugins`](../..) marketplace 分发：

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install agent-team@fomalhaut647-plugins
```

本地开发（marketplace 未推到远端）时，把 GitHub 路径换成 marketplace 仓库的绝对路径：

```
/plugin marketplace add <marketplace 仓库绝对路径>
/plugin install agent-team@fomalhaut647-plugins
```

## 用法

直接说「开个团队把这件事拆开并行做」之类的话，或者手动调用 `/agent-team:lead`。主会话会：

1. **拆分**：拆成互不依赖、改动文件不重叠的几块；有依赖的块等前一块通过后，从它的分支切出再派。
2. **派活**：每块开一个子会话，各用独立工作树。任务书只写做什么：目标、范围、验收标准和边界。子会话只在自己分支提交，有问题只找主会话。
3. **核实**：读子会话发来的完整报告，看它分支上的改动。
4. **审查**：每个改了代码的块，另开一次性审查会话，用内置 `code-review` 只读审查。主会话判定哪些值得修，发给做这块的子会话修复，每轮换新的审查会话，直到没有值得修的。
5. **合并**：向你汇报并征得同意后，把各分支合进主会话的分支，整体测试，再开一个总 PR；最后问你是否归档子会话。

## 设计取舍

- **只有主会话一侧的 skill**：子会话是完整的桌面会话，平台已经规定了它怎么提交、回报和发消息；它该守的规则写在任务书里，不需要再给它一个 skill。
- **只管做什么，不管怎么做**：主会话看得到其他 skill 的简介、看不到正文，转述它们的用法会被子会话当成权威而执行走样。要改变子会话的默认做法时，必须明说是覆盖并给出理由。
- **一次性审查会话**：每轮换新的审查会话，避免被上一轮结论带偏；修哪些由掌握全局的主会话判定。
- **本地合并 + 一个总 PR**：子会话不推送，减少远端噪音；各块在主会话里合到一起，整体测试后再提交审阅。
- **完整报告发消息，最后只回一句**：子会话主动发消息能立刻叫醒主会话、内容完整，不用等所有子会话都停下；它自己的最后一条回复只写一句话，免得同一份报告重复占用主会话的上下文。

## 目录结构

```
plugins/agent-team/
├── .claude-plugin/
│   └── plugin.json         # plugin 元数据
├── skills/
│   └── lead/
│       └── SKILL.md        # 主会话 skill
├── CLAUDE.md               # 贡献者指南（AI agent 改动前必读）
├── README.md               # 本文件（中文）
├── README.en.md            # 英文版
└── RELEASE-NOTES.md        # 版本历史
```

LICENSE 在 marketplace 仓库根目录，适用于本 plugin 与所有其他 plugin。

## 从 0.x 升级

1.0.0 是破坏性重写：`agent-team:teammate`、收件箱同步协议、`TeamCreate` 流程和 superpowers 开发流程参考文档全部删除，原因见 [RELEASE-NOTES](RELEASE-NOTES.md)。

## License

MIT —— 详见 [marketplace 根目录的 LICENSE](../../LICENSE)。
