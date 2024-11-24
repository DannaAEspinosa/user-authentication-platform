from flask import Blueprint, request, jsonify, session
from src.models import db, User
from datetime import datetime
from src.middlewares import login_required  # Importar middleware

auth_bp = Blueprint('auth', __name__)

# Ruta de login (para usuarios comunes y administradores)
@auth_bp.route('/login', methods=['POST'])
def login():
    
    # Verificar si ya hay un usuario logueado
    if 'user_id' in session:
        return jsonify({'message': 'A user is already logged in. Please logout before logging in again.'}), 400
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Buscar el usuario por su nombre de usuario
    user = User.query.filter_by(username=username).first()
    if user:
        # Verificar si la contraseña es vacía (hash de cadena vacía)
        if user.check_password(""):
            return jsonify({'message': 'Account not secure. Password reset required.'}), 403
        # Verificar si la contraseña es correcta y no está vacía
        if user.password_hash and user.check_password(password):
            # Guardar el ID del usuario en la sesión
            session['user_id'] = user.id
            
            # Actualizar la fecha/hora de último login
            user.last_login = datetime.now()
            db.session.commit()

            # Responder con éxito
            return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
        else:
            return jsonify({'message': 'Invalid credentials or empty password'}), 401
    return jsonify({'message': 'User not found'}), 404

@auth_bp.route('/change_password', methods=['POST'])
@login_required  # Middleware de autenticación
def change_password():
    data = request.get_json()
    new_password = data.get('new_password')

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user:
        user.password_hash, user.salt = user.hash_password(new_password)
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
    
@auth_bp.route('/last_login', methods=['GET'])
@login_required  # Middleware de autenticación
def get_last_login():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user:
        return jsonify({'last_login': user.last_login}), 200
    return jsonify({'message': 'User not found'}), 404

@auth_bp.route('/logout', methods=['POST'])
@login_required 
def logout():
    # Eliminar el ID de usuario de la sesión
    session.clear()
    
    # Responder indicando que el log out fue exitoso
    return jsonify({'message': 'Logged out successfully'}), 200

