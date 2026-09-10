import threading
from TeamTalk5 import TextMsgType


def _reply(bot, msg_from_id, channel_id, msg_type, text):
    if msg_type == TextMsgType.MSGTYPE_CHANNEL:
        bot._send_channel_message(channel_id, text)
    else:
        bot._send_pm(msg_from_id, text)


def _clear_current(bot, stop=True):
    if stop:
        try:
            bot.stopStreamingMediaFileToChannel()
        except Exception:
            pass
    bot._current_youtube_path = None
    bot._current_youtube_title = None
    bot._youtube_paused = False


def _reset_queue(bot):
    for item in bot._youtube_queue:
        if item.get("path"):
            bot.youtube_service.cleanup(item["path"])
    bot._youtube_queue = []
    bot._youtube_index = -1


def _play_queue_index(bot, index, msg_from_id, channel_id, msg_type):
    if not (0 <= index < len(bot._youtube_queue)):
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.queue_end"))
        return False
    item = bot._youtube_queue[index]
    if not item.get("path"):
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.download_error", error="Arquivo não disponível."))
        return False
    if not bot._play_youtube_queue_index(index):
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.play_failed"))
        return False
    _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.now_playing", title=item["title"]))
    return True


def handle_yt_play(bot, msg_from_id, args_str, channel_id, sender_nick, msg_type, **kwargs):
    if not bot.youtube_service.is_enabled():
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.disabled", error=bot.youtube_service.status_error() or "yt-dlp/ffmpeg"))
        return
    query = args_str.strip()
    if not query:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.usage"))
        return
    _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.searching", query=query))
    def _worker():
        file_path, title_or_error = bot.youtube_service.search_and_download(query)
        def _on_main_thread(bot):
            if not file_path:
                _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.download_error", error=title_or_error))
                return
            _reset_queue(bot)
            bot._youtube_queue = [{"title": title_or_error, "path": file_path, "url": query}]
            _play_queue_index(bot, 0, msg_from_id, channel_id, msg_type)
        bot._pending_main_thread_actions.put(_on_main_thread)
    threading.Thread(target=_worker, daemon=True).start()


def handle_yt_stop(bot, msg_from_id, channel_id, msg_type, **kwargs):
    _clear_current(bot, stop=True)
    _reset_queue(bot)
    _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.stopped"))


def handle_yt_pause(bot, msg_from_id, channel_id, msg_type, **kwargs):
    if not bot._current_youtube_path:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.nothing_playing")); return
    if bot._youtube_paused:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.already_paused")); return
    if bot._update_youtube_playback(paused=True):
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.paused"))
    else:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.control_failed"))


def handle_yt_resume(bot, msg_from_id, channel_id, msg_type, **kwargs):
    if not bot._current_youtube_path:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.nothing_playing")); return
    if not bot._youtube_paused:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.already_playing")); return
    if bot._update_youtube_playback(paused=False):
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.resumed"))
    else:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.control_failed"))


def _seek(bot, seconds, msg_from_id, channel_id, msg_type):
    if not bot._current_youtube_path:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.nothing_playing")); return
    target = max(0, min(int(bot._youtube_duration_ms), int(bot._youtube_elapsed_ms) + int(seconds * 1000)))
    if bot._update_youtube_playback(offset_ms=target):
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.seeked", seconds=abs(int(seconds)), direction="forward" if seconds >= 0 else "backward"))
    else:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.control_failed"))


def handle_yt_forward(bot, msg_from_id, args_str, channel_id, msg_type, **kwargs):
    try: seconds = max(1, int(args_str.strip() or "10"))
    except ValueError: seconds = 10
    _seek(bot, seconds, msg_from_id, channel_id, msg_type)


def handle_yt_backward(bot, msg_from_id, args_str, channel_id, msg_type, **kwargs):
    try: seconds = max(1, int(args_str.strip() or "10"))
    except ValueError: seconds = 10
    _seek(bot, -seconds, msg_from_id, channel_id, msg_type)


def handle_yt_next(bot, msg_from_id, channel_id, msg_type, **kwargs):
    if not bot._youtube_queue:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.queue_empty")); return
    if bot._youtube_index + 1 >= len(bot._youtube_queue):
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.queue_end")); return
    _play_queue_index(bot, bot._youtube_index + 1, msg_from_id, channel_id, msg_type)


def handle_yt_previous(bot, msg_from_id, channel_id, msg_type, **kwargs):
    if not bot._youtube_queue:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.queue_empty")); return
    if bot._youtube_index <= 0:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.queue_start")); return
    _play_queue_index(bot, bot._youtube_index - 1, msg_from_id, channel_id, msg_type)


def handle_yt_playlist(bot, msg_from_id, args_str, channel_id, msg_type, **kwargs):
    query = args_str.strip()
    if not query:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.playlist_usage")); return
    if not bot.youtube_service.is_enabled():
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.disabled", error=bot.youtube_service.status_error() or "yt-dlp/ffmpeg")); return
    _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.playlist_loading"))
    def _worker():
        try:
            items = bot.youtube_service.resolve_playlist(query)
            downloaded = bot.youtube_service.download_playlist_items(items)
            queue_items = [{"title": title, "path": path, "url": items[i]["url"]} for i, (path, title) in enumerate(downloaded)]
            error = None
        except Exception as exc:
            queue_items, error = [], str(exc)
        def _on_main_thread(bot):
            if error:
                _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.download_error", error=error)); return
            _reset_queue(bot)
            bot._youtube_queue = queue_items
            _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.playlist_loaded", count=len(queue_items)))
            _play_queue_index(bot, 0, msg_from_id, channel_id, msg_type)
        bot._pending_main_thread_actions.put(_on_main_thread)
    threading.Thread(target=_worker, daemon=True).start()


def handle_yt_clear(bot, msg_from_id, channel_id, msg_type, **kwargs):
    _clear_current(bot, stop=True)
    _reset_queue(bot)
    _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.queue_cleared"))


def handle_yt_download(bot, msg_from_id, args_str, channel_id, msg_type, **kwargs):
    if not bot._current_youtube_path or not bot._youtube_queue or not (0 <= bot._youtube_index < len(bot._youtube_queue)):
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.nothing_playing"))
        return
    item = bot._youtube_queue[bot._youtube_index]
    query = (item.get("url") or "").strip()
    title = item.get("title") or bot._current_youtube_title or "Desconhecido"
    if not query:
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.download_error", error="URL do vídeo atual não disponível."))
        return
    if not bot.youtube_service.is_enabled():
        _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.disabled", error=bot.youtube_service.status_error() or "yt-dlp/ffmpeg"))
        return
    _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.downloading", query=title))
    def _worker():
        path, result = bot.youtube_service.search_and_download(query)
        def _on_main_thread(bot):
            if not path:
                _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.download_error", error=result))
                return
            channel = channel_id if msg_type == TextMsgType.MSGTYPE_CHANNEL else bot.getMyChannelID()
            transfer_id = bot.doSendFile(channel, path) if channel else -1
            if transfer_id < 0:
                bot.youtube_service.cleanup(path)
                _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.upload_failed"))
                return
            _reply(bot, msg_from_id, channel_id, msg_type, bot.t("yt.upload_started", title=title))
        bot._pending_main_thread_actions.put(_on_main_thread)
    threading.Thread(target=_worker, daemon=True).start()
