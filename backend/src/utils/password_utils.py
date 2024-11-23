import hashlib
import os

class PasswordUtils:
    @staticmethod
    def hash_password(password, salt=None):
        if salt is None:
            salt = os.urandom(16).hex()
        return hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt.encode('utf-8'), 100_000
        ).hex(), salt

    @staticmethod
    def check_password(stored_password_hash, password, salt):
        hashed = PasswordUtils.hash_password(password, salt)[0]
        return hashed == stored_password_hash
