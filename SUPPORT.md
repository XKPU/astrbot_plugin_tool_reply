# 支持

插件的一般说明见 [README.md](README.md)。

## 目录

- [报告缺陷与建议](#报告缺陷与建议)
- [不在支持范围内](#不在支持范围内)
- [安全](#安全)
- [参与贡献](#参与贡献)
- [许可](#许可)

## 报告缺陷与建议

缺陷报告、功能建议与使用疑问，请提交到 GitHub Issues：

[https://github.com/XKPU/astrbot_plugin_tool_reply/issues](https://github.com/XKPU/astrbot_plugin_tool_reply/issues)

### 一份有用的缺陷报告通常包含

1. **你做了什么** —— 导致问题的操作步骤。
2. **预期结果** 与 **实际结果**。
3. **环境** —— AstrBot 版本、插件版本、Python 版本、操作系统。
4. **AstrBot 日志** —— 请裁剪出错的那一步，最好为 Debug 日志等级下。

> **请勿附带含有个人数据的日志或配置文件。**

## 不在支持范围内

- **非 AstrBot 标准环境。** 本插件基于 AstrBot 的 Provider 与 Session 机制开发，脱离 AstrBot 框架无法运行。

## 安全

发现安全问题请**不要**开公开 issue。可通过以下渠道私下报告：

- GitHub 安全公告：[https://github.com/XKPU/astrbot_plugin_tool_reply/security/advisories/new](https://github.com/XKPU/astrbot_plugin_tool_reply/security/advisories/new)
- 邮箱：`csaxongmail@gmail.com` 或 `u-eptm@u-eptm.top`

更详细的内容见 [SECURITY.md](SECURITY.md)。

## 参与贡献

欢迎提交 Pull Request 或参与 Issue 讨论。

提交前请确保：

- 代码通过 Ruff 格式化。
- 代码功能通过测试。

**未完成或未经测试的提交**同样欢迎，请在提交时说明其状态。

## 许可

本项目基于 **GNU Affero General Public License v3.0 (AGPL-3.0)** 发布。

```
astrbot_plugin_tool_reply - 使模型调用工具返回自己想返回的内容
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