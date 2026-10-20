# session-wrap

> [中文版](README.md)

A Claude Code desktop plugin with a single skill that wraps up a session: tidy docs with neat-freak, commit and push, open a PR from a feature branch, wait for CI within the same turn (fixing failures itself), and merge it into main (or push directly when on main), clean up stale branches and worktrees, then archive the session. On request, it first runs `code-review` in a sub-session before merging.

## Installation

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install session-wrap@fomalhaut647-plugins
```

## Prerequisites

- The Claude Code desktop app: starting sub-sessions, reading their results, and archiving rely on its session tools.
- The `neat-freak` skill, used in step 1 to tidy docs. Install it from this marketplace with `/plugin install neat-freak@fomalhaut647-plugins`.
- The GitHub CLI `gh`, used to open the PR, wait for CI, and merge.

## Usage

The skill activates only when the user's message contains the exact word session-wrap (hyphenation and case don't matter); looser phrasing such as "wrap up" or "merge it" does not trigger it. Optional arguments:

| Phrase | Effect |
|---|---|
| 调用 session-wrap | Tidy, commit, merge, clean up, archive |
| 调用 session-wrap，合并前 review | Review in one sub-session before merging; fix only major bugs |
| 调用 session-wrap，多轮 review | Re-review in a fresh sub-session after each fix until a round finds no major bug |

See [`skills/session-wrap/SKILL.md`](skills/session-wrap/SKILL.md) for the full text.

## License

MIT — see [LICENSE at the marketplace root](../../LICENSE).
