# typescript-lsp

> [中文版](README.md)

Gives Claude Code an understanding of TypeScript and JavaScript code through TypeScript 7's built-in language server (`tsc --lsp`): type errors and other diagnostics arrive automatically after each edit, plus go-to-definition and find-references.

## Source

Adapted from `typescript-lsp` in Anthropic's official marketplace [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (plugin version 1.0.0, upstream commit `58267944`) so it can be installed from this marketplace in the Claude desktop app. Differences from upstream:

- The language server is TypeScript 7's built-in `tsc --lsp --stdio` instead of typescript-language-server. TypeScript 7, rewritten in Go, no longer ships the tsserver that typescript-language-server depends on, so the upstream config fails to start once Homebrew's TypeScript is at 7.
- A relay ([`scripts/diagnostics_relay.py`](scripts/diagnostics_relay.py)) sits in between. TypeScript 7's language server only returns errors when asked, while Claude Code only takes errors pushed to it, so without the relay no type errors show up after an edit. After each file open, change, or save, the relay asks for the errors on Claude Code's behalf and pushes them; every other message passes through unchanged. When one file changes, the other open files are re-checked too and pushed only if their errors changed.
- The language server config moved from the upstream marketplace entry into `.lsp.json` in this directory.

From v2.0.0 on, the version is maintained here and no longer follows upstream.

## Prerequisite: install TypeScript 7

The plugin only tells Claude Code how to start the language server; you need the `tsc` command from TypeScript 7 or later installed and on your PATH:

```bash
brew install typescript
```

`npm install -g typescript` also works. `tsc` from TypeScript 6 or earlier has no `--lsp` mode and won't work.

The relay runs on `python3` and uses only the standard library. macOS has it once the Command Line Tools are installed; `brew install python` also works.

## Installation

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install typescript-lsp@fomalhaut647-plugins
```

## Supported files

`.ts`, `.tsx`, `.js`, `.jsx`, `.mts`, `.cts`, `.mjs`, `.cjs`

## License

Apache-2.0, upstream author Anthropic — see [LICENSE](LICENSE) in this directory.
