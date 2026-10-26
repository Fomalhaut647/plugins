# kill-guard

> [中文版](README.md)

A Claude Code plugin with a single hook: when a Bash command Claude is about to run finds processes by name or command-line text and kills them, the hook blocks it and tells Claude to stop processes by PID instead.

## Why

`pkill -f` matches substrings of the whole command line. On a Mac almost every app lives under `/Applications` or `Application Support`, so common letters like "cat" or "app" are already in the path. A single `pkill -f "cat"` once killed the Claude desktop app, every parallel session, Chrome and WeChat at once, losing work in progress and unsaved content. A rule in CLAUDE.md relies on the model remembering it; with permission prompts bypassed, nothing stops the command at run time. This hook does.

## What is blocked and what is allowed

| Blocked | Allowed |
|---|---|
| `pkill …`, `killall …` (including `sudo` and full paths) | `kill <PID>`, `kill $!`, `kill $(cat pidfile)` |
| `… \| xargs kill` (`ps \| grep \| xargs kill`, `pgrep \| xargs kill`, …) | `pgrep -fl`, `ps … \| grep …` to list only |
| `kill $(pgrep …)`, `kill $(pidof …)`, `kill $(ps …)` | `kill $(lsof -ti tcp:<port> -sTCP:LISTEN)` to stop only the listener on a port |

Only the command position counts: `grep pkill file` or `echo "don't use pkill"` merely mention the word and pass; commands run on another machine over ssh (the quoted remote command) also pass. A blocked command does not run, and Claude receives the reason and the alternatives.

## Installation

This plugin is distributed through the [`fomalhaut647-plugins`](../..) marketplace:

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install kill-guard@fomalhaut647-plugins
```

In the desktop app, sync this marketplace under Settings → Plugins and enable kill-guard. Requires `python3` on the machine.

## Directory layout

```
plugins/kill-guard/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   ├── hooks.json        # PreToolUse, matches Bash
│   └── kill_guard.py     # rules and the message to Claude
├── CLAUDE.md
├── README.md             # Chinese
├── README.en.md          # this file
└── RELEASE-NOTES.md
```

## License

MIT — see [LICENSE at the marketplace root](../../LICENSE).
