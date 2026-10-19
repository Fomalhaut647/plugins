# neat-freak

> [English version](README.en.md)

会话结束后的知识收尾：把项目文档、规则文件（CLAUDE.md / AGENTS.md）、Agent 记忆和工作区残留跟代码的真实状态对齐，并审计项目规则有没有被真正执行。[`session-wrap`](../session-wrap) 第 1 步就用它整理文档。

## 来源

原样搬运自 [数字生命卡兹克](https://github.com/KKKKhazix) 的 [khazix-skills](https://github.com/KKKKhazix/khazix-skills) 仓库中的 `neat-freak`（skill 版本 3.0.0，上游提交 `322346d`），只是打包成 plugin 方便从本 marketplace 安装。上游的 evals 测试集没有搬入。plugin 版本号跟随上游 skill 版本。

## 安装

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install neat-freak@fomalhaut647-plugins
```

## 用法

说「整理文档」「同步一下」「更新记忆」「/neat」之类的话即可触发，完整内容见 [`skills/neat-freak/SKILL.md`](skills/neat-freak/SKILL.md)。

## 许可证

MIT，版权归原作者数字生命卡兹克 —— 见本目录的 [LICENSE](LICENSE)。
