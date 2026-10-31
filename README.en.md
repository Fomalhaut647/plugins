> [中文版](README.md)

# fomalhaut647-plugins

Personal Claude Code plugins marketplace.

## Install

### In the Claude desktop app

Open Settings → Plugins, click **Add** in the top right, choose to add a marketplace, enter `Fomalhaut647/plugins` (or the full URL `https://github.com/Fomalhaut647/plugins`), and click **Sync**. Once synced, this repo's plugins show up in your plugin list, ready to enable one by one.

![Adding this marketplace in the Claude desktop app (Chinese UI)](docs/images/desktop-add-marketplace.webp)

### In the Claude Code CLI

```
/plugin marketplace add Fomalhaut647/plugins
```

Then browse via `/plugin > Discover` or install a specific plugin:

```
/plugin install <plugin-name>@fomalhaut647-plugins
```

## Plugins

| Name | Status | Description |
| --- | --- | --- |
| [`agent-team`](plugins/agent-team) | v3.1.0 | Make the current Claude Code desktop session a lead that splits work across parallel sub-sessions: an acceptance checklist before coding, one review and a bounded fix budget per piece, then one integration review and a single PR; development can also go to the local Codex CLI |
| [`kill-guard`](plugins/kill-guard) | v0.1.0 | Block commands that find processes by name or command-line text and kill them (`pkill`, `killall`, `xargs kill`, `kill $(pgrep …)`), so Claude stops processes by PID instead |
| [`later`](plugins/later) | v0.1.0 | Queue a message while Claude works so it arrives as a new user turn after the current turn ends, not slipped in between tool calls |
| [`neat-freak`](plugins/neat-freak) | v3.0.1 | After a session, reconcile project docs, CLAUDE.md, and agent memory with the code, and audit whether rules are followed; packaged from [数字生命卡兹克's khazix-skills](https://github.com/KKKKhazix/khazix-skills) |
| [`pyright-lsp`](plugins/pyright-lsp) | v1.0.0 | Python language server (Pyright) that gives Claude Code type diagnostics and go-to-definition; packaged from [Anthropic's official marketplace](https://github.com/anthropics/claude-plugins-official) |
| [`session-wrap`](plugins/session-wrap) | v0.5.0 | Wrap up a Claude Code desktop session: tidy docs, collect sub-sessions' changes, commit and push, merge a PR once CI passes, close fixed issues, archive the session |
| [`skill-simplifier`](plugins/skill-simplifier) | v0.3.0 | Audit a SKILL.md or CLAUDE.md and remove upstream duplication and imagined-error safeguards a fresh-session model would not need |
| [`typescript-lsp`](plugins/typescript-lsp) | v2.1.0 | Give Claude Code TypeScript / JavaScript type diagnostics and go-to-definition through TypeScript 7's built-in language server, with errors pushed automatically after each edit; adapted from [Anthropic's official marketplace](https://github.com/anthropics/claude-plugins-official) |

## Structure

```
.
├── .claude-plugin/
│   └── marketplace.json    # marketplace index
├── docs/images/            # screenshots used by the README
├── LICENSE                 # applies to the marketplace and in-house plugins
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/plugin.json
        ├── skills/             # or commands/ / agents/
        ├── README.md           # Chinese (primary bilingual version)
        ├── README.en.md        # English mirror
        ├── CLAUDE.md           # plugin's own contributor guide
        └── RELEASE-NOTES.md
```

A plugin may also optionally include `.mcp.json`, `.lsp.json`, and similar add-ons. See the [official plugin docs](https://code.claude.com/docs/en/plugins) for the full schema.

## License

[MIT](LICENSE) — applies to this marketplace and every in-house plugin. `neat-freak` is third-party work under its original author's MIT license; see [plugins/neat-freak/LICENSE](plugins/neat-freak/LICENSE). `pyright-lsp` and `typescript-lsp` derive from Anthropic's plugins under Apache-2.0; see the LICENSE in each directory.
