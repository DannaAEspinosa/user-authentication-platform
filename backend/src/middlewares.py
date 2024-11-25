from flask import request, jsonify
from functools import wraps
from src.models import User
from src.utils.jwt_utils import decode_jwt, generate_jwt  # Asegúrate de importar las funciones adecuadas

def login_required(f):
    """
    Middleware to ensure the user is authenticated using JWT before accessing a route.

    Parameters:
    -----------
    f : function
        The view function to wrap.

    Returns:
    --------
    function
        A decorated function that checks for user authentication via JWT.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtén el token desde la cabecera Authorization
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Unauthorized: Token is missing'}), 401  # No token provided

        # Verifica que el token esté en el formato 'Bearer <token>'
        if not token.startswith("Bearer "):
            return jsonify({'message': 'Unauthorized: Token must be prefixed with "Bearer "'}), 401

        # Extrae el token real
        token = token.split(" ")[1]

        # Decodifica el JWT
        payload = decode_jwt(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401  # Token inválido o expirado

        # Obtén el usuario desde la base de datos
        user = User.query.get(payload.get('user_id'))
        if not user:
            return jsonify({'message': 'User not found'}), 404  # Usuario no encontrado

        request.user = user  # Asigna el usuario a la solicitud para su uso posterior
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Middleware para asegurarse de que el usuario es un administrador.
    Decodifica el JWT, obtiene el user_id y verifica si el usuario es administrador.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtén el token desde la cabecera Authorization
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Forbidden: Token is missing'}), 403

        # Verifica que el token esté en el formato 'Bearer <token>'
        if not token.startswith("Bearer "):
            return jsonify({'message': 'Forbidden: Token must be prefixed with "Bearer "'}), 403

        # Extrae el token real
        token = token.split(" ")[1]

        try:
            # Decodifica el JWT
            payload = decode_jwt(token)
            if not payload:
                return jsonify({'message': 'Forbidden: Invalid or expired token'}), 403  # Token inválido o expirado

            # Obtén el user_id del payload y busca el usuario
            user_id = payload.get('user_id')
            if not user_id:
                return jsonify({'message': 'User ID is missing in the token'}), 403  # User ID no encontrado

            user = User.query.get(user_id)
            if user and user.is_admin:
                request.user = user  # Asigna el usuario a la solicitud para su uso posterior
                return f(*args, **kwargs)  # Si el usuario es administrador, ejecuta la función original
            else:
                return jsonify({'message': 'Forbidden: You are not authorized to access this resource'}), 403
        except Exception as e:
            # Si ocurre un error durante la decodificación, se devuelve un mensaje de error
            return jsonify({'message': 'Forbidden: Invalid token'}), 403

    return decorated_function
