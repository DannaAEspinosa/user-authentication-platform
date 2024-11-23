from flask import Blueprint, request, jsonify
from src.models import db, User
from src.middlewares import admin_required  # Importar middleware

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/reset_password/<int:user_id>', methods=['POST'])
@admin_required  # Middleware de autorización
def reset_password(user_id):
    user = User.query.get(user_id)
    if user:
        user.password_hash = user.hash_password("", user.salt)  # Restablecer contraseña
        db.session.commit()
        return jsonify({'message': 'Password reset successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
