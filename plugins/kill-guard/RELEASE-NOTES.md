# kill-guard 版本说明

## v0.1.0

初版，通过 `fomalhaut647-plugins` marketplace 首次发布。

- PreToolUse 钩子，匹配 Bash：挡住 `pkill`、`killall`、`… | xargs kill`、`kill $(pgrep|pidof|ps …)`，退出码 2 把原因和改法交给 Claude。
- 只认命令所在的位置，只是提到这个词的命令和 ssh 的远程命令不挡。
