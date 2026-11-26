# model-trio —— 贡献者指南

## 改动前

- **保持简单**（用户的决定）。MCP 服务器和两个 skill 都只写用得上的东西，新增规则或保护措施要有真实使用中观察到的问题作依据，不加臆想的防御。下面每条设计都对应一次实测，改之前先读。
- 改了行为就升 `plugin.json` 的版本号（服务器报给 Claude Code 的版本从它读），写进 `RELEASE-NOTES.md`，README 中英两份一起改。

## 设计要点

- **两个 skill 只在用户提到时启用**（用户的决定）。文章把分派规则写进 CLAUDE.md、由 Claude 主动分派，这里不这样做：简介里写明「只在用户的话里明确提到……时启用，不主动发起」，不要改成主动。
- **工具调用是同步的**。服务器起一个子进程，等它结束后返回汇报，不自建后台、进度和停止机制：Claude Code 会把主会话里超过两分钟的 MCP 调用自动转成后台任务，完成时通知 Claude，用户可以在 `/tasks` 里停掉（官方 MCP 文档 "Automatic backgrounding of long tool calls"）。每次调用跑在单独的线程里，Claude 才能同时调用两个工具。
- **`.mcp.json` 里的 `timeout` 是 4 小时**。stdio 服务器 30 分钟没有响应也没有进度通知，调用就会被中止；Codex 一次任务可能超过这个时间。按服务器设的 `timeout` 同时是空闲时限的下限（官方 MCP 文档 "Time limits on MCP tool calls"），所以设一个够长的值，不发进度通知。
- **服务器不用第三方包**。只实现 `initialize`、`tools/list`、`tools/call`、`ping` 和取消通知，装了 python3 就能运行。协议版本固定回 `2025-06-18`。
- **取消和退出时停掉子进程**。子进程自成一个进程组，收到取消通知（用户在 `/tasks` 里停止）或标准输入关闭（Claude Code 退出）时整组停掉，否则 Codex 会在没人看着的情况下继续改文件。
- **Codex 始终在沙箱里**。不管用户的 Codex 设置是不是完全放开（文章也提到 `codex exec` 默认完全访问），调研和审查用只读沙箱，写代码用只能写工作目录的沙箱，不开联网：照文章的分工，装依赖、联网测试、提交推送由 Claude 做。调用 Codex 的命令行沿用 `plugins/agent-team/skills/lead/codex.sh` 里经真实 Codex 验证过的写法；审查走 `codex exec review`，用它自带的审查流程。
- **固定规矩由服务器追加在任务书后面**，Claude 不用每次重写：Codex 不提交不推送、最后一条消息就是汇报；审查的每条发现带位置和出错场景；Antigravity 只读、没核实的判断标「推测」（文章里 Claude 对它标了推测的内容要先核实）。
- **模型和思考强度不写死**，不传就用两个命令行各自的设置。文章里的型号在用户的 Codex 模型列表里并不存在。
- **Antigravity 的只读是这样做到的**：让它在插件数据目录下的一个空目录里运行，用 `--settings` 传入本次有效的权限规则，把项目目录授权成只读（`read_file(<项目>)`），并禁止文件写入工具（`write_file(*)`）。2026-11-26 用 1.5.17 逐一试过别的做法，都不行：
  - 什么都不设：非交互模式默认是 auto 模式，直接改文件、运行命令。
  - `--mode plan`：命令需要批准，没人批准时被拒绝，这一轮当场结束，回复是空的。
  - 只禁止 `write_file(*)`：文件工具被挡住，但命令仍能写它的工作目录（`touch`、重定向都成功）。
  - 再禁止 `command(*)`：它没有不靠命令的列目录、搜代码的办法，只能读已知路径的文件，没法看项目。
  - 现在的做法：它的命令沙箱只允许写自己的工作目录，项目在工作目录之外，命令写不进去（`Operation not permitted`），读不受影响，被拒绝后这一轮照常继续。
  - `--settings` 在 `agy --help` 里有，官方文档当时还没写。
- **给 Antigravity 设了 `GIT_CONFIG_GLOBAL`**。它的命令沙箱读不到用户主目录下的 git 配置，`git` 一运行就报错退出；让 git 不读全局配置后，`git log`、`git status` 正常。

## 重测方法

改了 `server.py` 或 `.mcp.json` 之后，用真实的 Claude Code 加载本 plugin 调用一次：

```bash
claude --plugin-dir plugins/model-trio --model haiku --allowedTools "mcp__plugin_model-trio_peers__antigravity" -p "调用 mcp__plugin_model-trio_peers__antigravity，cwd 是 <某个项目的绝对路径>，task 是「读 README，用一句话说这个项目是做什么的」，把工具结果原样打印出来。"
```

Codex 同理，把工具名换成 `mcp__plugin_model-trio_peers__codex`，加上 `mode`。

## 还没验证的

- 真实的 Codex 调用：初版开发时本机的 Codex 没有登录，只用替身程序核对了命令行参数、续接、审查、出错和取消几条路径。
- 调用超过两分钟转到后台后，结果通知和在 `/tasks` 里停止的实际表现；超过 30 分钟的调用。
