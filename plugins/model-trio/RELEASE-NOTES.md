# model-trio 版本说明

## v0.1.0

初版，通过 `fomalhaut647-plugins` marketplace 首次发布。

- 新增一个本地 MCP 服务器，带两个工具：`codex` 把任务交给本机的 Codex 命令行（只读调研、写代码、审查三种模式，都限制在沙箱里），`antigravity` 向本机的 Antigravity 命令行提问或请它出方案（只读）。两个工具都等对方做完后返回它的汇报，都能续接上一次会话。
- 新增 skill `model-trio:codex`：什么活交给 Codex、任务书写什么、交回后怎么核实、审查发现怎么分级。只在用户的话里明确提到 Codex 时启用。它取代 `agent-team:codex`（在 agent-team 5.0.0 里删除）。
- 新增 skill `model-trio:antigravity`：请 Gemini 独立出一份方案，或给界面文案和交互提修改意见，结果由 Claude 核实后采纳。只在用户的话里明确提到 Antigravity、agy 或 Gemini 时启用。

为什么：用户的决定。分工照数字生命卡兹克[讲三家模型协同的文章](https://mp.weixin.qq.com/s/gwj0xLNHPfToQnQJN7IkMA)：Claude 站在中间，Codex 做严谨的硬活，Gemini 当军师。
