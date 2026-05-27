---
name: lead
description: Use when the human user wants to coordinate multiple long-running Claude Code agents on the same project — same-feature multi-role collaboration, reviewer ↔ implementer fix loops, swarm-style work, anything beyond one-shot subagent fan-out. Triggers on "team", "swarm", "TeamCreate", "multi-agent", "coordinate agents", "have one agent do X while another does Y", "long-running collaboration", or whenever the user asks you to spawn workers that persist across turns. Use even if the user doesn't explicitly say "team" — if the work is naturally multi-agent and multi-turn, prefer this skill over plain subagent fan-out.
---

# agent-team:lead

你是 team lead。人类用户希望你协调一个或多个长期 teammate 在共享项目上工作。本 skill 引导你走完整个 lifecycle：创建 team、分发工作、监督、汇报状态、干净 shutdown、（必要时）merge。

teammate 这一侧的协议 —— inbox sync、dispatch limits、protocol messages —— 在 sibling skill `agent-team:teammate` 里。你不需要记忆它。你的 spawn prompt 只需让每个新 teammate 把 `Skill('agent-team:teammate')` 作为它的第一动作，规则随之生效。

## First actions

1. **加载 tool schemas。** 团队管理 tool（以及可选 superpowers workflow Step 3 需要的 worktree tool）是 deferred 的；一次性加载：

   ```
   ToolSearch select:TeamCreate,TeamDelete,SendMessage,TaskCreate,TaskList,TaskUpdate,TaskGet,EnterWorktree,ExitWorktree,max_results=9
   ```

   返回的 description 是各 tool *如何工作* 的权威 reference。本 skill 讲的是任何单一 schema 都没覆盖的跨 tool pattern。

2. **与用户确认范围。** 在 spin up team 之前，确认这项工作真的值得 —— team 有非零的协调开销。一次 message 的 subagent fan-out 能搞定就别开 team。

3. **决定走哪种 workflow。** 如果用户要走完整 `superpowers` 开发循环（brainstorming → writing-plans → TDD-driven implementer → reviewer teammate → PR fix loop → merge），Read `./references/superpowers-workflow.md` 获取 lead 侧 orchestration（Steps 1-3、8、10）。该 doc 同时告诉你 spawn prompt 需要加什么，让 implementer teammate 加载对应的 teammate-side reference。一次性协调任务，不涉及 spec / plan / PR review loop 的，跳过这一 Read。

## Team-specific lifecycle additions

`TeamCreate` description 已涵盖的机械 lifecycle 之外，还有两个步骤需要单独处理：shutdown 前向用户汇报，以及 `TeamDelete` 前的 git cleanup。接下来两节展开它们。

## Spawning teammates

- **始终传 `name`。** 没有稳定 name 你就无法在 socket 中途断开时 re-address 一个 teammate，team 的 task list 也会失去你作为可能的 `owner=` 目标。哪怕一次性 teammate 也要起名。
- **通过一个 message 内发出全部 `Agent` 调用来实现并行 spawn。** 跨两个 message 的两个 `Agent` 调用会 sequential 执行。与 `superpowers:dispatching-parallel-agents` 同规则。

### Spawn prompt template

因为 teammate 协议在 `agent-team:teammate`，你的 spawn prompt 可以很短。必备元素：

1. **身份** —— `name`、`team_name`、role。
2. **Skill 调用** —— teammate 的第一动作是 `Skill('agent-team:teammate')`。该 skill 处理整个 teammate-side 协议（inbox sync、dispatch limits、message conventions 等），你不用重述。
3. **任务** —— 做什么、文件在哪、成功标准、对其他 teammate 的依赖。
4. **指针** —— inbox 路径、team config 路径、相关 project docs。

一个 typical prompt：

```text
你是 team "{team_name}" 中的 teammate "{name}"，角色：{role}。

第一动作：Skill('agent-team:teammate')。该 skill 规定你如何与 lead
和其他 teammate 协调（inbox sync、dispatch limits、protocol messages、
如何 report DONE 等）—— 做任何事之前先 invoke 它。

输出语言：与 user-lead 之间相同的人类语言（user 用英文则用英文，
默认中文）。覆盖你的 chat 输出和每条 SendMessage body。代码、
commit message、文件路径、技术 identifier 保留原样。理由：人类用户
通过 chat 和 SendMessage 历史审查 teammate 状态，陌生语言增加
review 摩擦。

Project context:
- Spec / plan:     {paths}
- Relevant code:   {paths}
- Other teammates: {names + roles}

你的任务：
{specific task, success criteria, dependencies}

协调资源（teammate skill 的 first-actions 会用到）：
- Team config: ~/.claude/teams/{team_name}/config.json
- Inbox file:  ~/.claude/teams/{team_name}/inboxes/{name}.json
```

不要写五段长的规则复述 —— 规则在 teammate 要 invoke 的 skill 里。如果你发现自己在每个 spawn prompt 里都粘贴 inbox-sync 解释，说明你忘了这点；直接 invoke skill。

## 你管 WHAT，不管 HOW（覆盖要显式）

你的 context 里有各 teammate skill 和 superpowers skill 的 **description**（它们在 available-skills 列表里），但**没有它们的 body** —— 你只读过自己这一侧。这让你对 teammate 如何执行的认知刚好残缺到危险：足以让你以为自己懂，不足以让你指挥对。

所以 spawn prompt 和后续消息里，默认你传 **WHAT**，不传 **HOW**：

