import time
import sys
from TeamTalk5 import UserRight, TT_STRLEN, ttstr, LOADED_TT_LIB
from utils import format_uptime
from version import VERSION

from . import ai_commands, poll_commands, communication_commands, youtube_commands, translator_commands
from .admin import bot_control, config_management, feature_toggles, user_management, channel_management, ai_instructions, scheduler_commands

def handle_help(bot, msg_from_id, **kwargs):
    is_admin = bot._is_admin(msg_from_id)
    help_lines = [bot.t("help.header_user")]

    for key in [
        "help.h", "help.ping", "help.info", "help.ddev", "help.whoami", "help.rights",
        "help.cn", "help.cs", "help.ct", "help.bm",
        "help.c", "help.ch", "help.cl", "help.n", "help.yt", "help.ytstop", "help.ytcontrols",
        "help.c_channel",
        "help.poll", "help.vote", "help.results",
    ]:
        help_lines.append(bot.t(key))

    if is_admin:
        help_lines.append(f"\n{bot.t('help.header_admin')}")
        admin_keys = [
            "help.admin.gapi", "help.admin.list_groq_models",
            "help.admin.set_groq_model", "help.admin.addword", "help.admin.delword",
            "help.admin.set_context_retention", "help.admin.jcl", "help.admin.tg_chanmsg",
            "help.admin.tg_broadcast", "help.admin.tg_groq_pm", "help.admin.tg_groq_chan",
            "help.admin.tgmmode", "help.admin.tfilter", "help.admin.tg_context_history",
            "help.admin.tg_debug_logging", "help.admin.lock", "help.admin.block_unblock",
            "help.admin.listusers", "help.admin.listchannels", "help.admin.move",
            "help.admin.kick", "help.admin.ban", "help.admin.unban", "help.admin.admins",
            "help.admin.instruct", "help.admin.setwelcomeinstruction", "help.admin.jc",
            "help.admin.addtask", "help.admin.deltask", "help.admin.listtasks",
            "help.admin.tg_translator", "help.admin.set_translate_lang", "help.admin.set_language",
        ]
        for key in admin_keys:
            help_lines.append(bot.t(key))
        help_lines.append(bot.t("help.admin.rs"))
        help_lines.append(bot.t("help.admin.q"))
    

    bot._send_pm(msg_from_id, "\n".join(help_lines))


def handle_developer(bot, msg_from_id, **kwargs):
    """Display developer and application information."""
    info_lines = [
        bot.t("developer.header"),
        bot.t("developer.program", name="AI-TeamTalk-Bot"),
        bot.t("developer.version", version=VERSION),
        bot.t("developer.developer", name="Otávio Santiago"),
    ]
    bot._send_pm(msg_from_id, "\n".join(info_lines))

def handle_ping(bot, msg_from_id, **kwargs):
    bot._send_pm(msg_from_id, bot.t("cmd.pong"))

def handle_info(bot, msg_from_id, **kwargs):
    uptime_str = format_uptime(time.time() - bot._start_time if bot._start_time > 0 else -1)

    on, off = bot.t("info.enabled"), bot.t("info.disabled")
    groq_status = on if bot.groq_service.is_enabled() else off
    debug_logging_status = on if bot.config['Bot']['debug_logging_enabled'] else off
    context_history_status = on if bot.config['Bot']['context_history_enabled'] else off
    groq_api_key_status = bot.t("info.set") if bot.config['Bot']['groq_api_key'] else bot.t("info.not_set_short")

    server_name, server_version = "N/A", "N/A"
    try:
        props = bot.getServerProperties()
        if props:
            server_name = ttstr(props.szServerName)
            server_version = ttstr(props.szServerVersion)
    except Exception:
        pass

    onoff = lambda v: on if v else off

    info_lines = [
        bot.t("info.bot_header"),
        bot.t("info.name", name=ttstr(bot.nickname)),
        bot.t("info.uptime", uptime=uptime_str),
        bot.t("info.current_channel", channel=ttstr(bot.getChannelPath(bot.getMyChannelID())) if bot._in_channel else bot.t("info.not_in_channel")),
        bot.t("info.target_channel", channel=ttstr(bot.target_channel_path)),
        bot.t("info.locked", value=bot.t("info.yes") if bot.bot_locked else bot.t("info.no")),
        bot.t("info.system_header"),
        bot.t("info.os", os=sys.platform),
        bot.t("info.python_version", version=sys.version.split(' ')[0]),
        bot.t("info.tt_library", lib=LOADED_TT_LIB),
        bot.t("info.features_header"),
        bot.t("info.groq_ai", status=groq_status, model=bot.groq_service.get_current_model_name(), instructions=bot.ai_system_instructions if bot.ai_system_instructions else bot.t("info.not_set")),
        bot.t("info.announce_jl", value=onoff(bot.announce_join_leave)),
        bot.t("info.allow_chanmsg", value=onoff(bot.allow_channel_messages)),
        bot.t("info.allow_broadcast", value=onoff(bot.allow_broadcast)),
        bot.t("info.allow_groq_pm", value=onoff(bot.allow_groq_pm)),
        bot.t("info.allow_groq_chan", value=onoff(bot.allow_groq_channel)),
        bot.t("info.welcome_mode", mode=bot.welcome_message_mode.upper()),
        bot.t("info.filter_enabled", value=onoff(bot.filter_enabled)),
        bot.t("info.debug_logging", status=debug_logging_status),
        bot.t("info.context_history", status=context_history_status),
        bot.t("info.groq_api_key", status=groq_api_key_status),
        bot.t("info.server_header"),
        bot.t("info.server_name", name=server_name, host=ttstr(bot.host)),
        bot.t("info.server_version", version=server_version),
    ]
    bot._send_pm(msg_from_id, "\n".join(info_lines))

