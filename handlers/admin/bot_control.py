
import logging
try:
    import wx
except ImportError:
    wx = None

def handle_lock(bot, msg_from_id, **kwargs):
    bot.toggle_bot_lock()
    new_state = bot.t("bot_control.on") if bot.bot_locked else bot.t("bot_control.off")
    bot._send_pm(msg_from_id, bot.t("bot_control.lock_state", state=new_state))
    if bot.main_window: bot.main_window.update_feature_list()

def handle_block_command(bot, msg_from_id, args_str, **kwargs):
    cmd_to_toggle = args_str.strip().lower()
    if not cmd_to_toggle:
        blocked = ', '.join(sorted(list(bot.blocked_commands))) or bot.t("poll.none")
        bot._send_pm(msg_from_id, bot.t("bot_control.usage_block", list=blocked)); return

    if cmd_to_toggle in bot.UNBLOCKABLE_COMMANDS:
        bot._send_pm(msg_from_id, bot.t("bot_control.cannot_block", command=cmd_to_toggle)); return

    if cmd_to_toggle in bot.blocked_commands:
        bot.blocked_commands.remove(cmd_to_toggle)
        feedback = bot.t("bot_control.unblocked", command=cmd_to_toggle)
    else:
        bot.blocked_commands.add(cmd_to_toggle)
        feedback = bot.t("bot_control.blocked", command=cmd_to_toggle)
    
    bot._send_pm(msg_from_id, feedback)

def handle_restart(bot, msg_from_id, **kwargs):
    bot._send_pm(msg_from_id, bot.t("bot_control.restarting"))
    bot._mark_stopped_intentionally()
    if bot.main_window and wx:
        wx.CallAfter(bot._initiate_restart)
    else:
        bot._initiate_restart()

def handle_quit(bot, msg_from_id, **kwargs):
    bot._send_pm(msg_from_id, bot.t("bot_control.quitting"))
    bot._mark_stopped_intentionally()
    if bot.main_window and wx:
        wx.CallAfter(bot.stop)
    else:
        bot.controller.request_shutdown() # Request application shutdown
