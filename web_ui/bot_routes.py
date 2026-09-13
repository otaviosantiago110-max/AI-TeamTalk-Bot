from flask import Blueprint, jsonify, request
from .auth import login_required
from logger_config import bot_logger
from .core import get_bot_controller, _current_web_language
from config_manager import is_setup_complete
import i18n
from version import VERSION, VERSION_LABEL, CLIENT_NAME, CLIENT_ID, TEAMTALK_VERSION

def _t(key, **kwargs):
    return i18n.t(key, lang=_current_web_language(), **kwargs)

bot_bp = Blueprint('bot', __name__)

def _sanitize_for_json(value):
    if hasattr(value, 'value'): # Handle ctypes objects (like c_uint, c_int)
        return value.value
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    return value

@bot_bp.route('/status', methods=['GET'])
@login_required
def get_status():
    bot_controller = get_bot_controller()
    status = {"running": False} # Default status

    try:
        if bot_controller:
            bot_logger.debug("get_status: bot_controller exists.")
            if bot_controller.bot_instance:
                bot_logger.debug("get_status: bot_controller.bot_instance exists.")
                status["running"] = bot_controller.bot_thread.is_alive() if bot_controller.bot_thread else False
                bot_logger.debug(f"get_status: running={status['running']}")
                
                status["logged_in"] = bot_controller.bot_instance._logged_in
                bot_logger.debug(f"get_status: logged_in={status['logged_in']}")
                
                status["in_channel"] = bot_controller.bot_instance._in_channel
                bot_logger.debug(f"get_status: in_channel={status['in_channel']}")

                status["features"] = {
                    "announce_join_leave": bot_controller.bot_instance.announce_join_leave,
                    "allow_channel_messages": bot_controller.bot_instance.allow_channel_messages,
                    "allow_broadcast": bot_controller.bot_instance.allow_broadcast,
                    "allow_groq_pm": bot_controller.bot_instance.allow_groq_pm,
                    "allow_groq_channel": bot_controller.bot_instance.allow_groq_channel,
                    "filter_enabled": bot_controller.bot_instance.filter_enabled,
                    "bot_locked": bot_controller.bot_instance.bot_locked,
                    "context_history_enabled": bot_controller.bot_instance.context_history_enabled,
                    "debug_logging_enabled": bot_controller.bot_instance.debug_logging_enabled,
                }
                bot_logger.debug(f"get_status: features={status['features']}")
                
                # Ensure config is JSON serializable
                if bot_controller.config:
                    try:
                        import json
                        # Basic check, but ideally we should sanitize config too if it has bytes
                        json.dumps(bot_controller.config) 
                        status["config"] = bot_controller.config
                        bot_logger.debug("get_status: config is JSON serializable.")
                    except TypeError as e:
                        bot_logger.error(f"get_status: Config is not JSON serializable: {e}", exc_info=True)
                        status["config"] = {"error": _t('web.api.config_not_serializable')}
                else:
                    status["config"] = {}
                    bot_logger.debug("get_status: bot_controller.config is None.")

                # Add TeamTalk server connection details
                if status["running"] and bot_controller.bot_instance._logged_in:
                    status["server_info"] = {
                        "host": _sanitize_for_json(bot_controller.bot_instance.host),
                        "tcp_port": bot_controller.bot_instance.tcp_port,
                        "udp_port": bot_controller.bot_instance.udp_port,
                        "nickname": _sanitize_for_json(bot_controller.bot_instance.nickname),
                        "username": _sanitize_for_json(bot_controller.bot_instance.username),
                        "target_channel_path": _sanitize_for_json(bot_controller.bot_instance.target_channel_path),
                        "my_user_id": bot_controller.bot_instance._my_user_id,
                        "my_rights": _sanitize_for_json(bot_controller.bot_instance.my_rights),
                        "client_name": CLIENT_NAME,
                        "client_id": CLIENT_ID,
                        "application_version": VERSION,
                        "application_version_label": VERSION_LABEL,
                        "teamtalk_version": TEAMTALK_VERSION,
                        "status_message": _sanitize_for_json(bot_controller.bot_instance.status_message),
                        "logged_in": bot_controller.bot_instance._logged_in,
                        "in_channel": bot_controller.bot_instance._in_channel,
                    }
                    bot_logger.debug(f"get_status: server_info={status['server_info']}")
            else:
                bot_logger.debug("get_status: bot_controller.bot_instance is None.")
        else:
            bot_logger.debug("get_status: bot_controller is None.")
    except Exception as e:
        bot_logger.error(f"Error in get_status: {e}", exc_info=True)
        status = {"running": False, "error": str(e)}
    
    return jsonify(status)

