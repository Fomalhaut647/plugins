---
name: skill-simplifier
description: 在即将编写、修改或审查一个 Skill（SKILL.md + references/）或一份 CLAUDE.md 文件时触发，用于审查其中与上游知识源（系统提示词、Tool Description、其他 Skill、其他 CLAUDE.md）重复的内容并去重。触发短语包括 "simplify this skill"、"review this CLAUDE.md"、"is there duplication in..."、"make this leaner"、"审查 / 精简 / 去重 / 瘦身 skill / CLAUDE.md"，或任何用户刚写完、改完一个 skill / CLAUDE.md 的场景。即使用户没有明说 "simplify"，只要他在批评自己的 skill 或 CLAUDE.md 体量或内容重叠，就应该优先调用本 skill —— 这正是它存在的意义。
---

# Skill Simplifier

Claude 写 SKILL.md 和 CLAUDE.md 时倾向于把它认为重要的事一股脑都写上，但分不清这些事是否已经由系统提示词、某个 Tool Description、其他 Skill、其他 CLAUDE.md 提供。重复内容既占 context token、挤压目标文档的独特价值，又会在上游变化时悄悄过时漂移。本 skill 审查一个目标文档，列出每一处重复，自动删除那些"无论如何都该删"的重复，并让用户决定那些"两侧都由用户拥有"的重复该删哪一侧。

## 何时适用

每次调用只处理一个目标，目标必须是以下之一：

- **一个 Skill**：包含 `SKILL.md` 以及可能的 `references/*.md` 的单个 skill 目录；或
- **一份 CLAUDE.md**：位于 `~/.claude/CLAUDE.md`、项目根目录、或某个子目录下的单个 CLAUDE.md 文件。

不适用于：仓库级批量审查；或审查既不是 SKILL.md 也不是 CLAUDE.md 的其他工作流文档。每个目标各跑一次工作流。

## 核心原则

"重复"是指目标文档中的某段内容 —— 如果删掉它，Claude 的行为不会变化，因为同样的约束已经由某个上游知识源提供。判定标准是**语义**重复，而非字面重复：措辞不同也可能是重复。反过来，字面相同的句子也可能不是重复 —— 如果目标补充了上游缺失的情境化"为什么 / 例子 / 取舍"，那它就在做独立的工作。

## 工作流

按顺序执行以下阶段。不要跳过 Stage 4 —— 它是任何改动前的闸门。

### Stage 0 — 确认目标

问用户要审查哪个目标，记下完整路径。若是 skill，列出 `SKILL.md` 和 `references/` 下每一个文件。若是 CLAUDE.md，标出它在 CLAUDE.md cascade 中的位置（global / project / subdir）。

### Stage 1 — 枚举上游知识源

每一处重复都会归到以下四类上游之一。Stage 4 的删除规则按类不同，所以分类要做准。

**1. 系统提示词**（隐式上游）

Claude 没法 Read 系统提示词，但 Claude 自己就带着它在 context 里，知道它说了什么。重点排查这些已经写在系统提示词里的事：用专用 tool 而非 `cat` / `echo`、独立的 tool 调用并行执行、`file_path:line_number` 引用约定、git commit 和 PR 工作流、sandbox 与安全规则、"破坏性操作先确认"等等。如果目标把这些当作规则重新陈述了一遍，就是在重复系统提示词。

**2. Tool Description**（随每个 tool 一同加载）

针对目标显式提到、或工作流隐式涉及的每一个 tool，去读它的 description。

- 内置 tool（Read、Edit、Bash、Write、Skill、...）的 description 已经在 context 里。
- **Deferred tool**（TeamCreate、SendMessage、WebFetch、Monitor、...）只在 `<system-reminder>` 块里以名字出现，schema 没被加载。用 `ToolSearch` 配合 `select:Name1,Name2,...` 把它们的 schema 拉进来。

如果目标重述了一条 tool description 已经提供的用法规则，就是在重复 Tool Description。

**3. 其他 Skill**

当前 Available Skills 列表会出现在 `<system-reminder>` 块里。扫一遍，挑出名字或一句话描述和目标领域重叠的 skill。对每个候选 skill 用 `Skill(name)` 调用它来读完整内容（**不要**用 `Read` 去读 SKILL.md 文件 —— plugin cache 路径不稳定）。如果目标重述了一条"另一个 skill 一旦激活就会提供"的指令，就是在重复 Skill。

**4. 其他 CLAUDE.md**

CLAUDE.md 是 cascade 的。对 CLAUDE.md 目标，上游链是从 `~/.claude/CLAUDE.md` 一直到目标父目录的所有 CLAUDE.md。对 Skill 目标，上游链是 `~/.claude/CLAUDE.md` 加上 skill 预期将运行其中的项目根 CLAUDE.md。逐个 Read。如果目标重述了一条更上游的 CLAUDE.md 已经提供的规则，就是在重复 CLAUDE.md。

### Stage 2 — 激活辅助 skill

辅助 skill 用来提醒你"好的 skill / 好的 CLAUDE.md 长什么样"。按目标类型分叉：

