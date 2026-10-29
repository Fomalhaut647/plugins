# later

> [中文版](README.md)

A Claude Code plugin with a single skill: queue a message while Claude is working so it arrives as a new user turn after the whole current turn ends, instead of being slipped in alongside a tool result between tool calls.

## Why

A message sent with Enter while Claude is working gets merged into the same turn as soon as the current tool call finishes. When what you want to add is "do this after you finish", slipping it in mid-turn interrupts what Claude is doing. Claude Code has no setting to hold a message until the turn ends, but a slash command sent while Claude is responding waits until the turn finishes before it runs. This skill does nothing itself: it passes the text after it through unchanged, using that behavior to defer the message to the end of the turn.

## Usage

While Claude is working, send this in the prompt box:

```
/later:later your message
```

When the turn ends, Claude receives "your message", exactly as if you had sent it directly at that point. Used while Claude is idle, it is the same as sending the message directly.

## Test results

Tested on 2026-10-29 in the desktop app (Claude Code 2.1.309), as a project skill: the message queued during the turn was not slipped in at any of three tool-call boundaries, and arrived as a new user turn after the turn ended.

Not yet tested:

- The CLI
- Whether several messages queued in one turn arrive one by one or merged into one

## Installation

This plugin is distributed through the [`fomalhaut647-plugins`](../..) marketplace:

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install later@fomalhaut647-plugins
```

In the desktop app, sync this marketplace under Settings → Plugins, then enable later.

## Directory layout

```
plugins/later/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── later/
│       └── SKILL.md      # body is just $ARGUMENTS
├── CLAUDE.md
├── README.md             # Chinese
├── README.en.md          # this file
└── RELEASE-NOTES.md
```

## License

MIT — see [LICENSE at the marketplace root](../../LICENSE).
