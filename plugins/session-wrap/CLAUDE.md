# session-wrap —— 贡献者指南

skill 只有 `skills/session-wrap/SKILL.md` 一个文件，刻意保持几句话的篇幅。

- **启用条件不可放宽**：description 把启用限定为用户原话里一字不差地出现「调用 session-wrap」。收尾会推送、合并、删分支、归档会话，误触发代价大，改 description 时必须保留这条限制。
- **不重述平台规则**：`start_session`、`list_events`、`archive_session` 等工具的用法以工具说明和桌面端系统提示词为准，skill 只写它们没覆盖的收尾流程。
- **不堆边界情况**：新增规则要有真实收尾会话里观察到的失败作为依据，能交给模型现场判断的不写。
