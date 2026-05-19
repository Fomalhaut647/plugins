# skill-simplifier 版本说明

## Unreleased

初版骨架。

- 新增 skill `skill-simplifier`: 审查一份 SKILL.md (含可选 `references/`) 或一份 CLAUDE.md 与上游知识源 (系统提示词 / Tool Description / 其他 Skill / 其他 CLAUDE.md) 之间的重复, 按"自动删 (Zone A) / 用户决定 (Zone B) / 内部分层 (Zone C)" 三区方法分类处理。
- 单 skill, 单文件 SKILL.md (无 `references/`)。
- 作为 `fomalhaut647-plugins` marketplace 的一员发布; LICENSE 由 marketplace 根目录统一提供。
- 文档双语: 英文 `README.en.md` + 中文 `README.md`; `CLAUDE.md` 和本文件为中文。
