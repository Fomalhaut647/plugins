# pyright-lsp

> [English version](README.en.md)

让 Claude Code 通过 Pyright 语言服务器理解 Python 代码：改完文件自动拿到类型错误等诊断，还能跳转定义、查找引用。

## 来源

搬运自 Anthropic 官方 marketplace [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) 中的 `pyright-lsp`（plugin 版本 1.0.0，上游提交 `58267944`），方便在 Claude 桌面端从本 marketplace 安装。唯一的改动是把语言服务器配置从上游的 marketplace 条目挪进本目录的 `.lsp.json`，内容不变。plugin 版本号跟随上游，只有本地改动时升 patch。

## 前置：安装 Pyright

plugin 只告诉 Claude Code 怎么启动语言服务器，`pyright-langserver` 命令要自己装好、能在 PATH 里找到：

```bash
brew install pyright
```

也可以用 `npm install -g pyright` 或 `pipx install pyright`。

## 安装

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install pyright-lsp@fomalhaut647-plugins
```

## 支持的文件

`.py`、`.pyi`

## 许可证

Apache-2.0，上游作者为 Anthropic —— 见本目录的 [LICENSE](LICENSE)。
