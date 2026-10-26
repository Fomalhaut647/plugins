# typescript-lsp

> [English version](README.en.md)

让 Claude Code 通过 TypeScript 7 自带的语言服务器（`tsc --lsp`）理解 TypeScript 和 JavaScript 代码：改完文件自动拿到类型错误等诊断，还能跳转定义、查找引用。

## 来源

改编自 Anthropic 官方 marketplace [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) 中的 `typescript-lsp`（plugin 版本 1.0.0，上游提交 `58267944`），方便在 Claude 桌面端从本 marketplace 安装。和上游的区别：

- 语言服务器从 typescript-language-server 换成 TypeScript 7 自带的 `tsc --lsp --stdio`。TypeScript 7 用 Go 重写后不再带 typescript-language-server 依赖的 tsserver，Homebrew 的 TypeScript 升到 7 之后，上游配置就启动不了了。
- 语言服务器配置从上游的 marketplace 条目挪进本目录的 `.lsp.json`。

从 v2.0.0 起版本号自行维护，不再跟随上游。

## 前置：安装 TypeScript 7

plugin 只告诉 Claude Code 怎么启动语言服务器，TypeScript 7 或更新版本的 `tsc` 命令要自己装好、能在 PATH 里找到：

```bash
brew install typescript
```

也可以用 `npm install -g typescript`。TypeScript 6 及更早版本的 `tsc` 没有 `--lsp` 模式，用不了。

## 安装

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install typescript-lsp@fomalhaut647-plugins
```

## 支持的文件

`.ts`、`.tsx`、`.js`、`.jsx`、`.mts`、`.cts`、`.mjs`、`.cjs`

## 许可证

Apache-2.0，上游作者为 Anthropic —— 见本目录的 [LICENSE](LICENSE)。
