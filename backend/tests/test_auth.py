import unittest
from flask import Flask, jsonify, session
from flask_testing import TestCase
from src.models import db, User
from src.routes.auth import auth_bp
from datetime import datetime
from unittest.mock import patch

class TestAuthRoutes(TestCase):
    
    def create_app(self):
        """
        Configures the Flask app for testing, including database setup and 
        registering the authentication blueprint.
        """
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'mysecretkey'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.register_blueprint(auth_bp)
        db.init_app(app)
        return app

    def setUp(self):
        """
        Sets up the test environment before each test. This creates a test user 
        and adds it to the in-memory database.
        """
        db.create_all()

        # Creates a test user
        self.user = User(username="testuser", password="Test1234!", is_admin=False)
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        """
        Cleans up the test environment after each test. This removes all data 
        from the database to ensure a fresh start for the next test.
        """
        db.session.remove()
        db.drop_all()

    def test_login_success(self):
        """
        Tests a successful login with valid credentials.
        """
        # Simulate a successful login with correct credentials
        response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
        
        # Verifies that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Verifies that 'user_id' is included in the response JSON
        self.assertIn('user_id', response.json)
        
        # Compares the 'user_id' from the response to the expected 'user.id'
        self.assertEqual(response.json['user_id'], self.user.id)

    def test_login_user_already_logged_in(self):
        """
        Tests that a user cannot log in if they are already logged in.
        """
        with self.client:
            self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            response = self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            self.assert400(response)  # Verifies a bad request status code
            self.assertIn('A user is already logged in', response.json['message'])

    def test_login_invalid_credentials(self):
        """
        Tests that login fails when invalid credentials are provided.
        """
        response = self.client.post('/login', json={'username': 'testuser', 'password': 'WrongPassword'})
        self.assert401(response)  # Verifies an unauthorized status code
        self.assertIn('Invalid credentials or empty password', response.json['message'])

    def test_change_password_success(self):
        """
        Tests that password change is successful when the user is logged in.
        """
        with self.client:
            self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            response = self.client.post('/change_password', json={'new_password': 'NewPassword123!'})
            self.assert200(response)  # Verifies a successful response status code
            self.assertIn('Password changed successfully', response.json['message'])
        
            # Verifies that the password has been updated
            user = User.query.get(self.user.id)
            self.assertTrue(user.check_password('NewPassword123!'))

    def test_change_password_not_logged_in(self):
        """
        Tests that the password cannot be changed if no user is logged in.
        """
        response = self.client.post('/change_password', json={'new_password': 'NewPassword123!'})
        self.assert401(response)  # Verifies an unauthorized status code
        self.assertIn('Unauthorized', response.json['message'])

    def test_get_last_login_success(self):
        """
        Tests that the last login time is returned correctly when the user is logged in.
        """
        with self.client:
            self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            response = self.client.get('/last_login')
            self.assert200(response)  # Verifies a successful response status code
            
            # Verifies that 'last_login' is included in the response JSON
            self.assertIn('last_login', response.json)
            
            # Ensures that 'last_login' is a string
            response_datetime_str = response.json['last_login']
            self.assertIsInstance(response_datetime_str, str)
            
            # Converts the response datetime string to a datetime object
            response_datetime = datetime.strptime(response_datetime_str, '%a, %d %b %Y %H:%M:%S GMT')
            
            # Removes microseconds from both the response and user datetime
            response_datetime = response_datetime.replace(microsecond=0)
            self.user.last_login = self.user.last_login.replace(microsecond=0)
            
            # Compares the datetime values
            self.assertEqual(response_datetime, self.user.last_login)

    def test_get_last_login_not_logged_in(self):
        """
        Tests that the last login time cannot be retrieved if no user is logged in.
        """
        response = self.client.get('/last_login')
        self.assert401(response)  # Verifies an unauthorized status code
        self.assertIn('Unauthorized', response.json['message'])

    def test_logout_success(self):
        """
        Tests a successful logout.
        """
        with self.client:
            self.client.post('/login', json={'username': 'testuser', 'password': 'Test1234!'})
            response = self.client.post('/logout')
            self.assert200(response)  # Verifies a successful response status code
            self.assertIn('Logged out successfully', response.json['message'])
            self.assertIsNone(session.get('user_id'))  # Verifies that the session is cleared

    def test_logout_not_logged_in(self):
        """
        Tests that a user cannot log out if they are not logged in.
        """
        response = self.client.post('/logout')
        self.assert401(response)  # Verifies an unauthorized status code
        self.assertIn('Unauthorized', response.json['message'])

if __name__ == '__main__':
    unittest.main()
