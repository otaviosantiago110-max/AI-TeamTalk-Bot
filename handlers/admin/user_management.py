
from TeamTalk5 import ttstr, UserRight, BanType, BannedUser

def handle_list_users(bot, msg_from_id, args_str, **kwargs):
    path_str = args_str.strip() or ttstr(bot.target_channel_path)
    chan_id = bot.getChannelIDFromPath(ttstr(path_str)) if path_str else bot._target_channel_id
    if chan_id <= 0: bot._send_pm(msg_from_id, bot.t("user_mgmt.channel_not_found")); return

    users = sorted(list(bot.getChannelUsers(chan_id) or []), key=lambda u: ttstr(u.szNickname).lower())
    user_list = [bot.t("user_mgmt.users_in_channel", path=path_str)]
    user_list.extend(f"- {ttstr(u.szNickname)} (ID:{u.nUserID}, User:{ttstr(u.szUsername)})" for u in users)
    bot._send_pm(msg_from_id, "\n".join(user_list) if users else bot.t("user_mgmt.no_users_found", path=path_str))

def handle_list_channels(bot, msg_from_id, **kwargs):
    channels = sorted(list(bot.getServerChannels() or []), key=lambda c: ttstr(c.szName).lower())
    chan_list = [bot.t("user_mgmt.channels_header")]
    chan_list.extend(f"- {ttstr(c.szName)} (ID:{c.nChannelID}, Path:{ttstr(bot.getChannelPath(c.nChannelID))})" for c in channels)
    bot._send_pm(msg_from_id, "\n".join(chan_list) if channels else bot.t("user_mgmt.no_channels_found"))

def handle_move_user(bot, msg_from_id, args_str, **kwargs):
    if not (bot.my_rights & UserRight.USERRIGHT_MOVE_USERS): bot._send_pm(msg_from_id, bot.t("user_mgmt.cannot_move")); return
    parts = args_str.split(maxsplit=1)
    if len(parts) < 2: bot._send_pm(msg_from_id, bot.t("user_mgmt.usage_move")); return
    
    nick, chan_path = parts
    user = bot._find_user_by_nick(nick)
    if not user: bot._send_pm(msg_from_id, bot.t("user_mgmt.user_not_found", nick=nick)); return
    chan_id = bot.getChannelIDFromPath(ttstr(chan_path))
    if chan_id <= 0: bot._send_pm(msg_from_id, bot.t("channel.not_found", path=chan_path)); return

    bot.doMoveUser(user.nUserID, chan_id)
    bot._send_pm(msg_from_id, bot.t("user_mgmt.move_sent", nick=nick))

def handle_kick_user(bot, msg_from_id, args_str, **kwargs):
    if not (bot.my_rights & UserRight.USERRIGHT_KICK_USERS): bot._send_pm(msg_from_id, bot.t("user_mgmt.cannot_kick")); return
    if not bot._in_channel: bot._send_pm(msg_from_id, bot.t("user_mgmt.not_in_channel_kick")); return
    
    nick = args_str.strip()
    user = next((u for u in bot.getChannelUsers(bot._target_channel_id) or [] if ttstr(u.szNickname).lower() == nick.lower()), None)
    if not user: bot._send_pm(msg_from_id, bot.t("user_mgmt.user_not_in_channel", nick=nick)); return

    bot.doKickUser(user.nUserID, bot._target_channel_id)
    bot._send_pm(msg_from_id, bot.t("user_mgmt.kick_sent", nick=nick))

def handle_ban_user(bot, msg_from_id, args_str, **kwargs):
    if not (bot.my_rights & UserRight.USERRIGHT_BAN_USERS): bot._send_pm(msg_from_id, bot.t("user_mgmt.cannot_ban")); return
    
    nick = args_str.strip()
    user = bot._find_user_by_nick(nick)
    if not user: bot._send_pm(msg_from_id, bot.t("user_mgmt.user_not_found", nick=nick)); return

    bot.doBanUserEx(user.nUserID, BanType.BANTYPE_USERNAME)
    bot._send_pm(msg_from_id, bot.t("user_mgmt.ban_sent", username=ttstr(user.szUsername)))

def handle_unban_user(bot, msg_from_id, args_str, **kwargs):
    if not (bot.my_rights & UserRight.USERRIGHT_BAN_USERS): bot._send_pm(msg_from_id, bot.t("user_mgmt.cannot_unban")); return
    
    username = args_str.strip()
    if not username: bot._send_pm(msg_from_id, bot.t("user_mgmt.usage_unban")); return
    
    ban_entry = BannedUser(); ban_entry.szUsername = ttstr(username); ban_entry.uBanTypes = BanType.BANTYPE_USERNAME
    bot.doUnBanUserEx(ban_entry)
    bot._send_pm(msg_from_id, bot.t("user_mgmt.unban_sent", username=username))

def handle_list_admins(bot, msg_from_id, **kwargs):
    configured_admins = set(bot.admin_usernames_config)
    online_users = bot.getServerUsers() or []
    online_usernames = {ttstr(u.szUsername).lower() for u in online_users}
    online_nicknames = {ttstr(u.szNickname).lower(): ttstr(u.szUsername).lower() for u in online_users}

    admin_status_messages = [bot.t("user_mgmt.admin_status_header")]

    # Check configured admins
    for admin_username in sorted(list(configured_admins)):
        status = bot.t("user_mgmt.offline")
        if admin_username in online_usernames:
            status = bot.t("user_mgmt.online")
        admin_status_messages.append(bot.t("user_mgmt.admin_configured", username=admin_username, status=status))
    
    # Check if any online user is an admin by nickname but not by username (less reliable)
    for online_nick, online_user in online_nicknames.items():
        if online_user not in configured_admins and online_nick in configured_admins:
             admin_status_messages.append(bot.t("user_mgmt.admin_online_by_nick", nick=online_nick))

    if not configured_admins:
        admin_status_messages.append(bot.t("user_mgmt.no_admins_configured"))

    bot._send_pm(msg_from_id, "\n".join(admin_status_messages))
