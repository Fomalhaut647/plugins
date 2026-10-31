> [English version](README.en.md)

# fomalhaut647-plugins

我个人的 Claude Code plugins marketplace。

## 安装

### 在 Claude 桌面端

打开「设置 → 插件」，点右上角「添加」，选择添加市场，填入 `Fomalhaut647/plugins`（或完整 URL `https://github.com/Fomalhaut647/plugins`），点「同步」。同步完成后，本仓库的 plugin 会出现在插件列表里，逐个启用即可。

![在 Claude 桌面端添加本 marketplace](docs/images/desktop-add-marketplace.webp)

### 在 Claude Code CLI

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
| [`agent-team`](plugins/agent-team) | v3.0.0 | 在 Claude Code 桌面端让当前会话当主会话，把工作拆给并行子会话：开工前定验收清单，每块审查一次、有预算地修复，最后整合审查并合并成一个 PR；开发也可以交给本机的 Codex |
| [`kill-guard`](plugins/kill-guard) | v0.1.0 | 挡住按名字或命令行文字找进程再停的命令（`pkill`、`killall`、`xargs kill`、`kill $(pgrep …)`），让 Claude 改成按进程号停 |
| [`later`](plugins/later) | v0.1.0 | Claude 干活时排队一条消息，等这一轮整个结束后才作为新的用户消息送到，不在工具调用间隙插进去 |
| [`neat-freak`](plugins/neat-freak) | v3.0.1 | 会话结束后把项目文档、CLAUDE.md、Agent 记忆跟代码对齐，并审计规则执行情况；搬运自[数字生命卡兹克的 khazix-skills](https://github.com/KKKKhazix/khazix-skills) |
| [`pyright-lsp`](plugins/pyright-lsp) | v1.0.0 | Python 语言服务器（Pyright），给 Claude Code 类型诊断和跳转定义；搬运自 [Anthropic 官方 marketplace](https://github.com/anthropics/claude-plugins-official) |
| [`session-wrap`](plugins/session-wrap) | v0.5.0 | 在 Claude Code 桌面端给会话收尾：整理文档、收齐子会话的改动后提交推送、开 PR 等 CI 后合并、关闭修复的 issue、归档会话 |
| [`skill-simplifier`](plugins/skill-simplifier) | v0.3.0 | 审查 SKILL.md / CLAUDE.md，删除上游重复和全新会话模型本不会犯的假想防错 |
| [`typescript-lsp`](plugins/typescript-lsp) | v2.1.0 | 用 TypeScript 7 自带的语言服务器给 Claude Code 提供 TypeScript / JavaScript 类型诊断和跳转定义，改完文件自动推送错误；改编自 [Anthropic 官方 marketplace](https://github.com/anthropics/claude-plugins-official) |

## 目录结构

```
.
├── .claude-plugin/
│   └── marketplace.json    # marketplace 索引
├── docs/images/            # README 用到的截图
├── LICENSE                 # 适用于本 marketplace 及自家 plugin
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/plugin.json
        ├── skills/             # 或 commands/ / agents/
        ├── README.md           # 中文（双语主版本）
        ├── README.en.md        # 英文镜像
        ├── CLAUDE.md           # plugin 自己的贡献者指南
        └── RELEASE-NOTES.md
```

每个 plugin 还可选 `.mcp.json`、`.lsp.json` 等附加文件。完整 schema 见 [官方 plugin 文档](https://code.claude.com/docs/en/plugins)。

## 许可证

[MIT](LICENSE) —— 适用于本 marketplace 及所有自家 plugin。`neat-freak` 是第三方作品，沿用其原作者的 MIT 许可证，见 [plugins/neat-freak/LICENSE](plugins/neat-freak/LICENSE)。`pyright-lsp` 和 `typescript-lsp` 源自 Anthropic，沿用 Apache-2.0 许可证，见各自目录下的 LICENSE。
