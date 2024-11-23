import os
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

    def check_password(self, password):
        return PasswordUtils.check_password(self.password_hash, password, self.salt)
