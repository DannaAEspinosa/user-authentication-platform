import unittest
from flask import Flask, jsonify, session
from flask_testing import TestCase
from src.models import db, User
from src.routes.auth import auth_bp
from datetime import datetime
from unittest.mock import patch

class TestAuthRoutes(TestCase):
    
    def create_app(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'mysecretkey'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.register_blueprint(auth_bp)
        db.init_app(app)
        return app

    def setUp(self):
        """
        Configura el entorno de prueba (se ejecuta antes de cada prueba).
        """
        db.create_all()

        # Crea un usuario de prueba
        self.user = User(username="testuser", password="Test1234!", is_admin=False)
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        """
        Limpia la base de datos después de cada prueba.
        """
        db.session.remove()
        db.drop_all()

    def test_login_success(self):
        """
        Prueba que el login sea exitoso.
        """
        # Simula un inicio de sesión exitoso con las credenciales correctas
        response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
        
        # Verifica que la respuesta sea exitosa (200)
        self.assertEqual(response.status_code, 200)
        
        # Verifica que el 'user_id' esté presente en la respuesta JSON
        self.assertIn('user_id', response.json)
        
        # Compara que el 'user_id' en la respuesta sea igual al 'user.id' esperado
        self.assertEqual(response.json['user_id'], self.user.id)

    def test_login_user_already_logged_in(self):
        """
        Prueba que no se permita logearse si ya hay un usuario en la sesión.
        """
        with self.client:
            self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            self.assert400(response)
            self.assertIn('A user is already logged in', response.json['message'])

    def test_login_invalid_credentials(self):
        """
        Prueba que el login falle con credenciales incorrectas.
        """
        response = self.client.post('/login', json={'username': 'testuser', 'password': 'WrongPassword'})
        self.assert401(response)
        self.assertIn('Invalid credentials or empty password', response.json['message'])

    def test_change_password_success(self):
        """
        Prueba que el cambio de contraseña sea exitoso.
        """
        with self.client:
            self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            response = self.client.post('/change_password', json={'new_password': 'NewPassword123!'})
            self.assert200(response)
            self.assertIn('Password changed successfully', response.json['message'])
        
            # Verificar que la contraseña ha sido actualizada
            user = User.query.get(self.user.id)
            self.assertTrue(user.check_password('NewPassword123!'))

    def test_change_password_not_logged_in(self):
        """
        Prueba que no se pueda cambiar la contraseña si no hay un usuario logueado.
        """
        response = self.client.post('/change_password', json={'new_password': 'NewPassword123!'})
        self.assert401(response)
        self.assertIn('Unauthorized', response.json['message'])

    def test_get_last_login_success(self):
        """
        Prueba que se pueda obtener la última fecha de login correctamente.
        """
        with self.client:
            self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            response = self.client.get('/last_login')
            self.assert200(response)
            
            # Verifica que la respuesta tenga la clave 'last_login'
            self.assertIn('last_login', response.json)
            
            # Asegúrate de que el formato de 'last_login' es correcto
            response_datetime_str = response.json['last_login']
            self.assertIsInstance(response_datetime_str, str)
            
            # Convierte la fecha de la respuesta a datetime
            response_datetime = datetime.strptime(response_datetime_str, '%a, %d %b %Y %H:%M:%S GMT')
            
            # Elimina los microsegundos de ambas fechas
            response_datetime = response_datetime.replace(microsecond=0)
            self.user.last_login = self.user.last_login.replace(microsecond=0)
            
            # Compara las fechas
            self.assertEqual(response_datetime, self.user.last_login)

    def test_get_last_login_not_logged_in(self):
        """
        Prueba que no se pueda obtener la última fecha de login si no hay un usuario logueado.
        """
        response = self.client.get('/last_login')
        self.assert401(response)
        self.assertIn('Unauthorized', response.json['message'])

    def test_logout_success(self):
        """
        Prueba que el logout sea exitoso.
        """
        with self.client:
            self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            response = self.client.post('/logout')
            self.assert200(response)
            self.assertIn('Logged out successfully', response.json['message'])
            self.assertIsNone(session.get('user_id'))

    def test_logout_not_logged_in(self):
        """
        Prueba que no se pueda hacer logout si no hay un usuario logueado.
        """
        response = self.client.post('/logout')
        self.assert401(response)
        self.assertIn('Unauthorized', response.json['message'])

if __name__ == '__main__':
    unittest.main()
