"""Tool-based reply plugin (entry point)."""

from __future__ import annotations

from astrbot.api import AstrBotConfig, ToolSet, logger
from astrbot.api.event import AstrMessageEvent, MessageChain, filter
from astrbot.api.message_components import At, Plain, Reply
from astrbot.api.platform import MessageType
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star, register

from .src import tools as tool_defs
from .src.constants import (
    DEFAULT_SUPPRESS_POLICY,
    DEFAULT_SYSTEM_PROMPT,
    EXTRA_SENT_COUNT,
    FOLLOW_ASTRBOT,
    POLICY_AFTER_TOOL,
    POLICY_NEVER,
    POLICY_VALUES,
    REPLY_TOOL_NAME,
    SENT_TEXTS_EXTRA,
    TRI_STATE_VALUES,
)

# metadata.yaml overrides the decorator name in the star registry, so lookups
# must use the metadata name. The version is a fallback for the rare case where
# the registry entry is unavailable.
PLUGIN_NAME = "astrbot_plugin_tool_reply"
PLUGIN_VERSION = "1.0.0"


@register(
    PLUGIN_NAME,
    "K_PU",
    "让模型通过调用工具来发送回复内容，而不是直接输出文本",
    PLUGIN_VERSION,
)
class ToolReplyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig | None = None):
        super().__init__(context)
        self.config = config or {}
        self._tool = None

    def _enabled(self) -> bool:
        """Return whether the master switch keeps the plugin active."""
        return bool(self.config.get("disable_streaming", True))

    async def initialize(self) -> None:
        manager = self.context.get_llm_tool_manager()
        manager.remove_func(REPLY_TOOL_NAME)
        self._tool = None
        if not self._enabled():
            logger.info("Tool reply is disabled by the master switch; skipped.")
            return

        tools = tool_defs.build_tools()
        for tool in tools:
            if tool.name == REPLY_TOOL_NAME:
                tool.handler = self.reply_to_user
        self._tool = tools[0]

        self.context.add_llm_tools(*tools)
        logger.info("Registered tool reply tool: %s", REPLY_TOOL_NAME)

    async def terminate(self) -> None:
        self.context.get_llm_tool_manager().remove_func(REPLY_TOOL_NAME)

    def _policy(self) -> str:
        """Return the configured policy for direct model output."""
        policy = self.config.get("suppress_policy", DEFAULT_SUPPRESS_POLICY)
        return policy if policy in POLICY_VALUES else DEFAULT_SUPPRESS_POLICY

    def _system_prompt(self) -> str:
        """Return the prompt fragment injected into every LLM request."""
        custom = str(self.config.get("custom_system_prompt", "") or "").strip()
        if custom:
            return custom
        return DEFAULT_SYSTEM_PROMPT

    def _follow_astrbot(self, event: AstrMessageEvent, key: str) -> bool:
        """Read a platform setting from the AstrBot config for this session."""
        try:
            setting = self.context.get_config(umo=event.unified_msg_origin)
        except Exception:  # noqa: BLE001 - fall back to the plain config section
            setting = None
        section = setting.get("platform_settings", {}) if setting else {}
        return bool(section.get(key, False))

    def _tri_state(self, name: str, event: AstrMessageEvent, fallback: str) -> bool:
        """Resolve a follow/on/off option into a boolean."""
        value = self.config.get(name, FOLLOW_ASTRBOT)
        if value not in TRI_STATE_VALUES:
            value = FOLLOW_ASTRBOT
        if value == "on":
            return True
        if value == "off":
            return False
        return self._follow_astrbot(event, fallback)

    def _build_chain(self, event: AstrMessageEvent, text: str) -> MessageChain:
        """Build the outgoing chain with the configured At / quote decoration."""
        chain: list = [Plain(text)]
        if self._tri_state("reply_with_mention", event, "reply_with_mention") and (
            event.get_message_type() != MessageType.FRIEND_MESSAGE
        ):
            chain.insert(0, At(qq=event.get_sender_id(), name=event.get_sender_name()))
            if isinstance(chain[-1], Plain):
                chain[-1].text = "\n" + chain[-1].text
        if self._tri_state("reply_with_quote", event, "reply_with_quote"):
            chain.insert(0, Reply(id=event.message_obj.message_id))
        return MessageChain(chain=chain)

    async def reply_to_user(
        self, event: AstrMessageEvent, messages: list[str] | str
    ) -> str:
        """Send reply messages to the current chat.

        Args:
            event: Message event of the current request.
            messages: Reply texts, one message bubble per item.

        Returns:
            A short confirmation understood by the model.
        """
        if isinstance(messages, str):
            messages = [messages]
        texts = [
            str(item)
            for item in messages or []
            if isinstance(item, str) and item.strip()
        ]
        if not texts:
            return "No content was sent: the messages list was empty."

        sent = 0
        for text in texts:
            try:
                await event.send(self._build_chain(event, text))
            except Exception as exc:  # noqa: BLE001 - report send failures to the model
                logger.error("Failed to send tool reply: %s", exc)
                return f"Failed to send reply: {exc}"
            sent += 1
            delivered = event.get_extra(SENT_TEXTS_EXTRA, [])
            if isinstance(delivered, list):
                delivered.append(text.strip())
                event.set_extra(SENT_TEXTS_EXTRA, delivered)

        event.set_extra(EXTRA_SENT_COUNT, event.get_extra(EXTRA_SENT_COUNT, 0) + sent)
        if self.config.get("log_tool_call", False):
            logger.info(
                "Tool reply sent %s message(s), length=%s",
                sent,
                sum(len(text) for text in texts),
            )
        return f"Sent {sent} message(s) to the user."

    @filter.on_llm_request()
    async def on_llm_request(self, event: AstrMessageEvent, req: ProviderRequest):
        """Prepare the request so replies can only leave through the tool."""
        if not self._enabled():
            return

        # Streaming deltas are sent as soon as they are generated, so the plugin
        # cannot drop them afterwards. This switch is also the master switch.
        event.set_extra("enable_streaming", False)

        if self.config.get("inject_system_prompt", True):
            fragment = self._system_prompt()
            if fragment:
                base = req.system_prompt or ""
                req.system_prompt = f"{base}\n\n{fragment}".strip()

        if self._tool is not None:
            if req.func_tool is None:
                # The run had no tool set at all; create one so the model can
                # still deliver its reply through the tool.
                req.func_tool = ToolSet(tools=[self._tool])
            elif req.func_tool.get_tool(REPLY_TOOL_NAME) is None:
                req.func_tool.add_tool(self._tool)

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        """Drop the model text that was not delivered through the tool."""
        if not self._enabled():
            return

        policy = self._policy()
        if policy == POLICY_NEVER:
            return
        if policy == POLICY_AFTER_TOOL and not event.get_extra(EXTRA_SENT_COUNT, 0):
            return

        result = event.get_result()
        if result is None or not result.chain:
            return
        if not result.is_llm_result():
            return
        if self.config.get("log_tool_call", False):
            logger.info("Suppressed direct model output: %s", result.get_plain_text())
        event.clear_result()
