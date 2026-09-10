import logging
from TeamTalk5 import TextMsgType


def _reply(bot, msg_from_id, channel_id, msg_type, text):
    if msg_type == TextMsgType.MSGTYPE_CHANNEL:
        bot._send_channel_message(channel_id, text)
    else:
        bot._send_pm(msg_from_id, text)


def handle_toggle_translator(bot, msg_from_id, **kwargs):
    bot.translator_mode_enabled = not bot.translator_mode_enabled
    bot._play_channel_sound("toggle.wav")
    key = "translator.toggled_on" if bot.translator_mode_enabled else "translator.toggled_off"
    bot._send_pm(msg_from_id, bot.t(key, target_lang=bot.translate_target_language))


def handle_set_translate_lang(bot, msg_from_id, args_str, **kwargs):
    lang = args_str.strip()
    if not lang:
        bot._send_pm(msg_from_id, bot.t("translator.usage_lang"))
        return
    bot.translate_target_language = lang
    bot._send_pm(msg_from_id, bot.t("translator.lang_set", target_lang=lang))


def handle_translate_message(bot, msg_from_id, channel_id, msg_type, text, **kwargs):
    """Called from the free-chat fallback in command_handler when translator
    mode is on, instead of the normal AI chat reply."""
    if not bot.groq_service.is_enabled():
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("translator.unavailable"))
        return
    target = bot.translate_target_language or "English"
    prompt = (
        f"Translate the following message to {target}. "
        f"Detect the source language automatically. "
        f"Reply with ONLY the translation, no explanations, no quotes:\n\n{text}"
    )
    translation = bot.groq_service.generate_simple_content(prompt)
    _reply(bot, msg_from_id, channel_id, msg_type, translation)
