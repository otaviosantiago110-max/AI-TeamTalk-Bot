
def handle_toggle_jcl(bot, msg_from_id, **kwargs):
    state = bot.toggle_feature('announce_join_leave', "Join/Leave Announce ON", "Join/Leave Announce OFF")
    bot._send_pm(msg_from_id, bot.t("toggle.jcl", state=bot.t("bot_control.on") if state else bot.t("bot_control.off")))
    if bot.main_window: bot.main_window.update_feature_list()

def handle_toggle_chanmsg(bot, msg_from_id, **kwargs):
    state = bot.toggle_feature('allow_channel_messages', "Allow Channel Msgs ON", "Allow Channel Msgs OFF")
    bot._send_pm(msg_from_id, bot.t("toggle.chanmsg", state=bot.t("bot_control.on") if state else bot.t("bot_control.off")))
    if bot.main_window: bot.main_window.update_feature_list()

def handle_toggle_broadcast(bot, msg_from_id, **kwargs):
    state = bot.toggle_feature('allow_broadcast', "Allow Broadcasts ON", "Allow Broadcasts OFF")
    bot._send_pm(msg_from_id, bot.t("toggle.broadcast", state=bot.t("bot_control.on") if state else bot.t("bot_control.off")))
    if bot.main_window: bot.main_window.update_feature_list()

def handle_toggle_groq_pm(bot, msg_from_id, **kwargs):
    state = bot.toggle_feature('allow_groq_pm', "Allow Groq PM ON", "Allow Groq PM OFF")
    bot._send_pm(msg_from_id, bot.t("toggle.groq_pm", state=bot.t("bot_control.on") if state else bot.t("bot_control.off")))
    if bot.main_window: bot.main_window.update_feature_list()

def handle_toggle_groq_chan(bot, msg_from_id, **kwargs):
    state = bot.toggle_feature('allow_groq_channel', "Allow Groq Channel ON", "Allow Groq Channel OFF")
    bot._send_pm(msg_from_id, bot.t("toggle.groq_chan", state=bot.t("bot_control.on") if state else bot.t("bot_control.off")))
    if bot.main_window: bot.main_window.update_feature_list()

def handle_toggle_welcome_mode(bot, msg_from_id, **kwargs):
    if bot.welcome_message_mode == "template":
        if not bot.groq_service.is_enabled():
            bot._send_pm(msg_from_id, bot.t("welcome_mode.groq_unavailable"))
            return
        bot.welcome_message_mode = "groq"
        feedback = bot.t("welcome_mode.set_groq")
    else:
        bot.welcome_message_mode = "template"
        feedback = bot.t("welcome_mode.set_template")
    bot._send_pm(msg_from_id, feedback)

def handle_toggle_filter(bot, msg_from_id, **kwargs):
    state = bot.toggle_feature('filter_enabled', "Word Filter ON", "Word Filter OFF")
    bot._send_pm(msg_from_id, bot.t("toggle.filter", state=bot.t("bot_control.on") if state else bot.t("bot_control.off")))
    if bot.main_window: bot.main_window.update_feature_list()

def handle_toggle_context_history(bot, msg_from_id, **kwargs):
    state = bot.toggle_feature('context_history_enabled', "Context History ON", "Context History OFF")
    bot._send_pm(msg_from_id, bot.t("toggle.context_history", state=bot.t("bot_control.on") if state else bot.t("bot_control.off")))
    if bot.main_window: bot.main_window.update_feature_list()

def handle_toggle_debug_logging(bot, msg_from_id, **kwargs):
    bot.toggle_debug_logging()
    state = bot.debug_logging_enabled
    bot._send_pm(msg_from_id, bot.t("toggle.debug_logging", state=bot.t("bot_control.on") if state else bot.t("bot_control.off")))
    if bot.main_window: bot.main_window.update_feature_list()
