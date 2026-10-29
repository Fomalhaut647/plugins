# later 版本说明

## v0.1.0

初版，通过 `fomalhaut647-plugins` marketplace 首次发布。

- 新增 skill `later`：只能手动调用（`/later:later <消息>`），把参数原样作为一条用户消息转交。借 Claude 回答期间发出的斜杠命令会等整轮结束才执行，把消息推迟到轮末送达。
