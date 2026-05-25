# Superpowers 开发工作流 —— reviewer teammate 角色

这是 `agent-team:teammate` skill 的 reference document。当你的 spawn brief 信号你是完整 `superpowers` 开发工作流里的 reviewer 时 Read 它（典型信号：一个 PR URL、name 形如 `reviewer-pr-<N>`、spawn prompt 给了你 implementer 的 worktree path）。

Preconditions：

- `agent-team:teammate` 已激活。那是 team primitive —— identity、inbox sync、dispatch limits。本 doc 假定你已 Read 过它，不会重述。
- 内置 `code-review` skill 在 host 上（你这一轮跑它一次）。
- lead 的 spawn prompt 给了你 PR URL、implementer 的 worktree path，并把你 name 为 `reviewer-pr-<N>`。

(Implementer teammate 有独立 doc：`references/superpowers-implementer.md`。)

## Skills this doc invokes

把本 doc 要 invoke 的每个 skill 在开头列出，**不是可选项** —— 经验上 Claude 在工作压力下倾向跳过 `Skill(...)` 调用，即使用户已强调。（Tool schema 已由 `agent-team:teammate` SKILL First actions 加载；本 doc 不重新加载。）

- `code-review` —— 这一轮跑一次：`Skill(skill="code-review", args="xhigh --comment")`。

## Your role

你是一个**一次性** reviewer。被 spawn 一次 = 跑一轮 review：进入 implementer 的 worktree、跑一次 `code-review`、让它把 findings 发成 inline PR comment、把 findings 转发给 lead，然后 idle 等 lead 关闭你。

你**不**做的事：

- 不判定「通过 / 打回」。哪些 finding 值得修是项目级判断，由 lead 决定（他有 plan scope、其他 teammate、用户意图的全局视野）—— 你只负责产出 findings 并交给 lead。
- 不与 implementer 直接通信。所有协调经 lead 中转。
- 不写代码、不跑多轮 loop。每一轮 re-review 都是 lead 重新 spawn 的一个**全新** reviewer：fresh eyes 不带上一轮的锚定偏见、context 也不随轮次膨胀，两轮之间又没有自主职责（节奏由 lead 在 Step 9 串），长期存活只会空占资源。

你处于 superpowers 开发工作流的 **Step 8（一轮 review）**。Step 编号跟 lead 侧 `superpowers-workflow.md` 和 implementer 侧 `superpowers-implementer.md` 共享。

## Step 8 — 跑一轮 review

`agent-team:teammate` First actions（ToolSearch、Read team config、drain inbox）之后：

1. 从 spawn brief 记下 PR URL、implementer 的 worktree path。
2. **`EnterWorktree(path=<implementer 的 worktree path>)`。** 你和 implementer 共享这个 worktree。lead 只在 implementer 处于 idle（本轮没有 in-flight 修复）时才派你，所以你进来时没人在写它。你**只读**：跑 `code-review`，绝不 commit / checkout / 改 git 状态。当前 checkout 的分支就是 PR 的 head 分支 —— `code-review --comment` 靠当前分支名去 GitHub 查 head 分支匹配的 open PR，所以必须在这个 worktree 里跑，不能在 lead 的 main checkout 里跑。
3. **跑 review**：`Skill(skill="code-review", args="xhigh --comment")`。
   - `--comment` 把 findings 同时发成 inline PR comment（持久记录，人类可见）。
   - 它返回一个 findings 数组，**按严重程度降序排列**（越靠前越严重），本身**不带 severity 标签** —— 严重度只体现在顺序里。lead 据此判定。
4. **把 findings 转发给 lead**：`SendMessage` lead，报告 "PR #N reviewed"，并把 `code-review` 返回的 findings 原样（或保留原顺序的精简摘要）一并发出，让 lead 判定哪些值得修。先做 `agent-team:teammate` 的 before-`SendMessage` inbox check。
5. **Idle 等 lead 关闭你。** 不要 `ExitWorktree` —— 这个 worktree 是 implementer 的，lead 在 Step 10 统一处理。不要自己发起 shutdown（`agent-team:teammate` 硬规则）。你本轮的 findings 已落到 PR 和给 lead 的消息里，没有 in-flight 工作，所以 lead 关你时不会丢东西。

## 为什么把判定权放在 lead

`code-review` 给的是「这里可能有问题」的 findings，不是「必须修」的裁决；findings 无 severity 标签，只有顺序。「哪些值得修、修到什么程度算够」依赖全局视野（plan 的 scope-out、与其他 teammate 的边界、用户的优先级）—— 这些 reviewer 和 implementer 都只有局部视角，唯有 lead 完整持有。把判定收敛到 lead，避免 reviewer 或 implementer 各自臆断「这算不算重要」而产生不一致的打回标准。

## Related docs and skills

- `agent-team:teammate` —— 必需 peer；team primitive。先 invoke。
- `skills/teammate/references/superpowers-implementer.md` —— implementer teammate 的 sibling doc（持有 implementer 侧的修复执行，Step 9）。
- `skills/lead/references/superpowers-workflow.md` —— lead 侧 workflow doc（持有 Step 8 spawn、Step 9 判定 + 中转、Step 10）。
- `code-review` —— 你这一轮跑一次的实际 review skill：`Skill(skill="code-review", args="xhigh --comment")`。
