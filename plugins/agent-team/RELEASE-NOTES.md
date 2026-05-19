# agent-team Release Notes

## Unreleased

### Joined `fomalhaut647-plugins` marketplace

Moved from a standalone repo + self-pointing dev marketplace into the multi-plugin `fomalhaut647-plugins` marketplace. Install path is now `/plugin install agent-team@fomalhaut647-plugins`.

- standalone repo → `plugins/agent-team/` inside the marketplace monorepo
- dropped own `.claude-plugin/marketplace.json` (the marketplace's top-level index now publishes this plugin)
- dropped own `LICENSE` (the marketplace root LICENSE applies)
- `plugin.json` `homepage` / `repository` updated to the monorepo subpath

Plugin functionality and skill contents are unchanged from v0.1.0 — only the packaging moved.

## v0.1.0

Initial release.

- `agent-team:lead` — orchestrates a multi-agent team: `TeamCreate`, spawn prompt template, task assignment, hub-and-spoke topology, shutdown sequence, merge + cleanup ordering.
- `agent-team:teammate` — first-action protocol for spawned teammates: load tool schemas, read team config, per-step + before-SendMessage inbox sync, "no nested teams" framework limit, completion reporting.
- Reference docs for layering the `superpowers` development workflow on top: `skills/lead/references/superpowers-workflow.md`, `skills/teammate/references/superpowers-implementer.md`, `skills/teammate/references/code-review.md`.
