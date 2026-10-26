# kill-guard

> [English version](README.en.md)

一个 Claude Code plugin，只含一个钩子：Claude 要执行的 Bash 命令里出现「按名字或命令行文字找进程再停」的写法时直接挡住，并告诉它改成按进程号停。

## 为什么需要

`pkill -f` 拿整条命令行做子串匹配。Mac 上几乎所有程序都在 `/Applications` 或 `Application Support` 下，路径里就含 cat、app 这些常见字母。一条 `pkill -f "cat"` 曾把 Claude 桌面端、所有并行会话、Chrome、微信一起杀掉，正在做的工作和没保存的内容全丢了。写在 CLAUDE.md 里的规矩靠模型自觉；开着跳过权限确认时，执行那一刻没有任何东西拦它。这个钩子在执行前把它挡住。

## 挡什么、放什么

| 挡住 | 放行 |
|---|---|
| `pkill …`、`killall …`（含 `sudo`、完整路径） | `kill <进程号>`、`kill $!`、`kill $(cat 进程号文件)` |
| `… \| xargs kill`（`ps \| grep \| xargs kill`、`pgrep \| xargs kill` 等） | `pgrep -fl`、`ps … \| grep …` 只列出来看 |
| `kill $(pgrep …)`、`kill $(pidof …)`、`kill $(ps …)` | `kill $(lsof -ti tcp:<端口> -sTCP:LISTEN)` 按端口只停监听者 |

只看命令所在的位置：`grep pkill 文件`、`echo "别用 pkill"` 这类只是提到这个词的不挡；ssh 到别的机器执行的（引号里的远程命令）也不挡。挡住时命令不执行，Claude 收到原因和改法。

## 安装

本 plugin 通过 [`fomalhaut647-plugins`](../..) marketplace 分发：

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install kill-guard@fomalhaut647-plugins
```

桌面端在「设置 → 插件」里同步本 marketplace 后启用 kill-guard。需要本机有 `python3`。

## 目录结构

```
plugins/kill-guard/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   ├── hooks.json        # PreToolUse，匹配 Bash
│   └── kill_guard.py     # 判断规则和提示语
├── CLAUDE.md
├── README.md             # 本文件（中文）
├── README.en.md          # English
└── RELEASE-NOTES.md
```

## 许可证

MIT —— 见 [marketplace 根目录的 LICENSE](../../LICENSE)。
