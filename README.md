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
| [`agent-team`](plugins/agent-team) | placeholder | 多 agent 协作团队，用于长程多轮 Claude Code 协同 |
| [`skill-simplifier`](plugins/skill-simplifier) | placeholder | 审查并简化已有的 Claude Code skills |

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

每个 plugin 可选 `commands/`、`agents/`、`skills/`、`.mcp.json`、`LICENSE` 等子目录与文件。完整 schema 见 [官方 plugin 文档](https://code.claude.com/docs/en/plugins)。
