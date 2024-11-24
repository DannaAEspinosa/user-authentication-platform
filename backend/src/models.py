import os
import re  # For password validation
from flask_sqlalchemy import SQLAlchemy
from src.utils.password_utils import PasswordUtils

db = SQLAlchemy()

class User(db.Model):
    """
    Represents a user in the database, with fields for username, password hash, salt, 
    last login timestamp, and admin status. Provides methods for password hashing, 
    validation, and verification.

    Attributes:
    -----------
    id : int
        Primary key for the User.
    username : str
        Unique username for the user, up to 150 characters.
    password_hash : str
        The hashed password for the user.
    salt : str
        The salt used for hashing the password, stored as a 64-character hexadecimal string.
    last_login : datetime
        Timestamp of the user's last login, nullable.
    is_admin : bool
        Indicates whether the user has administrative privileges, default is False.

    Methods:
    --------
    __init__(username, password, is_admin=False):
        Initializes a new User with a username, password, and optional admin status.

    hash_password(password):
        Hashes a given password using the user's current salt.

    check_password(password):
        Validates a provided password against the stored password hash.

    validate_password(password):
        Validates a password against security criteria.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, is_admin=False):
        """
        Initializes a new User instance.

        Parameters:
        -----------
        username : str
            The username of the user.
        password : str
            The plaintext password to be hashed and stored.
        is_admin : bool, optional
            Whether the user has administrative privileges, default is False.

        Generates a random salt and hashes the password during initialization.
        """
        self.username = username
        self.salt = os.urandom(16).hex()  # Generate a random salt.
        self.password_hash, self.salt = PasswordUtils.hash_password(password, self.salt)
        self.is_admin = is_admin

    def hash_password(self, password):
        """
        Hashes a password using the user's current salt.

        Parameters:
        -----------
        password : str
            The password to hash.

        Returns:
        --------
        tuple:
            A tuple containing the hashed password and the salt used.
        """
        return PasswordUtils.hash_password(password, self.salt)

    def check_password(self, password):
        """
        Verifies whether a provided password matches the stored password hash.

        Parameters:
        -----------
        password : str
            The password to validate.

        Returns:
        --------
        bool:
            True if the password matches, False otherwise.
        """
        return PasswordUtils.check_password(self.password_hash, password, self.salt)

    @staticmethod
    def validate_password(password):
        """
        Validates that a password meets specific security requirements.

        Parameters:
        -----------
        password : str
            The password to validate.

        Returns:
        --------
        bool:
            True if the password meets the following criteria, False otherwise:
            - At least 8 characters long.
            - Contains at least one uppercase letter.
            - Contains at least one lowercase letter.
            - Contains at least one digit.
            - Contains at least one special character (!@#$%^&*(),.?":{}|<>).
        """
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):  # At least one uppercase letter.
            return False
        if not re.search(r'[a-z]', password):  # At least one lowercase letter.
            return False
        if not re.search(r'\d', password):    # At least one digit.
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # At least one special character.
            return False
        return True
