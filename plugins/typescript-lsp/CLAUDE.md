# typescript-lsp —— 贡献者指南

本 plugin 改编自 [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) 中的 `typescript-lsp`，不是自家作品。

- **启动命令和上游不同**：`.lsp.json` 启动的是 TypeScript 7 自带的 `tsc --lsp --stdio`，不是上游的 typescript-language-server。2026-10-26 Fomalhaut647 定：TypeScript 7 不再带 tsserver，Homebrew 装出来的上游组合启动不了。上游目录只有 README 和 LICENSE，配置写在 marketplace 条目里（`strict: false`）；本仓库放在 `.lsp.json`。
- **同步上游**：只同步上游条目 `lspServers` 里的扩展名映射（`extensionToLanguage`），启动命令保持本地版本；同步后更新两份 README 里的上游提交号。版本号从 v2.0.0 起自行维护，按根目录 CLAUDE.md 的 semver 规则升。
- **保留 LICENSE**：本目录的 `LICENSE` 是上游原文（Apache-2.0），必须随 plugin 一起分发，不能换成根目录的 MIT LICENSE。
