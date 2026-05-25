# agent-team

> [中文版](README.md)

A Claude Code plugin that gives you two subskills for coordinating long-running multi-agent teams, plus optional reference docs for layering the `superpowers` development workflow on top.

- **Primitive skills** (`agent-team:lead` / `agent-team:teammate`) cover the team mechanism itself — `TeamCreate`, spawn rules, inbox sync, shutdown sequence — independent of any particular development methodology.
- **Optional reference docs** under each skill's `references/` directory layer the full `superpowers` development workflow (brainstorming → writing-plans → TDD implementers → reviewer teammates → PR fix loop → merge) on top of the primitive. Read on demand from the lead skill's Step 3 decision; spawn prompts ask teammates to read their corresponding doc when the workflow signals it.

Keeping the superpowers workflow as a reference doc rather than a separate skill keeps the per-session skill count and description-context overhead low while preserving all the content.

## Installation

This plugin is distributed through the [`fomalhaut647-plugins`](../..) marketplace. Install in two steps:

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install agent-team@fomalhaut647-plugins
```

For local development without a remote, replace the GitHub path with an absolute path to the marketplace repository:

```
/plugin marketplace add <absolute-path-to-marketplace-repo>
/plugin install agent-team@fomalhaut647-plugins
```

## Subskills

| Subskill | Activated by | Covers |
|---|---|---|
| `agent-team:lead` | The human user, when multi-agent long-running coordination is needed | `TeamCreate`, spawn prompt template (which asks teammates to invoke `agent-team:teammate`), task assignment, hub-and-spoke topology, shutdown sequence, merge + cleanup ordering, decision to also read the superpowers workflow doc |
| `agent-team:teammate` | A team lead's spawn prompt (`Skill('agent-team:teammate')` is the new teammate's first action) | Per-step + before-SendMessage inbox sync protocol (the within-turn complement to `TeamCreate`'s between-turns auto-delivery), "no nested teams" framework limit, completion reporting, optional superpowers workflow reference |

Both use `ToolSearch` to load live schemas for the deferred coordination tools (`TeamCreate`, `TeamDelete`, `SendMessage`, the `Task*` family, `EnterWorktree`, `ExitWorktree`) rather than restating them.

## Optional reference docs

| Doc | Read by | Covers |
|---|---|---|
| `skills/lead/references/superpowers-workflow.md` | The lead, when running the full superpowers development workflow | Steps 1-3 (brainstorming, writing-plans, worktree creation loop + spawn), Step 8 (reviewer teammate spawn), Step 10 (merge + cleanup using `ExitWorktree(action="remove")`) |
| `skills/teammate/references/superpowers-implementer.md` | An implementer teammate, when spawned into the superpowers workflow with a worktree + spec + plan | Step 4 startup (quadruple skill invoke including `requesting-code-review`, `EnterWorktree`, read brief), Step 5 implementer subagent prompt template, Step 6 two-stage review subagent pattern, Step 7 PR submission + per-teammate progress file, Step 9 implementer side of the fix loop |
| `skills/teammate/references/code-review.md` | A one-shot reviewer teammate (`reviewer-pr-<N>`), spawned with a PR URL + the implementer's worktree path | Enters the implementer's worktree and runs the bundled `code-review` once (`xhigh --comment`) → findings posted as inline PR comments and forwarded to the lead → idle until shutdown; the lead decides which findings are worth fixing and whether to re-review |

Note: `superpowers-workflow.md` also describes an optional `docs/` project layout (`vision.md` / `overview.md` / `specs/A-xxx.md` / `plans/PlanN-<teammate>.md` / `progress/PlanN-<teammate>.md`) for long-running projects that span multiple agent-team sessions. See its Step 0.

## Composition

- **Plain team coordination** (no superpowers): lead invokes `agent-team:lead`, decides at Step 3 not to read the workflow doc; spawn prompts invoke `agent-team:teammate`.
- **Superpowers workflow team**: lead invokes `agent-team:lead`, reads `lead/references/superpowers-workflow.md` at Step 3; spawn prompts invoke `agent-team:teammate` *and* tell the new teammate to Read the matching teammate-side doc (`superpowers-implementer.md` for implementers, `code-review.md` for reviewer teammates) as part of startup.

The skills don't auto-activate — the lead is responsible for invoking the right pair, and each spawn prompt names which docs the new teammate should read alongside.

## Usage

### Plain coordination

Invoke `Skill('agent-team:lead')` when you want multi-agent long-running collaboration. Follow its workflow; spawn teammates whose first action is `Skill('agent-team:teammate')`.

### Superpowers-driven coordination

Invoke `Skill('agent-team:lead')`, then at Step 3 Read `references/superpowers-workflow.md` for the orchestration. Spawn teammates whose first action is `Skill('agent-team:teammate')` and whose startup instructions tell them to Read the matching teammate-side reference doc (`references/superpowers-implementer.md` for implementers, `references/code-review.md` for reviewer teammates).

## Directory layout

```
plugins/agent-team/
├── .claude-plugin/
│   └── plugin.json         # Plugin metadata
├── skills/
│   ├── lead/
│   │   ├── SKILL.md
│   │   └── references/superpowers-workflow.md
│   └── teammate/
│       ├── SKILL.md
│       └── references/
│           ├── code-review.md
│           └── superpowers-implementer.md
├── CLAUDE.md               # Contributor guide (AI agents must read before PR)
├── README.md               # Chinese
├── README.en.md            # this file
└── RELEASE-NOTES.md        # Version history
```

LICENSE lives at the marketplace repo root and applies to this plugin alongside every other plugin.

## Why these splits

- **Lead vs teammate**: their first actions and ongoing protocols are non-overlapping; mixing both into one skill produces 500+ lines of mostly-irrelevant content for whichever role is reading.
- **Skill vs reference doc**: the superpowers workflow is one mode of using the team primitive — not always relevant. Keeping it as a reference doc means zero context cost when not used and full content when needed.

## License

MIT — see [LICENSE at the marketplace root](../../LICENSE).
