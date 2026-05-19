# CLAUDE.md

本文件为后续在本仓库工作的 Claude Code 实例提供指引。

## 仓库用途

我个人的 Claude Code plugins marketplace，发布名为 `fomalhaut647-plugins`。`plugins/` 下每个子目录是一个可独立安装的 plugin；`.claude-plugin/marketplace.json` 是对外发布它们的索引。Marketplace 通过 `/plugin marketplace add Fomalhaut647/plugins` 添加，plugin 通过 `/plugin install <name>@fomalhaut647-plugins` 安装。

目前已发布 `agent-team` 与 `skill-simplifier` 两个 plugin。

## 双源一致性：新增 / 重命名 / 删除 plugin

一个 plugin 只有在以下两处同时存在且一致时才是"真实"的：

1. 目录 `plugins/<name>/` 内含 `.claude-plugin/plugin.json`（`name` 字段须匹配）
2. `.claude-plugin/marketplace.json` 的 `plugins[]` 数组里有对应条目，且 `"source": "./plugins/<name>"`

只改一边而不改另一边会**静默地**让安装失败。任何增删改务必两边同步。本仓库故意不设 `external_plugins/` —— 所有 plugin 都是自家的，统一用本地 `./plugins/<name>` source，不用 git-subdir 或 url source。

## 公开 artifact 中的身份

凡是会公开的 author / owner 字段（`marketplace.json` 的 `owner`、`plugin.json` 的 `author`、git commit author、README 署名、任何可能 push 到 GitHub 的内容）必须使用：

- **Name**：`Fomalhaut647`
- **Email**：`fomalhaut@stu.pku.edu.cn`

绝不能用全局 CLAUDE.md「北大作业 PDF」一节里那个真名 —— 那个身份只用于学术 LaTeX 作业。同样，全局列为 `userEmail` 的 `usafomalhaut@gmail.com` 也不用于本仓库。

## README 是双语 —— 必须同步

`README.md` 是中文主版本；`README.en.md` 是英文镜像。两者顶部互相链接。任何内容改动必须在同一个 commit 里两边一起改。

## 参考克隆 —— 只读，永不 commit

`claude-plugins-official/` 是 Anthropic 官方 marketplace 的本地克隆，已 gitignore，留在这里方便参考 schema 与示例（尤其是 `plugins/example-plugin/` 和 `.claude-plugin/marketplace.json` 的结构）。可随意读；绝不 `git add` 它，也绝不把它的 plugin 整段抄进本仓库。

## 没有 build、没有 tests —— JSON 合法性是唯一校验

这是个静态 marketplace。改完任何 `*.json` 后，校验是否能 parse：

```bash
python3 -c "import json,sys; [json.load(open(p)) for p in sys.argv[1:]]" .claude-plugin/marketplace.json plugins/*/.claude-plugin/plugin.json
```

无法 parse 的 `marketplace.json` 会让所有下游用户的 `/plugin marketplace add` 失败 —— 严重程度等同于把 build 搞坏。
