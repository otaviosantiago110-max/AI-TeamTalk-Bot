import logging
import os
import tempfile
import uuid

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


class YouTubeService:
    """Searches YouTube and downloads audio-only files that can be handed off
    to TeamTalk's StartStreamingMediaFileToChannel."""

    def __init__(self, download_dir=None):
        self.download_dir = download_dir or os.path.join(tempfile.gettempdir(), "ai_teamtalk_bot_youtube")
        os.makedirs(self.download_dir, exist_ok=True)

    def is_enabled(self):
        return YT_DLP_AVAILABLE

    def search_and_download(self, query):
        """Accepts either a search query or a direct YouTube URL. Downloads
        the best available audio-only stream.

        Returns (file_path, title) on success, or (None, error_message) on
        failure.
        """
        if not YT_DLP_AVAILABLE:
            return None, "yt-dlp não está instalado (pip install yt-dlp)."

        unique_id = uuid.uuid4().hex
        out_template = os.path.join(self.download_dir, f"{unique_id}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_template,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1',
            'nocheckcertificate': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=True)
                if info is None:
                    return None, "Nenhum resultado encontrado."
                if 'entries' in info:
                    entries = [e for e in info['entries'] if e]
                    if not entries:
                        return None, "Nenhum resultado encontrado."
                    info = entries[0]

                title = info.get('title', 'Desconhecido')
                file_path = ydl.prepare_filename(info)

                if not os.path.exists(file_path):
                    # Fall back to scanning the download dir for anything
                    # that starts with our unique id (extension guessing
                    # inside yt-dlp can vary depending on postprocessors).
                    for f in os.listdir(self.download_dir):
                        if f.startswith(unique_id):
                            file_path = os.path.join(self.download_dir, f)
                            break

                if not os.path.exists(file_path):
                    return None, "Download concluído, mas o arquivo de áudio não foi encontrado."

                return file_path, title
        except Exception as e:
            logging.error(f"YouTube download error for query '{query}': {e}", exc_info=True)
            return None, str(e)

    def cleanup(self, file_path):
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logging.warning(f"Failed to remove temp audio file '{file_path}': {e}")
