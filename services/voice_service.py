import asyncio
import io
import logging
import os
import re
import tempfile
import threading
import time
import unicodedata
import wave

try:
    import edge_tts
except ImportError:
    edge_tts = None


class VoiceService:
    WAKE_PHRASES = {
        "pt": ("ola ai bot", "oi ai bot", "ola a i bot", "oi a i bot"),
        "en": ("hello ai bot", "hey ai bot", "hi ai bot"),
        "es": ("hola ai bot", "hola a i bot"),
        "fr": ("bonjour ai bot", "salut ai bot"),
        "de": ("hallo ai bot", "hi ai bot"),
        "it": ("ciao ai bot",),
    }

    VOICES = {
        "pt": "pt-BR-ThalitaMultilingualNeural",
        "en": "en-US-AvaMultilingualNeural",
        "es": "es-ES-ElviraNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-AmalaNeural",
        "it": "it-IT-ElsaNeural",
        "ar": "ar-EG-SalmaNeural",
    }

    def __init__(self, bot):
        self.bot = bot
        self._lock = threading.RLock()
        self._buffers = {}
        self._last_speech = {}
        self._timers = {}
        self._active_user_id = None
        self._active_channel_id = None
        self._active_until = 0.0
        self._deactivate_timer = None
        self._processing = set()
        self._enabled = bool(getattr(bot.groq_service, "api_key", None)) and edge_tts is not None
        self._temp_dir = os.path.join(tempfile.gettempdir(), "ai_teamtalk_bot_voice")
        os.makedirs(self._temp_dir, exist_ok=True)

    def is_enabled(self):
        return self._enabled and self.bot.groq_service.is_enabled()

    def status_error(self):
        if edge_tts is None:
            return "Biblioteca edge-tts não instalada."
        if not self.bot.groq_service.is_enabled():
            return "Groq não está configurado."
        return None

    def enable_user(self, user_id):
        try:
            from TeamTalk5 import AudioFormat, StreamType
            fmt = AudioFormat()
            fmt.nAudioFmt = 2
            fmt.nSampleRate = 16000
            fmt.nChannels = 1
            return self.bot.enableAudioBlockEventEx(user_id, StreamType.STREAMTYPE_VOICE, fmt, True)
        except Exception as exc:
            self.bot.logger.warning("Voice audio event enable failed for user %s: %s", user_id, exc)
            return False

    def disable_user(self, user_id):
        try:
            from TeamTalk5 import StreamType
            return self.bot.enableAudioBlockEvent(user_id, StreamType.STREAMTYPE_VOICE, False)
        except Exception as exc:
            self.bot.logger.warning("Voice audio event disable failed for user %s: %s", user_id, exc)
            return False

    def feed_audio_block(self, user_id, block):
        if not self.is_enabled() or not block or not block.lpRawAudio or block.nSamples <= 0:
            return
        channels = max(1, int(block.nChannels))
        samples = int(block.nSamples)
        size = samples * channels * 2
        try:
            raw = bytes(__import__("ctypes").string_at(block.lpRawAudio, size))
        except Exception as exc:
            self.bot.logger.warning("Voice audio block read failed: %s", exc)
            return
        if not self._has_speech(raw):
            return
        now = time.monotonic()
        with self._lock:
            self._buffers[user_id] = self._buffers.get(user_id, bytearray()) + raw
            self._last_speech[user_id] = now
            if self._active_user_id == user_id:
                self._active_until = now + 3.0
                old_active_timer = self._deactivate_timer
                if old_active_timer:
                    old_active_timer.cancel()
                self._deactivate_timer = threading.Timer(3.0, self.deactivate, args=(user_id,))
                self._deactivate_timer.daemon = True
                self._deactivate_timer.start()
            old_timer = self._timers.pop(user_id, None)
            if old_timer:
                old_timer.cancel()
            timer = threading.Timer(3.0, self._finish_after_silence, args=(user_id, now))
            timer.daemon = True
            self._timers[user_id] = timer
            timer.start()

    def _has_speech(self, raw):
        if not raw:
            return False
        count = len(raw) // 2
        if count <= 0:
            return False
        import array
        values = array.array("h")
        values.frombytes(raw[: count * 2])
        peak = max(abs(v) for v in values) if values else 0
        return peak >= 450

    def _finish_after_silence(self, user_id, expected_last_speech):
        with self._lock:
            if self._last_speech.get(user_id) != expected_last_speech:
                return
            raw = bytes(self._buffers.pop(user_id, bytearray()))
            self._timers.pop(user_id, None)
        if len(raw) < 6400 or user_id in self._processing:
            return
        self._processing.add(user_id)
        threading.Thread(target=self._process_utterance, args=(user_id, raw), daemon=True).start()

    def _process_utterance(self, user_id, raw):
        try:
            user = self.bot.getUser(user_id)
            channel_id = int(user.nChannelID)
            wav = self._make_wav(raw)
            result = self._transcribe(wav)
            if not result:
                return
            text = result.get("text", "").strip()
            language = (result.get("language") or "").lower().split("-")[0]
            if not text:
                return
            normalized = self._normalize(text)
            wake = self._find_wake(normalized)
            with self._lock:
                active = self._active_user_id == user_id and self._active_channel_id == channel_id and time.monotonic() < self._active_until
            if not active and wake:
                with self._lock:
                    self._active_user_id = user_id
                    self._active_channel_id = channel_id
                    self._active_until = time.monotonic() + 3.0
                    old_active_timer = self._deactivate_timer
                    if old_active_timer:
                        old_active_timer.cancel()
                    self._deactivate_timer = threading.Timer(3.0, self.deactivate, args=(user_id,))
                    self._deactivate_timer.daemon = True
                    self._deactivate_timer.start()
                self.bot._play_channel_sound("appear.wav")
                remainder = self._remove_wake(text, wake)
                if remainder.strip():
                    self._handle_command(user_id, channel_id, remainder.strip(), language)
                return
            if not active:
                return
            with self._lock:
                self._active_until = time.monotonic() + 3.0
            self._handle_command(user_id, channel_id, text, language)
        except Exception as exc:
            self.bot.logger.error("Voice processing error: %s", exc, exc_info=True)
        finally:
            self._processing.discard(user_id)

    def _transcribe(self, wav_bytes):
        if not self.bot.groq_service.is_enabled():
            return None
        try:
            response = self.bot.groq_service.client.audio.transcriptions.create(
                file=("voice.wav", wav_bytes),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
            )
            if isinstance(response, dict):
                return response
            return {
                "text": getattr(response, "text", "") or "",
                "language": getattr(response, "language", "") or "",
            }
        except Exception as exc:
            self.bot.logger.error("Whisper transcription failed: %s", exc, exc_info=True)
            return None

    def _make_wav(self, raw):
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(raw)
        return buf.getvalue()

    def _normalize(self, text):
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if not unicodedata.combining(c))
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
        return re.sub(r"\s+", " ", text).strip()

    def _find_wake(self, normalized):
        for phrases in self.WAKE_PHRASES.values():
            for phrase in phrases:
                if phrase in normalized:
                    return phrase
        return None

    def _remove_wake(self, text, normalized_wake):
        norm = self._normalize(text)
        pos = norm.find(normalized_wake)
        if pos < 0:
            return ""
        end = pos + len(normalized_wake)
        return norm[end:].strip(" ,.!?;:")

    def _handle_command(self, user_id, channel_id, text, language):
        response = self.bot.groq_service.generate_content(text)
        if not response or response.startswith("[Groq Error]") or response.startswith("[Bot Error]"):
            return
        self._speak(channel_id, response, language)

    def _speak(self, channel_id, text, language):
        voice = self.VOICES.get(language, self.VOICES["en"])
        path = os.path.join(self._temp_dir, f"voice_{time.time_ns()}.mp3")
        processing_sound = os.path.join(self.bot._sounds_dir, "voice_processing.wav")
        if os.path.isfile(processing_sound):
            self.bot._play_channel_sound("voice_processing.wav")
        try:
            asyncio.run(edge_tts.Communicate(text, voice).save(path))
            self.bot._pending_main_thread_actions.put(lambda bot: bot._play_voice_response(path, channel_id))
        except Exception as exc:
            self.bot.logger.error("Edge TTS failed: %s", exc, exc_info=True)
            try:
                os.remove(path)
            except OSError:
                pass

    def deactivate(self, user_id=None):
        with self._lock:
            if user_id is not None and self._active_user_id != user_id:
                return
            old_timer = self._deactivate_timer
            self._deactivate_timer = None
            if old_timer:
                old_timer.cancel()
            self._active_user_id = None
            self._active_channel_id = None
            self._active_until = 0.0
        self.bot._play_channel_sound("disappear.wav")
