# aiic

> [中文版](README.md)

A Claude Code plugin with three analysis skills distilled from course material: `deep-thinking` works a question through four passes of thinking, `demand-analysis` analyzes product demand as user × scenario × motivation, and `market-sizing` estimates market size as breadth × intensity × frequency.

## Skills

| Skill | When it activates | What it does |
|---|---|---|
| `aiic:deep-thinking` | You ask for deep thinking or in-depth analysis of a question; you ask why a social or business phenomenon happens and how to solve it; you face a major choice and want to think it through | Runs four passes in order: gut answer → breadth and depth → comparison across places and time → abstraction, to find the key point, solutions, and transferable patterns |
| `aiic:demand-analysis` | Demand research, differentiation, and opportunity assessment | Breaks a product idea into user × scenario × motivation, analyzes demand-side key factors and competitors, supply-side barriers, Why NOW / Why ME, and designs research and MVP validation |
| `aiic:market-sizing` | Market capacity estimates, parameter validation, sensitivity analysis, and auditing a sizing calculation | Estimates or audits market size as annual size = breadth × intensity × frequency, keeps brand and category scopes apart, and ships a calculator script |

`demand-analysis` and `market-sizing` connect: the first defines the demand to measure and its counting boundaries, and the second sizes it. Each also works on its own.

## Usage

Describe the problem directly; the model activates all three skills on demand. For example:

- "Think deeply about this: why is the birth rate falling?"
- "Analyze the demand behind this product idea: AI mock interviews for new graduates."
- "Size the market for AI mock interviews for new graduates in China."

You can also invoke one manually, for example `/aiic:deep-thinking why is the birth rate falling`.

`deep-thinking` also has a practice mode: when you say you want to think step by step yourself, it asks for your answer at each pass first, then points out what is missing and asks follow-up questions, instead of giving the whole analysis at once.

The skill instructions and reference material are written in Chinese; `deep-thinking` answers in the language of your question.

## Calculator script

`market-sizing` ships `scripts/size_market.py`, which uses only the Python standard library (Python 3.10 or later), makes no network calls, and writes no files. It multiplies out the factors of each scenario in the input JSON and checks whether an amount claimed by the source material matches the result computed from its parameters. It checks numbers and structure only; it does not verify that the data is real, that denominators match, or that populations are deduplicated. The input format is described in [`skills/market-sizing/references/calculator.md`](skills/market-sizing/references/calculator.md).

## Source of the content

The three skills are distilled from course material: `deep-thinking` from a course on deep thinking, and `demand-analysis` and `market-sizing` from a demand analysis course held on 2026-09-19. The cases in the skills (the Wanzhou bus plunge, Douyin, Haidilao, an AI interviewer) are classroom demonstrations, and their numbers are teaching assumptions, not verified current data.

## Installation

This plugin is distributed through the [`fomalhaut647-plugins`](../..) marketplace. Install in two steps:

```
/plugin marketplace add Fomalhaut647/plugins
/plugin install aiic@fomalhaut647-plugins
```

For local development, when the marketplace has not been pushed to a remote, replace the GitHub path with the absolute path of the marketplace repository:

```
/plugin marketplace add <absolute path to the marketplace repository>
/plugin install aiic@fomalhaut647-plugins
```
