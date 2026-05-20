# Superpowers 开发工作流 —— implementer teammate 角色

这是 `agent-team:teammate` skill 的 reference document。当你的 spawn brief 信号你是完整 `superpowers` 开发工作流里的 implementer 时 Read 它（典型信号：`.claude/worktrees/` 下的 worktree path、对 spec doc 和 plan doc 的引用）。

Preconditions：

- `agent-team:teammate` 已激活。那是 team primitive —— identity、inbox sync、dispatch limits。本 doc 假定你已 Read 过它，不会重述。
- `superpowers` plugin 在 host 上；`superpowers:using-superpowers` 由 hook 自动注入你的上下文，不需要你显式 `Skill(...)` 激活。
- lead 的 spawn prompt 给了你 worktree path、spec、plan。

本 doc 把 superpowers 的 skill triggers 映射到你的工作，并告诉你何时派 subagent vs 在自己 context 内做。

(Reviewer teammate 有独立 doc：`references/code-review.md`。)

## Build your task list before doing anything else

读完 `agent-team:teammate` 和本 doc 后**立刻**用 `TaskCreate` 把整个 session 要做的事建成 task list —— 在 `EnterWorktree`、Read project docs、派任何 subagent **之前**。每完成一项立刻 `TaskUpdate(status="completed")`。

理由：implementer teammate 经验上最常见的失败是"做完一件忘了下一件" —— 漏激活 skill、漏读 prompt 模板、漏派 reviewer subagent、task 跑完忘记 Step 7 wrap-up、PR open 后忘记 Step 9 fix loop。Task list up-front 让 *每个* skill 激活、reference 读取、subagent dispatch 都被显式承认 + 完成后被 mark off，比仰赖记忆稳健得多。本 doc 不另外维护"哪个 skill 何时激活"的索引 —— 下面这份 task list 模板就是索引。

按下面模板生成你自己的 list。模板基于虚构 plan（`docs/plans/Plan3-alice.md` 含 Task A 和 Task B）：把 `<...>` 占位符替换成你环境里的实际值，Task A/B 替换成你 plan 文件里的实际 task 命名，按 plan 里的 task 数扩展（Task C/D/... 各一条，形式同 Task B）：

```
1.  EnterWorktree(path=".claude/worktrees/<your-branch>")                               [Step 4.1]
2.  Read docs/overview.md + docs/vision.md + docs/specs/<module>.md
         + docs/plans/PlanN-<your-name>.md                                              [Step 4.2]
3.  Invoke Skill('superpowers:subagent-driven-development')
         + Skill('superpowers:dispatching-parallel-agents')
       + Read <base>/subagent-driven-development/implementer-prompt.md                  [Step 5]
4.  Task A: Dispatch implementer subagent — <A 一句话描述>
        (prompt 内点名 superpowers:test-driven-development /
         systematic-debugging / verification-before-completion)                         [Step 5]
5.  Read <base>/subagent-driven-development/spec-reviewer-prompt.md                     [Step 6]
6.  Task A: Dispatch spec reviewer subagent                                             [Step 6]
7.  Read <base>/subagent-driven-development/code-quality-reviewer-prompt.md
       + Invoke Skill('superpowers:requesting-code-review')
       + Read <base>/requesting-code-review/code-reviewer.md                            [Step 6]
8.  Task A: Dispatch code-quality reviewer subagent                                     [Step 6]
9.  Invoke Skill('superpowers:receiving-code-review')                                   [Step 6 起持续生效]
10. Task B: implementer → spec reviewer → code-quality reviewer (按 Task A 模板复用，
        skill / template 已在 context，不再重复 Read / Invoke)                          [Step 5/6]
11. (Task C / D / ... 各一条，形式同 Task B)                                            [Step 5/6]
12. Invoke Skill('superpowers:finishing-a-development-branch')                          [Step 7]
13. Write docs/progress/PlanN-<your-name>.md                                            [Step 7]
14. Invoke Skill('commit-commands:commit-push-pr')                                      [Step 7]
15. Commit + push + open PR; SendMessage lead with PR URL                               [Step 7]
16. Fix loop with reviewer teammate (PR open 后才执行，可能多轮)                          [Step 9]
```

