# agent-team Release Notes

## v1.8.0

- 发去修的发现是一整类问题里的一个时，要求整类堵上，并让这一类再出现时能被测试或检查自动发现，不只修点名的例子。
- 复审只审这一轮修复的改动，不再把整块审一遍。

为什么：用户的决定，依据一次真实协调。第一轮修复只补了审查点名的写法，复审报的 3 条高级全是同类没堵全，另有六七处是修复带出的新问题；复审范围一大，又会在没动过的代码里挑出新问题，审查修复不收敛。

## v1.7.0

- 审查修复循环里，某一轮修的都是小 bug（改动少、只涉及局部）时，不再开新的审查会话，由主会话自己看修复的改动复审；改动大的修复仍开新的审查会话。
- 「大 bug」改称「严重 bug」：按后果判断，不看 bug 本身大小，小而严重的也修。

为什么：用户的决定。修复只改了几行时，开一个审查会话把整块从头审一遍，花的时间和 token 远超修复本身；主会话手里有上一轮的发现和修复要求，看修复改动就能判断修对没有。原来的「大 bug」容易被读成「改动大的 bug」，和「小 bug 由主会话复审」放在一起会自相矛盾。

## v1.6.0

合并不再等用户同意：全部审查通过后，主会话直接把各分支合进自己的分支，整体测试、推送、开总 PR，然后再向用户汇报每块的分支、验证情况、审查轮数、遗留问题和 PR 链接。

为什么：用户的决定，合并这一步不需要再点头，在总 PR 上把关即可。

## v1.5.0

- 只能手动调用：加上 `disable-model-invocation: true`，只在用户输入 `/agent-team:lead` 时启用。说「开个团队」之类的话不再触发，模型也不会自己调用；简介不再占每个会话的上下文。

## v1.4.0

- 审查之后，主会话只把大 bug（如主要功能出错、丢数据、安全隐患）发给子会话修，中小问题不修，合并前汇报时列进遗留问题；反复审查直到没有大 bug，而不是直到没有值得修的。
- 后一批提前开工时，被依赖的那块审查通过前的修订不逐次转告它们，通过后发一次消息让它们合进来。
- 「不用问我，自动完成整个流程」也算要求提前开会话：提前开好后一批的开发会话，和每块一两个审查会话待命。
- 待命的会话用完、又开不了新会话时，留任务卡片等用户点，不改用会话内的子代理审查。

为什么（依据 issue #3 报告的一次真实协调）：

- 中小问题也修的话，每轮修复都带来新改动，新的审查会话又能挑出新的中小问题，审查修复一轮接一轮迟迟不收敛。那次协调里一块审了 9 轮，合计约 40 个审查会话，后几轮多是小问题和修出来的新问题。
- 五块依赖第一块并提前开工，第一块审查期间每出一个提交，主会话就给五个开发会话群发一遍「请合进来」，前后约 30 次，每次都叫醒五个上下文三四十万 token 的会话。
- 用户说「你不用询问我，自动完成整个流程就行」，主会话不提前开会话的话，下一次审查就停在卡片上。
- 提前开的审查会话用完后，主会话自己派了 31 个会话内子代理审查，结果全回到主会话，上下文涨到约 50 万 token。

## v1.3.0

子会话（含审查会话）默认思考强度从 medium 改为 high；审查会话调用 `code-review` 的档位也从 `medium` 改为 `high`。用户强调了别的强度仍按用户的。

## v1.2.1

主会话默认不提前开子会话，哪块要审了再开审查会话；被子会话叫醒、开不了新会话时留任务卡片。只有用户明确要求提前开（换个说法也算）时，才提前开一批审查会话待命。「说明之后没法操作」不再单独算作提前开的理由。

为什么：一次真实协调里，用户既没要求提前开、也没说之后没法操作，主会话仍提前开了一大批审查会话。

## v1.2.0

