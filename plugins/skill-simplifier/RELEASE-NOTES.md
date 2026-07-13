# skill-simplifier 版本说明

## v0.2.0

- 新增 Stage 4 全新会话反事实检查：排除当前对话污染，识别未污染模型本不会犯的假想防错。
- 新增自动删除的 Zone B；原用户决定区与内部分层区顺延为 Zone C / Zone D，报告与应用顺延为 Stage 5 / Stage 6。

## v0.1.0

初版骨架，通过 `fomalhaut647-plugins` marketplace 首次发布。

- 新增 skill `skill-simplifier`：审查一份 SKILL.md（含可选 `references/`）或一份 CLAUDE.md 与上游知识源（系统提示词 / Tool Description / 其他 Skill / 其他 CLAUDE.md）之间的重复，按"自动删（Zone A）/ 用户决定（Zone B）/ 内部分层（Zone C）"三区方法分类处理。
- 单 skill，单文件 SKILL.md（无 `references/`）。
- 文档双语：英文 `README.en.md` + 中文 `README.md`；`CLAUDE.md` 和本文件为中文。
