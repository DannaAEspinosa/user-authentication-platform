import unittest
from flask import Flask, jsonify, session
from flask_testing import TestCase
from src.models import db, User
from src.routes.admin import admin_bp  # Asegúrate de tener el blueprint de admin correctamente importado
from datetime import datetime
from unittest.mock import patch

class TestAdminRoutes(TestCase):
    
    def create_app(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'mysecretkey'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.register_blueprint(admin_bp, url_prefix='/admin')
        db.init_app(app)
        return app

    def setUp(self):
        """
        Configura el entorno de prueba (se ejecuta antes de cada prueba).
        """
        db.create_all()

        # Crea un usuario de prueba con privilegios de admin
        user = User(username='admin', password='password', is_admin=True)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        """
        Limpia la base de datos después de cada prueba.
        """
        db.session.remove()
        db.drop_all()
        
    def test_get_all_users(self):
        with self.client:
            # Simular el inicio de sesión con un usuario admin
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Usuario con ID 1 (admin)

            response = self.client.get('/admin/users')  # Ruta protegida por admin_required
            self.assert200(response)  # Debería tener acceso como admin

    def test_register_user(self):
        with self.client:
            # Simular el inicio de sesión con un usuario admin
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Usuario con ID 1 (admin)

            # Datos de prueba para el registro
            data = {
                'username': 'new_user',
                'password': 'Password1!',
                'is_admin': False
            }

            response = self.client.post('/admin/register', json=data)
            self.assertStatus(response, 201)  # Verificar que la respuesta sea 201 (creado)

            # Verificar si el nuevo usuario fue creado en la base de datos
            new_user = User.query.filter_by(username='new_user').first()
            self.assertIsNotNone(new_user)
            self.assertEqual(new_user.username, 'new_user')
        
    def test_change_password(self):
        with self.client:
            # Simular el inicio de sesión con un usuario admin
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Usuario con ID 1 (admin)

            # Crear un usuario para cambiarle la contraseña
            user = User(username='test_user', password='OldPassword1!', is_admin=False)
            db.session.add(user)
            db.session.commit()

            # Datos de prueba para el cambio de contraseña
            data = {'new_password': 'NewPassword1!'}

            response = self.client.post(f'/admin/change_password/{user.id}', json=data)
            self.assertStatus(response, 200)  # Verificar que la respuesta sea 200 (OK)

            # Verificar que la contraseña fue cambiada (espero que el hash de la contraseña haya cambiado)
            user = User.query.get(user.id)
            self.assertNotEqual(user.password_hash, 'OldPassword1!')

    def test_reset_password(self):
        with self.client:
            # Simular el inicio de sesión con un usuario admin
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Usuario con ID 1 (admin)

            # Crear un usuario para resetear su contraseña
            user = User(username='test_user', password='OldPassword1!', is_admin=False)
            db.session.add(user)
            db.session.commit()

            response = self.client.post(f'/admin/reset_password/{user.id}')
            self.assertStatus(response, 200)  # Verificar que la respuesta sea 200 (OK)

            # Obtener el usuario actualizado de la base de datos
            user = User.query.get(user.id)

            # Generar el hash esperado para una contraseña vacía
            expected_password_hash, _ = user.hash_password("")  # Generar el hash vacío

            # Comparar el hash actual con el esperado
            self.assertEqual(user.password_hash, expected_password_hash)

    def test_delete_user(self):
        with self.client:
            # Simular el inicio de sesión con un usuario admin
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Usuario con ID 1 (admin)

            # Crear un usuario para eliminar
            user = User(username='user_to_delete', password='Password1!', is_admin=False)
            db.session.add(user)
            db.session.commit()

            response = self.client.delete(f'/admin/delete_user/{user.id}')
            self.assertStatus(response, 200)  # Verificar que la respuesta sea 200 (OK)

            # Verificar que el usuario fue eliminado
            deleted_user = User.query.get(user.id)
            self.assertIsNone(deleted_user)

    def test_reset_password_user_not_found(self):
        """
        Prueba negativa: Intentar resetear la contraseña de un usuario inexistente.
        """
        with self.client:
            # Simular el inicio de sesión como admin
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Usuario admin con ID 1

            # Intentar resetear contraseña de un usuario con ID inválido
            response = self.client.post('/admin/reset_password/999')  # ID 999 no existe
            self.assert404(response)  # Espera un 404 Not Found
            self.assertEqual(response.json['message'], 'User not found')

    def test_reset_password_without_admin(self):
        """
        Prueba negativa: Un usuario no administrador intenta resetear la contraseña.
        """
        with self.client:
            # Simular el inicio de sesión con un usuario normal
            with self.client.session_transaction() as sess:
                sess['user_id'] = 2  # Usuario normal con ID 2

            # Intentar resetear contraseña de un usuario
            response = self.client.post('/admin/reset_password/2')  # Intento no autorizado
            self.assert403(response)  # Espera un 403 Forbidden
            self.assertEqual(response.json['message'], 'Forbidden: Admin access required')

    def test_reset_password_without_login(self):
        """
        Prueba negativa: Intentar resetear la contraseña sin estar autenticado.
        """
        with self.client:
            # No iniciar sesión
            response = self.client.post('/admin/reset_password/1')  # Intentar acceder sin sesión
            self.assert401(response)  # Espera un 401 Unauthorized
            self.assertEqual(response.json['message'], 'Unauthorized')

    def test_reset_password_invalid_method(self):
        """
        Prueba negativa: Usar un método HTTP no permitido en la ruta.
        """
        with self.client:
            # Simular el inicio de sesión como admin
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Usuario admin con ID 1

            # Intentar hacer una solicitud GET en lugar de POST
            response = self.client.get('/admin/reset_password/1')
            self.assert405(response)  # Espera un 405 Method Not Allowed

    def test_reset_password_missing_user_id(self):
        """
        Prueba negativa: Intentar acceder a la ruta sin proporcionar un ID de usuario.
        """
        with self.client:
            # Simular el inicio de sesión como admin
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1  # Usuario admin con ID 1

            # Intentar acceder sin ID en la URL
            response = self.client.post('/admin/reset_password/')
            self.assert404(response)  # Espera un 404 Not Found
if __name__ == '__main__':
    unittest.main()
