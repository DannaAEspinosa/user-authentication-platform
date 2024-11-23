import os
import re  # Para validaciones de contraseñas
from flask_sqlalchemy import SQLAlchemy
from src.utils.password_utils import PasswordUtils

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.salt = os.urandom(16).hex()
        self.password_hash, self.salt = PasswordUtils.hash_password(password, self.salt)
        self.is_admin = is_admin
        
    def hash_password(self, password):
        """
        Genera un hash de la contraseña con el salt actual del usuario.
        Si no se pasa un salt, se usa el salt del objeto `User`.
        """
        # Usamos PasswordUtils internamente para generar el hash con el salt actual
        return PasswordUtils.hash_password(password, self.salt)

    def check_password(self, password):
        return PasswordUtils.check_password(self.password_hash, password, self.salt)
    
    @staticmethod
    def validate_password(password):
        """
        Verifica que la contraseña cumpla con los siguientes criterios:
        - Longitud mínima de 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un dígito
        - Al menos un carácter especial
        """
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):  # Al menos una mayúscula
            return False
        if not re.search(r'[a-z]', password):  # Al menos una minúscula
            return False
        if not re.search(r'\d', password):    # Al menos un número
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # Al menos un carácter especial
            return False
        return True
