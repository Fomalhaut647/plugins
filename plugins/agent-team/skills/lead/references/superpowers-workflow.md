# Superpowers 开发工作流 —— lead 角色

这是 `agent-team:lead` skill 的 reference document。当你在跑完整的 `superpowers` 开发工作流时 Read 它（brainstorming → writing-plans → 并行 implementer teammate → reviewer teammate → PR fix loop → user 批准的 merge）。

Preconditions：

- `agent-team:lead` 已激活。那是 team primitive —— TeamCreate、spawn 规则、hub-and-spoke、shutdown 序列、merge 顺序。本 doc 假定你已 Read 过它，不会重述。
- `superpowers` plugin 已安装在 host。
- 用户要走完整纪律：brainstormed spec → 写好的 plan → TDD 实现 → 两阶段 code review → PR ↔ reviewer fix loop → user 批准的 merge。

本 doc 把 `superpowers:*` skill triggers 映射到 team 的 lifecycle。

## Skills this doc invokes

把本 doc 要 invoke 的每个 skill 在开头列出，**不是可选项** —— 经验上 Claude 在工作压力下倾向跳过 `Skill(...)` 调用，即使用户已强调。把它们作为 checklist 加载在这里让你保持诚实。（Tool schemas —— TeamCreate / SendMessage / EnterWorktree 等 —— 已由 `agent-team:lead` SKILL First actions 加载；本 doc 不重新加载。）

- `superpowers:brainstorming` (Step 1)
- `superpowers:writing-plans` (Step 2)
- `superpowers:using-git-worktrees` (Step 3.1)

其他 `superpowers:*` 和内置 `code-review` skill 在 teammate *内部* 跑（详见 teammate-side reference docs），不在你的 context。

## Step 0 — project doc layout (optional convention)

很多长期项目一次 agent-team session 跑不完，需要跨多次 session 推进。如果项目采用该模式下的标准 `docs/` layout，约定是：

```
docs/
├── vision.md                       产品愿景（永恒：终态、核心价值、不变的设计原则）
├── overview.md                     当前版本的项目地图（模块、里程碑）
├── specs/                          active per-module 设计（A-xxx.md / B-xxx.md；立项时草稿，session 不断 refine 时覆盖）
├── plans/PlanN-<teammate>.md       per-session plan，每 teammate 一个文件（扁平，无共享 overview）
├── progress/PlanN-<teammate>.md    per-session 交付报告，与对应 plan 文件 1:1
└── archive/                        冻结历史版本
```

划分：**specs** 按 functional module 划，**plans + progress** 按 session × teammate 划。一个 PlanN session 可覆盖多个 spec module，但每个 teammate 拥有自己的 `PlanN-<teammate>.md` plan 和对应的 `PlanN-<teammate>.md` progress 文件。**没有共享 `PlanN.md` overview 文件** —— cross-cutting context（session scope、为何这样切分 teammate、teammate 间依赖）写在 lead 的 spawn prompt 里，不进 doc。

项目采用该 layout 时，下面的 Step 1、2、7、10 直接引用这些路径。不采用时，把路径引用当作 "随 brief 说的位置"。

## Step 1 — brainstorming

Invoke `superpowers:brainstorming`。两条 team-specific 补充：

- **在 main 跑，不在 worktree 跑。** Brainstorming 产出的 spec content 会成为每个 downstream worktree 实现所对照的 contract；必须存活在 main 历史里。worktree 在 Step 3.2 才创建。如果你当前不在 main，向用户暴露这点并先问再切 —— 不要静默 checkout。
- **输出覆盖 `docs/specs/<module>.md`**（项目采用 Step 0 layout 时）。kickoff 期的草稿被本 session refined 后的理解替换，覆盖 scope 内每个 module。新内容成为后续的 canonical spec。

## Step 2 — writing-plans

Invoke `superpowers:writing-plans`。在 skill 标准 plan 结构之上的 team-specific 补充：

- **在 main 跑，不在 worktree 跑**（同 Step 1 理由）。
- **一个 teammate 一个 plan 文件。** 输出到 `docs/plans/PlanN-<teammate>.md`（项目采用 Step 0 layout 时），N 是本 session 序号。无共享 `PlanN.md` overview 文件 —— cross-cutting context（session scope、为何这样切分 teammate、teammate 间依赖）在 Step 3.4 的每个 spawn prompt 里写，不进 doc。
- **明确的并行切分。** 决定 teammate 数量和每个 teammate 拥有的 module。这驱动文件数（每 slot 一个 `PlanN-<teammate>.md`）和 Step 3 的 spawn 数。
- **Naming。** 每个并行 slot 有一个 logical name（teammate 的 `name`）。三样东西原样共享该 name：worktree directory basename、`docs/plans/PlanN-<teammate>.md` 后缀、`docs/progress/PlanN-<teammate>.md` 后缀 —— 保持这三者一致，让 filesystem-based 检测（以及未来的 hook 自动化）能基于 `cwd` basename 做 key。git **branch** 名是独立 concern：从 EnterWorktree 输出行里读，而不是自己构造，因为 EnterWorktree 可能 transform 输入（如加前缀）。EnterWorktree 报回的就是 PR URL 和 `gh pr list` 里看到的 branch。
- **不需要预建 progress skeleton。** 每个 implementer 在 Step 7 自己创建 `docs/progress/PlanN-<teammate>.md` —— 独立文件，所以并行 PR 永远不会在这条路径上冲突。

