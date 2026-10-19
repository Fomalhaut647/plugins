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
| [`agent-team`](plugins/agent-team) | v1.1.1 | Make the current Claude Code desktop session a lead that splits work across parallel sub-sessions, gates each piece with one-shot `code-review` sessions, and merges everything into one PR once the user approves |
| [`session-wrap`](plugins/session-wrap) | v0.2.0 | Wrap up a Claude Code desktop session: tidy docs, commit and push, merge a PR once CI passes, clean up branches and worktrees, archive the session, with optional pre-merge `code-review` |
| [`skill-simplifier`](plugins/skill-simplifier) | v0.2.1 | Audit a SKILL.md or CLAUDE.md and remove upstream duplication and imagined-error safeguards a fresh-session model would not need |

## Structure

```
.
├── .claude-plugin/
│   └── marketplace.json    # marketplace index
├── docs/images/            # screenshots used by the README
├── LICENSE                 # applies to this marketplace and every plugin
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/plugin.json
        ├── skills/             # or commands/ / agents/
        ├── README.md           # Chinese (primary bilingual version)
        ├── README.en.md        # English mirror
        ├── CLAUDE.md           # plugin's own contributor guide
        └── RELEASE-NOTES.md
```

A plugin may also optionally include `.mcp.json` and similar add-ons. See the [official plugin docs](https://code.claude.com/docs/en/plugins) for the full schema.

## License

[MIT](LICENSE) — applies to this marketplace and every plugin.
