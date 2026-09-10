from startup_check import run_startup_check
run_startup_check()
from web_ui.app import app
from config_manager import load_config, DEFAULT_CONFIG
import logging

if __name__ == '__main__':
    cfg = load_config()
    webui_cfg = (cfg or {}).get('WebUI', {})
    host = webui_cfg.get('host', DEFAULT_CONFIG['WebUI']['host'])
    port = int(webui_cfg.get('port', DEFAULT_CONFIG['WebUI']['port']))
    logging.info(f"Starting Flask Web UI on {host}:{port}...")
    app.run(host=host, port=port, debug=False, use_reloader=False)
