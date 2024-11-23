from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from src.models import db
from src.routes.auth import auth_bp
from src.routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Clave para manejar sesiones

    db.init_app(app)
    CORS(app)  # Permitir CORS para el frontend React

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
