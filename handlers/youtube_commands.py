import logging
import threading
from TeamTalk5 import TextMsgType


def _reply(bot, msg_from_id, channel_id, msg_type, text):
    if msg_type == TextMsgType.MSGTYPE_CHANNEL:
        bot._send_channel_message(channel_id, text)
    else:
        bot._send_pm(msg_from_id, text)


def handle_yt_play(bot, msg_from_id, args_str, channel_id, sender_nick, msg_type, **kwargs):
    if not bot.youtube_service.is_enabled():
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.disabled"))
        return

    query = args_str.strip()
    if not query:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.usage"))
        return

    _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.searching", query=query))

    # Downloading is slow and must NEVER touch the TeamTalk SDK directly from
    # a background thread (not guaranteed thread-safe). So: download here,
    # then hand the actual "start streaming" call back to the main event
    # loop via bot._pending_main_thread_actions.
    def _worker():
        file_path, title_or_error = bot.youtube_service.search_and_download(query)

        def _on_main_thread(bot):
            if not file_path:
                _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.download_error", error=title_or_error))
                return
            _start_playback(bot, msg_from_id, channel_id, msg_type, file_path, title_or_error)

        bot._pending_main_thread_actions.put(_on_main_thread)

    threading.Thread(target=_worker, daemon=True).start()


def _start_playback(bot, msg_from_id, channel_id, msg_type, file_path, title):
    # Stop and clean up whatever was playing before.
    if bot._current_youtube_path:
        bot.stopStreamingMediaFileToChannel()
        bot.youtube_service.cleanup(bot._current_youtube_path)

    ok = bot._start_youtube_stream(file_path)
    if not ok:
        bot.youtube_service.cleanup(file_path)
        bot._current_youtube_path, bot._current_youtube_title = None, None
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.play_failed"))
        return

    bot._current_youtube_path, bot._current_youtube_title = file_path, title
    _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.now_playing", title=title))


def handle_yt_stop(bot, msg_from_id, channel_id, msg_type, **kwargs):
    bot.stopStreamingMediaFileToChannel()
    if bot._current_youtube_path:
        bot.youtube_service.cleanup(bot._current_youtube_path)
    bot._current_youtube_path, bot._current_youtube_title = None, None
    _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.stopped"))
