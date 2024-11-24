import hashlib
import os

class PasswordUtils:
    """
    A utility class for handling password hashing and verification.
    Provides methods to securely hash passwords and validate them against stored hashes.

    Methods:
    --------
    hash_password(password, salt=None):
        Hashes a given password using the PBKDF2-HMAC-SHA256 algorithm with a specified or randomly generated salt.

    check_password(stored_password_hash, password, salt):
        Verifies whether a provided password matches a stored hash using the same salt.
    """

    @staticmethod
    def hash_password(password, salt=None):
        """
        Hashes a password using the PBKDF2-HMAC-SHA256 algorithm.

        Parameters:
        -----------
        password : str
            The password to hash.
        salt : str, optional
            A hexadecimal salt to use for hashing. If not provided, a random 16-byte salt will be generated.

        Returns:
        --------
        tuple:
            A tuple containing the hashed password (as a hexadecimal string) and the salt used.

        Example:
        --------
        hashed_password, salt = PasswordUtils.hash_password("my_secure_password")
        """
        if salt is None:
            salt = os.urandom(16).hex()  # Generate a random 16-byte salt in hexadecimal format.
        return hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt.encode('utf-8'), 100_000
        ).hex(), salt  # Return the hashed password and the salt.

    @staticmethod
    def check_password(stored_password_hash, password, salt):
        """
        Validates a password against a stored hash using a given salt.

        Parameters:
        -----------
        stored_password_hash : str
            The hash of the stored password to compare against.
        password : str
            The password to validate.
        salt : str
            The salt used to hash the stored password.

        Returns:
        --------
        bool:
            True if the password matches the stored hash, False otherwise.

        Example:
        --------
        is_valid = PasswordUtils.check_password(stored_password_hash, "my_secure_password", salt)
        """
        hashed = PasswordUtils.hash_password(password, salt)[0]  # Hash the input password with the provided salt.
        return hashed == stored_password_hash  # Compare the newly hashed password with the stored hash.
