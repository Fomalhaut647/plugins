# model-trio

> [中文版](README.md)

A Claude Code plugin that puts Claude in the middle: it hands the right jobs to two other models on this machine and checks their work before reporting to you.

- **Codex (GPT)** is rigorous: it writes self-contained backend, algorithm, and data-processing modules, reviews code, and does read-only research.
- **Antigravity (Gemini)** has ideas and writes good copy, but is careless: it drafts an independent plan, or suggests changes to UI copy and interaction. It is read-only and only gives advice.

The division of labor follows the workflow in [this article by 数字生命卡兹克](https://mp.weixin.qq.com/s/gwj0xLNHPfToQnQJN7IkMA) (in Chinese). One difference: the article puts the dispatch rules in CLAUDE.md so that Claude dispatches on its own; here each skill activates only when your message explicitly mentions Codex or Antigravity.

## Requirements

- The Codex CLI (`codex`) and the [Antigravity CLI](https://antigravity.google/docs/getting-started) (`agy`), installed and logged in on this machine. If you only use one of them, the other is not needed.
- python3 (3.9 or later, no extra packages).
- A directory handed to Codex must be inside a git working copy.

## Installation

This plugin is distributed through the [`fomalhaut647-plugins`](../..) marketplace:

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install model-trio@fomalhaut647-plugins
```

In the desktop app, sync this marketplace under Settings → Plugins, then enable model-trio.

## Usage

Say something that mentions "Codex", "Antigravity", "Gemini", or "agy", or invoke `/model-trio:codex` or `/model-trio:antigravity` by hand.

### Codex

- "Have Codex write this import module": Claude fixes the interface and the acceptance criteria and writes them into a brief. When Codex is done, Claude reads the changes and runs the tests itself, and the job only counts as done once they pass. When you do not say which part to hand over, Claude only hands over self-contained modules whose interface is settled and that do not touch the UI; small changes, front-end work, and visuals stay with Claude.
- "Have Codex review the changes just made": Codex reviews with its own built-in review flow, and Claude checks each finding against the code and drops the ones that do not hold. The ones that hold fall into two levels: a finding that would lose data, miscalculate money, bypass permissions, send a wrong message, or break a release, and that comes with a concrete way it happens, must be fixed; everything else is listed for you as a suggestion. There is one review round.
- "Have Codex find the cause of this bug": read-only research.

### Antigravity

- "Have Gemini draft a plan for this too": Claude drafts its own plan and gives Gemini only your original words and the necessary background, never its own draft or leaning. Claude then merges the two into one plan for you, stating where they agree, what it took from Gemini, and what it rejected and why; where both sides have a point and it cannot decide, it puts the choice to you as is.
- "Have Gemini rework the copy on this page": Claude writes a first version, tells Gemini who the page is for and what it should get people to do, and asks for changes. Claude checks each change against how the feature really works before adopting it.

The model and reasoning effort default to each CLI's own settings; name one in the conversation and Claude passes it on. When a call runs past two minutes, Claude Code moves it to the background automatically, so Claude can do other work and is notified when it finishes.

## What they can touch

- **Codex**: whatever your Codex settings allow, this plugin keeps it in a sandbox. Research and review are read-only; when coding it can only write the directory it was given. No network, no commits, no pushes: installing dependencies, tests that need the network, and committing are done by Claude.
- **Antigravity**: it cannot change any file. It runs in an empty directory with the project directory granted read-only, so it can read files and run read-only commands.

## What has been tested

2026-11-26, Claude Code 2.1.325, Antigravity CLI 1.5.17:

- Loaded the plugin in a real Claude Code run: both tools and both skills load, and a tool call reached Antigravity and returned its reply.
- Antigravity is read-only: asked to write a file and to create one with a shell command, both were refused, while reading files and `git log` worked; continuing an earlier conversation worked.
- Cancelling a call, or closing Claude Code, stops the running child process.

Not tested yet:

- **A real Codex call.** Codex was not logged in on the test machine, so only the command line used to call it was checked against a stand-in program; that command line is the one already verified against the real Codex in `agent-team`.
- What actually happens when a call moves to the background after two minutes, and when it is stopped from `/tasks`.

## Directory layout

```
plugins/model-trio/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json                 # Registers the MCP server
├── server.py                 # The MCP server: the codex and antigravity tools
├── skills/
│   ├── codex/SKILL.md        # What to hand to Codex and how to check what comes back
│   └── antigravity/SKILL.md  # How to ask Antigravity for a plan or for copy changes
├── CLAUDE.md                 # Contributor guide
├── README.md                 # Chinese
├── README.en.md              # this file
└── RELEASE-NOTES.md
```

## License

MIT — see the [LICENSE at the marketplace root](../../LICENSE).
