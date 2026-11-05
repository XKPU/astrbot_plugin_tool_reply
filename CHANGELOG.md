# Changelog

## [v1.0.0] - 2026-11-05

### 新增

- 注册 `reply_to_user` 工具，模型通过该工具提交回复文本，每个列表项为一条独立消息。
- `on_llm_request` 钩子：追加工具化回复提示词、关闭流式输出、补齐被过滤掉的工具。
- `on_decorating_result` 钩子：按策略清除模型直接输出的文本，避免与工具发送的内容重复。
- 声明式配置：「处理策略」「提示词注入与自定义」「流式开关」「调用日志开关」「回复时 @ 发送人」「回复时引用发送人消息」。

[v1.0.0]: https://github.com/XKPU/astrbot_plugin_tool_reply/compare/4c73cdeef896ae1eba77229f59a6054b0b3cba36...v1.0.0