# model-trio

> [English version](README.en.md)

一个 Claude Code plugin：让 Claude 站在中间，把合适的活交给本机的另外两家模型，结果由 Claude 核实后再告诉你。

- **Codex（GPT）** 干活严谨：写成块的后端、算法、数据处理，审查代码，做只读调研。
- **Antigravity（Gemini）** 点子多、文案好，但粗心：独立出一份方案，给界面文案和交互提修改意见。它只读、只给意见。

分工照[数字生命卡兹克《毫无保留地分享一下，我是如何让 Claude、GPT 和 Gemini 完美协同的。》](https://mp.weixin.qq.com/s/gwj0xLNHPfToQnQJN7IkMA)里的工作流。和文章不同的一点：文章把分派规则写进 CLAUDE.md，由 Claude 主动分派；这里的两个 skill 只在你的话里明确提到 Codex 或 Antigravity 时才启用。

## 要求

- 本机装好并登录 Codex 命令行（`codex`）和 [Antigravity 命令行](https://antigravity.google/docs/getting-started)（`agy`）。只用其中一个时，另一个可以不装。
- python3（3.9 及以上，不需要额外的包）。
- 交给 Codex 的目录要在 git 工作副本里。

## 安装

本 plugin 通过 [`fomalhaut647-plugins`](../..) marketplace 分发：

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install model-trio@fomalhaut647-plugins
```

桌面端在「设置 → 插件」里同步本 marketplace 后启用 model-trio。

## 用法

在对话里说一句带「Codex」「Antigravity」「Gemini」或「agy」的话，也可以手动调用 `/model-trio:codex`、`/model-trio:antigravity`。

### Codex

- 「这个导入模块交给 Codex 写」：Claude 定好接口和验收标准写成任务书，Codex 写完后，Claude 自己读改动、运行测试，通过了才算完成。你没有指定交哪一部分时，Claude 只把接口已经定死、和页面无关的独立模块交出去，小修改、前端和视觉自己做。
- 「用 Codex 审一下刚才的改动」：Codex 用它自带的审查流程审，Claude 逐条对照代码复核，丢掉不成立的。成立的分两级：会丢数据、算错钱、越权、发错消息或让发布出事故，并且说得出具体怎么发生的，必须修；其余只作建议列给你。只审一轮。
- 「让 Codex 查一下这个 bug 的原因」：只读调研。

### Antigravity

- 「这个方案让 Gemini 也出一份」：Claude 自己出一份，同时只把你的原话和必要背景交给 Gemini，不给它自己的草稿和倾向。两份由 Claude 合并成一份给你，写明两份一致的、采纳了 Gemini 的、不采纳的和理由；两边都有道理、定不下来的，原样摆给你拍板。
- 「这一页的文案请 Gemini 改一遍」：Claude 先做一版，告诉 Gemini 这一页是给谁用的、要让人做成什么，请它修改；它的修改由 Claude 对照功能实际怎么用核实后采纳。

模型和思考强度默认用两个命令行各自的设置，对话里指定了就按你说的。调用超过两分钟时，Claude Code 会自动把它转到后台，Claude 可以先做别的，完成时会收到通知。

## 它们能动什么

- **Codex**：不管你的 Codex 设置是不是完全放开，这里都把它限制在沙箱里。调研和审查时只读；写代码时只能写交给它的那个目录。不联网，不提交、不推送：装依赖、要联网的测试和提交都由 Claude 做。
- **Antigravity**：不能改任何文件。它在一个空目录里运行，项目目录只以只读方式授权给它，能读文件、能运行只读命令。

## 实测情况

2026-11-26，Claude Code 2.1.325、Antigravity 命令行 1.5.17：

- 用真实的 Claude Code 加载本 plugin，两个工具和两个 skill 都能加载，经工具调用 Antigravity 并拿到回复。
- Antigravity 只读：让它写文件、用命令创建文件，都被拒绝，读文件和 `git log` 正常；续接上一次对话正常。
- 取消调用、关闭 Claude Code 时，运行中的子进程会被停掉。

还没测过的：

- **真实的 Codex 调用**。测试时本机的 Codex 没有登录，只用替身程序核对了调用它的命令行；命令行的写法沿用 `agent-team` 里经真实 Codex 验证过的那一份。
- 运行超过两分钟后转到后台、在 `/tasks` 里停止的实际表现。

## 目录结构

```
plugins/model-trio/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json                 # 注册 MCP 服务器
├── server.py                 # MCP 服务器：codex、antigravity 两个工具
├── skills/
│   ├── codex/SKILL.md        # 什么活交给 Codex、交回后怎么核实
│   └── antigravity/SKILL.md  # 怎么请 Antigravity 出方案、改文案
├── CLAUDE.md                 # 贡献者指南
├── README.md                 # 本文件（中文）
├── README.en.md              # English
└── RELEASE-NOTES.md
```

## 许可证

MIT —— 见 [marketplace 根目录的 LICENSE](../../LICENSE)。
