
import logging
from TeamTalk5 import ttstr
import TeamTalk5
from datetime import datetime

def handle_channel_text(bot, msg_from_id, sender_nick, args_str, **kwargs):
    if not bot._in_channel:
        bot._send_pm(msg_from_id, bot.t("common.not_in_channel")); return
    if not args_str:
        bot._send_pm(msg_from_id, bot.t("common.usage_ct")); return

    if bot._send_channel_message(bot._target_channel_id, f"<{sender_nick}> {args_str}"):
        bot._send_pm(msg_from_id, bot.t("common.channel_message_sent"))
    else:
        bot._send_pm(msg_from_id, bot.t("common.channel_message_failed"))

def handle_broadcast_message(bot, msg_from_id, args_str, **kwargs):
    if not args_str:
        bot._send_pm(msg_from_id, bot.t("common.usage_bm")); return
    if bot._send_broadcast(ttstr(args_str)):
        bot._send_pm(msg_from_id, bot.t("common.broadcast_sent"))
    else:
        bot._send_pm(msg_from_id, bot.t("common.broadcast_failed"))

def handle_channel_text(bot, msg_from_id, sender_nick, args_str, **kwargs):
    if not bot._in_channel:
        bot._send_pm(msg_from_id, bot.t("common.not_in_channel")); return
    if not args_str:
        bot._send_pm(msg_from_id, bot.t("common.usage_ct")); return

    if bot._send_channel_message(bot._target_channel_id, f"<{sender_nick}> {args_str}"):
        bot._send_pm(msg_from_id, bot.t("common.channel_message_sent"))
    else:
        bot._send_pm(msg_from_id, bot.t("common.channel_message_failed"))

def handle_broadcast_message(bot, msg_from_id, args_str, **kwargs):
    if not args_str:
        bot._send_pm(msg_from_id, bot.t("common.usage_bm")); return
    if bot._send_broadcast(ttstr(args_str)):
        bot._send_pm(msg_from_id, bot.t("common.broadcast_sent"))
    else:
        bot._send_pm(msg_from_id, bot.t("common.broadcast_failed"))

