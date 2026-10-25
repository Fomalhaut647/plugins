# session-wrap

> [中文版](README.md)

A Claude Code desktop plugin with a single skill that wraps up a session: tidy the docs the session's changes touch, collect the sub-sessions' changes, commit and push, open a PR from a feature branch, wait for CI within the same turn (fixing failures itself), and merge it into main (or push directly when on main), close the issues the session fixed, then archive the session.

## Installation

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install session-wrap@fomalhaut647-plugins
```

## Prerequisites

- The Claude Code desktop app: looking up sub-sessions and archiving rely on its session tools.
- The GitHub CLI `gh`, used to open the PR, wait for CI, merge, and close issues.

## Usage

The skill activates only when the user's message contains the exact word session-wrap (hyphenation and case don't matter); looser phrasing such as "wrap up" or "merge it" does not trigger it.

See [`skills/session-wrap/SKILL.md`](skills/session-wrap/SKILL.md) for the full text.

## License

MIT — see [LICENSE at the marketplace root](../../LICENSE).
