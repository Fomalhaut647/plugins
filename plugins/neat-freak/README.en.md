# neat-freak

> [中文版](README.md)

End-of-session knowledge cleanup: reconciles project docs, rule files (CLAUDE.md / AGENTS.md), agent memory, and workspace residue with what the code actually does, and audits whether project rules are really followed.

## Source

Copied from `neat-freak` in [数字生命卡兹克](https://github.com/KKKKhazix)'s [khazix-skills](https://github.com/KKKKhazix/khazix-skills) repository (skill version 3.0.0, upstream commit `322346d`) and packaged as a plugin so it can be installed from this marketplace. The only local change is `disable-model-invocation: true`. The upstream evals suite is not included. The plugin version follows the upstream skill version, with a patch bump for local-only changes.

## Installation

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install neat-freak@fomalhaut647-plugins
```

## Usage

Runs only when you type `/neat-freak:neat-freak`; phrases like "tidy up docs" do not trigger it, and the model never invokes it on its own. See [`skills/neat-freak/SKILL.md`](skills/neat-freak/SKILL.md) for the full text.

## License

MIT, copyright held by the original author 数字生命卡兹克 — see [LICENSE](LICENSE) in this directory.
