# skill-simplifier

> [中文版](README.md)

A Claude Code plugin with a single skill that audits a SKILL.md (with optional `references/`) or a CLAUDE.md and removes both content duplicated from upstream knowledge sources and safeguards against mistakes an unpolluted model would never make.

## Why

Claude tends to write SKILL.md and CLAUDE.md by dumping everything it considers important, but cannot tell what upstream sources already supply. It can also fossilize a mistake that just appeared in the current session into a safeguard future models do not need. Both duplication and imagined-error safeguards consume context; the latter can teach a fresh-session model a misconception it did not previously have. This skill auto-deletes read-only-upstream duplication and imagined-error safeguards, then asks the user to decide duplication between user-owned sources.

## Installation

This plugin is distributed through the [`fomalhaut647-plugins`](../..) marketplace. Install in two steps:

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install skill-simplifier@fomalhaut647-plugins
```

For local development without a remote, replace the GitHub path with an absolute path to the marketplace repository:

```
/plugin marketplace add <absolute-path-to-marketplace-repo>
/plugin install skill-simplifier@fomalhaut647-plugins
```

## The skill

| Skill | Activated by | What it does |
|---|---|---|
| `skill-simplifier` | The user, when about to write / edit / review a SKILL.md or a CLAUDE.md | Enumerates upstream knowledge sources, checks imagined-error safeguards against a fresh-session counterfactual, auto-deletes Zones A/B, and asks the user to decide Zone C (and Zone D when present) |

The skill loads deferred tool schemas via `ToolSearch` rather than restating them.

## Workflow at a glance

1. **Stage 0** — confirm the target (one skill or one CLAUDE.md per invocation).
2. **Stage 1** — enumerate four upstream source classes: system prompt, Tool Descriptions, other Skills, other CLAUDE.md files.
3. **Stage 2** — activate helper skills appropriate to the target type.
4. **Stage 3** — read the target in full.
5. **Stage 4** — imagine the target loading for the first time in a fresh session unpolluted by the current conversation, then test whether the model would actually make each guarded-against mistake.
6. **Stage 5** — produce an audit report with two to four zones. **Do NOT edit yet.**
   - **Zone A**: upstream is system prompt / Tool Description → auto-delete from target (upstream is read-only).
   - **Zone B**: an imagined-error safeguard that cannot arise in a fresh session and has no observed failure evidence → auto-delete from target.
   - **Zone C**: upstream is another Skill / CLAUDE.md → user decides which side to delete (both sides are user-owned).
   - **Zone D** (skill target with `references/` only): internal duplication between SKILL.md and `references/`.
7. **Stage 6** — apply via `Edit`, per Stage 5 decisions.

See [`skills/skill-simplifier/SKILL.md`](skills/skill-simplifier/SKILL.md) for the full text.

## Directory layout

```
plugins/skill-simplifier/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── skill-simplifier/
│       ├── SKILL.md
│       └── references/      # currently empty
├── CLAUDE.md                # contributor guide (AI agents must read before PR)
├── README.md                # Chinese
├── README.en.md             # this file
└── RELEASE-NOTES.md
```

LICENSE lives at the marketplace repo root and applies to this plugin alongside every other plugin.

## Why a skill (not a subagent)

This plugin is deliberately shaped as a skill rather than a `code-simplifier`-style subagent. Stage 5 hands control back to the user to decide every Zone C item, and subagents are dispatch-and-return — they cannot pause mid-run to ask the user. Running the audit in the main agent's session lets it use recent editing context to judge "specific beats generic," while Stage 4 deliberately removes that context when modeling what a fresh-session agent would know.

## License

MIT — see [LICENSE at the marketplace root](../../LICENSE).
