> [中文版](README.md)

# fomalhaut647-plugins

Personal Claude Code plugins marketplace.

## Add the marketplace

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
| [`agent-team`](plugins/agent-team) | v0.1.0 | `lead` / `teammate` subskills coordinating long-running multi-agent teams; optional reference docs layer the `superpowers` + `code-review` development workflow on top |
| [`skill-simplifier`](plugins/skill-simplifier) | v0.1.0 | Audit a SKILL.md or CLAUDE.md for content that duplicates upstream knowledge sources (system prompt, Tool Descriptions, other Skills, other CLAUDE.md files) and remove the duplication |

## Structure

```
.
├── .claude-plugin/
│   └── marketplace.json    # marketplace index
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