## Step 3 — worktrees + TeamCreate + spawn

### 3.1 Invoke `superpowers:using-git-worktrees`

它治理你即将用的 `EnterWorktree` / `ExitWorktree` 流程。

### 3.2 Create one worktree per teammate (serial loop)

一个 session 只能有一个 worktree active，所以你一个一个建，每个在 disk 上 "keep" 后再做下一个：

```
for each teammate (per the plan's split):
    EnterWorktree(name="<branch-name>")    # creates and enters
    ExitWorktree(action="keep")            # leaves worktree on disk; you return to main
```

循环之后：所有 worktree 存在于 `.claude/worktrees/<branch-name>/`，你回到主 worktree / main branch。

### 3.3 `TeamCreate` + `TaskCreate`

标准 `agent-team:lead` 机制 —— 创建 team，填充共享 task list。

### 3.4 Spawn implementing teammates in parallel

在一个 message 内发出全部 `Agent` 调用（one message → parallel；multiple messages → serial）。每个 spawn prompt 遵循标准 `agent-team:lead` 结构，外加三个 superpowers-specific 元素在 task block 里：

1. **Worktree path** —— 告诉 teammate 精确去 `EnterWorktree(path=".claude/worktrees/<branch>")` 哪条路径。他们加入你预创建的 worktree。
2. **Docs to read** —— `overview.md`、该 module 的 spec、该 module 的 plan。
3. **Startup instruction** —— 在 `Skill('agent-team:teammate')`（标准第一动作）之后，告诉 teammate Read 自己 skill 的 `references/superpowers-implementer.md`。该 doc 覆盖 Step 4-7 + 他们这一侧的 Step 9。

一个 typical implementer spawn prompt：

```text
你是 team "{team_name}" 中的 teammate "{name}"，角色：{role}。

按顺序的第一动作：
1. Skill('agent-team:teammate') —— team 协调协议。
2. Read 你 skill 的 references/superpowers-implementer.md —— 你接下来
   整个 session 要跑的 per-task TDD + 两阶段 review + PR pattern。

Project context:
- Worktree:        .claude/worktrees/{branch}   (lead 预创建; EnterWorktree(path=...))
- Overview:        {path}
- Your spec:       {path}
- Your plan:       {path}
- Other teammates: {names + roles + worktrees}

你的任务：
{specific module, success criteria, dependencies on other teammates}

协调资源：
- Team config: ~/.claude/teams/{team_name}/config.json
- Inbox file:  ~/.claude/teams/{team_name}/inboxes/{name}.json
```

## Monitoring while teammates run Steps 4–7

Steps 4-7 在实施 teammate *内部* 发生（per-task TDD → two-stage review → PR）。本阶段你的工作：

- 响应 `SendMessage` —— 进度报告、BLOCKED 请求、最终的 PR URL。
- 如果人类用户更新了 plan，`SendMessage` 方向变化。teammate 的 inbox-sync 协议（来自 `agent-team:teammate`）会在他们的下一个 step 边界 pick up。
- 抵制偷看 worktree / log 文件。`TaskList`、`TaskGet`、incoming `SendMessage` 是 canonical 可见面。

## Step 8 — spawn a one-shot reviewer teammate

每当需要 review 一个 PR（implementer 首次报 PR URL，或后续每轮 implementer 报「修复已 push，ready for re-review」），对该 PR spawn 一个**一次性**的 reviewer teammate。它跑一轮 `code-review` 就完事 —— 每轮都换一个全新 reviewer（fresh eyes 防锚定偏见、修复期间不空占资源），loop 由你在 Step 9 串。

先确保该 PR 的 implementer 此刻 idle（已报 PR ready 或修复已 push、不在写 worktree）—— reviewer 会进 implementer 的 worktree 只读跑 review，时序上不能和 implementer 的写撞上。

Spawn-prompt 结构同 Step 3.4，区别在：

- `name="reviewer-pr-<N>"`（上一轮的同名 reviewer 已在上一轮结束时被你 shutdown，所以名字可复用）。
- brief 告诉 reviewer：PR URL、**implementer 的 worktree path**、第一动作 `Skill('agent-team:teammate')`、然后 Read 自己 skill 的 `references/code-review.md`。
- **有 worktree** —— reviewer `EnterWorktree(path=<implementer 的 worktree>)` 进 PR head 分支的 checkout，内置 `code-review` 的 `--comment` 靠当前分支名定位 open PR。reviewer 只读，不 commit、不 `ExitWorktree`。

## Step 9 — fix loop（你是中枢）

reviewer 不直接联系 implementer —— 你串起每一轮。一轮长这样：

