# later —— 贡献者指南

- 整个 plugin 靠一条实测过的行为：Claude 回答期间发出的斜杠命令会等这一轮结束才执行，普通消息则在下一次工具调用结束时插进同一轮。前半句官方命令文档有写（"runs after the current turn finishes"）。Claude Code 改了这个行为，本 plugin 就失效，改动前先重测。
- `SKILL.md` 正文只有 `$ARGUMENTS`，让 Claude 收到的内容和用户直接发的一样。不要往正文里加说明或指令。
- 保持 `disable-model-invocation: true`：这个 skill 只给用户手动排队用，模型自己调用没有意义。
- 重测方法：在桌面端让 Claude 依次执行几条各约 20 秒的命令，期间发一条 `/later:later 测试`，再看这条消息是在哪次工具调用后送到的。会话记录 JSONL（`~/.claude/projects/<项目>/<会话 id>.jsonl`）里 `queue-operation` 的 `enqueue` / `dequeue` 时间戳可以和工具调用的时间对照。
- 改了行为就升 `plugin.json` 的版本号，写进 `RELEASE-NOTES.md`，README 中英两份一起改。