def handle_whoami(bot, msg_from_id, sender_nick, **kwargs):
    try:
        user = bot.getUser(msg_from_id)
        if not user:
            raise ValueError(bot.t("whoami.error"))
        admin_status = bot.t("info.yes") if bot._is_admin(msg_from_id) else bot.t("info.no")
        bot._send_pm(msg_from_id, bot.t("whoami.result", nick=sender_nick, id=user.nUserID, username=ttstr(user.szUsername), admin=admin_status))
    except Exception as e:
        bot._send_pm(msg_from_id, bot.t("whoami.get_error", error=e))

def handle_rights(bot, msg_from_id, **kwargs):
    rights_map = {v: k for k, v in UserRight.__dict__.items() if k.startswith('USERRIGHT_')}
    output = [bot.t("rights.header", rights=f"{bot.my_rights:#010x}")]
    output.extend(f"- {flag_name.replace('USERRIGHT_', '')}" for flag_val, flag_name in rights_map.items() if bot.my_rights & flag_val)
    bot._send_pm(msg_from_id, "\n".join(output))

def handle_change_nick(bot, msg_from_id, args_str, **kwargs):
    if not args_str: bot._send_pm(msg_from_id, bot.t("nick.usage")); return
    new_nick = ttstr(args_str)
    if len(new_nick) > TT_STRLEN: bot._send_pm(msg_from_id, bot.t("nick.too_long")); return
    bot.doChangeNickname(new_nick)
    bot._send_pm(msg_from_id, bot.t("nick.change_requested", nick=new_nick))

def handle_change_status(bot, msg_from_id, args_str, **kwargs):
    new_status = ttstr(args_str)
    if len(new_status) > TT_STRLEN:
        bot._send_pm(msg_from_id, bot.t("status.too_long"))
        return
    bot.doChangeStatus(0, new_status)
    bot._send_pm(msg_from_id, bot.t("status.change_requested"))

COMMAND_MAP_PM = {
    # User Commands
    "h": handle_help,
    "ping": handle_ping,
    "info": handle_info,
    "ddev": handle_developer,
    "whoami": handle_whoami,
    "rights": handle_rights,
    "cn": handle_change_nick,
    "cs": handle_change_status,
    # Communication Commands
    # AI Commands
    "c": ai_commands.handle_pm_ai,
    "ch": ai_commands.handle_new_chat,
    "cl": ai_commands.handle_clear_chat,
    "n": ai_commands.handle_end_chat,
    # YouTube Commands
    "yt": youtube_commands.handle_yt_play,
    "ytstop": youtube_commands.handle_yt_stop,
    "ytpause": youtube_commands.handle_yt_pause,
    "ytresume": youtube_commands.handle_yt_resume,
    "ytforward": youtube_commands.handle_yt_forward,
    "ytback": youtube_commands.handle_yt_backward,
    "ytnext": youtube_commands.handle_yt_next,
    "ytprev": youtube_commands.handle_yt_previous,
    "ytplaylist": youtube_commands.handle_yt_playlist,
    "ytclear": youtube_commands.handle_yt_clear,
    "dl": youtube_commands.handle_yt_download,
    "ytdownload": youtube_commands.handle_yt_download,
    "ytpausar": youtube_commands.handle_yt_pause,
    "ytcontinuar": youtube_commands.handle_yt_resume,
    "ytavancar": youtube_commands.handle_yt_forward,
    "ytretroceder": youtube_commands.handle_yt_backward,
    "ytproxima": youtube_commands.handle_yt_next,
    "ytanterior": youtube_commands.handle_yt_previous,
    "ytbaixar": youtube_commands.handle_yt_download,
    # Poll Commands
    "poll": poll_commands.handle_poll_create,
    "vote": poll_commands.handle_vote,
    "results": poll_commands.handle_results,
    "instruct": ai_instructions.handle_instruct_command,
    "setwelcomeinstruction": config_management.handle_set_welcome_instruction,
}

