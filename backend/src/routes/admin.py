from flask import Blueprint, request, jsonify
from src.models import db, User
from src.middlewares import admin_required  # Authorization middleware

admin_bp = Blueprint('admin', __name__)

# Route to register new users (admin only)
@admin_bp.route('/register', methods=['POST'])
@admin_required  # Authorization middleware
def register():
    """
    Register a new user with provided username, password, and admin flag.

    POST Parameters:
    ----------------
    - username: The username for the new user.
    - password: The password for the new user.
    - is_admin: Optional flag to determine if the user is an admin (default: False).

    Response:
    ---------
    - 200: 'User registered successfully' if registration is successful.
    - 400: 'Username already exists' if the username is already taken.
    - 400: Password validation failure if the password does not meet security requirements.

    Behavior:
    ---------
    - Validates if the username already exists.
    - Validates the password strength (length, uppercase, lowercase, number, special character).
    - Creates a new user and stores them in the database.
    """
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
@admin_required  # Authorization middleware
def change_password(user_id):
    """
    Change the password of an existing user.

    POST Parameters:
    ----------------
    - new_password: The new password for the user.

    Response:
    ---------
    - 200: 'Password changed successfully' if the password is updated.
    - 400: 'New password is required' if no new password is provided.
    - 404: 'User not found' if the user with the given ID does not exist.

    Behavior:
    ---------
    - Validates the provided new password.
    - Updates the user's password in the database with a hashed version.
    """
    data = request.get_json()
    new_password = data.get('new_password')
    
    # Ensure new password is provided
    if not new_password:
        return jsonify({'message': 'New password is required'}), 400

    # Search for the user by ID
    user = User.query.get(user_id)
    if user:
        # Hash the new password and update the user record
        user.password_hash, user.salt = user.hash_password(new_password)
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


# Route to reset a user's password (blank password)
@admin_bp.route('/reset_password/<int:user_id>', methods=['POST'])
@admin_required  # Authorization middleware
def reset_password(user_id):
    """
    Reset the password of a user by setting it to a blank password.

    Response:
    ---------
    - 200: 'Password reset (blank) successfully' if the password is reset to blank.
    - 404: 'User not found' if the user with the given ID does not exist.

    Behavior:
    ---------
    - Resets the user's password to a blank (hashed empty string) value.
    """
    user = User.query.get(user_id)
    if user:
        # Set password to blank (hash empty string)
        user.password_hash, user.salt = user.hash_password("")
        db.session.commit()
        return jsonify({'message': 'Password reset (blank) successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


# Route to get all users (admin only)
@admin_bp.route('/users', methods=['GET'])
@admin_required  # Authorization middleware
def get_users():
    """
    Retrieve a list of all users.

    Response:
    ---------
    - 200: List of all users with their ID, username, and last login timestamp.

    Behavior:
    ---------
    - Retrieves all users from the database.
    - Returns a list of dictionaries containing user details.
    """
    users = User.query.all()
    users_data = [{"id": user.id, "username": user.username, "last_login": user.last_login} for user in users]
    return jsonify(users_data), 200


# Route to delete a user (admin only)
@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@admin_required  # Authorization middleware
def delete_user(user_id):
    """
    Delete a user by their ID.

    Response:
    ---------
    - 200: 'User deleted successfully' if the user is deleted.
    - 404: 'User not found' if the user with the given ID does not exist.

    Behavior:
    ---------
    - Deletes the specified user from the database.
    """
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
