---
name: teammate
description: Use when spawned as a teammate in a Claude Code agent team — activated by a team lead's spawn instruction. Required reading for the inbox sync protocol, dispatch limits, and protocol-message responses that keep multi-agent coordination from drifting into stale-state race conditions. Invoke this skill as your FIRST action whenever a spawn prompt names you as a teammate, says you joined a team, gives you a team_name / inbox path, or instructs you to coordinate with other agents via SendMessage and a shared task list.
---

# agent-team:teammate

你是 Claude Code agent team 里的一个长期 teammate。本 skill 收纳了维持 teammate ↔ teammate ↔ lead 协调正确性的协议 —— 大多数是非显然的、不在任何单一 tool 文档里、跳过过会引起真实 bug 的。

## First actions (before any task work)

按顺序做下面这些，在回应用户或尝试任何任务级工作之前：

1. **加载 tool schemas。** 团队的协调 tool（以及 lead 帮你预创建的 worktree 可能用到的 worktree tool）是 deferred 的，不先加载 schema 直接调用会触发 `InputValidationError`。一次性加载：

   ```
   ToolSearch select:SendMessage,TaskCreate,TaskList,TaskUpdate,TaskGet,EnterWorktree,ExitWorktree,max_results=7
   ```

   ToolSearch 返回的 description 是各 tool *如何工作*（`SendMessage` 的 message-type union、`TaskUpdate` 的 status 字段等）的权威 reference。本 skill 刻意不重述这些 —— 只讲任何单一 schema 都没覆盖的跨 tool pattern。

2. **Read team config**：`~/.claude/teams/<team_name>/config.json`，一次性读取，让你手头有 peer name 供 `SendMessage` 的 `to=` 和 `TaskUpdate` 的 `owner=` 使用。（`TeamCreate` 的 description 涵盖了该文件的内容和 "use name not `agentId`" 规则 —— 本 skill 不重述。）

## Dispatch limits

你的 dispatch 深度是 2：你 → subagent。`Agent(team_name=..., name=...)` 和 `TeamCreate` / `TeamDelete` 都会被框架 reject —— 只有 lead 管理 team 成员。如果工作超过你 + subagent 能搞定的范围，`SendMessage` lead 请求另一个 teammate。

## Inbox sync —— 本 skill 最重要的协议

### 问题

`TeamCreate` description 说 "Messages from teammates are automatically delivered to you. You do NOT need to manually check your inbox."。这在 **turn 之间** 是真的 —— 框架在 turn 边界注入新消息。下面这条协议是给 description 没覆盖的情况：**在单个 turn 内**，即使 peer 在毫秒前往你的 inbox 写入了消息，你的世界观依然是冻结的。在那个 stale 世界观上行动正是本协议要防止的。

teammate 通信是异步的。`SendMessage` 沉积到接收方的 inbox 文件；接收方只在后续的 turn 上、框架注入时才看见消息。在单个 turn 内你收不到新消息 —— 即使 peer 毫秒前刚往你 inbox 写过。

这种不对称使一种 "rendezvous failure" 成为可能：

> A 和 B 约定在位置 X 见面。A 朝 X 走。B 中途改变主意，发出 "let's meet at Y instead"。A 不读 inbox 继续走，到达 X，*然后*发 "I'm at X" *再然后* 才读 inbox —— 发现切换到 Y 的请求。A 走向 Y。同时 B 收到 "I'm at X" 又转回来，发 "ok, back to X"。如此反复。它们永远差一步，各自基于对对方位置的 stale 印象行动。

根因：**任一方在持有 stale 世界观的情况下发了新消息或启动了新动作**。更快的通信不能修复 —— 只能缩小窗口。唯一消除该 failure mode 的方法是拒绝在 stale 世界观上*行动*。

### 修复：在两个 trigger point 上 check inbox

只要你的 inbox 非空，就必须停下、让框架注入这些消息后再做任何事。两种情况触发 check：

1. **完成一步之后。** "步" = shared task list 里的一个 task，或 lead 在你 spawn brief 里列举的一个 sub-task。序列：

   ```
   do the work
   → TaskUpdate(status="completed")
   → Read ~/.claude/teams/<team_name>/inboxes/<your_name>.json
   → branch:
       []          → start the next step
       non-empty   → STOP THE TURN. Don't call any more tools.
   ```

   你停下后，框架在下一个 turn 注入 inbox 内容并清空文件。你那时再处理它们并决定下一步。