`<base>` 用 `Skill(...)` 返回里 "Base directory for this skill: <path>" 给的目录路径。

**review fix loop round-trip 不拆新条目**：reviewer 提 issue → 重派 implementer → 重派 reviewer 这条链全部在原 reviewer dispatch 项下完成（保持 list 干净）—— 但该条 **不能 mark completed 直到 reviewer 返回 clean**。Task A 的 "implementer subagent" 项同理：implementer 报 DONE 不等于 mark completed，要等 spec + code-quality reviewer 全部 clean 才算。Task B / C / ... 那种合并条目同样规则 —— 三个 subagent 全 clean 才 mark。

下面的 Step 4-9 是 task list 各条的详细执行手册。

## Step 4 — startup

`agent-team:teammate` 的 First actions（ToolSearch、Read team config、drain inbox）之后，做这些：

### 4.1 Enter your worktree

```
EnterWorktree(path=".claude/worktrees/<your-branch>")
```

lead 在 Step 3.2 预创建。你的 `name`、branch 名、worktree basename 按约定相同 —— 这种一致性让 filesystem-based 检测（以及未来 hook 自动化）能识别你的 session。

### 4.2 Read the brief and the static docs

按顺序：

- spawn prompt 里的 brief（已在 context）。
- 项目 overview（约定 `docs/overview.md`，或 brief 命名的路径）。
- 产品 vision（`docs/vision.md`）若存在 —— 永恒的项目意图；当你的任务有多条可行实现路径时有用。
- 你这个 module 的 spec（约定 `docs/specs/<module>.md`）。
- **你自己的 plan 文件**（约定 `docs/plans/PlanN-<your-name>.md`）—— 每个 teammate 都有自己的 plan 文件；你只读自己的。Cross-cutting context（其他 teammate 的 scope、你与他们之间的依赖）来自 lead 的 spawn prompt，不来自共享 overview doc。

理解好这些可以省下很多 subagent round-trip —— 你派的 subagent 没读过这些，如果你不能在 prompt 里总结相关约束，它们会产出混乱的输出。

### 4.3 The work loop

per-step 工作循环，每个 "step" = 你 task list 里的一条：

```
do the step's work (Steps 5–6 for implement+review; Step 7 for PR)
→ TaskUpdate(status="completed")
→ Read your inbox
→ branch per agent-team:teammate's inbox-sync rules
```

只在以下情况主动发起 `SendMessage` 给 lead：BLOCKED、所有 task 完成、回复 injected message、发 `shutdown_response`。

## Steps 5–6 — per-task implementer + two-stage review (run via `superpowers:subagent-driven-development`)

对每个实现 task，按 `superpowers:subagent-driven-development`：implementer subagent → spec reviewer subagent → code-quality reviewer subagent → fix loop。

**实际写 production code 的是 subagent，不是你**。如果你发现自己开始 `Edit`/`Write` task 里的 prod 文件，停下 —— 你漏掉了 dispatch 步骤，回去派 implementer subagent。同理，implementer subagent 报告 DONE 之后**不要直接 mark task completed**，必须先派 spec reviewer subagent，spec clean 后再派 code-quality reviewer subagent，**两个都 clean** 才能 mark completed。如果你发现自己即将跳过 reviewer 直接进入下一个 task，停下 —— 这是最常被漏的步骤。

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

1. **`superpowers:finishing-a-development-branch`** —— 选 Option 2（Push and Create PR）。它会指导你下面的 progress doc + commit + PR 流程。
2. **创建你自己的 `docs/progress/PlanN-<your-name>.md`**（项目采用 docs/ layout 时 —— 文件名与你的 `docs/plans/PlanN-<your-name>.md` 1:1）。写你 module 里实际发生了什么：你实现了什么、你哪里偏离 spec/plan、你跳过了什么及为何、未解决 concern、follow-up 建议。这是项目对你 module 的永久 "what happened" 记录 —— 你写它因为你对自己 module 视角最清楚。每 teammate 独立文件，所以并行 PR 永远不会在这条路径冲突。
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
- 每个 superpowers / commit-commands skill 何时激活、何时 Read sibling reference —— 见文档开头的 task list 模板，不在这里重复列。
