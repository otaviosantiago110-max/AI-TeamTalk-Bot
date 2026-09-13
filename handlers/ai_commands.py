
import logging
import re


def sanitize_ai_response(text):
    """Keep normal AI prose screen-reader friendly while preserving code blocks.

    Normal prose keeps letters, numbers, spaces, and sentence punctuation.
    Mathematical expressions may keep +, - and = when the line looks like a
    calculation. Fenced code blocks are preserved exactly.
    """
    if not text:
        return text

    parts = re.split(r"(```(?:\n|.)*?```)", text, flags=re.DOTALL)
    for i in range(0, len(parts), 2):
        chunk = parts[i]
        lines = []
        for line in chunk.splitlines():
            stripped = line.strip()
            is_math = bool(
                re.search(r"\d\s*[+\-]\s*\d", stripped)
                or re.search(r"\d\s*=\s*[-+]?\d", stripped)
                or re.search(r"[-+]?\d+(?:[.,]\d+)?\s*=\s*[-+]?\d", stripped)
            )
            if is_math:
                cleaned = re.sub(r"[^\w\s.,!?+\-=]", "", line, flags=re.UNICODE)
            else:
                cleaned = re.sub(r"[^\w\s.,!?]", "", line, flags=re.UNICODE)
            lines.append(cleaned)
        parts[i] = "\n".join(lines)
    return "".join(parts).strip()

from TeamTalk5 import TextMsgType

def handle_pm_ai(bot, msg_from_id, args_str, **kwargs):
    logging.debug(f"handle_pm_ai called for user_id: {msg_from_id}, prompt: '{args_str}'")
    if not bot.allow_groq_pm:
        logging.debug(f"Groq PM disabled for user_id: {msg_from_id}")
        bot._send_pm(msg_from_id, bot.t("ai.disabled_pm")); return
    if not bot.groq_service.is_enabled():
        logging.debug(f"Groq service not enabled for user_id: {msg_from_id}")
        bot._send_pm(msg_from_id, bot.t("ai.not_available")); return

    prompt = args_str.strip()
    if not prompt:
        logging.debug(f"Empty prompt from user_id: {msg_from_id}")
        return

    history = bot.context_history_manager.get_history(str(msg_from_id))
    logging.debug(f"Retrieved history for user_id {msg_from_id}: {history}")
    reply = bot.groq_service.generate_content(prompt, history=history)
    reply = sanitize_ai_response(reply)
    logging.debug(f"Groq reply for user_id {msg_from_id}: {reply}")
    bot._send_pm(msg_from_id, reply)

def handle_channel_ai(bot, msg_from_id, sender_nick, channel_id, args_str, **kwargs):
    if not bot.allow_groq_channel:
        return
    if not bot.groq_service.is_enabled():
        bot._send_channel_message(channel_id, bot.t("ai.not_available")); return

    prompt = args_str.strip()
    if not prompt:
        return

    # Create a unique context key for the user in this channel
    user_channel_context_key = f"{channel_id}-{msg_from_id}"

    # Add user's prompt to their specific channel context history
    bot.context_history_manager.add_message(user_channel_context_key, prompt, sender_nick, is_bot=False)

    history = bot.context_history_manager.get_history(user_channel_context_key)
    logging.debug(f"Retrieved history for user_channel_context_key {user_channel_context_key}: {history}")
    reply = bot.groq_service.generate_content(prompt, history=history)
    reply = sanitize_ai_response(reply)
    logging.debug(f"Groq reply for user_channel_context_key {user_channel_context_key}: {reply}")
    # Add bot's reply to user's specific channel context history
    bot.context_history_manager.add_message(user_channel_context_key, reply, bot.nickname, is_bot=True)

    # Reply only where the question came from: channel in, channel out.
    bot._send_channel_message(channel_id, reply)


def _get_chat_context_key(msg_from_id, channel_id, msg_type):
    """Resolve which context-history bucket the current message belongs to:
    the PM bucket (keyed by user id) or the per-user channel bucket."""
    if msg_type == TextMsgType.MSGTYPE_CHANNEL:
        return f"{channel_id}-{msg_from_id}", True
    return str(msg_from_id), False


def _reply(bot, msg_from_id, channel_id, is_channel, text):
    # Reply only where the command came from - never both at once.
    if is_channel:
        bot._send_channel_message(channel_id, text)
    else:
        bot._send_pm(msg_from_id, text)


def handle_new_chat(bot, msg_from_id, channel_id=None, msg_type=None, **kwargs):
    """'ch' (PM) / '/ch' (channel): starts a fresh conversation, discarding
    whatever context the AI had built up so far."""
    context_key, is_channel = _get_chat_context_key(msg_from_id, channel_id, msg_type)
    bot.context_history_manager.clear_history(context_key)
    logging.debug(f"New chat started for context key: {context_key}")
    _reply(bot, msg_from_id, channel_id, is_channel, bot.t("chat.new_started"))


def handle_clear_chat(bot, msg_from_id, channel_id=None, msg_type=None, **kwargs):
    """'cl' (PM) / '/cl' (channel): clears the stored conversation history."""
    context_key, is_channel = _get_chat_context_key(msg_from_id, channel_id, msg_type)
    bot.context_history_manager.clear_history(context_key)
    logging.debug(f"Chat history cleared for context key: {context_key}")
    _reply(bot, msg_from_id, channel_id, is_channel, bot.t("chat.cleared"))


def handle_end_chat(bot, msg_from_id, channel_id=None, msg_type=None, **kwargs):
    """'n' (PM) / '/n' (channel): ends the current conversation."""
    context_key, is_channel = _get_chat_context_key(msg_from_id, channel_id, msg_type)
    bot.context_history_manager.clear_history(context_key)
    logging.debug(f"Chat ended for context key: {context_key}")
    _reply(bot, msg_from_id, channel_id, is_channel, bot.t("chat.ended"))
