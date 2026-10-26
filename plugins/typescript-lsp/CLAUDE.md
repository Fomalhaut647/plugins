# typescript-lsp —— 贡献者指南

本 plugin 是 [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) 中 `typescript-lsp` 的搬运，不是自家作品。

- **配置跟上游保持一致**：`.lsp.json` 等于上游 `.claude-plugin/marketplace.json` 里 `typescript-lsp` 条目的 `lspServers`。上游目录只有 README 和 LICENSE，配置写在 marketplace 条目里（`strict: false`）；本仓库改放 `.lsp.json`，让 plugin 目录自带完整配置。
- **同步方式**：对照上游条目的 `lspServers` 和 `version` 更新 `.lsp.json` 与 `plugin.json`，再更新两份 README 里的上游提交号和根目录 README 的版本列。版本号跟随上游，只有本地改动时升 patch。
- **保留 LICENSE**：本目录的 `LICENSE` 是上游原文（Apache-2.0），必须随 plugin 一起分发，不能换成根目录的 MIT LICENSE。
