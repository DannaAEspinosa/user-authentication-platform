import unittest
from flask import Flask, jsonify
from flask_testing import TestCase
from src.models import db, User
from src.routes.auth import auth_bp
from datetime import datetime
from unittest.mock import patch
from src.utils.jwt_utils import generate_jwt

class TestAuthRoutes(TestCase):

    def create_app(self):
        """
        Configura la aplicación Flask para las pruebas, incluyendo la configuración de la base de datos 
        y el registro del blueprint de autenticación.
        """
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'mysecretkey'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria para pruebas
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.register_blueprint(auth_bp)
        db.init_app(app)
        return app

    def setUp(self):
        """
        Configura el entorno de prueba antes de cada prueba. Crea un usuario de prueba 
        y lo agrega a la base de datos en memoria.
        """
        db.create_all()

        # Crea un usuario de prueba
        self.user = User(username="testuser", password="Test1234!", is_admin=False)
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        """
        Limpia el entorno de prueba después de cada prueba. Elimina todos los datos 
        de la base de datos para asegurar un inicio limpio para la siguiente prueba.
        """
        db.session.remove()
        db.drop_all()

    def test_login_success(self):
        """
        Prueba que el login es exitoso con credenciales válidas.
        """
        response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
        self.assertEqual(response.status_code, 200)
        
        # Verifica si la respuesta contiene un token
        self.assertIn('token', response.json)
        
        token = response.json['token']
        
        # Verifica si el token es un JWT válido
        self.assertIsInstance(token, str)
        
        # Simula una solicitud autenticada usando el token
        response = self.client.get('/user-info', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        
        # Verifica que el nombre de usuario se devuelve en la respuesta
        self.assertIn('username', response.json)
        self.assertEqual(response.json['username'], 'testuser')

    def test_login_user_already_logged_in(self):
        """
        Prueba que un usuario no puede hacer login si ya está autenticado.
        """
        with self.client:
            # Realiza el login y obtiene el token
            login_response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            token = login_response.json['token']
            
            # Intenta hacer login nuevamente con el mismo usuario
            response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            self.assertEqual(response.status_code, 400)
            self.assertIn('A user is already logged in', response.json['message'])

    def test_login_invalid_credentials(self):
        """
        Prueba que el login falla cuando se proporcionan credenciales inválidas.
        """
        response = self.client.post('/login', json={'username': 'testuser', 'password': 'WrongPassword'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid credentials or empty password', response.json['message'])

    def test_change_password_success(self):
        """
        Prueba que el cambio de contraseña es exitoso cuando el usuario está autenticado.
        """
        with self.client:
            # Inicia sesión y obtiene el token
            login_response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            token = login_response.json['token']
            
            # Cambia la contraseña
            response = self.client.post('/change_password', json={'new_password': 'NewPassword123!'},
                                        headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('Password changed successfully', response.json['message'])
        
            # Verifica que la nueva contraseña sea correcta
            user = User.query.get(self.user.id)
            self.assertTrue(user.check_password('NewPassword123!'))

    def test_change_password_not_logged_in(self):
        """
        Prueba que la contraseña no se puede cambiar si el usuario no está autenticado.
        """
        response = self.client.post('/change_password', json={'new_password': 'NewPassword123!'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['message'])

    def test_get_last_login_success(self):
        """
        Prueba que la última hora de login se devuelve correctamente cuando el usuario está autenticado.
        """
        with self.client:
            login_response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            token = login_response.json['token']
            
            response = self.client.get('/last_login', headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            
            self.assertIn('last_login', response.json)
            
            # Compara la fecha y hora devueltas por la API con la última fecha de login en la base de datos
            response_datetime_str = response.json['last_login']
            self.assertIsInstance(response_datetime_str, str)
            
            response_datetime = datetime.strptime(response_datetime_str, '%Y-%m-%d %H:%M:%S')
            self.user.last_login = self.user.last_login.replace(microsecond=0)
            self.assertEqual(response_datetime, self.user.last_login)

    def test_get_last_login_not_logged_in(self):
        """
        Prueba que no se puede obtener la última hora de login si el usuario no está autenticado.
        """
        response = self.client.get('/last_login')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['message'])

    def test_logout_success(self):
        """
        Prueba que el logout es exitoso.
        """
        with self.client:
            login_response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            token = login_response.json['token']
            
            response = self.client.post('/logout', headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('Logged out successfully', response.json['message'])

    def test_logout_not_logged_in(self):
        """
        Prueba que un usuario no puede hacer logout si no está autenticado.
        """
        response = self.client.post('/logout')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['message'])

if __name__ == '__main__':
    unittest.main()
