# agent-team

> [English version](README.en.md)

一个 Claude Code plugin，提供两个 subskill 用于协调长期运行的多 agent 团队，外加可选 reference docs 用于在其上叠加 `superpowers` 软件开发工作流。

- **Primitive skills**（`agent-team:lead` / `agent-team:teammate`）覆盖团队机制本身 —— `TeamCreate`、spawn 规则、inbox sync、shutdown 顺序 —— 独立于任何特定开发方法论。
- **Optional reference docs** 位于各 skill 的 `references/` 目录下，在 primitive 之上叠加完整的 `superpowers` 软件开发工作流（brainstorming → writing-plans → TDD implementers → reviewer teammates → PR fix loop → merge）。lead skill 的 Step 3 决策时按需 Read；spawn prompt 在 workflow 信号触发时让 teammate Read 对应的 doc。

把 superpowers workflow 作为 reference doc 而非独立 skill，可以让 per-session skill 数量和 description-context 开销保持低水位，同时保留全部内容。

## 安装

本 plugin 通过 [`fomalhaut647-plugins`](../..) marketplace 分发。两步安装：

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install agent-team@fomalhaut647-plugins
```

本地开发（marketplace 未推到远端）时，把 GitHub 路径替换为 marketplace 仓库的绝对路径：

```
/plugin marketplace add <marketplace 仓库绝对路径>
/plugin install agent-team@fomalhaut647-plugins
```

## Subskills

| Subskill | 激活时机 | 涵盖 |
|---|---|---|
| `agent-team:lead` | 人类用户需要多 agent 长期协调时 | `TeamCreate`、spawn prompt 模板（让 teammate invoke `agent-team:teammate`）、任务分配、hub-and-spoke 拓扑、shutdown 序列、merge + cleanup 顺序、是否再读 superpowers workflow doc 的决策 |
| `agent-team:teammate` | team lead 的 spawn prompt（新 teammate 的第一动作是 `Skill('agent-team:teammate')`） | 每步 + SendMessage 前的 inbox sync 协议（`TeamCreate` 自动 between-turns delivery 的 within-turn 补充）、"no nested teams" 框架限制、完成报告、可选 superpowers workflow reference |

两者都用 `ToolSearch` 加载 deferred coordination tools (`TeamCreate`、`TeamDelete`、`SendMessage`、`Task*` 族、`EnterWorktree`、`ExitWorktree`) 的实时 schema，而非重述它们。

## Optional reference docs

| Doc | 由谁 Read | 涵盖 |
|---|---|---|
| `skills/lead/references/superpowers-workflow.md` | lead，运行完整 superpowers 开发工作流时 | Step 1-3（brainstorming、writing-plans、worktree 创建循环 + spawn）、Step 8（reviewer teammate spawn）、Step 10（merge + cleanup，使用 `ExitWorktree(action="remove")`） |
| `skills/teammate/references/superpowers-implementer.md` | implementer teammate，被 spawn 进 superpowers workflow 并带 worktree + spec + plan 时 | Step 4 startup（quadruple skill invoke 含 `requesting-code-review`、`EnterWorktree`、Read brief）、Step 5 implementer subagent prompt 模板、Step 6 两阶段 review subagent pattern、Step 7 PR 提交 + per-teammate progress 文件、Step 9 implementer 这一侧的 fix loop |
| `skills/teammate/references/code-review.md` | reviewer teammate（`reviewer-pr-<N>`），spawn 时带 PR URL | review loop —— invoke `code-review:code-review`、用 `gh pr comment` 发布，首行约定 `**APPROVED**` / `**Changes requested**`、与 implementer 之间的 SendMessage 握手直至批准 |

Note：`superpowers-workflow.md` 同时描述了一个可选的 `docs/` 项目 layout（`vision.md` / `overview.md` / `specs/A-xxx.md` / `plans/PlanN-<teammate>.md` / `progress/PlanN-<teammate>.md`），适合跨多次 agent-team session 的长期项目。详见其 Step 0。

## Composition

- **纯团队协调**（不带 superpowers）：lead invoke `agent-team:lead`，在 Step 3 决定不 Read workflow doc；spawn prompt invoke `agent-team:teammate`。
- **Superpowers workflow team**：lead invoke `agent-team:lead`，在 Step 3 Read `lead/references/superpowers-workflow.md`；spawn prompt invoke `agent-team:teammate` *并* 告诉新 teammate 在 startup 时 Read 对应的 teammate-side doc（implementer 读 `superpowers-implementer.md`，reviewer teammate 读 `code-review.md`）。

各 skill 不会自动激活 —— lead 负责 invoke 正确的 pair，每个 spawn prompt 命名新 teammate 应当一同 Read 的文档。

## 使用方法

### 纯协调

需要多 agent 长期协作时 invoke `Skill('agent-team:lead')`。按它的 workflow 执行；spawn teammate 时让其第一动作是 `Skill('agent-team:teammate')`。

### Superpowers 驱动的协调

Invoke `Skill('agent-team:lead')`，在 Step 3 Read `references/superpowers-workflow.md` 获取 orchestration。Spawn teammate 时让其第一动作是 `Skill('agent-team:teammate')`，并在 startup 指令里让它 Read 对应的 teammate-side reference doc（implementer 读 `references/superpowers-implementer.md`，reviewer teammate 读 `references/code-review.md`）。

## 目录结构

```
plugins/agent-team/
├── .claude-plugin/
│   └── plugin.json         # Plugin metadata
├── skills/
│   ├── lead/
│   │   ├── SKILL.md
│   │   └── references/superpowers-workflow.md
│   └── teammate/
│       ├── SKILL.md
│       └── references/
│           ├── code-review.md
│           └── superpowers-implementer.md
├── CLAUDE.md               # Contributor 指南（AI agent PR 前必读）
├── README.md               # 本文件（中文）
├── README.en.md            # 英文版本
└── RELEASE-NOTES.md        # 版本历史
```

LICENSE 在 marketplace 仓库根目录，适用于本 plugin 与所有其他 plugin。

## 设计原则

- **Lead vs teammate**：两者的 first actions 和 ongoing protocols 不重叠；混进一个 skill 会让任一角色读到 500+ 行无关内容。
- **Skill vs reference doc**：superpowers workflow 是 team primitive 的一种使用模式 —— 不总相关。保留为 reference doc 意味着不用时上下文成本为零，用时内容完整。

## License

MIT —— 详见 [marketplace 根目录的 LICENSE](../../LICENSE)。