- **目标是 Skill**：激活 `superpowers:writing-skills` 和 `skill-creator`。
- **目标是 CLAUDE.md**：激活 `claude-md-management:claude-md-improver`。如果改动涉及吸收当前 session 的学到的经验，再激活 `claude-md-management:revise-claude-md`。

### Stage 3 — 完整读一遍目标

- Skill 目标：Read `SKILL.md` 和 `references/` 下每一个文件。
- CLAUDE.md 目标：Read 目标文件本身。Stage 1.4 已经读过其 cascade 链 —— 确认覆盖即可，不必重读。

### Stage 4 — 输出重复审查报告（**不要**改写）

产出一份两区（或三区）报告交给用户。**Stage 5 之前不要做任何 Edit。** 报告写长没关系，覆盖完整比简短更重要。

**Zone A — 自动删除**（上游是系统提示词或 Tool Description）

这些条目会从目标中删除，不必逐条征求用户同意。理由：上游不可改 —— 用户没法编辑系统提示词或 Tool Description，唯一的处理路径就是删目标侧。仍然把每一条 Zone A 列出来，方便用户做合理性核查；同时明确说明 Stage 5 会把它们都删掉，除非用户对具体某条提出反对。

每条格式：

```
A.<n>  [目标文件 : 起行号-止行号]  重复于 [系统提示词 | tool:<工具名> 的 description]
       <目标内容的引用或意译>
       → 从目标中删除
```

**Zone B — 用户决定**（上游是其他 Skill 或其他 CLAUDE.md）

两侧都由用户拥有，由用户决定。每条三选一：删目标侧、删上游侧、或两侧都留并加显式的交叉引用。

每条格式：

```
B.<n>  [目标文件 : 起行号-止行号]  重复于 [skill:<名字> | CLAUDE.md:<路径>]
       目标侧:    <引用或意译>
       上游侧:    <引用或意译>
       → 选择: (a) 删目标侧  (b) 删上游侧  (c) 两侧都留, 加交叉引用
```

明显成组的条目可以合并成一个决定，但**不要**把上游来源不同的条目合并成同一条 —— 用户可能想对不同上游做不同选择。

**Zone C — 内部分层**（仅当目标是带 `references/` 的 Skill 时出现）

一个 skill 的 `SKILL.md` 总是在激活时加载；`references/*.md` 按需加载。内容在两层都出现就破坏了 progressive disclosure。用 Zone B 同款格式，因为"哪一层拥有这段内容"是一个设计决策。

等用户给出 Zone B 和 Zone C 的回应再进入 Stage 5。

### Stage 5 — 应用

用 `Edit`（不要整体重写）按 Stage 4 的决定逐条删除或合并。

- Zone A 条目：从目标中删除。用户明确反对的那几条跳过。
- Zone B 条目：按用户选择执行。如果选了 "(c) 两侧都留, 加交叉引用"，把两侧都改写成简短的相互引用。
- Zone C 条目：把共享内容上提（或下移）到合适的那一层，另一层换成指针。

不要碰审查范围之外的内容。不要为风格调结构、不要为语气改措辞、不要新增内容。本 skill 的工作是"删除重复"，不是"重写"。

## 判定规则（难判时的依据）

**语义，而非字面。** 目标里一个 paraphrase 了系统提示词规则的句子仍然算重复。反之，两处字面相同的句子可能并非重复 —— 如果目标补充了上游缺失的情境化"为什么 / 例子 / 取舍"，保留信息更丰富的那一侧。

**保守删除。** 拿不准时保留目标内容，加一句 "see X" 的指针即可。多一句话的代价很小；丢掉用户依赖的情境化指引的代价更大。漏删（false-negative）在下一次审查时还能补救；误删（false-positive）则悄悄回退了 Claude 的行为。

**不要把临时知识固化进去。** 通过 ToolSearch / WebSearch / Read 一次性获取的 schema、版本号、API 字段名等，**绝不能**抄进 SKILL.md 或 CLAUDE.md 作为"方便的 inline 参考"。上游会变，inline 副本会过时。让目标在每次调用时重新获取。

**触发内容神圣不可动。** Skill 的 `description:` frontmatter，以及 CLAUDE.md 里的触发短语（"看到 X 时做 Y"），是这份文档被激活或被应用的入口。即便它们和某条上游措辞重叠，也要保留 —— 删掉就破坏了触发路径。

**具体胜过泛化。** 一份重述了系统提示词泛化规则、但补上了具体例子、取舍或为什么的 skill / CLAUDE.md 是在做真实工作。当这种张力出现时，保留情境化的那一版，只裁掉冗余的泛化前言。

## 红线（不要做的事）

- 不要在用户给出 Zone B 和 Zone C 决定之前进入 Stage 5。
- 不要删目标的 `description:` frontmatter，或任何触发激活的短语。
- 不要为风格重写。本 skill 只删重复。
- 一次调用不要审超过一个目标。如果用户有多个 skill 或 CLAUDE.md 要审，每个文件各跑一次工作流 —— 上游枚举可能因目标而异。
- 不要建议改系统提示词或 Tool Description。它们是只读上游；唯一可动的杠杆是目标。