2. **你主动发起 `SendMessage` 之前。** 同样 Read + branch。

你 *主动发起* `SendMessage` 只有四种情况：

- 你所有任务都做完了 —— 向 lead 汇报 DONE。
- 你 blocked 需要 lead 介入。
- 你在回复框架刚注入的消息。
- 你在响应一个 protocol message（`shutdown_response` 等）。

对一个 self-contained brief 的其他每个进展步骤，安静工作。lead 在你的 spawn prompt 里设定了 plan；干净地执行而不带状态噪音是关键。

### 为什么 stop the turn 而不是自己处理 inbox

当框架在下一个 turn 注入 inbox 内容时，它也 **清空 inbox 文件** —— 这是它跟踪哪些消息已被消费的方式。如果你在本 turn 里读文件并 inline 回复消息，文件保持非空。下一个 turn 框架会再次注入同样的消息，你会处理它们两次。

所以：**read to check, not to act**。要对 inbox 消息行动必须经过框架的注入循环。

## 如果你的 spawn brief 是 superpowers 开发工作流的一部分

lead 可能在本 skill 之上跑完整 `superpowers` + `code-review` 开发循环。spawn brief 里有两个信号告诉你扮演哪个角色、startup 时 Read 哪份 reference doc：

- **Worktree path + spec doc + plan doc** → 你是 implementer。Read `./references/superpowers-implementer.md`。
- **PR URL + name 形如 `reviewer-pr-<N>`、无 worktree** → 你是 reviewer。Read `./references/code-review.md`。

纯协调工作不需要这两份 doc —— 很多 team 用 `agent-team:teammate` 完全不带任何开发工作流。只有 brief 信号触发时才 Read 对应 doc。

## 完成上报

当所有分配给你的任务都 `completed`：

1. 最后一次 `Read` inbox。非空则停 —— 让框架注入。不要在未读消息上面报 DONE。
2. `SendMessage` lead 一个简洁的纯文本摘要：你完成了什么、outputs 在哪（路径、PR URL）、任何 lead 应该知道的事 —— 偏离 plan、未解决 concern、follow-up 建议。
3. Idle。lead 会向用户汇报状态并请求 shutdown 批准。你等。

不要自己发起 shutdown。

## Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Startup 跳过 ToolSearch | 第一次 `SendMessage` / `Task*` 调用触发 `InputValidationError` | 第 1 步跑 bulk `ToolSearch select:...` |
| 跳过 per-step inbox check | lead 中途的方向调整落进 inbox，你继续执行过时的 plan | per-step check 不可妥协 |
| 在 mid-turn 读 inbox 并行动 | 同一消息下 turn 再次注入 → 双重处理 | Read to *check*；非空则停 turn |
| `SendMessage` 之前没 check inbox | stale 世界观发信 → rendezvous failure | before-`SendMessage` inbox check，同规则 |
| 试图 `Agent(team_name=..., name=...)` spawn 一个 teammate | 框架 reject (no nested teams) | `SendMessage` lead 请求另一个 teammate |
| 试图 `TeamCreate` / `TeamDelete` | 框架 reject (fixed lead) | 找 lead |
| 任务中途批准 `shutdown_request` | 丢 in-flight 工作 | 先发 DONE / status，再从干净状态批准 |

## Red flags — stop and reconsider

- 准备调 `SendMessage` 但没 read inbox → 停下，先 read inbox。
- inbox 非空你想在本 turn 内处理 → 停下，结束 turn。
- 准备 spawn 一个 teammate (`Agent(team_name=..., name=...)`) → 停下，改 `SendMessage` lead。
- 准备批准 `shutdown_request` 但你还有最终 DONE / status 要发 → 停下，先发，再批准。

## Related docs and skills

- **`agent-team:lead`** —— 你的 sibling skill，由 lead 在自己 context 内 invoke。你不读它；它管 team 创建、spawn、shutdown、merge 等 lead 侧职责。
- **`superpowers:dispatching-parallel-agents`** —— 你派 subagent 做 fan-out 时同样适用 "parallel spawn 必须一个 message" 规则。
- **`./references/superpowers-implementer.md`** —— spawn brief 含 worktree path + spec doc + plan doc 时 Read（implementer 角色）。
- **`./references/code-review.md`** —— spawn brief 含 PR URL + name 形如 `reviewer-pr-<N>` 且无 worktree 时 Read（reviewer 角色）。
