import unittest
from flask import Flask, jsonify, session
from flask_testing import TestCase
from src.models import db, User
from src.routes.admin import admin_bp  # Ensure the admin blueprint is correctly imported
from datetime import datetime
from unittest.mock import patch

class TestAdminRoutes(TestCase):
    
    def create_app(self):
        """
        This method sets up the Flask app and configures it for testing.
        It creates an in-memory SQLite database for testing purposes.
        The admin blueprint is registered under the '/admin' URL prefix.
        """
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'mysecretkey'  # Secret key for session management
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory SQLite database for testing
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
        app.register_blueprint(admin_bp, url_prefix='/admin')  # Register the admin blueprint
        db.init_app(app)  # Initialize the database with the app
        return app

    def setUp(self):
        """
        This method runs before each test.
        It initializes the database and creates a test user with admin privileges.
        """
        db.create_all()

        # Create a test admin user
        user = User(username='admin', password='password', is_admin=True)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        """
        This method runs after each test.
        It cleans up the database by removing all data and closing the session.
        """
        db.session.remove()
        db.drop_all()

    def test_get_all_users(self):
        """
        This test simulates a successful request to get all users by an admin user.
        It checks if the route '/admin/users' is accessible by an admin.
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Simulate an admin user with ID 1

            response = self.client.get('/admin/users')  # Access the protected admin route
            self.assert200(response)  # Should return 200 OK status

    def test_register_user(self):
        """
        This test simulates the registration of a new user by an admin.
        It checks if the new user is correctly added to the database.
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Simulate an admin user with ID 1

            data = {
                'username': 'new_user',
                'password': 'Password1!',
                'is_admin': False
            }

            response = self.client.post('/admin/register', json=data)  # Send a POST request to register a new user
            self.assertStatus(response, 201)  # Should return status 201 (Created)

            # Verify the new user was added to the database
            new_user = User.query.filter_by(username='new_user').first()
            self.assertIsNotNone(new_user)
            self.assertEqual(new_user.username, 'new_user')

    def test_change_password(self):
        """
        This test simulates changing the password of a user by an admin.
        It checks if the password update is successful and the password hash changes.
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Simulate an admin user with ID 1

            user = User(username='test_user', password='OldPassword1!', is_admin=False)
            db.session.add(user)
            db.session.commit()

            data = {'new_password': 'NewPassword1!'}  # New password data

            response = self.client.post(f'/admin/change_password/{user.id}', json=data)  # Request to change the password
            self.assertStatus(response, 200)  # Should return status 200 (OK)

            # Verify that the password hash has changed
            user = User.query.get(user.id)
            self.assertNotEqual(user.password_hash, 'OldPassword1!')

    def test_reset_password(self):
        """
        This test simulates resetting the password of a user by an admin.
        It checks if the password is reset to an empty string and the hash is correctly generated.
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Simulate an admin user with ID 1

            user = User(username='test_user', password='OldPassword1!', is_admin=False)
            db.session.add(user)
            db.session.commit()

            response = self.client.post(f'/admin/reset_password/{user.id}')  # Request to reset the password
            self.assertStatus(response, 200)  # Should return status 200 (OK)

            # Verify the password hash has been reset
            user = User.query.get(user.id)
            expected_password_hash, _ = user.hash_password("")  # Expected hash for an empty password
            self.assertEqual(user.password_hash, expected_password_hash)

    def test_delete_user(self):
        """
        This test simulates deleting a user by an admin.
        It checks if the user is successfully removed from the database.
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Simulate an admin user with ID 1

            user = User(username='user_to_delete', password='Password1!', is_admin=False)
            db.session.add(user)
            db.session.commit()

            response = self.client.delete(f'/admin/delete_user/{user.id}')  # Request to delete the user
            self.assertStatus(response, 200)  # Should return status 200 (OK)

            # Verify the user was deleted
            deleted_user = User.query.get(user.id)
            self.assertIsNone(deleted_user)

    def test_reset_password_user_not_found(self):
        """
        Negative test: Attempt to reset the password of a non-existent user.
        It checks if a 404 Not Found error is returned.
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Simulate an admin user with ID 1

            response = self.client.post('/admin/reset_password/999')  # User with ID 999 does not exist
            self.assert404(response)  # Should return status 404 (Not Found)
            self.assertEqual(response.json['message'], 'User not found')

    def test_reset_password_without_admin(self):
        """
        Negative test: A non-admin user attempts to reset the password of another user.
        It checks if a 403 Forbidden error is returned.
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 2  # Simulate a normal user with ID 2

            response = self.client.post('/admin/reset_password/2')  # Unauthorized password reset attempt
            self.assert403(response)  # Should return status 403 (Forbidden)
            self.assertEqual(response.json['message'], 'Forbidden: Admin access required')

    def test_reset_password_without_login(self):
        """
        Negative test: Attempt to reset the password without being authenticated.
        It checks if a 401 Unauthorized error is returned.
        """
        with self.client:
            response = self.client.post('/admin/reset_password/1')  # Attempt to access without login
            self.assert401(response)  # Should return status 401 (Unauthorized)
            self.assertEqual(response.json['message'], 'Unauthorized')

    def test_reset_password_invalid_method(self):
        """
        Negative test: Attempt to use an invalid HTTP method (GET instead of POST).
        It checks if a 405 Method Not Allowed error is returned.
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Simulate an admin user with ID 1

            response = self.client.get('/admin/reset_password/1')  # Invalid method (GET)
            self.assert405(response)  # Should return status 405 (Method Not Allowed)

    def test_reset_password_missing_user_id(self):
        """
        Negative test: Attempt to reset the password without providing a user ID.
        It checks if a 404 Not Found error is returned.
        """
        with self.client:
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Simulate an admin user with ID 1

            response = self.client.post('/admin/reset_password/')  # Missing user ID in the URL
            self.assert404(response)  # Should return status 404 (Not Found)

if __name__ == '__main__':
    unittest.main()
