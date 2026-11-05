"""LLM tool definitions for delivering replies through a tool call."""

from __future__ import annotations

from astrbot.api import FunctionTool

from .constants import REPLY_TOOL_NAME


class ReplyToUserFunctionTool(FunctionTool):
    """Dedicated tool subclass so the handler is bound to this plugin."""


def build_tools() -> list[FunctionTool]:
    """Build the reply delivery tool.

    Returns:
        A list holding the single reply tool instance.
    """
    return [
        ReplyToUserFunctionTool(
            name=REPLY_TOOL_NAME,
            description=(
                "Send reply text to the user. Every user-visible answer must go "
                "through this tool; text output directly is discarded. One item per "
                "message bubble."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "description": "Reply texts to send, in order.",
                        "items": {"type": "string"},
                        "minItems": 1,
                    }
                },
                "required": ["messages"],
            },
        )
    ]
