from flask import Blueprint, request, jsonify
from src.models import db, User
from datetime import datetime
from src.utils.jwt_utils import generate_jwt, decode_jwt  # Asumimos que estas funciones están en jwt_utils
from src.middlewares import login_required  # Importando middleware

auth_bp = Blueprint('auth', __name__)

# Route for login (for both regular users and admins)
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login route. It allows users to log in by providing a username and password.

    POST Parameters:
    ----------------
    - username: The username for the user trying to log in.
    - password: The password for the user.

    Response:
    ---------
    - 200: Login successful with user ID and JWT token returned.
    - 400: 'A user is already logged in. Please logout before logging in again.' if the user is already logged in.
    - 401: 'Invalid credentials or empty password' if the credentials are invalid.
    - 403: 'Account not secure. Password reset required.' if the password is empty (reset required).

    Behavior:
    ---------
    - Verifies that the user exists and the password matches.
    - Updates the user's last login time.
    - Generates a JWT token for the logged-in user.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user:
        if user.check_password(""):  # Placeholder for checking if the account is secure
            return jsonify({'message': 'Account not secure. Password reset required.'}), 403
        if user.password_hash and user.check_password(password):
            user.last_login = datetime.now()
            db.session.commit()
            
            # Generate JWT token
            token = generate_jwt(user.id)
            return jsonify({'message': 'Login successful', 'success': True, 'user_id': user.id, 'token': token}), 200

        else:
            return jsonify({'message': 'Invalid credentials or empty password','success': False}), 401
    return jsonify({'message': 'User not found'}), 404

# Route for changing password (only for logged-in users)
@auth_bp.route('/change_password', methods=['POST'])
@login_required  # Authentication middleware
def change_password():
    """
    Allows a logged-in user to change their password.

    POST Parameters:
    ----------------
    - new_password: The new password for the user.

    Response:
    ---------
    - 200: 'Password changed successfully' if the password is successfully updated.
    - 404: 'User not found' if the user with the provided JWT token does not exist.

    Behavior:
    ---------
    - Retrieves the user ID from the decoded JWT token and updates the user's password in the database.
    - The password is hashed before being saved to the database.
    """
    data = request.get_json()
    new_password = data.get('new_password')

    user_id = decode_jwt(request.headers.get('Authorization'))  # Extract user ID from the token
    user = User.query.get(user_id)
    if user:
        user.password_hash, user.salt = user.hash_password(new_password)
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

# Route for getting the last login time of a user (only for logged-in users)
@auth_bp.route('/last_login', methods=['GET'])
@login_required  # Authentication middleware
def get_last_login():
    """
    Retrieves the last login timestamp of the currently logged-in user.

    Response:
    ---------
    - 200: 'last_login' timestamp if the user exists.
    - 404: 'User not found' if no user is found for the given JWT token.

    Behavior:
    ---------
    - Checks the decoded JWT token to find the logged-in user and retrieves their last login time.
    """
    user_id = decode_jwt(request.headers.get('Authorization'))  # Extract user ID from the token
    user = User.query.get(user_id)
    if user:
        return jsonify({'last_login': user.last_login}), 200
    return jsonify({'message': 'User not found'}), 404

# Route for logging out (JWT does not require server-side logout, but we can clear the token)
@auth_bp.route('/logout', methods=['POST'])
@login_required  # Authentication middleware
def logout():
    """
    Logs the user out by removing the JWT token from the client-side.

    Response:
    ---------
    - 200: 'Logged out successfully' after clearing the token.
    """
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/user-info', methods=['GET'])
@login_required  # Authentication middleware
def user_info():
    """
    Retrieves the information of the currently logged-in user.

    Response:
    ---------
    - 200: Returns the user's information (username, isAdmin, lastLogin).
    - 404: 'User not found' if no user exists for the decoded JWT token.

    Behavior:
    ---------
    - Uses decode_jwt to extract user ID and fetch user details from the database.
    """
    # Obtiene el token del encabezado Authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Authorization header missing'}), 401

    # Valida que el formato del token sea 'Bearer <token>'
    if not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Invalid token format'}), 401

    # Extrae el token real
    token = auth_header.split(' ')[1]

    try:
        # Decodifica el token para obtener el user_id
        decoded_data = decode_jwt(token)
        if not decoded_data:
            return jsonify({'message': 'Invalid or expired token'}), 401

        user_id = decoded_data.get('user_id')  # Asegúrate de usar el campo correcto
        if not user_id:
            return jsonify({'message': 'Token missing user_id'}), 401

        # Busca al usuario en la base de datos
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Respuesta exitosa con información del usuario
        return jsonify({
            'username': user.username,
            'isAdmin': user.is_admin,
            'lastLogin': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
        }), 200

    except Exception as e:
        return jsonify({'message': 'Error decoding token', 'error': str(e)}), 401
