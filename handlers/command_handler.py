import logging
import re
from TeamTalk5 import TextMsgType, ttstr, UserRight

from . import user_commands, ai_commands, poll_commands, communication_commands, youtube_commands, translator_commands
from .admin import bot_control, config_management, feature_toggles, user_management, channel_management, ai_instructions

COMMAND_MAP_PM = user_commands.COMMAND_MAP_PM
ADMIN_COMMANDS = user_commands.ADMIN_COMMANDS

COMMAND_MAP_CHANNEL = {
    "h": user_commands.handle_help,
    "ddev": user_commands.handle_developer,
    "c": ai_commands.handle_channel_ai,
    "ch": ai_commands.handle_new_chat,
    "cl": ai_commands.handle_clear_chat,
    "n": ai_commands.handle_end_chat,
    "yt": youtube_commands.handle_yt_play,
    "ytstop": youtube_commands.handle_yt_stop,
    "poll": poll_commands.handle_poll_create,
    "vote": poll_commands.handle_vote,
    "results": poll_commands.handle_results,
    "instruct": ai_instructions.handle_instruct_command,
}

# Commands belonging to OTHER bots sharing the channel (e.g. the music bot).
# When one of these is used, this bot must stay completely silent instead of
# replying "Unknown command" or treating it as AI chat.
EXTERNAL_BOT_COMMANDS = {
    "p", "pause", "resume", "stop", "next", "prev", "sf", "sb", "seek",
    "l", "v", "mute", "unmute", "r", "join", "leave", "playlist",
    "sunucu", "status", "adminhelp",
}

def _is_from_other_bot(bot, sender_nick):
    """True if the sender is very likely another bot (not this one, not a
    human) — e.g. a nickname ending in 'bot', like a music/management bot."""
    nick = (sender_nick or "").strip().lower()
    if not nick:
        return False
    own_nick = (bot.nickname or "").strip().lower()
    if nick == own_nick:
        return False
    return nick.endswith("bot")

def handle_message(bot, textmessage, full_message_text):
    msg_from_id = textmessage.nFromUserID
    msg_type = textmessage.nMsgType
    msg_channel_id = textmessage.nChannelID
    
    sender_nick = f"UserID_{msg_from_id}"
    try:
        sender_user = bot.getUser(msg_from_id)
        if sender_user and sender_user.nUserID == msg_from_id:
            sender_nick = ttstr(sender_user.szNickname)
    except Exception: pass

    log_and_process(bot, msg_type, msg_from_id, msg_channel_id, sender_nick, full_message_text)

