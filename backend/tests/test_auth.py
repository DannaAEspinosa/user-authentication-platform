import unittest
from flask import Flask
from flask_testing import TestCase
from src.models import db, User
from src.routes.auth import auth_bp
from datetime import datetime
from src.utils.jwt_utils import generate_jwt, decode_jwt  # JWT utils
from unittest.mock import patch

class TestAuthRoutes(TestCase):
    def create_app(self):
        """
        Set up the Flask application for testing.
        """
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test_secret_key'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.register_blueprint(auth_bp)
        db.init_app(app)
        return app

    def setUp(self):
        """
        Set up the test environment before each test.
        - Creates an in-memory database.
        - Adds a test user to the database with all required fields.
        """
        db.create_all()

        # Crear un usuario de prueba con el constructor adecuado
        self.user = User(
            username="testuser",
            password="Test1234!",  # Contraseña en texto plano, será manejada internamente
            is_admin=False
        )

        # Guardar el usuario en la base de datos
        db.session.add(self.user)
        db.session.commit()

        # Validar que los campos hash y salt se hayan generado correctamente
        assert self.user.password_hash is not None
        assert self.user.salt is not None


    def tearDown(self):
        """
        Clean up the test environment after each test.
        """
        db.session.remove()
        db.drop_all()

    def generate_auth_header(self, user_id):
        """
        Generate an authorization header with a valid JWT token for a user.
        """
        token = generate_jwt(user_id)
        return {'Authorization': f'Bearer {token}'}

    def test_login_success(self):
        """
        Test successful login with valid credentials.
        """
        response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)
        self.assertIn('user_id', response.json)
        self.assertTrue(response.json['success'])

    def test_login_invalid_credentials(self):
        """
        Test login failure with invalid credentials.
        """
        response = self.client.post('/login', json={'username': 'testuser', 'password': 'WrongPassword'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid credentials', response.json['message'])

    def test_change_password_success(self):
        """
        Test that a user can successfully change their password.
        """
        login_response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
        token = login_response.json['token']
        response = self.client.post('/change_password', json={'new_password': 'NewPassword123!'},
                                    headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Password changed successfully', response.json['message'])

    def test_change_password_missing_token(self):
        """
        Test that a user cannot change their password without a token.
        """
        response = self.client.post('/change_password', json={'new_password': 'NewPassword123!'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token is missing', response.json['message'])


    
    def test_get_last_login_user_not_found(self):
        """
        Test that it returns an error if the user does not exist.
        """
        invalid_token = generate_jwt(999)  # Nonexistent user ID
        response = self.client.get('/last_login', headers={'Authorization': f'Bearer {invalid_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', response.json['message'])

    def test_logout(self):
        """
        Test that a user can successfully log out.
        """
        login_response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
        token = login_response.json['token']
        response = self.client.post('/logout', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Logged out successfully', response.json['message'])

    def test_user_info(self):
        """
        Test that an authenticated user can retrieve their information.
        """
        login_response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
        token = login_response.json['token']
        response = self.client.get('/user-info', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.json)
        self.assertEqual(response.json['username'], 'testuser')
        self.assertIn('isAdmin', response.json)

    def test_user_info_invalid_token(self):
        """
        Test that it returns an error if the token is invalid.
        """
        invalid_token = 'invalid.token.here'
        response = self.client.get('/user-info', headers={'Authorization': f'Bearer {invalid_token}'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid or expired token', response.json['message'])


if __name__ == "__main__":
    unittest.main()