1. **reviewer 报 findings。** 它跑完 `code-review` 后 `SendMessage` 你 "PR #N reviewed" 外加 findings（按严重度排序、无 severity 标签的数组）。
2. **关闭本轮 reviewer。** 直接 `SendMessage(to=<reviewer>, message={"type":"shutdown_request"})` 并等它的 `shutdown_response`。`agent-team:lead` SKILL.md 有条硬规则「发 `shutdown_request` 前先向用户汇报」，理由是「搞错会丢 in-flight 工作或让用户惊讶」。一次性 reviewer 不触发这个理由：它的 findings 已落到 PR 和给你的消息里，没有 in-flight 工作可丢。所以**这是那条硬规则对一次性 reviewer 的 workflow 特定例外，关闭它无须先汇报用户**。implementer **不在**例外内（它持有 worktree + in-flight 修复，仍须先汇报 —— 见 Step 10）。
3. **判定哪些值得修。** 看 findings，按你的全局视野（plan scope、与其他 teammate 的边界、用户优先级）挑出值得修的。`code-review` 给的是「可能有问题」不是「必须修」—— 不是每条都要修，靠前的更严重。
4. **把判定结果发给 implementer：**
   - 没有值得修的 → `SendMessage` implementer「review 通过」。该 PR 的 fix loop 到此结束，implementer 会回你最终 DONE。
   - 有值得修的 → `SendMessage` implementer 一份要修的 bug 清单。implementer 修完、push、回你 "ready for re-review"。
5. **收到 implementer 的 "ready for re-review" 后**，回到 Step 8 对同一 PR spawn 下一轮一次性 reviewer。循环，直到第 4 步你判定「无值得修的」。

implementer 若对某条 finding push back（认为误报），由你定夺要不要从清单里撤掉。

## Step 10 — merge + shutdown + TeamDelete

全部 PR 都已通过你的 review 判定（Step 9 第 4 步「review 通过」）。从这里开始：

1. **向用户汇报团队状态。** 每个 teammate：最新已知状态、PR URL + 状态、worktree path。请求 shutdown 批准。
2. **拿到独立的 merge 批准。** 用户可能想 merge 前最后看一眼 PR —— 不要把它与 shutdown 批准 bundle 在一起。
3. **并行 shutdown 剩下的 teammate** —— 此时只剩 implementer（reviewer 已在 Step 9 第 2 步逐轮关闭）。一个 message，每个 teammate 一条 `SendMessage(to=<member>, message={"type":"shutdown_request"})`。等每个 `shutdown_response{approve: true}` 都回来。
4. **删除每个 implementer worktree 并 merge 它的 PR。** Reviewer teammate 是一次性的、每轮已在 Step 9 关闭，且没有自己的 worktree（进的是 implementer 的），所以这里无需再管它们。对每个 implementer teammate：

   ```
   EnterWorktree(name="<branch>")               # re-enter (still exists from Step 3.2)
   ExitWorktree(action="remove")                # delete worktree dir + local branch
   gh pr merge <PR#> --squash --delete-branch   # merge PR + delete remote branch
   ```

   按 commit 粒度对每个 PR 选 `--squash` 还是 `--rebase`（`--squash` 当 commit 紧密关联，`--rebase` 当 commit 跨域且各自完整）。一批 PR 可以混用。永不 `--merge`。

5. **验证每个 `docs/progress/PlanN-<teammate>.md` 存在于 main**（项目采用 Step 0 layout 时）。每个 implementer 在 Step 7 创建了自己的文件；所有 PR merge 后，每个期望的文件都应存在。如果缺了某个，teammate 已 shutdown —— 要么自己写一段 placeholder 注明 "module <teammate> — implementation summary missing"，要么问用户怎么处理。这些文件是该 session 实际发生了什么的项目永久记录，每 teammate 一份。

6. **`TeamDelete()`。**

## When this workflow does *not* apply

- 一次性团队协调，不涉及 spec/plan 文档或 PR review loop → 留在 `agent-team:lead` 单独使用，跳过本 doc。
- 用户想自己撰写 spec/plan 而不跑 `superpowers:brainstorming` / `writing-plans` → 跳过 Step 1-2，如果仍需并行切分则从 Step 3 接手。
- 单模块工作 / 无并行切分 → 考虑在 lead 自己的 context 内跑 plain `superpowers:subagent-driven-development` session 而非 spin up team。

## Related docs and skills

- `agent-team:lead` —— 必需 peer；team primitive。先读。
- `skills/teammate/references/superpowers-implementer.md` —— implementer 侧的 workflow doc。每个 implementer teammate 在 startup 时 Read，当你的 spawn prompt 信号 superpowers workflow。
- `skills/teammate/references/code-review.md` —— reviewer 侧的 workflow doc。每个 reviewer teammate 在 startup 时 Read。
- `superpowers:brainstorming` / `writing-plans` / `using-git-worktrees` —— 在本 doc 的 Step 1-3 直接 invoke。
- 其他 `superpowers:*` 和内置 `code-review` —— 在 teammate 内部按自己的 skill 协议 invoke，不由你调用。