def log_and_process(bot, msg_type, msg_from_id, msg_channel_id, sender_nick, full_message_text):
    process_commands = False
    
    if msg_type == TextMsgType.MSGTYPE_CHANNEL:
        if bot._in_channel: # Process if bot is in *any* channel
            process_commands = True
    elif msg_type == TextMsgType.MSGTYPE_USER:
        process_commands = True
    else: return

    if not process_commands: return
    
    if msg_type == TextMsgType.MSGTYPE_CHANNEL and check_word_filter(bot, msg_from_id, msg_channel_id, sender_nick, full_message_text):
        return

    is_channel = msg_type == TextMsgType.MSGTYPE_CHANNEL
    stripped_text = full_message_text.strip()
    if not stripped_text: return

    if is_channel and _is_from_other_bot(bot, sender_nick):
        # Status messages from other bots sharing the channel (e.g. a music
        # bot announcing "playing", "stopped", "searching"...) must never be
        # treated as chat or as a command.
        return

    # Sleep gate: while asleep (or having given up on reminders), the bot
    # ignores EVERYTHING — no commands, no chat, no translator, nothing —
    # unless the message mentions its nickname somewhere. A mention wakes
    # it up and the same message is then processed normally below.
    if bot._sleep_state != "awake":
        nickname = (bot.nickname or "").strip().lower()
        if not nickname or nickname not in stripped_text.lower():
            return  # completely ignored, no side effects at all
        bot.register_activity()
    else:
        # Real user activity confirmed — resets the idle/sleep clock.
        bot.register_activity()

    parts = stripped_text.split(maxsplit=1)
    first_word = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    # Figure out whether this message is an actual command, or just plain
    # chat that should be routed straight to the AI.
    command_word, args_str = None, ""
    if is_channel:
        if first_word.startswith('/'):
            candidate = first_word[1:]
            if candidate in COMMAND_MAP_CHANNEL:
                command_word, args_str = candidate, rest
    else:
        if first_word in user_commands.ALL_COMMANDS:
            command_word, args_str = first_word, rest

    if command_word:
        if bot.bot_locked and command_word not in bot.UNBLOCKABLE_COMMANDS:
            msg = bot.t("command.locked")
            if msg_type == TextMsgType.MSGTYPE_USER: bot._send_pm(msg_from_id, msg)
            else: bot._send_channel_message(msg_channel_id, msg)
            return
        if command_word in bot.blocked_commands and command_word not in ['block', 'unblock']:
            msg = bot.t("command.blocked", command=command_word)
            if msg_type == TextMsgType.MSGTYPE_USER: bot._send_pm(msg_from_id, msg)
            else: bot._send_channel_message(msg_channel_id, msg)
            return

        handler_func = user_commands.ALL_COMMANDS.get(command_word) if not is_channel else COMMAND_MAP_CHANNEL.get(command_word)

        if command_word in ADMIN_COMMANDS and not bot._is_admin(msg_from_id):
            bot._send_pm(msg_from_id, bot.t("command.unauthorized", command=command_word))
            logging.warning(f"Unauthorized admin command '{command_word}' by {sender_nick}.")
            return

        _dispatch(bot, handler_func, command_word, msg_from_id, args_str, msg_channel_id, sender_nick, msg_type)
        return

    # No recognized command: if this looks like a command attempt (channel
    # message starting with '/'), figure out whether it belongs to another
    # bot sharing the channel (stay silent) or is genuinely unknown (tell
    # the user).
    if is_channel and first_word.startswith('/'):
        candidate = first_word[1:]
        if candidate in EXTERNAL_BOT_COMMANDS:
            return  # Someone else's bot command (music bot, etc.) — not ours to answer.
        bot._send_channel_message(msg_channel_id, bot.t("command.unknown", command=first_word))
        return

    # Plain channel messages must explicitly mention the bot before they can
    # trigger free-form AI chat. Translator mode is intentionally exempt from
    # the mention gate: when the translator is enabled, ordinary channel
    # messages must continue to be translated without requiring the bot
    # nickname. PM messages remain unaffected.
    if is_channel and not bot.translator_mode_enabled:
        nickname = (bot.nickname or "").strip()
        if not nickname:
            return
        mention_pattern = re.compile(re.escape(nickname), re.IGNORECASE)
        if not mention_pattern.search(stripped_text):
            return
        # Remove the bot nickname from the prompt so the AI receives only
        # the user's actual request.
        stripped_text = mention_pattern.sub("", stripped_text, count=1).strip(" \t:,-;.!?\u2013\u2014")
        if not stripped_text:
            return

    # Otherwise, treat the plain message as free-form AI chat, same as if
    # the user had typed 'c <message>' / '/c <message>'. When translator
    # mode is on, every plain message gets translated instead of chatted with.
    if bot.translator_mode_enabled:
        try:
            translator_commands.handle_translate_message(
                bot=bot, msg_from_id=msg_from_id, channel_id=msg_channel_id,
                msg_type=msg_type, text=stripped_text
            )
        except Exception as e:
            logging.error(f"Error in translator mode: {e}", exc_info=True)
        return

    allow_ai = bot.allow_groq_pm if not is_channel else bot.allow_groq_channel
    if not allow_ai or not bot.groq_service.is_enabled():
        return  # AI chat isn't available/enabled; ignore plain chatter quietly.

    ai_handler = ai_commands.handle_pm_ai if not is_channel else ai_commands.handle_channel_ai
    _dispatch(bot, ai_handler, "c", msg_from_id, stripped_text, msg_channel_id, sender_nick, msg_type)

def _dispatch(bot, handler_func, command_word, msg_from_id, args_str, msg_channel_id, sender_nick, msg_type):
    try:
        handler_func(bot=bot, msg_from_id=msg_from_id, args_str=args_str, channel_id=msg_channel_id, sender_nick=sender_nick, command=command_word, msg_type=msg_type)
    except Exception as e:
        logging.error(f"Error executing command '{command_word}': {e}", exc_info=True)
        error_msg = bot.t("command.unexpected_error", command=command_word, error=e)
        # Reply where the command came from, so channel commands don't
        # silently fail with the error only visible in a PM nobody checks.
        if msg_type == TextMsgType.MSGTYPE_USER:
            bot._send_pm(msg_from_id, error_msg)
        else:
            bot._send_channel_message(msg_channel_id, error_msg)

def check_word_filter(bot, user_id, channel_id, user_nick, message):
    if not bot.filter_enabled or not bot.filtered_words: return False
    
    msg_lower = message.lower()
    found_bad_word = next((word for word in bot.filtered_words if re.search(r'\b' + re.escape(word) + r'\b', msg_lower, re.IGNORECASE)), None)
    
    if found_bad_word:
        bot.warning_counts[user_id] = bot.warning_counts.get(user_id, 0) + 1
        warning_msg = bot.t("filter.warning", count=bot.warning_counts[user_id], nick=user_nick)
        bot._send_channel_message(channel_id, warning_msg)

        if bot.warning_counts[user_id] >= 3:
            if bot.my_rights & UserRight.USERRIGHT_KICK_USERS:
                bot.doKickUser(user_id, channel_id)
                bot._send_channel_message(channel_id, bot.t("filter.kicked", nick=user_nick))
            else:
                bot._send_channel_message(channel_id, bot.t("filter.cannot_kick", nick=user_nick))
            bot.warning_counts[user_id] = 0
        return True
    return False