- 子会话（含审查会话）默认用 medium 思考强度开，不随主会话的强度；用户强调了别的强度才按用户的。
- 用户强调要提前开审查会话，或说明之后没法操作（如要去睡觉）时，主会话趁用户发消息的那一轮提前开一批审查会话待命，轮到时再发消息派给它。

为什么：只有用户发消息的那一轮，主会话才能开新会话；被子会话的消息唤醒时只能留任务卡片。用户不在时，开发会话做完回报，主会话开不了审查会话，协调就停住了。修 bug 不受影响，因为发给原来的开发会话只需要发消息。

## v1.1.1

派审查会话时，任务书明说「第一步调用 `code-review` 这个 skill，参数是 `medium` 和审查范围，不要自己手工审」。

为什么：原来写的是「让它用 code-review（medium 档）只读审查」，模型可以读成「做一次中等力度的审查」。一次真实协调里，有个审查会话就没调 skill，自己手工审了。

## v1.1.0

主会话每次被唤醒时，先把已经不需要的子会话归档，不再逐个问用户：审查会话的发现读完之后、调研会话的结论转告用户之后、做代码的子会话的分支合进主会话分支之后（或这块作废之后）。还在干活、还要返工、分支没合的不归档。合并那一步不再「最后问用户是否归档」。

为什么：一次真实协调里，一次性的审查、调研会话开了十几个，做完以后一直堆在侧边栏；用户要求主会话自己清，并同意不用逐个确认。实测归档只清工作树，分支和提交都还在。

## v1.0.1

子会话改成做完时用 `SendMessage` 把完整报告发给主会话，自己的最后一条回复只写一句话；审查会话的全部发现也这样发。

为什么：一次真实协调里同时开着五六个子会话，主会话要等它们全部停下、自己也空闲才会被叫醒，先做完的子会话的回报一直攒着，结束通知又只引用开头一段，主会话得再用 `list_events` 翻记录才读得全。子会话主动发消息会立刻叫醒主会话、内容完整；最后一条只回一句，是为了不让同一份报告在结束通知里再占一遍上下文。

## v1.0.0

破坏性重写：从 CLI 的 agent teams 改为 Claude Code 桌面端的并行子会话（2026 年 10 月更新：主会话用 `start_session` 开子会话，子会话挂在主会话下、结束时自动回报）。整个 plugin 只剩一个 skill `agent-team:lead`，不到 30 行。

为什么旧版不能沿用：

- 桌面端不支持 agent teams，官方文档写明它只在 CLI 里提供。
- 官方已去掉 `TeamCreate` / `TeamDelete`：现在给子 agent 起名就自动组队，团队目录随会话自动生成。
- 旧版核心的收件箱同步协议，前提是「一轮之内收不到新消息」。现在消息会在两次工具调用之间送达，这个前提不成立了。

改动：

- **删除 `agent-team:teammate`** 及其全部 reference doc。子会话是完整的桌面会话，平台已经规定了它怎么提交、回报、发消息；它该守的规则写在主会话派活的任务书里。
- **删除 superpowers 开发流程层**（brainstorming → writing-plans → TDD implementer → 两阶段 review）和 `docs/` 目录约定。子会话用什么方法论由它自己的 skill 和项目规则决定。
- **审查默认开启**：每个改了代码的块，由主会话另开一次性审查会话（工作树从该块分支切出），用内置 `code-review`（`medium` 档，v0.3.0 起用的是 `xhigh`）只读审查，用文字列出全部发现。主会话判定哪些值得修、发给做这块的子会话修复，每轮换新的审查会话，直到没有值得修的。发现从会话记录里读，不再发成 PR inline comment。
- **合并改为本地合并 + 一个总 PR**：子会话只在自己分支提交、不推送；全部通过后向用户汇报，用户同意后主会话把各分支合进自己的分支、整体测试，再开一个 PR。
- 子会话之间不直接通信，统一经主会话中转。

保留：v0.4.0 的「只管做什么，不管怎么做」边界，以及 v0.3.0 的「一次性审查 + 主会话判定修哪些」。

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
