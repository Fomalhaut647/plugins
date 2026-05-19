> [English version](README.en.md)

# fomalhaut647-plugins

我个人的 Claude Code plugins marketplace。

## 添加 marketplace

```
/plugin marketplace add Fomalhaut647/plugins
```

之后可以在 `/plugin > Discover` 里浏览，或直接安装某个 plugin：

```
/plugin install <plugin-name>@fomalhaut647-plugins
```

## Plugins 列表

| 名字 | 状态 | 说明 |
| --- | --- | --- |
| [`agent-team`](plugins/agent-team) | v0.1.0 | 提供 `lead` / `teammate` 两个 subskill 协调长程多 agent 团队；可选 reference docs 叠加 `superpowers` + `code-review` 开发工作流 |
| [`skill-simplifier`](plugins/skill-simplifier) | v0.1.0 | 审查 SKILL.md / CLAUDE.md 与上游知识源（系统提示词、Tool Description、其他 Skill、其他 CLAUDE.md）的重复并去重 |

## 目录结构

```
.
├── .claude-plugin/
│   └── marketplace.json    # marketplace 索引
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json
        └── README.md
```

每个 plugin 可选 `commands/`、`agents/`、`skills/`、`.mcp.json` 等子目录与文件。完整 schema 见 [官方 plugin 文档](https://code.claude.com/docs/en/plugins)。

## 许可证

[MIT](LICENSE) —— 根目录 LICENSE 适用于本 marketplace 及所有 plugin（个别 plugin 若要不同许可，会在自身目录下放置覆盖性 LICENSE）。
