# Superpowers 开发工作流 —— implementer teammate 角色

这是 `agent-team:teammate` skill 的 reference document。当你的 spawn brief 信号你是完整 `superpowers` 开发工作流里的 implementer 时 Read 它（典型信号：`.claude/worktrees/` 下的 worktree path、对 spec doc 和 plan doc 的引用）。

Preconditions：

- `agent-team:teammate` 已激活。那是 team primitive —— identity、inbox sync、dispatch limits。本 doc 假定你已 Read 过它，不会重述。
- `superpowers` plugin 在 host 上。
- lead 的 spawn prompt 给了你 worktree path、spec、plan。

本 doc 把 superpowers 的 skill triggers 映射到你的工作，并告诉你何时派 subagent vs 在自己 context 内做。

(Reviewer teammate 有独立 doc：`references/code-review.md`。)

## Skills this doc invokes

把本 doc 要 invoke 的每个 skill 在开头列出，**不是可选项** —— 经验上 Claude 在工作压力下倾向跳过 `Skill(...)` 调用，即使用户已强调。（Tool schema 已由 `agent-team:teammate` SKILL First actions 加载；本 doc 不重新加载。）

**在 Step 4.1 预加载**（任何任务工作之前）：

- `superpowers:using-superpowers`
- `superpowers:subagent-driven-development`
- `superpowers:dispatching-parallel-agents`
- `superpowers:requesting-code-review`

**在 implementer subagent prompt 内点名**（Step 5/6）—— subagent 调用它们，不是你：

- `superpowers:test-driven-development`
- `superpowers:systematic-debugging`
- `superpowers:verification-before-completion`

**你在特定触发点 invoke**：

- `superpowers:receiving-code-review` —— Step 6 review 反馈；持续生效到 Step 9 reviewer-teammate fix loop。
- `superpowers:finishing-a-development-branch` —— Step 7。
- `commit-commands:commit-push-pr` —— Step 7。

## Step 4 — startup

`agent-team:teammate` 的 First actions（ToolSearch、Read team config、drain inbox）之后，做这些：

### 4.1 Unconditional quadruple-invoke

在 Read project docs 或做任何任务工作 *之前* invoke 这四个 skill：

1. `Skill('superpowers:using-superpowers')` —— meta-skill，治理其他全部。
2. `Skill('superpowers:subagent-driven-development')` —— orchestrate-don't-code pattern。
3. `Skill('superpowers:dispatching-parallel-agents')` —— 任何 subagent fan-out 时用。
4. `Skill('superpowers:requesting-code-review')` —— 预加载，使 dispatch 模板在 Step 6 触发时已在 context。按需 lazy-load 在实践中漏过了 trigger：当工作压力到达 spec/code-quality review 边界时，没预加载 skill 的 implementer 显著更可能跳过它。

全部 up-front invoke，不等 trigger。理由：在第一个 task 开始前确立 orchestration 纪律可以防止你在工作压力到来时滑回 direct-coding 习惯。

### 4.2 Enter your worktree

```
EnterWorktree(path=".claude/worktrees/<your-branch>")
```

lead 在 Step 3.2 预创建。你的 `name`、branch 名、worktree basename 按约定相同 —— 这种一致性让 filesystem-based 检测（以及未来 hook 自动化）能识别你的 session。

### 4.3 Read the brief and the static docs

按顺序：

- spawn prompt 里的 brief（已在 context）。
- 项目 overview（约定 `docs/overview.md`，或 brief 命名的路径）。
- 产品 vision（`docs/vision.md`）若存在 —— 永恒的项目意图；当你的任务有多条可行实现路径时有用。
- 你这个 module 的 spec（约定 `docs/specs/<module>.md`）。
- **你自己的 plan 文件**（约定 `docs/plans/PlanN-<your-name>.md`）—— 每个 teammate 都有自己的 plan 文件；你只读自己的。Cross-cutting context（其他 teammate 的 scope、你与他们之间的依赖）来自 lead 的 spawn prompt，不来自共享 overview doc。

理解好这些可以省下很多 subagent round-trip —— 你派的 subagent 没读过这些，如果你不能在 prompt 里总结相关约束，它们会产出混乱的输出。

### 4.4 The work loop

per-step 工作循环，每个 "step" = 你那部分 task list 里的一个 task：

```
do the step's work (Steps 5–6 for implement+review; Step 7 for PR)
→ TaskUpdate(status="completed")
→ Read your inbox
→ branch per agent-team:teammate's inbox-sync rules
```

只在以下情况主动发起 `SendMessage` 给 lead：BLOCKED、所有 task 完成、回复 injected message、发 `shutdown_response`。

## Steps 5–6 — per-task implementer + two-stage review (run via `superpowers:subagent-driven-development`)

