# agent-team

> [中文版](README.md)

A Claude Code plugin that makes the current desktop session a lead: it splits a larger piece of work across several parallel sub-sessions. The lead splits, dispatches, agrees acceptance checklists, verifies, triages reviews, and merges; the sub-sessions write the code, and reviews go to the local Codex CLI by default.

It builds on the October 2026 parallel-sessions update to the Claude Code desktop app: a session can start sub-sessions directly, each with its own worktree and branch, nested under the lead and reporting back when they finish. It does **not** use the experimental agent teams feature, which is only available in the CLI.

## Requirements

- The Claude Code desktop app (Code tab), where the session has the sub-session tools such as `start_session`, `list_events`, and `SendMessage`. The CLI has no such tools, so the plugin does not work there.
- A git repository: sub-sessions are isolated in git worktrees.
- The Codex CLI installed and logged in on this machine: it does the reviews by default (not needed when Claude reviews instead); checking Codex's progress needs python3.

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

Invoke `/agent-team:lead` followed by what to do, for example "/agent-team:lead finish cards C2, C3, and C4 on line C" (manual invocation only; phrases like "set up a team" do not trigger it). The lead then:

1. **Splits** the work into independent pieces that touch different files, breaking up cards that are too big. A piece that depends on another starts from that piece's branch once it passes.
2. **Starts the sessions** for the whole run in the turn you send your message: one development session per piece plus one integration fix session, each in its own worktree, at high effort by default; reviews go to Codex, so no review sessions are started. Sessions whose turn has not come stand by without reading anything, so you never have to click task cards mid-run.
3. **Agrees an acceptance checklist first**: each development session first sends a checklist (the behaviors to deliver, the red lines that apply, what is explicitly out of scope, open product questions) and writes code only after the lead confirms it. Questions that change product behavior are batched into one message to you, each with a recommendation, plus a notification; if you said "don't ask me", the lead follows its recommendations and lists those decisions in the final report for you to overrule.
4. **Develops and verifies**: every checklist item needs an automated test; the lead runs the tests itself and checks that the changes stay in scope.
5. **Reviews once**: each piece is reviewed exactly once, by the local Codex in its own built-in review mode, read-only, checking every item of the acceptance checklist. The lead sorts the findings by a fixed standard: serious issues that break the checklist, cross a red line, or come with a concrete failure scenario block the merge; design questions the checklist does not settle are decided as in step 3; everything else goes into issues labeled 「审查遗留」 (review backlog) and is not fixed in this run.
6. **Fixes small and verifies with tests**: blocking issues go back to the development session, which first writes a test that fails before the fix, then makes the smallest change; the lead verifies through the tests, without another review, and sends the fix back for one more try if the check fails. A fix that needs a class-wide rework or a structural change becomes a separate piece.
7. **Budget and circuit breaker**: each piece gets one review and at most two fixes, the second only when the first fails the check. If it still does not pass, that piece stops while the others carry on, and the lead brings you options with a recommendation; nothing that crosses a red line merges as is.
8. **Integrates and merges**: once every piece passes, without asking you first, it merges every branch into the lead's branch, runs all the tests, and has Codex run one integration review that looks at how the pieces fit together and at every piece's fixes; issues found at this stage go to the integration fix session, which fixes them on the merged branch instead of waking each piece's original development session; then it opens one PR and reports, per card, which behaviors are proven by tests, what is not verified, which decisions it made for you, the review backlog, and the PR link.

Ask for progress any time and the lead answers in one screen: where each piece is, how much of its budget is used, and roughly how long is left. Every report opens by saying whether the whole task is closed, and if not, what is left and what it is waiting on; questions and reports explain each thing they mention in a sentence, without assuming you remember the design docs and task cards. Each run's state file (every piece's stage, budget, decisions, and where every finding went, plus Codex's time and usage when development goes to Codex) stays in `~/.claude/plugins/data/agent-team-fomalhaut647-plugins/runs/`, named after the lead's session id, for later retrospectives. Each time the lead wakes up, it also archives the sub-sessions it no longer needs: review sessions whose findings it has read (only when Claude reviews), research sessions whose conclusions it has passed on to you, development sessions once their piece passes, and the integration fix session once the integration review passes.

Every so often (say, at each stage boundary), clear the accumulated backlog with "/agent-team:lead 清理审查遗留问题" (clear the review backlog): the lead rechecks each item against the latest code and closes stale ones, groups the rest by root cause, adds automatic checks for recurring classes, and writes the lessons back into the design docs or project rules.

Reviews and the integration review go to the Codex CLI on this machine by default, so a different model reviews; by default it runs gpt-6.1-sol at xhigh reasoning effort with Fast mode on, unless the invocation says otherwise. Codex can only read while reviewing, and a background script wakes the lead when it is done; reviews are quick, so there is no heartbeat. To have Claude review instead (say, without Codex on this machine), add "审查用 Claude" (review with Claude) to the invocation: each piece and the integration then get a Claude review session running the built-in `code-review`.

To save more Claude usage, add "开发用 Codex" (develop with Codex) to the invocation: each piece is then developed by Codex, while reviews and the integration review go to Claude review sessions. While developing, Codex can only write the piece's own worktree (with network access), and it never commits or pushes; once it finishes, a background script runs the full test suite and hands failures back to it, waking the lead only when all of that is done. While Codex develops, a heartbeat wakes the lead every 55 minutes and it replies in one line, so its prompt cache does not expire.

If Codex errors out or runs out of usage, that piece stops and you are notified; the lead never quietly switches to Claude.

## Design choices

