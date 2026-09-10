import sys, threading, signal, time
from config_manager import load_config, save_config, DEFAULT_CONFIG, is_setup_complete
from bot import MyTeamTalkBot, TeamTalkError
from logger_config import bot_logger, setup_logging # Import from new module
from startup_sound import play_program_started_sound

# InteractiveShell dihapus karena tidak relevan untuk Web UI

class ApplicationController:
    def __init__(self, nogui_mode):
        self.nogui = nogui_mode
        self.bot_instance = None
        self.bot_thread = None
        self.config = None
        self.app_instance = None
        self.exit_event = threading.Event()
        self.restart_requested = threading.Event()
        self.logger = bot_logger # Use the named logger
        self.webui_server = None
        self.webui_thread = None
        # Desired bot state is controlled exclusively by the WebUI. The bot
        # starts stopped and never auto-starts or auto-restarts.
        self.bot_should_run = False
        self._recovery_lock = threading.Lock()
        self._recovery_in_progress = False

    def start(self):
        # Give local audio feedback once when the application itself starts.
        # This is separate from TeamTalk bot start/stop sounds.
        play_program_started_sound()

        # GUI mode is only the first-run configuration wizard. Once the
        # configuration is saved, the window closes and the application
        # continues in the background; operational control belongs to the
        # WebUI.
        if not self.nogui:
            if not self._ensure_gui_config():
                self.logger.info("Configuration cancelled. Exiting.")
                return
        else:
            self.config = self._load_or_prompt_config()
            if not self.config:
                self.logger.critical("Configuration failed. Exiting.")
                return

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        if not self._start_webui_server():
            self.logger.critical("Web UI could not be started. Exiting.")
            return

        # The bot is deliberately STOPPED at application startup.
        # Completing setup only makes the Start control available in the WebUI.
        self.bot_should_run = False
        self.logger.info("Web UI ready. Bot is stopped until started from the WebUI.")

        while not self.exit_event.is_set():
            # Do not auto-start or auto-restart the bot here. The WebUI is the
            # single source of truth for bot start/stop control.
            time.sleep(0.5)

        self.shutdown()

    def _start_webui_server(self):
        """Start the Flask WebUI in the background using this controller instance."""
        try:
            from web_ui.app import app
            from web_ui.core import init_bot_controller
            from werkzeug.serving import make_server

            init_bot_controller(app, self)
            webui_cfg = (self.config or load_config() or DEFAULT_CONFIG).get('WebUI', {})
            host = str(webui_cfg.get('host', DEFAULT_CONFIG['WebUI']['host']))
            port = int(webui_cfg.get('port', DEFAULT_CONFIG['WebUI']['port']))
            self.webui_server = make_server(host, port, app, threaded=True)
            self.webui_thread = threading.Thread(
                target=self.webui_server.serve_forever,
                name='WebUI',
                daemon=False
            )
            self.webui_thread.start()
            self.logger.info(f"Web UI started on http://{host}:{port}")
            return True
        except Exception as e:
            self.logger.critical(f"Failed to start Web UI: {e}", exc_info=True)
            return False

    def _load_or_prompt_config(self):
        loaded_config = load_config()
        if loaded_config:
            return loaded_config
        self.logger.warning("Configuration not found. Please configure via Web UI.")
        return None

    def _ensure_gui_config(self):
        """Load config, or show the first-run GUI setup dialog."""
        self.config = load_config()
        if self.config:
            return True

        try:
            import wx
            from gui.config_dialog import ConfigDialog
        except ImportError:
            self.logger.critical("wxPython or GUI modules not found. Cannot open configuration dialog.")
            return False

        if not self.app_instance:
            self.app_instance = wx.App(False)

        defaults = {}
        defaults.update(DEFAULT_CONFIG.get('Connection', {}))
        defaults.update(DEFAULT_CONFIG.get('Bot', {}))
        defaults.update(DEFAULT_CONFIG.get('WebUI', {}))
        dialog = ConfigDialog(None, "TeamTalk Bot - Initial Configuration", defaults)
        try:
            if dialog.ShowModal() != wx.ID_OK:
                return False
            save_config(dialog.GetConfigData())
            self.config = load_config()
            if not self.config:
                wx.MessageBox(
                    "The configuration could not be saved or loaded. Check the application folder permissions.",
                    "Configuration Error", wx.OK | wx.ICON_ERROR
                )
                return False
            self.logger.info("Initial configuration saved successfully.")
            return True
        finally:
            dialog.Destroy()

    def _prompt_for_config_gui(self):
        return self._ensure_gui_config()

    def _prompt_for_config_console(self):
        # Tidak digunakan oleh Web UI
        pass

    def start_bot_session(self):
        self.bot_should_run = True
        if self.bot_thread and self.bot_thread.is_alive():
            self.logger.info("Bot session already running.")
            return
        
        if not self.config:
            self.logger.error("Cannot start bot: Configuration is not loaded.")
            return

        self.exit_event.clear() # Clear exit event for new session
        self.restart_requested.clear() # Clear restart event

        self.bot_thread = threading.Thread(target=self._bot_thread_func, daemon=True)
        self.bot_thread.start()
        self.logger.info("New bot session started.")

    def _bot_thread_func(self):
        bot = None
        try:
            bot = MyTeamTalkBot(self.config, self)
            self.bot_instance = bot
            # if not self.nogui: # Only set main_window if in GUI mode
            #     self.bot_instance.set_main_window(self.main_gui_window)
            bot.start()
        except Exception as e:
            self.logger.critical(f"Bot thread failed with unhandled exception: {e}", exc_info=True)
        finally:
            # Capture the stop reason before dropping the instance. A manual
            # WebUI stop marks the bot as intentional; an unexpected TeamTalk
            # failure leaves it unintentional.
            intentional_stop = bool(getattr(bot, '_intentional_stop', False)) if bot else False
            self.bot_instance = None
            self.logger.info("Bot thread finished execution.")

            # If the user still wants the bot running and the bot died without
            # an intentional stop, recover it automatically. This is deliberately
            # handled by the controller rather than the WebUI status endpoint.
            if (self.bot_should_run and not intentional_stop
                    and not self.exit_event.is_set()):
                self._schedule_unexpected_recovery()

    def _schedule_unexpected_recovery(self):
        """Recover a bot session that died unexpectedly without user stop."""
        with self._recovery_lock:
            if self._recovery_in_progress:
                return
            self._recovery_in_progress = True

        def recovery_worker():
            try:
                self.logger.warning(
                    "Bot stopped unexpectedly while still marked as running. "
                    "Automatic recovery will be attempted in 3 seconds."
                )
                for _ in range(30):
                    if self.exit_event.is_set() or not self.bot_should_run:
                        return
                    time.sleep(0.1)

                if self.exit_event.is_set() or not self.bot_should_run:
                    return

                self.logger.info("Starting recovered bot session...")
                self.start_bot_session()
            finally:
                with self._recovery_lock:
                    self._recovery_in_progress = False

        threading.Thread(
            target=recovery_worker,
            name='BotRecovery',
            daemon=True
        ).start()

    def request_stop(self):
        """Stop only the TeamTalk bot, keeping the WebUI/controller alive."""
        self.bot_should_run = False
        if self.bot_instance:
            self.logger.info("Stopping bot instance by WebUI request...")
            self.bot_instance._mark_stopped_intentionally()
            self.bot_instance.stop()
        elif self.bot_thread and self.bot_thread.is_alive():
            self.logger.info("Waiting for bot thread to terminate...")
        else:
            self.logger.info("Bot is already stopped.")

    def request_restart(self):
        self.bot_should_run = True
        if self.restart_requested.is_set():
            self.logger.warning("Restart is already in progress.")
            return

        self.logger.info("Restart requested by controller.")
        self.restart_requested.set()

        def restart_thread_func():
            if self.bot_instance:
                self.logger.info("Stopping bot instance...")
                self.bot_instance._mark_stopped_intentionally()
                self.bot_instance.stop()
            
            if self.bot_thread and self.bot_thread.is_alive():
                self.logger.info("Waiting for bot thread to terminate...")
                self.bot_thread.join(10.0) # Wait up to 10 seconds
                if self.bot_thread.is_alive():
                    self.logger.error("Bot thread did not terminate gracefully. Restart aborted.")
                    self.restart_requested.clear()
                    return

            self.logger.info("Bot stopped. Restarting in 3 seconds...")
            time.sleep(3)

            # Start a new bot session
            self.logger.info("Starting new bot session...")
            self.start_bot_session()
            self.restart_requested.clear()
            self.logger.info("Bot restart process completed.")

        restart_thread = threading.Thread(target=restart_thread_func, daemon=True)
        restart_thread.start()

    def _signal_handler(self, sig, frame):
        if self.exit_event.is_set():
            self.logger.warning("Shutdown already in progress.")
            return
        self.logger.info(f"Signal {sig} received, initiating shutdown...")
        self.exit_event.set()

    def request_shutdown(self):
        self.logger.info("Shutdown requested by controller.")
        self.exit_event.set()
        if self.bot_instance:
            self.bot_instance._mark_stopped_intentionally()
            self.bot_instance.stop()

    def shutdown(self):
        self.logger.info("Shutdown sequence started.")
        self.bot_should_run = False
        if self.bot_instance:
            self.bot_instance._mark_stopped_intentionally()
            self.bot_instance.stop()
        if self.bot_thread and self.bot_thread.is_alive():
            self.logger.info("Waiting for bot thread to terminate...")
            self.bot_thread.join(5.0)
        if self.webui_server:
            try:
                self.webui_server.shutdown()
            except Exception:
                self.logger.debug("WebUI server shutdown error.", exc_info=True)
        self.logger.info("Cleanup complete. Exiting.")