from flask import Blueprint, jsonify, request, session
from .auth import login_required, super_admin_required
from .database import db, User
from .core import _current_web_language
import i18n

def _t(key, **kwargs):
    return i18n.t(key, lang=_current_web_language(), **kwargs)

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "role": user.role} for user in users])

@user_bp.route('/users', methods=['POST'])
@login_required
@super_admin_required
def add_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'admin') # Default to 'admin' if not provided

    if not username or not password:
        return jsonify({"status": "error", "message": _t('web.api.username_password_required')}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": _t('web.api.username_exists')}), 400

    new_user = User(username=username, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"status": "success", "message": _t('web.api.user_added'), "user": {"id": new_user.id, "username": new_user.username, "role": new_user.role}}), 201

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@super_admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_password = data.get('password')

    if new_password:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({"status": "success", "message": _t('web.api.password_updated')}), 200
    return jsonify({"status": "error", "message": _t('web.api.password_required')}), 400

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@super_admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == session.get('username'):
        return jsonify({"status": "error", "message": _t('web.api.cannot_delete_self')}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({"status": "success", "message": _t('web.api.user_deleted')}), 200