- **A lead-side skill only**: sub-sessions are full desktop sessions, and the platform already tells them how to commit, report, and message. The rules they follow travel in the brief, so they need no skill of their own.
- **What, not how**: the lead sees other skills' descriptions but not their bodies. Paraphrasing how to use them makes sub-sessions treat the paraphrase as authoritative and degrade. Changing a sub-session's default behavior must be stated as an explicit override with a reason.
- **Done means the acceptance checklist, not a quiet review**: a review that looks for problems always finds something, and the built-in `code-review` at high is built to surface more rather than less, with no verification and up to 10 findings per run. Across two real runs, none of the 11 pieces ever reached "no serious issues left", and the review-fix rounds kept coming.
- **One review per piece, sorted by a fixed standard**: the first review finds almost only real defects; in later rounds, 70–90% of what got fixed came from the previous round's fixes or from fixes that missed part of the class. Picking the "serious" ones by feel drifts from round to round.
- **Checklist first**: design left undecided gets decided inside the fix loop, with each review raising the bar; asking up front, once, avoids that.
- **Small fixes, verified by tests**: once a fix grows into a redesign, it breeds the next round's issues; a minimal change plus a test that fails before the fix needs no further review round.
- **Budget and circuit breaker**: a loop needs a stopping rule; a stuck piece stops and changes course instead of holding up the whole run.
- **Integration review**: issues where pieces meet are invisible to per-piece reviews; the fixes also get their one independent review here.
- **Integration fixes go to a fresh session**: by the time the integration review reports, the development sessions have usually sat idle for over an hour, their prompt caches have expired, and waking one rewrites its whole long context; issues where pieces meet also often span several pieces. So each development session is archived as soon as its piece passes, and integration issues go to an integration fix session started at kickoff, which fixes them together on the merged branch.
- **Start every session up front**: with a capped number of rounds, the number of sessions is known at kickoff; standby sessions read nothing, so waking one costs the same in cache as starting a new session.
- **Later pieces wait for their dependencies**: upstream review and fixes end quickly, so downstream pieces start from the upstream branch once it passes, with no fix-by-fix relays and no long-context sessions sitting idle.
- **Local merge + one PR**: sub-sessions never push, which keeps the remote quiet; the pieces come together in the lead's branch and are tested as a whole before review.
- **Full report by message, one line at the end**: a message from a sub-session wakes the lead right away with the full content, instead of waiting until every sub-session has stopped; its own last reply is a single sentence, so the same report does not take up the lead's context twice.
- **Automatic archiving**: one-shot review and research sessions pile up and crowd the sidebar; archiving only removes the worktree, and the branch and its commits stay.
- **A state file that outlives the session**: the scratchpad is cleared along with the session, so the state file lives in this plugin's data folder, named after the session id, where a retrospective can match it to the session transcript.
- **A different model reviews**: by default Claude develops and Codex reviews; when development goes to Codex, Claude reviews. The other model catches the developing model's own blind spots.
- **Development can go to Codex**: in past runs, development sessions used about 80% of the Claude usage, the lead and the reviews about 10% each.
- **Codex reviews in its own review mode**: just as Claude review sessions run the built-in `code-review`, the reviewer uses its own review flow instead of reviewing by hand.
- **Dispatch once, wake once**: Claude usage is driven by the number of model calls, since every call rereads the whole context; so the full test suite and the automatic fix rounds run to completion inside the script before the lead is woken.
- **Heartbeat while Codex develops**: the lead's prompt cache expires after an hour idle, and waking after that rewrites the whole context; Codex development sometimes runs past an hour, and a heartbeat every 55 minutes that replies in one line costs far less. Reviews are quick, so they get no heartbeat.
- **Codex stays in a sandbox**: whatever your Codex settings allow, the dispatch script only lets it read, or write the piece's own worktree; the lead commits and pushes.

## Directory layout

```
plugins/agent-team/
├── .claude-plugin/
│   └── plugin.json         # Plugin metadata
├── skills/
│   └── lead/
│       ├── SKILL.md        # The lead skill
│       └── codex.sh        # Dispatch script for handing reviews or development to Codex
├── CLAUDE.md               # Contributor guide (AI agents read before changing anything)
├── README.md               # Chinese
├── README.en.md            # this file
└── RELEASE-NOTES.md        # Version history
```

LICENSE lives at the marketplace repo root and applies to this plugin alongside every other plugin.

## Upgrading from 3.x

4.0.0 hands reviews and the integration review to the local Codex CLI by default, while Claude sub-sessions still develop, so no review sessions are started at kickoff. Codex must be installed and logged in on this machine; to have Claude review as in 3.x, add "审查用 Claude" (review with Claude) to the invocation. "开发用 Codex" (develop with Codex) works as before. See [RELEASE-NOTES](RELEASE-NOTES.md) for details.

## Upgrading from 2.x

3.0.0 adds handing development to the local Codex CLI, together with its dispatch script; without "开发用 Codex" (develop with Codex) in the invocation, the lead works as in 2.x. See [RELEASE-NOTES](RELEASE-NOTES.md) for details.

## Upgrading from 1.x

2.0.0 replaces the whole review-fix approach: instead of reviewing until no serious bug remains, each piece gets an acceptance checklist up front, one review, at most two fixes (the second only when the first fails the check), and one integration review at the end; sessions are started all at once at kickoff; and the lead can now clear the accumulated review backlog. See [RELEASE-NOTES](RELEASE-NOTES.md) for why.

## Upgrading from 0.x

1.0.0 is a breaking rewrite: `agent-team:teammate`, the inbox sync protocol, the `TeamCreate` flow, and the superpowers workflow reference docs are all gone. See [RELEASE-NOTES](RELEASE-NOTES.md) for why.

## License

MIT — see [LICENSE at the marketplace root](../../LICENSE).