ADMIN_COMMANDS = {
    # Admin - Bot Control
    "lock": bot_control.handle_lock,
    "block": bot_control.handle_block_command,
    "unblock": bot_control.handle_block_command,
    "rs": bot_control.handle_restart,
    "set_language": config_management.handle_set_language,
    "q": bot_control.handle_quit,
    # Admin - Config Management
    "gapi": config_management.handle_set_gapi,
    "list_groq_models": config_management.handle_list_groq_models,
    "lgm": config_management.handle_list_groq_models,
    "set_groq_model": config_management.handle_set_groq_model,
    "sgm": config_management.handle_set_groq_model,
    "addword": config_management.handle_add_word,
    "delword": config_management.handle_del_word,
    "set_context_retention": config_management.handle_set_context_retention,
    # Admin - Feature Toggles
    "jcl": feature_toggles.handle_toggle_jcl,
    "tg_chanmsg": feature_toggles.handle_toggle_chanmsg,
    "tg_broadcast": feature_toggles.handle_toggle_broadcast,
    "tg_groq_pm": feature_toggles.handle_toggle_groq_pm,
    "tg_groq_chan": feature_toggles.handle_toggle_groq_chan,
    "tgmmode": feature_toggles.handle_toggle_welcome_mode,
    "tfilter": feature_toggles.handle_toggle_filter,
    "tg_context_history": feature_toggles.handle_toggle_context_history,
    "tg_debug_logging": feature_toggles.handle_toggle_debug_logging,
    # Admin - User Management
    "listusers": user_management.handle_list_users,
    "listchannels": user_management.handle_list_channels,
    "move": user_management.handle_move_user,
    "kick": user_management.handle_kick_user,
    "ban": user_management.handle_ban_user,
    "unban": user_management.handle_unban_user,
            "admins": user_management.handle_list_admins,
            "instruct": ai_instructions.handle_instruct_command,
    # Admin - Channel Management
    "jc": channel_management.handle_join_channel,
    "ct": communication_commands.handle_channel_text,
    "bm": communication_commands.handle_broadcast_message,
    # Admin - Task Scheduler
    "addtask": scheduler_commands.handle_add_task,
    "deltask": scheduler_commands.handle_del_task,
    "listtasks": scheduler_commands.handle_list_tasks,
    # Admin - Translator
    "tg_translator": translator_commands.handle_toggle_translator,
    "set_translate_lang": translator_commands.handle_set_translate_lang,
}

# Combine all commands for easy lookup in command_handler
ALL_COMMANDS = {**COMMAND_MAP_PM, **ADMIN_COMMANDS}

# Commands that can be executed in channel by prefixing with '/'
CHANNEL_COMMANDS = {
    "c": ai_commands.handle_channel_ai,
    "ch": ai_commands.handle_new_chat,
    "cl": ai_commands.handle_clear_chat,
    "n": ai_commands.handle_end_chat,
}

def get_command_handler(command):
    return ALL_COMMANDS.get(command)

def is_channel_command(command):
    return command in CHANNEL_COMMANDS

def get_channel_command_handler(command):
    return CHANNEL_COMMANDS.get(command)

def is_admin_command(command):
    return command in ADMIN_COMMANDS

def get_admin_command_handler(command):
    return ADMIN_COMMANDS.get(command)

def get_all_commands():
    return ALL_COMMANDS.keys()

def get_pm_commands():
    return COMMAND_MAP_PM.keys()

def get_channel_commands():
    return CHANNEL_COMMANDS.keys()

def get_admin_commands():
    return ADMIN_COMMANDS.keys()

def get_command_description(command):
    # This is a placeholder. In a real app, you'd have descriptions for each command.
    return f"Description for {command}"

def get_command_usage(command):
    # This is a placeholder. In a real app, you'd have usage for each command.
    return f"Usage for {command}"