@bot_bp.route('/start', methods=['POST'])
@login_required
def start_bot():
    bot_controller = get_bot_controller()
    if not bot_controller:
        return jsonify({"status": "error", "message": _t('web.api.controller_not_initialized')}), 500

    if bot_controller.bot_thread and bot_controller.bot_thread.is_alive():
        return jsonify({"status": "info", "message": _t('web.api.already_running')})
    
    if not bot_controller.config:
        from config_manager import load_config
        bot_controller.config = load_config()
    if not is_setup_complete(bot_controller.config):
        return jsonify({"status": "error", "message": _t('web.api.config_missing')}), 400

    try:
        bot_controller.start_bot_session()
        return jsonify({"status": "success", "message": _t('web.api.starting')})
    except Exception as e:
        bot_logger.error(_t('web.api.start_error', error=e), exc_info=True)
        return jsonify({"status": "error", "message": _t('web.api.start_error', error=e)}), 500

@bot_bp.route('/stop', methods=['POST'])
@login_required
def stop_bot():
    bot_controller = get_bot_controller()
    if bot_controller and bot_controller.bot_thread and bot_controller.bot_thread.is_alive():
        bot_logger.info("Web UI: Stop request received.")
        bot_controller.request_stop()
        bot_controller.bot_thread.join(5) 
        if not bot_controller.bot_thread.is_alive():
            bot_logger.info("Web UI: Bot thread successfully stopped.")
            return jsonify({"status": "success", "message": _t('web.api.stopping')})
        else:
            bot_logger.warning("Web UI: Bot thread did not stop gracefully within 5 seconds.")
            return jsonify({"status": "warning", "message": _t('web.api.shutdown_slow')})
    return jsonify({"status": "info", "message": _t('web.api.not_running')})

@bot_bp.route('/restart', methods=['POST'])
@login_required
def restart_bot():
    bot_controller = get_bot_controller()
    if not bot_controller:
        return jsonify({"status": "error", "message": _t('web.api.controller_not_initialized')}), 500

    if bot_controller.bot_thread and bot_controller.bot_thread.is_alive():
        if bot_controller.restart_requested.is_set():
             return jsonify({"status": "info", "message": _t('web.api.restart_in_progress')})
        
        bot_logger.info("Web UI: Restart request received.")
        bot_controller.request_restart()
        return jsonify({"status": "success", "message": _t('web.api.restart_initiated')})
    else:
        bot_logger.info("Web UI: Bot is not running, starting instead.")
        bot_controller.start_bot_session()
        return jsonify({"status": "success", "message": _t('web.api.starting_now')})


@bot_bp.route('/toggle_feature/<feature_name>', methods=['POST'])
@login_required
def toggle_feature(feature_name):
    bot_controller = get_bot_controller()
    if not bot_controller or not bot_controller.bot_instance:
        return jsonify({"status": "error", "message": _t('web.api.not_running')}), 400

    feature_map = {
        "jcl": "announce_join_leave",
        "chanmsg": "allow_channel_messages",
        "broadcast": "allow_broadcast",
        "groqpm": "allow_groq_pm",
        "groqchan": "allow_groq_channel",
        "filter": "filter_enabled",
        "lock": "bot_locked",
        "context_history": "context_history_enabled",
        "debug_logging": "debug_logging_enabled"
    }
    
    full_feature_name = feature_map.get(feature_name)
    if not full_feature_name:
        return jsonify({"status": "error", "message": _t('web.api.unknown_feature', feature=feature_name)}), 400

    toggle_method_name = f"toggle_{full_feature_name}"
    toggle_method = getattr(bot_controller.bot_instance, toggle_method_name, None)

    if callable(toggle_method):
        toggle_method()
        new_status = getattr(bot_controller.bot_instance, full_feature_name, False)
        return jsonify({"status": "success", "message": _t('web.api.feature_state', feature=full_feature_name, state=('ON' if new_status else 'OFF')), "new_state": new_status})
    else:
        return jsonify({"status": "error", "message": _t('web.api.toggle_missing', feature=full_feature_name)}), 500