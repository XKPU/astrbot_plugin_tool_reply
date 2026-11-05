"""Shared constants of the tool reply plugin."""

REPLY_TOOL_NAME = "reply_to_user"

# Event extra holding how many replies the tool already delivered.
EXTRA_SENT_COUNT = "_tool_reply_sent_count"

# Event extra that the built-in respond stage uses for duplicate detection.
SENT_TEXTS_EXTRA = "_send_message_to_user_current_session_plain_texts"

POLICY_AFTER_TOOL = "suppress_after_tool"
POLICY_ALWAYS = "always_suppress"
POLICY_NEVER = "never_suppress"
POLICY_VALUES = (POLICY_AFTER_TOOL, POLICY_ALWAYS, POLICY_NEVER)

DEFAULT_SYSTEM_PROMPT = (
    "[Reply delivery rule]\n"
    f"Every user-visible reply must be delivered by calling the `{REPLY_TOOL_NAME}` "
    "tool. Text that you output directly without calling the tool is discarded "
    "before it reaches the user.\n"
    "You can split longer answers into multiple calls. After a call succeeds, do "
    "not repeat the same content in your final text."
)

# Direct-output policy default: always drop model text so the model may stay silent.
DEFAULT_SUPPRESS_POLICY = POLICY_ALWAYS

# Tri-state follow options for the At / quote reply settings.
FOLLOW_ASTRBOT = "follow"
TRI_STATE_VALUES = (FOLLOW_ASTRBOT, "on", "off")
