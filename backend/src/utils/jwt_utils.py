import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_jwt(user_id):
    """
    Generates a JWT token for the authenticated user.

    Args:
    - user_id (int): The ID of the user.

    Returns:
    - str: The JWT token.
    """
    expiration = datetime.now() + timedelta(days=1)  # Token expires in 1 day
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_jwt(token):
    """
    Decodes the JWT token to get the user ID.

    Args:
    - token (str): The JWT token.

    Returns:
    - dict: The decoded JWT payload if the token is valid, else None.
    """
    try:
        # Asegúrate de usar la misma clave secreta utilizada para firmar el token
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        # Verificar si el token está expirado
        if payload['exp'] < datetime.now().timestamp():
            return None  # El token ha expirado
        return payload
    except jwt.ExpiredSignatureError:
        return None  # El token ha expirado
    except jwt.InvalidTokenError:
        return None  # El token no es válido
