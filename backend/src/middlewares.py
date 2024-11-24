from flask import session, jsonify
from functools import wraps
from src.models import User

def login_required(f):
    """
    Middleware to ensure the user is authenticated before accessing a route.

    Parameters:
    -----------
    f : function
        The view function to wrap.

    Returns:
    --------
    function
        A decorated function that checks for user authentication.

    Behavior:
    ---------
    - Checks if 'user_id' is present in the session.
    - If not, returns a 401 Unauthorized response with a JSON message.
    - If authenticated, proceeds to execute the wrapped function.

    Example:
    --------
    @app.route('/protected')
    @login_required
    def protected_route():
        return jsonify({'message': 'Welcome to the protected route'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized'}), 401  # User not logged in
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Middleware to ensure the user has admin privileges before accessing a route.

    Parameters:
    -----------
    f : function
        The view function to wrap.

    Returns:
    --------
    function
        A decorated function that checks for admin access.

    Behavior:
    ---------
    - Checks if 'user_id' is present in the session.
    - Retrieves the user from the database using the `User` model.
    - Verifies if the user exists and has `is_admin` set to True.
    - If not, returns a 403 Forbidden response with a JSON message.
    - If the user is an admin, proceeds to execute the wrapped function.

    Example:
    --------
    @app.route('/admin')
    @admin_required
    def admin_route():
        return jsonify({'message': 'Welcome, Admin!'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'Unauthorized'}), 401  # User not logged in

        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'message': 'Forbidden: Admin access required'}), 403  # Not an admin

        return f(*args, **kwargs)
    return decorated_function
