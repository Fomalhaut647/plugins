# agent-team Release Notes

## v0.4.0

确立 lead 的「你管 WHAT，不管 HOW」职责边界。根因：lead 的 context 里只有各 teammate / superpowers skill 的 description、没有 body，残缺转述执行细节（code-review effort 档位、何时派 subagent、起手调哪个 skill 等）会被 teammate 当权威而跳过自己 skill 的完整流程、退化执行。

- **lead 默认只传 WHAT**（任务 / scope / 依赖 / 该读哪份 doc），不随口转述 teammate skill 的 HOW；scope 意图用意图措辞，不 translate 成操作档位 / 步骤。
- **覆盖要显式**：lead 持全局视野，有权因全局原因让 teammate 偏离 skill 默认做法，但必须明说「这是覆盖 + 理由」，不能把覆盖伪装成「教 skill 怎么用」。
- 收编此前三类点状退化为同一根因的实例：reviewer effort 降档、implementer 退化为 inline development、reviewer 不并行探索。
- 本版只加固 lead 侧；teammate 侧是否需要配套改动（如偏离 skill 前的澄清闸门）留待真实 session 实测后再定。

## v0.3.0

Reviewer teammate 改为一次性模型，并从 `code-review:code-review` 插件切换到 Claude Code 内置 `code-review` skill。

- **一次性 reviewer**：每轮 review 由 lead 重新 spawn 一个 reviewer teammate，它 `EnterWorktree` 进 implementer 的 worktree、跑一次 `Skill(skill="code-review", args="xhigh --comment")`、把 findings 发成 inline PR comment 并转发给 lead，然后 idle 等关闭。每轮换全新 reviewer 而非长期存活 —— fresh eyes 防锚定偏见、修复期间零 idle 占用。
- **fix loop 由 lead 中枢驱动**：`code-review` 的 findings 无 severity 标签、按数组顺序排严重度，所以「哪些值得修」由 lead 判定（凭 plan scope、teammate 边界、用户优先级的全局视野），发清单给 implementer；implementer 只修清单内的 bug、push 后由 lead spawn 下一轮 reviewer。取消旧的 `**APPROVED**` / `**Changes requested**` PR-comment verdict 约定。
- **shutdown 规则**：lead 关闭一次性 reviewer 无须先汇报用户（findings 已持久化到 PR、无 in-flight 工作）；关闭 implementer 仍须先汇报。

## v0.1.0

Initial release through the `fomalhaut647-plugins` marketplace.

- `agent-team:lead` — orchestrates a multi-agent team: `TeamCreate`, spawn prompt template, task assignment, hub-and-spoke topology, shutdown sequence, merge + cleanup ordering.
- `agent-team:teammate` — first-action protocol for spawned teammates: load tool schemas, read team config, per-step + before-SendMessage inbox sync, "no nested teams" framework limit, completion reporting.
- Reference docs for layering the `superpowers` development workflow on top: `skills/lead/references/superpowers-workflow.md`, `skills/teammate/references/superpowers-implementer.md`, `skills/teammate/references/code-review.md`.
