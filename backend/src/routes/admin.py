from flask import Blueprint, request, jsonify
from src.models import db, User
from src.middlewares import admin_required  # Middleware de autorización

admin_bp = Blueprint('admin', __name__)
# Ruta para registrar nuevos usuarios (solo administradores)
@admin_bp.route('/register', methods=['POST'])
@admin_required  # Solo los administradores pueden registrar
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)  # Si no se especifica, el valor por defecto es False
    
    # Verificar si el nombre de usuario ya existe
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    # Crear el nuevo usuario con los datos proporcionados
    new_user = User(username=username, password=password, is_admin=is_admin)
    
    # Agregar el nuevo usuario a la base de datos
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

# Ruta para cambiar la contraseña de un usuario (solo administrador)
@admin_bp.route('/change_password/<int:user_id>', methods=['POST'])
@admin_required  # Middleware de autorización
def change_password(user_id):
    data = request.get_json()
    new_password = data.get('new_password')

    # Buscar el usuario por ID
    user = User.query.get(user_id)
    if user:
        # Hash de la nueva contraseña y actualizarla
        user.password_hash = user.hash_password(new_password, user.salt)
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

# Ruta para resetear la contraseña de un usuario (poner en blanco la contraseña)
@admin_bp.route('/reset_password/<int:user_id>', methods=['POST'])
@admin_required  # Middleware de autorización
def reset_password(user_id):
    user = User.query.get(user_id)
    if user:
        # Poner la contraseña en blanco (almacenando un hash de la cadena vacía)
        user.password_hash = user.hash_password("", user.salt)
        db.session.commit()
        return jsonify({'message': 'Password reset (blank) successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

# Ruta para ver todos los usuarios (solo administrador)
@admin_bp.route('/users', methods=['GET'])
@admin_required  # Middleware de autorización
def get_users():
    users = User.query.all()
    users_data = [{"id": user.id, "username": user.username, "last_login": user.last_login} for user in users]
    return jsonify(users_data), 200

# Ruta para eliminar un usuario (solo administrador)
@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@admin_required  # Middleware de autorización
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
