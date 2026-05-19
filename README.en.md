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
| [`agent-team`](plugins/agent-team) | placeholder | Multi-agent team coordination for long-running collaborative Claude Code sessions |
| [`skill-simplifier`](plugins/skill-simplifier) | placeholder | Review and simplify existing Claude Code skills for clarity and reuse |

## Structure

```
.
├── .claude-plugin/
│   └── marketplace.json    # marketplace index
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json
        └── README.md
```

Each plugin may optionally include `commands/`, `agents/`, `skills/`, `.mcp.json`, and a `LICENSE`. See the [official plugin docs](https://code.claude.com/docs/en/plugins) for the full schema.
