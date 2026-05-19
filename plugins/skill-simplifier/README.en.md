# skill-simplifier

A Claude Code plugin with a single skill that audits a SKILL.md (with optional `references/`) or a CLAUDE.md for content duplicating its upstream knowledge sources — the system prompt, Tool Descriptions, other Skills, or other CLAUDE.md files — and removes the duplication.

中文版见 [README.md](README.md)。

## Why

Claude tends to write SKILL.md and CLAUDE.md by dumping everything it considers important, but cannot tell which of those facts the system prompt, a Tool Description, another Skill, or another CLAUDE.md already supplies. Duplicated content steals context tokens from the document's unique value and drifts out of sync when the upstream changes. This skill audits one target, names every duplication, deletes the duplications that always belong deleted (upstream = system prompt / Tool Description), and asks the user to decide the duplications between user-owned sources (upstream = other Skills / other CLAUDE.md).

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
| `skill-simplifier` | The user, when about to write / edit / review a SKILL.md or a CLAUDE.md | Enumerates upstream knowledge sources, classifies duplications into two (or three) zones, auto-deletes Zone A, asks the user to decide Zone B (and Zone C when present) |

The skill loads deferred tool schemas via `ToolSearch` rather than restating them.

## Workflow at a glance

1. **Stage 0** — confirm the target (one skill or one CLAUDE.md per invocation).
2. **Stage 1** — enumerate four upstream source classes: system prompt, Tool Descriptions, other Skills, other CLAUDE.md files.
3. **Stage 2** — activate helper skills appropriate to the target type.
4. **Stage 3** — read the target in full.
5. **Stage 4** — produce a duplication audit report with two (or three) zones. **Do NOT edit yet.**
   - **Zone A**: upstream is system prompt / Tool Description → auto-delete from target (upstream is read-only).
   - **Zone B**: upstream is another Skill / CLAUDE.md → user decides which side to delete (both sides are user-owned).
   - **Zone C** (skill target with `references/` only): internal duplication between SKILL.md and `references/`.
6. **Stage 5** — apply via `Edit`, per Stage 4 decisions.

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

This plugin is deliberately shaped as a skill rather than a `code-simplifier`-style subagent. Stage 4 hands control back to the user to decide every Zone B item, and subagents are dispatch-and-return — they cannot pause mid-run to ask the user. Running the audit in the main agent's session also lets it use the user's recent editing context to tell apart "specific-beats-generic" content from real duplication.

## License

MIT — see [LICENSE at the marketplace root](../../LICENSE).
