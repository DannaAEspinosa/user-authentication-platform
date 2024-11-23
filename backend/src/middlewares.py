from flask import session, jsonify
from functools import wraps
from src.models import User

# Middleware para verificar si el usuario está autenticado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized'}), 401  # No está logueado
        return f(*args, **kwargs)
    return decorated_function

# Middleware para verificar si el usuario es administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'Unauthorized'}), 401  # No está logueado
        
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'message': 'Forbidden: Admin access required'}), 403  # No es admin
        
        return f(*args, **kwargs)
    return decorated_function
