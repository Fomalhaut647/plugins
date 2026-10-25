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

Invoke `/agent-team:lead` (manual invocation only; phrases like "set up a team" do not trigger it). The lead then:

1. **Splits** the work into independent pieces that touch different files. A piece that depends on another waits until that one passes review, then starts from its branch. If later pieces were started early, the earlier piece's fixes during review are not relayed to them one by one; they get one message to merge it once it passes.
2. **Dispatches** one sub-session per piece, each in its own worktree, at high effort by default. The brief says what to do, not how: goal, scope, acceptance criteria, boundaries. Sub-sessions commit only on their own branch and take questions to the lead only.
3. **Verifies** each result by reading the full report the sub-session sends and the changes on its branch.
4. **Reviews** every piece that changed code with a one-shot review session running the built-in `code-review` read-only. The lead picks out only the major bugs and sends them back to the original sub-session, leaving medium and minor issues alone and listing them as open issues in the final report, with a fresh review session each round until no major bug remains. By default it starts no sub-sessions in advance; only when you explicitly ask for that (say, "I'm going offline, start the sessions you'll need now" or "don't ask me, run the whole thing on your own") does the lead start the later pieces' development sessions and one or two review sessions per piece in advance to stand by. Once the standby sessions are used up, it leaves task cards for you to start.
5. **Merges**: once everything passes, without asking you first, it merges every branch into the lead's branch, tests the whole, opens one PR, and then reports to you.

Each time the lead wakes up, it also archives the sub-sessions it no longer needs: review sessions whose findings it has read, research sessions whose conclusions it has passed on to you, and development sessions whose branch it has merged.

## Design choices

- **A lead-side skill only**: sub-sessions are full desktop sessions, and the platform already tells them how to commit, report, and message. The rules they follow travel in the brief, so they need no skill of their own.
- **What, not how**: the lead sees other skills' descriptions but not their bodies. Paraphrasing how to use them makes sub-sessions treat the paraphrase as authoritative and degrade. Changing a sub-session's default behavior must be stated as an explicit override with a reason.
- **One-shot review sessions**: a fresh session each round avoids anchoring on the previous round's conclusions; the lead, holding the global view, decides what gets fixed.
- **Major bugs only**: fixing medium and minor issues too brings new changes every round, a fresh review session finds new minor issues in them, and the review-fix loop never settles.
- **No fix-by-fix relay downstream**: each relay wakes every downstream session and makes it reread its long context; one message after the upstream piece passes review is enough.
- **Local merge + one PR**: sub-sessions never push, which keeps the remote quiet; the pieces come together in the lead's branch and are tested as a whole before review.
- **Full report by message, one line at the end**: a message from a sub-session wakes the lead right away with the full content, instead of waiting until every sub-session has stopped; its own last reply is a single sentence, so the same report does not take up the lead's context twice.
- **Automatic archiving**: one-shot review and research sessions pile up and crowd the sidebar; archiving only removes the worktree, and the branch and its commits stay.

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
