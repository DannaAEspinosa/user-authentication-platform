from flask import Blueprint, request, jsonify, session
from src.models import db, User
from datetime import datetime
from src.middlewares import login_required  # Importing middleware

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
    - 200: Login successful with user ID returned.
    - 400: 'A user is already logged in. Please logout before logging in again.' if the user is already logged in.
    - 401: 'Invalid credentials or empty password' if the credentials are invalid.
    - 403: 'Account not secure. Password reset required.' if the password is empty (reset required).

    Behavior:
    ---------
    - Verifies that the user is not already logged in by checking the session.
    - Checks if the username exists and if the password matches.
    - Updates the user's last login time.
    - Saves the user ID in the session for tracking the logged-in user.
    """
    if 'user_id' in session:
        return jsonify({'message': 'A user is already logged in. Please logout before logging in again.'}), 400
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user:
        if user.check_password(""):
            return jsonify({'message': 'Account not secure. Password reset required.'}), 403
        if user.password_hash and user.check_password(password):
            session['user_id'] = user.id
            user.last_login = datetime.now()
            db.session.commit()
            return jsonify({'message': 'Login successful', 'success': True, 'user_id': user.id}), 200
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
    - 404: 'User not found' if the user with the provided session ID does not exist.

    Behavior:
    ---------
    - Retrieves the user ID from the session and updates the user's password in the database.
    - The password is hashed before being saved to the database.
    """
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

# Route for getting the last login time of a user (only for logged-in users)
@auth_bp.route('/last_login', methods=['GET'])
@login_required  # Authentication middleware
def get_last_login():
    """
    Retrieves the last login timestamp of the currently logged-in user.

    Response:
    ---------
    - 200: 'last_login' timestamp if the user exists.
    - 404: 'User not found' if no user is found for the given session.

    Behavior:
    ---------
    - Checks the session to find the logged-in user and retrieves their last login time.
    """
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user:
        return jsonify({'last_login': user.last_login}), 200
    return jsonify({'message': 'User not found'}), 404

# Route for logging out (removes the user session)
@auth_bp.route('/logout', methods=['POST'])
@login_required 
def logout():
    """
    Logs the user out by clearing the session data.

    Response:
    ---------
    - 200: 'Logged out successfully' after clearing the session.

    Behavior:
    ---------
    - Clears the user session and logs the user out.
    """
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# Route for getting information about the currently logged-in user
@auth_bp.route('/user-info', methods=['GET'])
@login_required  # Authentication middleware
def user_info():
    """
    Retrieves the information of the currently logged-in user.

    Response:
    ---------
    - 200: Returns the user's information (username, isAdmin, lastLogin).
    - 404: 'User not found' if no user exists for the session ID.

    Behavior:
    ---------
    - Checks the session to identify the logged-in user and retrieves their information.
    """
    user_id = session.get('user_id')  # Get user ID from session
    user = User.query.get(user_id)   # Query the database for user info

    if user:
        return jsonify({
            'username': user.username,
            'isAdmin': user.is_admin,  # Assuming `is_admin` is a Boolean field in your User model
            'lastLogin': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
        }), 200

    return jsonify({'message': 'User not found'}), 404
