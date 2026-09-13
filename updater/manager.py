import logging
import threading
import time

from version import RELEASE_ASSET_NAME, TAG
from .checker import fetch_latest_release, fetch_latest_release_status
from .downloader import download_release
from .installer import launch_installer, prepare_install

CHECK_INTERVAL_SECONDS = 15 * 60


class UpdateManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self._lock = threading.Lock()
        self._check_in_progress = False
        self._download_in_progress = False
        self._pending_release = None
        self._download_path = None
        self._next_check_time = time.time()
        self._timer_stop = threading.Event()
        self._timer_thread = None

    @property
    def pending_release(self):
        with self._lock:
            return self._pending_release

    @property
    def downloading(self):
        with self._lock:
            return self._download_in_progress

    def start(self):
        with self._lock:
            if self._timer_thread and self._timer_thread.is_alive():
                return
            self._timer_stop.clear()
            self._next_check_time = time.time() + CHECK_INTERVAL_SECONDS

        self.check_async()
        self._timer_thread = threading.Thread(
            target=self._timer_worker,
            name="UpdateTimer",
            daemon=True,
        )
        self._timer_thread.start()

    def stop(self):
        self._timer_stop.set()
        thread = self._timer_thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=1.0)
        self._timer_thread = None

    def _timer_worker(self):
        while not self._timer_stop.wait(CHECK_INTERVAL_SECONDS):
            self.check_async()

    def tick(self):
        # Kept for compatibility with the bot event loop. Periodic checks are
        # driven by the dedicated timer so source and frozen builds behave the
        # same even when the event loop is busy.
        return

    def check_async(self):
        with self._lock:
            if self._check_in_progress or self._download_in_progress or self._pending_release:
                return False
            self._check_in_progress = True

        thread = threading.Thread(target=self._check_worker, name="UpdateCheck", daemon=True)
        thread.start()
        return True

    def _check_worker(self):
        try:
            self.bot._pending_main_thread_actions.put(lambda bot: bot._send_system_channel_message(bot._target_channel_id, bot.t("updater.checking")))
            release, up_to_date = fetch_latest_release_status(RELEASE_ASSET_NAME, TAG, self.logger)
            if release:
                self.bot._pending_main_thread_actions.put(lambda bot: self._announce_update(bot, release))
            elif up_to_date:
                self.bot._pending_main_thread_actions.put(lambda bot: bot._send_system_channel_message(bot._target_channel_id, bot.t("updater.up_to_date")))
        except Exception as exc:
            self.logger.warning("Update check failed: %s", exc, exc_info=True)
        finally:
            with self._lock:
                self._check_in_progress = False

    def _announce_update(self, bot, release):
        with self._lock:
            if self._pending_release or self._download_in_progress:
                return
            self._pending_release = release

        bot._play_channel_sound("update_found.wav")
        message = bot.t("updater.update_available", version=release.tag)
        if bot._target_channel_id > 0:
            bot._send_system_channel_message(bot._target_channel_id, message)
        bot._send_system_broadcast_message(message)
        bot._log_to_gui(f"Update available: {release.tag}")

    def handle_response(self, user_id, text):
        with self._lock:
            release = self._pending_release
            if not release or self._download_in_progress:
                return False

        if not self.bot._is_admin(user_id):
            return False

        answer = text.strip().lower()
        if answer not in {"y", "n"}:
            return False

        with self._lock:
            self._pending_release = None

        if answer == "n":
            self.bot._send_system_broadcast_message(self.bot.t("updater.download_cancelled"))
            self.bot._send_system_channel_message(self.bot._target_channel_id, self.bot.t("updater.download_cancelled"))
            return True

        with self._lock:
            self._download_in_progress = True
        self.bot._pending_main_thread_actions.put(lambda bot: bot._start_updating_sound())
        self.bot._send_system_broadcast_message(self.bot.t("updater.download_started", version=release.tag))
        self.bot._send_system_channel_message(self.bot._target_channel_id, self.bot.t("updater.download_started", version=release.tag))
        thread = threading.Thread(target=self._download_worker, args=(release,), name="UpdateDownload", daemon=True)
        thread.start()
        return True

    def _download_worker(self, release):
        try:
            path = download_release(release, self._progress)
            plan = prepare_install(path)
            with self._lock:
                self._download_path = path
            self.bot._pending_main_thread_actions.put(lambda bot: self._download_completed(bot, release, plan))
        except Exception as exc:
            self.logger.error("Update preparation failed: %s", exc, exc_info=True)
            self.bot._pending_main_thread_actions.put(lambda bot: self._download_failed(bot, release, exc))

    def _progress(self, downloaded, total):
        if total and downloaded % (1024 * 1024) < 256 * 1024:
            self.logger.info("Update download: %.1f%%", downloaded * 100 / total)

    def _download_completed(self, bot, release, plan):
        bot._stop_updating_sound()
        with self._lock:
            self._download_in_progress = False
        bot._send_system_broadcast_message(bot.t("updater.download_complete", version=release.tag))
        bot._send_system_channel_message(bot._target_channel_id, bot.t("updater.download_complete", version=release.tag))
        bot._log_to_gui(f"Update package downloaded and validated: {release.tag}")
        try:
            with self._lock:
                path = self._download_path
            launch_installer(plan)
            bot._log_to_gui(f"Update installation prepared: {release.tag}")
            bot._send_system_broadcast_message(bot.t("updater.install_started", version=release.tag))
            bot._send_system_channel_message(bot._target_channel_id, bot.t("updater.install_started", version=release.tag))
            controller = getattr(bot, "controller", None)
            if controller:
                controller.request_shutdown()
            else:
                bot.stop()
        except Exception as exc:
            self.logger.error("Update installation preparation failed: %s", exc, exc_info=True)
            bot._send_system_broadcast_message(bot.t("updater.install_failed"))
            bot._send_system_channel_message(bot._target_channel_id, bot.t("updater.install_failed"))
            bot._log_to_gui(f"Update installation failed: {exc}")

    def _download_failed(self, bot, release, exc):
        bot._stop_updating_sound()
        with self._lock:
            self._download_in_progress = False
        bot._send_system_broadcast_message(bot.t("updater.download_failed"))
        bot._send_system_channel_message(bot._target_channel_id, bot.t("updater.download_failed"))
        bot._log_to_gui(f"Update {release.tag} failed: {exc}")
