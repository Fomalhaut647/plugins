# aiic —— 贡献者指南

- 三个 skill 提炼自课程课件，方法框架以课件为准。课件里的案例和数字是教学材料，修改 skill 时不要把它们改写成当前事实，也不要删掉「教学假设」「未经核验」这类标注。
- skill 之间互相引用时写带前缀的全名（`aiic:market-sizing`、`aiic:demand-analysis`），模型在 skill 列表里看到的是这个名字。两个 skill 互为可选衔接，不是硬依赖，这一点要保留。
- `${CLAUDE_SKILL_DIR}` 只在 SKILL.md 里会被替换成 skill 的安装目录，`references/` 下的文件不会。所以脚本的完整路径写在 `market-sizing` 的 SKILL.md 里，`references/calculator.md` 用 `<skill 目录>` 占位。
- 改了 `skills/market-sizing/scripts/size_market.py` 或 `skills/market-sizing/references/teaching-cases.json` 后，在仓库根目录运行测试，全部通过才能提交（`-B` 避免在 plugin 目录里留下 `__pycache__`）：

  ```bash
  python3 -B plugins/aiic/skills/market-sizing/scripts/test_size_market.py
  ```

- 计算脚本保持只用 Python 标准库、不联网、不写文件、不自动汇总各情景。
- `demand-analysis` 和 `market-sizing` 的原始压缩包里带有 Codex 用的 `agents/openai.yaml`，Claude Code 不读取，没有搬进来，不要加回。
- 改了内容就升 `plugin.json` 的版本号，写进 `RELEASE-NOTES.md`，README 中英两份一起改。
