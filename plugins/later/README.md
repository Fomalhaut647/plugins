# later

> [English version](README.en.md)

一个 Claude Code plugin，只含一个 skill：Claude 干活时排队一条消息，让它等这一轮整个结束后，才作为一条新的用户消息送到，而不是在某次工具调用结束时跟着工具结果一起插进去。

## 为什么需要

Claude 干活时直接回车发出的消息，会在当前这次工具调用结束后马上并进同一轮。想补充的是「做完手上的事再做」的事情时，中途插进去会打断 Claude 正在做的工作。Claude Code 没有「等整轮结束再发」的设置，但 Claude 回答期间发出的斜杠命令会一直等到这一轮结束才执行。这个 skill 本身什么都不做，只把你写在后面的文字原样转交，借这一点把消息推迟到轮末。

## 用法

Claude 干活时，在输入框里发：

```
/later:later 你的消息
```

这一轮结束后，Claude 收到的就是「你的消息」，跟你那时直接发出去一样。Claude 没在干活时用它，效果和直接发消息相同。

## 实测情况

2026-10-29 在桌面端（Claude Code 2.1.309）以项目内 skill 的形式实测：执行期间排队的消息经过了三次工具调用间隙都没有插进来，这一轮结束后才作为新的用户消息送到。

还没测过的：

- 命令行版
- 一轮里连续排多条时，是逐条送达还是合并成一条

## 安装

本 plugin 通过 [`fomalhaut647-plugins`](../..) marketplace 分发：

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install later@fomalhaut647-plugins
```

桌面端在「设置 → 插件」里同步本 marketplace 后启用 later。

## 目录结构

```
plugins/later/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── later/
│       └── SKILL.md      # 正文只有 $ARGUMENTS
├── CLAUDE.md
├── README.md             # 本文件（中文）
├── README.en.md          # English
└── RELEASE-NOTES.md
```

## 许可证

MIT —— 见 [marketplace 根目录的 LICENSE](../../LICENSE)。
