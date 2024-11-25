from flask import Blueprint, request, jsonify
from src.models import db, User
from src.middlewares import admin_required  # Middleware para autorización

admin_bp = Blueprint('admin', __name__)


# Route to register new users (admin only)
@admin_bp.route('/register', methods=['POST'])
@admin_required # Usando el middleware que verifica si es administrador
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)  # Default value is False if not provided
    
    # Check if the username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    # Validate password security requirements
    if not User.validate_password(password):
        return jsonify({
            'message': 'Password must be at least 8 characters long, include an uppercase letter, '
                       'a lowercase letter, a number, and a special character.'
        }), 400

    # Create the new user with provided details
    new_user = User(username=username, password=password, is_admin=is_admin)
    
    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201


# Route to change a user's password (admin only)
@admin_bp.route('/change_password/<int:user_id>', methods=['POST'])
@admin_required  # Usando el middleware que verifica si es administrador
def change_password(user_id):
    data = request.get_json()
    new_password = data.get('new_password')
    
    if not new_password:
        return jsonify({'message': 'New password is required'}), 400

    user = User.query.get(user_id)
    if user:
        user.password_hash, user.salt = user.hash_password(new_password)
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


# Route to reset a user's password (blank password) (admin only)
@admin_bp.route('/reset_password/<int:user_id>', methods=['POST'])
@admin_required  # Usando el middleware que verifica si es administrador
def reset_password(user_id):
    user = User.query.get(user_id)
    if user:
        user.password_hash, user.salt = user.hash_password("")
        db.session.commit()
        return jsonify({'message': 'Password reset (blank) successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


# Route to get all users (admin only)
@admin_bp.route('/users', methods=['GET'])
@admin_required  # Usando el middleware que verifica si es administrador
def get_users():
    users = User.query.all()
    users_data = [{"id": user.id, "username": user.username, "last_login": user.last_login} for user in users]
    return jsonify(users_data), 200


# Route to delete a user (admin only)
@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@admin_required  # Usando el middleware que verifica si es administrador
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
