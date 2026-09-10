from flask import Blueprint, render_template, flash, redirect, url_for
from .auth import login_required
from .core import get_bot_controller, _current_web_language
import i18n
from config_manager import is_setup_complete

def _t(key, **kwargs):
    return i18n.t(key, lang=_current_web_language(), **kwargs)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    bot_controller = get_bot_controller()
    if not is_setup_complete(bot_controller.config):
        flash(_t('web.flash.config_missing'), 'warning')
        return redirect(url_for('config.setup_config'))
    return render_template('index.html')