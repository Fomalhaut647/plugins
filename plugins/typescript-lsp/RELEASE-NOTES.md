# typescript-lsp 版本说明

## v2.0.0

- 语言服务器换成 TypeScript 7 自带的 `tsc --lsp --stdio`，不再用 typescript-language-server。TypeScript 7 不再带 tsserver，Homebrew 把 TypeScript 升到 7 之后，原配置启动时报「找不到可用的 TypeScript」。
- 破坏性变更：需要 TypeScript 7 或更新版本的 `tsc` 在 PATH 里。只装了 typescript-language-server 和旧版 TypeScript 的环境，要改装 TypeScript 7（`brew install typescript`）。
- 版本号从这一版起自行维护，不再跟随上游。

## v1.0.0

从 [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) 搬入（上游提交 `58267944`），通过 `fomalhaut647-plugins` marketplace 首次发布。语言服务器配置从上游的 marketplace 条目挪到 `.lsp.json`，内容不变。版本号跟随上游。
