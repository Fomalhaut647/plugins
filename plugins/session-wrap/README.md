# session-wrap

> [English version](README.en.md)

一个 Claude Code 桌面端 plugin，只含一个 skill，用于给会话收尾：整理本会话改动涉及的文档，收齐子会话的改动后提交并推送，功能分支开 PR、在本轮里等 CI 通过（失败就自己修）后合并进 main（在 main 上就直接推送），关闭本会话修复的 issue，最后归档本会话。用户要求时，合并前先开子会话用 `code-review` 审查。

## 安装

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install session-wrap@fomalhaut647-plugins
```

## 前置条件

- Claude Code 桌面端：开子会话、读子会话结果和归档会话都依赖桌面端的会话工具。
- 已装 GitHub CLI `gh`，用于开 PR、等 CI、合并和关闭 issue。

## 用法

只有原话里一字不差地出现 session-wrap 这个词（连字符、大小写不算不同）才会启用，「收尾」「合并吧」之类的说法不会触发。可以附带参数：

| 说法 | 效果 |
|---|---|
| 调用 session-wrap | 整理、提交、合并、关 issue、归档 |
| 调用 session-wrap，合并前 review | 合并前开一个子会话审查，只修大 bug |
| 调用 session-wrap，多轮 review | 修完再开新子会话审，直到某一轮没有大 bug |

完整内容见 [`skills/session-wrap/SKILL.md`](skills/session-wrap/SKILL.md)。

## 许可证

MIT —— 见 [marketplace 根目录的 LICENSE](../../LICENSE)。
