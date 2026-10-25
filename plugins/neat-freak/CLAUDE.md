# neat-freak —— 贡献者指南

本 plugin 是 [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) 中 `neat-freak` 的搬运，不是自家作品。

- **不改 skill 内容**：`skills/neat-freak/` 下的文件与上游保持一致，只做同步，不做本地修改。要改行为就向上游提。唯一例外是 SKILL.md 开头的 `disable-model-invocation: true`（2026-10-25 Fomalhaut647 定：只许用户手动调用，简介也不进上下文），同步上游后要补回来。
- **同步方式**：用上游最新的 `neat-freak/SKILL.md`、`references/`、`scripts/` 整体覆盖 `skills/neat-freak/`；不搬 `evals/`（其中的 CLAUDE.md 等测试夹具会被在本仓库工作的会话误当成规则加载）。同步后把 `plugin.json` 的 `version` 改成上游 SKILL.md 里的 `metadata.version`（只动本地例外时升 patch），并更新两份 README 里的上游提交号和根目录 README 的版本列。
- **保留 LICENSE**：本目录的 `LICENSE` 是上游原文，版权属于原作者，必须随 skill 一起分发，不能换成根目录的 LICENSE。
