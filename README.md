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
├── LICENSE                 # 适用于本 marketplace 及所有 plugin
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/plugin.json
        ├── skills/             # 或 commands/ / agents/
        ├── README.md           # 中文（双语主版本）
        ├── README.en.md        # 英文镜像
        ├── CLAUDE.md           # plugin 自己的贡献者指南
        └── RELEASE-NOTES.md
```

每个 plugin 还可选 `.mcp.json` 等附加文件。完整 schema 见 [官方 plugin 文档](https://code.claude.com/docs/en/plugins)。

## 许可证

[MIT](LICENSE) —— 适用于本 marketplace 及所有 plugin。
