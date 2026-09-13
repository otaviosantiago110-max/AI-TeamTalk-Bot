from flask import Flask
import os
from datetime import timedelta
from dotenv import load_dotenv

from bot_controller import ApplicationController
from config_manager import load_config, DEFAULT_CONFIG
from logger_config import setup_logging, bot_logger
from .database import db
from version import VERSION, VERSION_LABEL, CLIENT_NAME, CLIENT_ID, TEAMTALK_VERSION
import i18n

load_dotenv()

_bot_controller_instance = None

def _current_web_language():
    """Resolves which language the Web UI itself should render in, based on
    the bot's configured language (same setting used for chat replies)."""
    try:
        controller = get_bot_controller()
        cfg = (controller.config if controller and controller.config else None) or load_config()
        if cfg:
            return i18n.normalize_language(cfg.get('Bot', {}).get('language', i18n.DEFAULT_LANGUAGE))
    except Exception as e:
        bot_logger.debug(f"Could not resolve web language, defaulting: {e}")
    return i18n.DEFAULT_LANGUAGE

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    initial_config = load_config()
    bot_logger.debug(f"Initial config loaded: {initial_config is not None}")

    app.secret_key = os.getenv('SECRET_KEY', 'a_fallback_secret_key_if_env_not_set')
    app.permanent_session_lifetime = timedelta(days=30)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    @app.after_request
    def disable_web_cache(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        return response

    db.init_app(app)
    app.logger.propagate = False

    setup_logging()

    @app.context_processor
    def inject_translator():
        lang = _current_web_language()
        # Expose the Web UI translations to JavaScript so dynamic elements use the same locale as the server-rendered page.
        locale_data = i18n._load(lang)
        web_i18n = {key: value for key, value in locale_data.items() if key.startswith('web.')}
        return dict(t=lambda key, **kwargs: i18n.t(key, lang=lang, **kwargs), current_lang=lang, web_i18n=web_i18n, application_version=VERSION, application_version_label=VERSION_LABEL, client_name=CLIENT_NAME, client_id=CLIENT_ID, teamtalk_version=TEAMTALK_VERSION)

    with app.app_context():
        db.create_all()
        log_file_path = os.path.join(os.getcwd(), 'bot.log')
        if os.path.exists(log_file_path):
            try:
                pass # Temporarily disable log clearing on app start for modularization
            except Exception as e:
                bot_logger.error(f"Error clearing bot.log: {e}")
    
    return app

def init_bot_controller(app, controller=None):
    global _bot_controller_instance
    if controller is not None:
        _bot_controller_instance = controller
        bot_logger.debug("Web UI is using the main application controller instance.")
    elif _bot_controller_instance is None:
        _bot_controller_instance = ApplicationController(nogui_mode=True)
        initial_config = load_config()
        _bot_controller_instance.config = initial_config
        bot_logger.debug(f"Bot controller config set: {_bot_controller_instance.config is not None}")
    return _bot_controller_instance

def get_bot_controller():
    global _bot_controller_instance
    if _bot_controller_instance is None:
        # This case should ideally not happen if init_bot_controller is called correctly
        # but as a fallback, we can try to initialize it here (though it might lack app context)
        bot_logger.warning("get_bot_controller called before initialization. Attempting fallback initialization.")
        _bot_controller_instance = ApplicationController(nogui_mode=True)
        _bot_controller_instance.config = load_config() # Load config as fallback
    return _bot_controller_instance