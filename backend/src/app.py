from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS 
import os
from datetime import datetime
from src.models import db, User  # Importar el modelo User desde models.py
from src.utils.password_utils import PasswordUtils  # Importar la clase PasswordUtils

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Para manejar las sesiones
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#Configurar CORS para todas las rutas. (Para que el front pueda consumir)
CORS(app)

# Ruta para registrar usuarios nuevos (solo el admin puede hacerlo)
@app.route('/register', methods=['POST'])
def register():
    if not session.get('user') or not session['user']['is_admin']:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Verificar que el usuario no exista
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} created successfully"}), 201


# Ruta para login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['user'] = {"id": user.id, "username": user.username, "is_admin": user.is_admin}
        user.last_login = datetime.now()
        db.session.commit()
        return jsonify({"message": f"Welcome {username}!"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


# Ruta para cambiar contraseña (solo el usuario o el admin pueden hacerlo)
@app.route('/change_password', methods=['POST'])
def change_password():
    if not session.get('user'):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    new_password = data.get('new_password')
    
    user = User.query.get(session['user']['id'])

    if user:
        user.password_hash, user.salt = PasswordUtils.hash_password(new_password, user.salt)
        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 200
    else:
        return jsonify({"message": "User not found"}), 404


# Ruta para consultar la fecha de último login del usuario (solo para usuarios comunes)
@app.route('/last_login', methods=['GET'])
def last_login():
    if not session.get('user'):
        return jsonify({"message": "Unauthorized"}), 403

    user = User.query.get(session['user']['id'])
    if user:
        return jsonify({"last_login": user.last_login}), 200
    else:
        return jsonify({"message": "User not found"}), 404


# Ruta para que el admin vea y pueda modificar usuarios (eliminar o poner contraseña en blanco)
@app.route('/admin/users', methods=['GET', 'DELETE', 'PATCH'])
def admin_users():
    if not session.get('user') or not session['user']['is_admin']:
        return jsonify({"message": "Unauthorized"}), 403

    if request.method == 'GET':
        # El admin puede ver todos los usuarios
        users = User.query.all()
        user_list = [{"id": user.id, "username": user.username} for user in users]
        return jsonify(user_list), 200

    if request.method == 'DELETE':
        data = request.get_json()
        user_id = data.get('user_id')

        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404

    if request.method == 'PATCH':
        data = request.get_json()
        user_id = data.get('user_id')

        user = User.query.get(user_id)
        if user:
            # Dejar la contraseña en blanco (hash de una cadena vacía)
            user.password_hash, user.salt = PasswordUtils.hash_password("", user.salt)
            db.session.commit()
            return jsonify({"message": "Password reset to blank"}), 200
        else:
            return jsonify({"message": "User not found"}), 404


# Ruta para logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)  # Eliminar la sesión
    return jsonify({"message": "Logged out successfully"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear tablas si no existen
    app.run(debug=True)