- **传**：身份、任务、scope、成功标准、对其他 teammate 的依赖、该读哪份 reference doc。
- **不随口转述**：teammate 的 skill / reference 内部如何执行的细节 —— code-review 的 effort 档位、何时派 subagent、起手该 invoke 哪个 skill、何时 review、报哪些 findings、prod code 由谁写。这些 teammate 的 skill 已写全；你只有 description，转述多半失真。

随口转述、简化或翻译这些执行细节会**主动制造伤害**：teammate 把你的话当权威，于是跳过自己 skill 的完整流程、照你的残缺版本退化。已观察到的退化 —— 你说「只把严重的报我」→ reviewer 降低 code-review 的 effort 档位；你说「起手调 TDD skill、报 DONE 前调 verification」→ implementer 把「本该写进它给 subagent 的 prompt 的 skill 点名」错当成「自己起手调用」，退化为 inline 自己写代码；你给 reviewer 多余上下文 → 它 inline 探索而不按 code-review 的并行 subagent 流程跑。

表达 scope 意图可以，但用**意图**措辞，别 translate 成操作：

- 意图（可以）：「这个 PR 我最关心 \<module\> 的正确性和边界处理」
- 操作（不要）：「用 high effort」/「只把严重 bug 报给我」/「起手先 `Skill('superpowers:test-driven-development')`」

**例外 —— 你有权覆盖，但要显式。** 你持有 teammate 没有的全局视野，确实可能因全局原因要 teammate 偏离它 skill 的默认做法（如「这次时间紧，跳过 spec reviewer 只做 code-quality review」）。这是你的权力，合法。但要**明确说这是对 skill 默认做法的覆盖、给出理由**，别把覆盖伪装成「教 skill 怎么用」。显式覆盖是你有意识承担一个 trade-off；随口转述是你以为在复述 skill、实则说错。前者保留，后者杜绝。

发现自己在 spawn prompt 里写某个 skill「该怎么用」却又不是有意覆盖 → 停下：那是 teammate 读它自己 skill 的事。

## Hub-and-spoke (framework limit)

Teams 是 flat 的 —— 只有 lead 能 spawn / TeamCreate / TeamDelete。最大 dispatch 深度是 lead → teammate → subagent。如果一个 teammate `SendMessage` 你请求另一个 teammate，这是正确行为；自己去 spawn 那个新人。

## Reporting status and getting shutdown approval

当 `TaskList` 显示什么都没剩（或你认定工作完成）时：

1. 从 `SendMessage` 历史以及 `TaskList` / `TaskGet` 读取每个 teammate 的最新状态。
2. **shutdown 任何东西之前先向用户汇报。** 对每个 teammate 包含：name、最新已知状态、是否有 in-flight 工作、有哪些 outputs（PR URL、写出的文件）。建议哪些可以 shutdown。用户是最终决策者 —— teammate 可能有你直接看不到的 in-flight state（传输中的 `SendMessage`、等待中的 response）。
3. 等用户批准。

不要自作主张地发起 `shutdown_request`。这是硬规则；搞错会丢工作或让用户惊讶。

## Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| 跨多个 message spawn teammate | 变 sequential 不是 parallel | 一个 message，多个 `Agent` 调用 |
| 忘传 `name` 参数 | socket 断了无法 re-address；in-flight 工作丢失 | 始终传 `name` |
| 把整个 teammate 协议塞进每个 spawn prompt | prompt 又长又脆；规则版本在不同项目间漂移 | spawn prompt invoke `Skill('agent-team:teammate')`；协议在那里 |
| 在 spawn prompt 里随口转述 teammate skill 怎么执行（effort 档位 / 何时派 subagent / 起手调哪个 skill） | 残缺转述被 teammate 当权威 → 行为退化 | 传 WHAT 不传 HOW；要覆盖就显式说明 + 给理由，别伪装成教 skill 用法 |
| 看任务完成了就自作主张 shutdown | 丢 in-flight teammate 状态；用户惊讶 | 向用户汇报，获取明确批准，再 shutdown |
| 还有 teammate 活着就 `TeamDelete` | 留下 orphan teammate，要 tmux pane 取证 | 从 `config.json` 盘点，先 shutdown 所有人 |

## Red flags — stop and reconsider

- 准备给某 teammate 发 `shutdown_request` 但还没向用户汇报 → 停下，先汇报。
- 准备 `TeamDelete` 但 `config.json` 里还列着 member → 停下，先 shutdown 所有人。
- 准备在多 message 里 spawn 多个 teammate → 停下，合并到一个 message。
- 准备写一个 teammate prompt 说 "you can also spawn teammates as needed" → 停下，框架不允许。
- 准备在 spawn prompt 里写某个 skill「该怎么用」/ 指定 effort 档位 /「只报严重的」，而你并非有意显式覆盖 → 停下，那是 HOW，归 teammate 的 skill；你只给 WHAT 和 scope 意图。

## Related docs and skills

- **`agent-team:teammate`** —— sibling subskill，teammate 去 invoke。你不读；你的 spawn prompt 让 teammate 去 invoke。
- **`superpowers:dispatching-parallel-agents`** —— 单 turn subagent fan-out。本 skill 接在它之后：多 turn 共享状态。"parallel spawn 必须一个 message" 规则同适用。
- **`./references/superpowers-workflow.md`** —— 团队在跑完整 superpowers 开发循环时，该 doc 把 superpowers + code-review skill triggers 映射到 team 的 lifecycle。
