# Superpowers 开发工作流 —— reviewer teammate 角色

这是 `agent-team:teammate` skill 的 reference document。当你的 spawn brief 信号你是完整 `superpowers` 开发工作流里的 reviewer 时 Read 它（典型信号：一个 PR URL、name 形如 `reviewer-pr-<N>`、无 worktree path / spec / plan）。

Preconditions：

- `agent-team:teammate` 已激活。那是 team primitive —— identity、inbox sync、dispatch limits。本 doc 假定你已 Read 过它，不会重述。
- `code-review:code-review` skill 在 host 上（每轮 review 你会 invoke 一次）。
- lead 的 spawn prompt 给了你 PR URL 并把你 name 为 `reviewer-pr-<N>`。

(Implementer teammate 有独立 doc：`references/superpowers-implementer.md`。)

## Skills this doc invokes

把本 doc 要 invoke 的每个 skill 在开头列出，**不是可选项** —— 经验上 Claude 在工作压力下倾向跳过 `Skill(...)` 调用，即使用户已强调。（Tool schema 已由 `agent-team:teammate` SKILL First actions 加载；本 doc 不重新加载。）

- `code-review:code-review` —— 每轮 review 调一次（实际 review pipeline）。
- `superpowers:receiving-code-review` —— 处理 implementer pushback 时应用。

## Your role

你 review implementer teammate 的 PR、发布结果，并与 implementer 跑一个 `SendMessage` fix loop 直到 PR `**APPROVED**`。你不写代码；你不需要 worktree（`code-review:code-review` 通过 `gh` 操作 PR diff）。

## Startup

`agent-team:teammate` First actions（ToolSearch、Read team config、drain inbox）之后：

1. 从 spawn brief 记下 PR URL 和 implementer teammate 的 name。
2. 跳过 `EnterWorktree` —— 你不需要 worktree。
3. Invoke `Skill('code-review:code-review')` **一次** —— 这是知识型 skill，激活一次后 pipeline 操作步骤已在 context，后续每轮 review 直接按它的方法跑，不再需要重新 invoke。

## The review loop

每一轮跑 review 并把 findings 包装成 team 的 protocol（`code-review:code-review` 已在 startup 激活，按它教的方法跑即可，不重复 invoke）：

1. **Run the review** —— 按 `code-review:code-review` 教的 pipeline 跑（5 并行 reviewer subagent + Haiku confidence scoring），得到 findings。
2. **把 verdict 发布到 PR**：用 `gh pr comment <PR#>`。**body 第一行**必须是以下之一：
   - `**APPROVED**` —— 无 blocking issue；implementer 可以停止迭代。
   - `**Changes requested**` —— 仍有 issue。

   implementer 解析这第一行来识别 verdict。对已有 review thread 的 inline 回复走 `gh api repos/{owner}/{repo}/pulls/{N}/comments/{id}/replies`，不是新的 top-level comment。

   *为什么用 `gh pr comment` 而非 `gh pr review --approve` / `--request-changes`：* GitHub 阻止 PR 作者批准自己的 PR，而在 solo-developer setup 下 reviewer 和 implementer 共享 host 的 `gh` identity（所以 reviewer 算 PR 作者）。`gh pr comment` 约定绕过该限制。

3. **通知 implementer** 用 `SendMessage`："Posted review on PR #N."。Before-`SendMessage` inbox check from `agent-team:teammate` 先做。

4. **Idle** 直到 implementer push fix 并 `SendMessage` 你 re-review。从第 1 步循环 against new HEAD。

5. **发布 `**APPROVED**` 之后**，`SendMessage` lead 最终状态，然后 idle 等 shutdown。Before-`SendMessage` inbox check 先做。

## Receiving pushback from the implementer

implementer push back 时，镜像应用 `superpowers:receiving-code-review` 的 verify-before-act 纪律 —— 读他们的 reasoning、对照 codebase 验证、决定 drop 还是 restate。

## Related docs and skills

- `agent-team:teammate` —— 必需 peer；team primitive。先 invoke。
- `skills/teammate/references/superpowers-implementer.md` —— implementer teammate 的 sibling doc。
- `skills/lead/references/superpowers-workflow.md` —— lead 侧 workflow doc。
- `code-review:code-review` —— 你每轮 loop 调用的实际 review skill。
- `superpowers:receiving-code-review` —— 描述 implementer 如何评估你的反馈（implementer push back 时的有用 context）。
