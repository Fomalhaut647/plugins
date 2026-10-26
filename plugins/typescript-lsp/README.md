# typescript-lsp

> [English version](README.en.md)

让 Claude Code 通过 typescript-language-server 理解 TypeScript 和 JavaScript 代码：改完文件自动拿到类型错误等诊断，还能跳转定义、查找引用。

## 来源

搬运自 Anthropic 官方 marketplace [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) 中的 `typescript-lsp`（plugin 版本 1.0.0，上游提交 `58267944`），方便在 Claude 桌面端从本 marketplace 安装。唯一的改动是把语言服务器配置从上游的 marketplace 条目挪进本目录的 `.lsp.json`，内容不变。plugin 版本号跟随上游，只有本地改动时升 patch。

## 前置：安装语言服务器

plugin 只告诉 Claude Code 怎么启动语言服务器，`typescript-language-server` 命令要自己装好、能在 PATH 里找到：

```bash
brew install typescript-language-server
```

Homebrew 会一并装上它依赖的 TypeScript。也可以用 `npm install -g typescript-language-server typescript`。

## 安装

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install typescript-lsp@fomalhaut647-plugins
```

## 支持的文件

`.ts`、`.tsx`、`.js`、`.jsx`、`.mts`、`.cts`、`.mjs`、`.cjs`

## 许可证

Apache-2.0，上游作者为 Anthropic —— 见本目录的 [LICENSE](LICENSE)。
