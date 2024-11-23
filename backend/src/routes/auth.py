from flask import Blueprint, request, jsonify, session
from src.models import db, User
from datetime import datetime
from src.middlewares import login_required  # Importar middleware

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/change_password', methods=['POST'])
@login_required  # Middleware de autenticación
def change_password():
    data = request.get_json()
    new_password = data.get('new_password')

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user:
        user.password_hash = user.hash_password(new_password, user.salt)
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
