# typescript-lsp

> [中文版](README.md)

Gives Claude Code an understanding of TypeScript and JavaScript code through typescript-language-server: type errors and other diagnostics arrive automatically after each edit, plus go-to-definition and find-references.

## Source

Copied from `typescript-lsp` in Anthropic's official marketplace [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (plugin version 1.0.0, upstream commit `58267944`) so it can be installed from this marketplace in the Claude desktop app. The only change is that the language server config moved from the upstream marketplace entry into `.lsp.json` in this directory, unchanged. The plugin version follows upstream, with a patch bump for local-only changes.

## Prerequisite: install the language server

The plugin only tells Claude Code how to start the language server; you need the `typescript-language-server` command installed and on your PATH:

```bash
brew install typescript-language-server
```

Homebrew also installs the TypeScript it depends on. `npm install -g typescript-language-server typescript` also works.

## Installation

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install typescript-lsp@fomalhaut647-plugins
```

## Supported files

`.ts`, `.tsx`, `.js`, `.jsx`, `.mts`, `.cts`, `.mjs`, `.cjs`

## License

Apache-2.0, upstream author Anthropic — see [LICENSE](LICENSE) in this directory.
