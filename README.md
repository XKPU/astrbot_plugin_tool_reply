# astrbot_plugin_tool_reply

[![GitHub release](https://img.shields.io/github/v/release/XKPU/astrbot_plugin_tool_reply?logo=github)](https://github.com/XKPU/astrbot_plugin_tool_reply)
[![License](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-AstrBot-purple)](https://github.com/AstrBotDevs/AstrBot)
[![Author](https://custom-icon-badges.demolab.com/badge/author-K__PU-orange?logo=k_pu)](https://github.com/XKPU)

让模型不直接输出文本，而是调用 `reply_to_user` 工具把回复内容发送给用户。

## 目录

- [功能](#功能)
- [快速开始](#快速开始)
- [配置项](#配置项)
- [实现说明](#实现说明)
- [已知限制](#已知限制)
- [代码结构](#代码结构)
- [许可证](#许可证)

## 功能

| 功能 | 说明 |
| --- | --- |
| 总开关 | 「插件开关」开启时启用、关闭时完全停用（不注册工具、不注入提示词、不拦截输出） |
| `reply_to_user` 工具 | 模型通过该工具提交回复文本，每个列表项对应一条独立消息 |
| 提示词注入 | 在每次 LLM 请求的 System Prompt 末尾追加规则，要求模型必须通过工具回复 |
| 直接输出拦截 | 在发送前按策略清除模型直接生成的文本，默认「始终丢弃」，模型可不调用工具而不回复 |
| 工具补齐 | 请求前检查 `func_tool` 是否包含 `reply_to_user`，缺失时补入，避免被插件工具过滤剔除 |
| @ / 引用 | 发送回复时可按配置 @ 发送人或引用发送人消息，默认跟随 AstrBot 配置 |

## 快速开始

1. 将本目录放入 AstrBot 的 `data/plugins/` 下并重载插件。
2. 无需额外配置即可使用，模型会在下一轮对话开始通过 `reply_to_user` 输出。
3. 在插件配置页按需调整策略、提示词与日志开关。

## 配置项

| 配置项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `disable_streaming` | 开关 | 开启 | 插件总开关。开启时启用插件并关闭流式输出；关闭时插件完全停用，行为与未安装本插件一致 |
| `suppress_policy` | 选项 | `always_suppress` | 直接输出的处理策略：`always_suppress` 始终丢弃 `LLM_RESULT`（模型不调用工具即可不回复）；`suppress_after_tool` 仅在本轮已通过工具发送后丢弃；`never_suppress` 不处理 |
| `inject_system_prompt` | 开关 | 开启 | 是否追加要求模型使用工具的提示词 |
| `custom_system_prompt` | 文本 | 空 | 留空使用内置提示词，填写后完全替换 |
| `reply_with_mention` | 三态 | 跟随 | 回复时 @ 发送人：跟随 AstrBot 配置 / 开 / 关 |
| `reply_with_quote` | 三态 | 跟随 | 回复时引用发送人消息：跟随 AstrBot 配置 / 开 / 关 |
| `log_tool_call` | 开关 | 关闭 | 记录工具调用与拦截日志，便于排查模型是否绕过工具 |

## 实现说明

1. `initialize()` 先检查总开关：关闭时不注册任何工具并直接返回；开启时通过 `context.add_llm_tools()` 注册 `reply_to_user`，`terminate()` 中移除，重载插件不会残留旧实例。
2. `@filter.on_llm_request` 在请求发出前工作（总开关关闭时直接返回）：
   - 设置 `event.set_extra("enable_streaming", False)`，`internal.py` 会读取该 extra 覆盖全局流式配置。
   - 把提示词追加到 `req.system_prompt`。
   - 若 `req.func_tool` 为空则新建只含 `reply_to_user` 的工具集，缺少该工具时补入，因为 `_plugin_tool_fix` 可能按启用插件列表过滤掉本插件工具。
3. 工具 handler 用 `_build_chain` 组装消息链：先按 `reply_with_mention` / `reply_with_quote`（三态，`follow` 时读 `platform_settings`）插入 `At` / `Reply`，再 `await event.send(...)`；同时维护 `_send_message_to_user_current_session_plain_texts` 供内置回复阶段去重。
4. `@filter.on_decorating_result`（总开关关闭时直接返回）在发送前按策略 `event.clear_result()`。结果被清空后 `respond` 阶段因 `result is None` 直接返回，模型直出的文本不会发出。

## 已知限制

- 无法强制模型必须调用工具：`tool_choice` 不在 `ProviderRequest` 上，插件无法从钩子把它设为 `required`，只能依靠提示词与结果拦截约束。
- 流式模式下模型文本一经生成即下发，无法拦截，因此总开关与「关闭流式输出」合并为同一项：要工作就必须关闭流式。
- 若模型既不调用工具也不产生文本，本轮不会有任何回复。

## 代码结构

```
main.py             插件入口（注册工具、请求钩子、发送前钩子）
_conf_schema.json   声明式配置
metadata.yaml       插件元信息
src/constants.py    工具名、extra 键、策略枚举、内置提示词
src/tools.py        FunctionTool 定义与 JSON Schema
```

## 许可证

本项目基于 **GNU Affero General Public License v3.0 (AGPL-3.0)** 发布。

```
aastrbot_plugin_tool_reply - 使模型调用工具返回自己想返回的内容
Copyright (C) 2025 K_PU

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```