# pyright-lsp

> [中文版](README.md)

Gives Claude Code an understanding of Python code through the Pyright language server: type errors and other diagnostics arrive automatically after each edit, plus go-to-definition and find-references.

## Source

Copied from `pyright-lsp` in Anthropic's official marketplace [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (plugin version 1.0.0, upstream commit `58267944`) so it can be installed from this marketplace in the Claude desktop app. The only change is that the language server config moved from the upstream marketplace entry into `.lsp.json` in this directory, unchanged. The plugin version follows upstream, with a patch bump for local-only changes.

## Prerequisite: install Pyright

The plugin only tells Claude Code how to start the language server; you need the `pyright-langserver` command installed and on your PATH:

```bash
brew install pyright
```

`npm install -g pyright` or `pipx install pyright` also work.

## Installation

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install pyright-lsp@fomalhaut647-plugins
```

## Supported files

`.py`, `.pyi`

## License

Apache-2.0, upstream author Anthropic — see [LICENSE](LICENSE) in this directory.
