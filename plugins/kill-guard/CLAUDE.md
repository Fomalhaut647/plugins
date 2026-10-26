# kill-guard —— 贡献者指南

- 规则和提示语都在 `hooks/kill_guard.py`。改规则前先想清楚两头：漏挡会让误杀重演，误挡会让 Claude 连提到这个词的命令都跑不了。
- 改完照下面这样喂几条命令，确认该挡的退出码是 2、该放的是 0，至少覆盖 README「挡什么、放什么」表里的每一种：

```bash
printf '%s' '{"tool_input":{"command":"pkill -f cat"}}' | python3 plugins/kill-guard/hooks/kill_guard.py; echo $?
```

- 只用 Python 标准库，不引第三方依赖。
- 改了行为就升 `plugin.json` 的版本号，写进 `RELEASE-NOTES.md`，README 中英两份一起改。
