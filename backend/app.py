from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from src.models import db, User
from src.routes.auth import auth_bp
from src.routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Clave para manejar sesiones

    db.init_app(app)

    
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)  # Permitir CORS para el frontend React
    app.config['SESSION_COOKIE_NAME'] = 'session'  # Nombre de la cookie de sesión
    app.config['SESSION_COOKIE_SECURE'] = False  # Establecer a True si usas HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Hacer que la cookie solo sea accesible por HTTP (no a través de JavaScript)
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Opcional: ayuda a prevenir ataques CSRF

    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

# Crear el usuario administrador único si no existe
    with app.app_context():
        # Verifica si el admin ya existe
        admin_exists = User.query.filter_by(is_admin=True).first()
        if not admin_exists:
            # Si no existe, crear uno nuevo
            admin_user = User(username='adminuser', password='adminpassword', is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
         # Agregar un log para ver si se llega a crear la base de datos
        print("Creating the database tables...")
        db.create_all()
        print("Database created successfully!")
    app.run(debug=True)
