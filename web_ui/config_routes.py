from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .auth import login_required, super_admin_required
from config_manager import load_config, save_config, DEFAULT_CONFIG, is_setup_complete
from logger_config import bot_logger
from .core import get_bot_controller, _current_web_language
import i18n

def _t(key, **kwargs):
    return i18n.t(key, lang=_current_web_language(), **kwargs)

config_bp = Blueprint('config', __name__)

@config_bp.route('/setup_config', methods=['GET', 'POST'])
@login_required
def setup_config():
    bot_controller = get_bot_controller()
    current = load_config() or DEFAULT_CONFIG

    if request.method == 'POST':
        import copy
        new_config = copy.deepcopy(current)
        for key, value in request.form.items():
            if key == 'Bot_ai_gender':
                continue
            if '_' not in key:
                continue
            section, option = key.split('_', 1)
            if section not in new_config:
                new_config[section] = {}
            if value == 'on' and option in DEFAULT_CONFIG.get(section, {}):
                default_value = DEFAULT_CONFIG[section][option]
                new_config[section][option] = 'True' if str(default_value).lower() == 'true' else value
            elif option in DEFAULT_CONFIG.get(section, {}) and str(DEFAULT_CONFIG[section][option]).lower() in ('true', 'false'):
                new_config[section][option] = 'False'
            else:
                new_config[section][option] = value

        new_config.setdefault('WebUI', {})['setup_complete'] = 'True'
        if not save_config(new_config):
            bot_logger.error("Initial Web UI configuration could not be saved.")
            flash(_t('web.api.config_save_error'), 'danger')
            return render_template('setup_config.html', default_config=new_config)

        bot_controller.config = load_config() or new_config
        flash(_t('web.flash.config_saved'), 'success')
        bot_logger.info("Initial TeamTalk configuration saved. Bot remains stopped until Start is pressed in the WebUI.")
        return redirect(url_for('main.index'))

    if is_setup_complete(bot_controller.config):
        return redirect(url_for('main.index'))

    setup_defaults = {section: dict(options) for section, options in DEFAULT_CONFIG.items()}
    setup_defaults['WebUI'].pop('setup_complete', None)
    return render_template('setup_config.html', default_config=setup_defaults)

@config_bp.route('/config', methods=['GET', 'POST'])
@login_required
@super_admin_required
def manage_config():
    bot_controller = get_bot_controller()
    if request.method == 'GET':
        if bot_controller and bot_controller.config:
            return jsonify(bot_controller.config)
        else:
            config = load_config()
            if config:
                return jsonify(config)
            return jsonify({"status": "error", "message": _t('web.api.config_not_loaded')}), 404
    elif request.method == 'POST':
        new_config_data = request.get_json()

        bot_logger.debug(f"DEBUG: new_config_data from JSON in manage_config: {new_config_data}")

        current_config = bot_controller.config if bot_controller.config else load_config() or DEFAULT_CONFIG
        bot_logger.debug(f"DEBUG: current_config before merge in manage_config: {current_config}")
        
        for section, settings in new_config_data.items():
            if section in current_config:
                for key, value in settings.items():
                    if section == 'Bot' and key == 'ai_gender':
                        continue
                    current_config[section][key] = value
            else:
                current_config[section] = settings

        bot_logger.debug(f"DEBUG: current_config after merge in manage_config: {current_config}")

        save_config(current_config)
        bot_controller.config = current_config
        
        if bot_controller.bot_thread and bot_controller.bot_thread.is_alive():
            bot_logger.info("Bot is running, initiating restart to apply new configuration.")
            bot_controller.request_restart()
            return jsonify({"status": "success", "message": _t('web.api.config_updated_restart')})
        else:
            return jsonify({"status": "success", "message": _t('web.api.config_updated')})