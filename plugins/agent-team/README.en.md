# agent-team

> [中文版](README.md)

A Claude Code plugin that makes the current desktop session a lead: it splits a larger piece of work across several parallel sub-sessions. The lead splits, dispatches, verifies, triages reviews, and merges; the sub-sessions write the code.

It builds on the October 2026 parallel-sessions update to the Claude Code desktop app: a session can start sub-sessions directly, each with its own worktree and branch, nested under the lead and reporting back when they finish. It does **not** use the experimental agent teams feature, which is only available in the CLI.

## Requirements

- The Claude Code desktop app (Code tab), where the session has the sub-session tools such as `start_session`, `list_events`, and `SendMessage`. The CLI has no such tools, so the plugin does not work there.
- A git repository: sub-sessions are isolated in git worktrees.

## Installation

This plugin is distributed through the [`fomalhaut647-plugins`](../..) marketplace:

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install agent-team@fomalhaut647-plugins
```

For local development without a remote, replace the GitHub path with an absolute path to the marketplace repository:

```
/plugin marketplace add <absolute-path-to-marketplace-repo>
/plugin install agent-team@fomalhaut647-plugins
```

## Usage

Ask for it in plain words, such as "set up a team and split this across parallel sessions", or invoke `/agent-team:lead`. The lead then:

1. **Splits** the work into independent pieces that touch different files. A piece that depends on another waits until that one passes review, then starts from its branch.
2. **Dispatches** one sub-session per piece, each in its own worktree. The brief says what to do, not how: goal, scope, acceptance criteria, boundaries. Sub-sessions commit only on their own branch and take questions to the lead only.
3. **Verifies** each result by reading the full report the sub-session sends and the changes on its branch.
4. **Reviews** every piece that changed code with a one-shot review session running the built-in `code-review` read-only. The lead decides which findings are worth fixing and sends them back to the original sub-session, with a fresh review session each round until nothing is worth fixing.
5. **Merges**: after reporting to you and getting your approval, it merges every branch into the lead's branch, tests the whole, and opens one PR; finally it asks whether to archive the sub-sessions.

## Design choices

- **A lead-side skill only**: sub-sessions are full desktop sessions, and the platform already tells them how to commit, report, and message. The rules they follow travel in the brief, so they need no skill of their own.
- **What, not how**: the lead sees other skills' descriptions but not their bodies. Paraphrasing how to use them makes sub-sessions treat the paraphrase as authoritative and degrade. Changing a sub-session's default behavior must be stated as an explicit override with a reason.
- **One-shot review sessions**: a fresh session each round avoids anchoring on the previous round's conclusions; the lead, holding the global view, decides what gets fixed.
- **Local merge + one PR**: sub-sessions never push, which keeps the remote quiet; the pieces come together in the lead's branch and are tested as a whole before review.
- **Full report by message, one line at the end**: a message from a sub-session wakes the lead right away with the full content, instead of waiting until every sub-session has stopped; its own last reply is a single sentence, so the same report does not take up the lead's context twice.

## Directory layout

```
plugins/agent-team/
├── .claude-plugin/
│   └── plugin.json         # Plugin metadata
├── skills/
│   └── lead/
│       └── SKILL.md        # The lead skill
├── CLAUDE.md               # Contributor guide (AI agents read before changing anything)
├── README.md               # Chinese
├── README.en.md            # this file
└── RELEASE-NOTES.md        # Version history
```

LICENSE lives at the marketplace repo root and applies to this plugin alongside every other plugin.

## Upgrading from 0.x

1.0.0 is a breaking rewrite: `agent-team:teammate`, the inbox sync protocol, the `TeamCreate` flow, and the superpowers workflow reference docs are all gone. See [RELEASE-NOTES](RELEASE-NOTES.md) for why.

## License

MIT — see [LICENSE at the marketplace root](../../LICENSE).