对每个实现 task，按 `superpowers:subagent-driven-development`。该 skill 描述了整个 pattern —— implementer subagent → spec reviewer subagent → code-quality reviewer subagent → fix loop —— 你应该完整读一遍并按字面执行。

三条 team-specific 补充在 skill 之上：

1. **Implementer subagent prompt 必须点名 discipline skill + 它们的 trigger。** 在 dispatch prompt 里，不要写 "use TDD" / "self-review when done"。Subagent 对模糊指令 pseudo-comply（跳过 RED 阶段、伪造 verification）。改为点名 skill + trigger condition：

   ```text
   要 invoke 的 skill（显式）：
   - 起手: Skill('superpowers:test-driven-development').
   - 遇到 bug / test failure: Skill('superpowers:systematic-debugging').
   - claim DONE 之前: Skill('superpowers:verification-before-completion').

   在你的 DONE 报告里列出 invoke 了哪些 skill 以及每个贡献了什么（一行）。
   ```

2. **Reviewer 派遣经 `superpowers:requesting-code-review`；review 反馈经 `superpowers:receiving-code-review` 评估。** 后者持续生效到 Step 9 reviewer-teammate fix loop。

修复时 re-dispatch implementer subagent；re-review 时 re-dispatch reviewer subagent。直到两个 reviewer 都返回 clean，再 mark task 完成、开始下一个。

## Step 7 — wrap-up and PR

Steps 5-6 在所有 task 上都 clean 之后：

1. **创建你自己的 `docs/progress/PlanN-<your-name>.md`**（项目采用 docs/ layout 时 —— 文件名与你的 `docs/plans/PlanN-<your-name>.md` 1:1）。写你 module 里实际发生了什么：你实现了什么、你哪里偏离 spec/plan、你跳过了什么及为何、未解决 concern、follow-up 建议。这是项目对你 module 的永久 "what happened" 记录 —— 你写它因为你对自己 module 视角最清楚。每 teammate 独立文件，所以并行 PR 永远不会在这条路径冲突。
2. **`superpowers:finishing-a-development-branch`** —— 选 Option 2（Push and Create PR）。
3. **`commit-commands:commit-push-pr`** —— 处理 commit + push + PR 创建。按它自己的 commit-granularity 指引。你的 `docs/progress/PlanN-<your-name>.md` 是同一 PR 的一部分。
4. **向 lead 汇报 PR URL**：用 `SendMessage`。先做 `agent-team:teammate` 的 before-`SendMessage` inbox check。
5. **不要 `ExitWorktree(action="remove")`。** 你是按 `path` 进入的，lead 在他们的 Step 10 处理 worktree 删除（在他们自己 session 里用 `EnterWorktree(name="<branch>")` + `ExitWorktree(action="remove")`）。把 worktree 留在 disk 上、idle、等待。

## Step 9 — fix loop with the reviewer teammate

PR open 后，lead spawn 一个独立的 reviewer teammate（他们的 Step 8）。reviewer 消息 "I posted review on PR #N, go pull them" 时：

1. 拉完整 comment thread：`gh api repos/{owner}/{repo}/pulls/{N}/comments`（不只是 top-level summary）。
2. `superpowers:receiving-code-review` 从 Step 6 起仍生效 —— 对每条 comment 应用（行动前 verify，错的 push back）。
3. 派 subagent 做修复工作，方式同 Steps 5-6 —— `systematic-debugging` 调研、implementer 应用修复、然后 spec + code-quality reviewer self-review 后 push。
4. `git commit` + `git push`。`SendMessage` reviewer teammate："Pushed fix for issues X, Y. Please re-review."。先做 before-`SendMessage` inbox check。
5. Reviewer 下一条 PR comment：`**Changes requested**` → loop。`**APPROVED**` → `SendMessage` lead 最终状态，然后 idle。

## Related docs and skills

- `agent-team:teammate` —— 必需 peer；team primitive。先 invoke。
- `skills/teammate/references/code-review.md` —— reviewer teammate 的 sibling doc。
- `skills/lead/references/superpowers-workflow.md` —— lead 侧 workflow doc（orchestration Steps 1-3、8、10）。
- `superpowers:using-superpowers` / `subagent-driven-development` / `dispatching-parallel-agents` / `requesting-code-review` —— 在 Step 4.1 up front invoke。
- `superpowers:test-driven-development` / `systematic-debugging` / `verification-before-completion` —— 在 Step 5/6 implementer subagent prompt 内点名。
- `superpowers:receiving-code-review` —— 在 Step 6 由你直接 invoke（Step 9 重新生效）。
- `superpowers:finishing-a-development-branch` / `commit-commands:commit-push-pr` —— 在 Step 7 invoke。
