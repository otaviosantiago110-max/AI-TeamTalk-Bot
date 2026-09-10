import logging
import os
import shutil
import subprocess
import tempfile
import uuid

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


class YouTubeService:
    def __init__(self, download_dir=None):
        self.download_dir = download_dir or os.path.join(tempfile.gettempdir(), "ai_teamtalk_bot_youtube")
        os.makedirs(self.download_dir, exist_ok=True)
        self._resource_base = self._find_resource_base()
        self.yt_dlp_exe = self._find_tool("yt-dlp.exe", "yt-dlp")
        self.ffmpeg_exe = self._find_tool("ffmpeg.exe", "ffmpeg")

    def _find_resource_base(self):
        import sys
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _find_tool(self, filename, path_name):
        candidates = [
            os.path.join(self._resource_base, "tools", filename),
            os.path.join(os.path.dirname(self._resource_base), "tools", filename),
        ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                return candidate
        return shutil.which(path_name) or shutil.which(filename)

    def is_enabled(self):
        return bool(self.yt_dlp_exe and self.ffmpeg_exe)

    def status_error(self):
        missing = []
        if not self.yt_dlp_exe:
            missing.append("yt-dlp.exe")
        if not self.ffmpeg_exe:
            missing.append("ffmpeg.exe")
        return "Ferramentas ausentes: " + ", ".join(missing) if missing else None

    def _resolve_query(self, query, allow_playlist=False):
        if not self.yt_dlp_exe:
            raise RuntimeError("yt-dlp.exe não encontrado.")
        target = query.strip()
        if not target:
            raise ValueError("Consulta vazia.")
        if not (target.startswith("http://") or target.startswith("https://")):
            target = f"ytsearch1:{target}"
        cmd = [self.yt_dlp_exe, "--flat-playlist", "--dump-single-json", "--no-warnings", "--skip-download"]
        if not allow_playlist:
            cmd.append("--no-playlist")
        cmd.append(target)
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout).strip() or "Falha ao consultar o YouTube.")
        import json
        data = json.loads(result.stdout)
        if data.get("entries") is not None:
            entries = [e for e in data.get("entries", []) if e]
            if not entries:
                raise RuntimeError("Nenhum resultado encontrado.")
            return entries
        return [data]

    def _entry_url(self, entry):
        url = entry.get("webpage_url") or entry.get("original_url")
        if url and (url.startswith("http://") or url.startswith("https://")):
            return url
        video_id = entry.get("id") or entry.get("url")
        extractor = (entry.get("ie_key") or entry.get("extractor_key") or "").lower()
        if video_id and "youtube" in extractor:
            return f"https://www.youtube.com/watch?v={video_id}"
        return video_id or ""

    def _download_entry(self, entry):
        uid = uuid.uuid4().hex
        source_template = os.path.join(self.download_dir, f"{uid}.%(ext)s")
        output_path = os.path.join(self.download_dir, f"{uid}.mp3")
        source_cmd = [
            self.yt_dlp_exe,
            "--no-warnings",
            "--no-playlist",
            "--format", "bestaudio/best",
            "--output", source_template,
            "--no-part",
            self._entry_url(entry),
        ]
        result = subprocess.run(source_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout).strip() or "Falha no download do YouTube.")

        source_path = None
        prefix = uid + "."
        for name in os.listdir(self.download_dir):
            if name.startswith(prefix) and name != os.path.basename(output_path):
                source_path = os.path.join(self.download_dir, name)
                break
        if not source_path or not os.path.isfile(source_path):
            raise RuntimeError("Download concluído, mas o arquivo de origem não foi encontrado.")

        ffmpeg_cmd = [
            self.ffmpeg_exe,
            "-y",
            "-i", source_path,
            "-vn",
            "-codec:a", "libmp3lame",
            "-b:a", "320k",
            "-ar", "48000",
            "-id3v2_version", "3",
            "-metadata", f"title={entry.get('title', 'YouTube')}",
            output_path,
        ]
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        try:
            os.remove(source_path)
        except OSError:
            pass
        if result.returncode != 0 or not os.path.isfile(output_path):
            raise RuntimeError((result.stderr or result.stdout).strip() or "Falha na conversão para MP3.")
        return output_path, entry.get("title", "Desconhecido")

    def search_and_download(self, query):
        if not self.is_enabled():
            return None, self.status_error()
        try:
            entries = self._resolve_query(query, allow_playlist=False)
            return self._download_entry(entries[0])
        except Exception as exc:
            logging.error("YouTube download error for query %r: %s", query, exc, exc_info=True)
            return None, str(exc)

    def resolve_playlist(self, query):
        if not self.is_enabled():
            raise RuntimeError(self.status_error())
        entries = self._resolve_query(query, allow_playlist=True)
        result = []
        for entry in entries:
            title = entry.get("title") or "Desconhecido"
            url = entry.get("webpage_url") or entry.get("url")
            if url:
                result.append({"title": title, "url": url})
        if not result:
            raise RuntimeError("Nenhum item encontrado na playlist.")
        return result

    def download_playlist_items(self, items):
        downloaded = []
        try:
            for item in items:
                downloaded.append(self._download_entry(item))
            return downloaded
        except Exception:
            for path, _ in downloaded:
                self.cleanup(path)
            raise

    def cleanup(self, file_path):
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as exc:
            logging.warning("Failed to remove temporary YouTube file %r: %s", file_path, exc)
