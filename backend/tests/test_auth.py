"""
Tests unitaires et d'intégration pour les routes d'authentification.
"""

import unittest
import json
from app import create_app, db
from backend.models import User


class AuthTestCase(unittest.TestCase):
    """Test case pour les routes d'authentification"""

    def setUp(self):
        """Configuration initiale avant chaque test"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Utilisateur de test
        self.test_user = {
            'email': 'test@massy.fr',
            'password': 'SecurePassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def tearDown(self):
        """Nettoyage après chaque test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register_user(self, user_data=None):
        """Helper pour enregistrer un utilisateur"""
        if user_data is None:
            user_data = self.test_user
        return self.client.post(
            '/api/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )

    def login_user(self, email=None, password=None):
        """Helper pour connecter un utilisateur"""
        if email is None:
            email = self.test_user['email']
        if password is None:
            password = self.test_user['password']
        return self.client.post(
            '/api/auth/login',
            data=json.dumps({'email': email, 'password': password}),
            content_type='application/json'
        )

    def test_user_registration_success(self):
        """Test l'enregistrement d'un nouvel utilisateur"""
        response = self.register_user()
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], 'success')
        self.assertIn('access_token', data['data'])
        self.assertIn('refresh_token', data['data'])
        self.assertIn('user', data['data'])
        self.assertEqual(data['data']['user']['email'], self.test_user['email'])

    def test_user_registration_existing_email(self):
        """Test l'enregistrement avec un email déjà existant"""
        self.register_user()
        response = self.register_user()
        data = response.get_json()

        self.assertEqual(response.status_code, 409)
        self.assertEqual(data['status'], 'error')
        self.assertIn('existe déjà', data['message'])

    def test_user_registration_invalid_email(self):
        """Test l'enregistrement avec un email invalide"""
        invalid_user = self.test_user.copy()
        invalid_user['email'] = 'invalid-email'
        response = self.register_user(invalid_user)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'error')
        self.assertIn('email', data['message'].lower())

    def test_user_registration_weak_password(self):
        """Test l'enregistrement avec un mot de passe faible"""
        weak_user = self.test_user.copy()
        weak_user['password'] = '123'
        response = self.register_user(weak_user)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'error')
        self.assertIn('mot de passe', data['message'].lower())

    def test_user_login_success(self):
        """Test la connexion d'un utilisateur existant"""
        self.register_user()
        response = self.login_user()
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn('access_token', data['data'])
        self.assertIn('refresh_token', data['data'])
        self.assertIn('user', data['data'])

    def test_user_login_wrong_password(self):
        """Test la connexion avec un mauvais mot de passe"""
        self.register_user()
        response = self.login_user(password='WrongPassword123!')
        data = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['status'], 'error')
        self.assertIn('email ou mot de passe', data['message'].lower())

    def test_user_login_nonexistent_email(self):
        """Test la connexion avec un email inexistant"""
        response = self.login_user(email='nonexistent@massy.fr')
        data = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['status'], 'error')
        self.assertIn('email ou mot de passe', data['message'].lower())

    def test_token_refresh(self):
        """Test le rafraîchissement du token d'accès"""
        self.register_user()
        login_resp = self.login_user().get_json()
        refresh_token = login_resp['data']['refresh_token']

        response = self.client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn('access_token', data['data'])

    def test_protected_route_with_valid_token(self):
        """Test l'accès à une route protégée avec token valide"""
        self.register_user()
        login_resp = self.login_user().get_json()
        access_token = login_resp['data']['access_token']

        response = self.client.get(
            '/api/auth/profile',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn('user', data['data'])

    def test_protected_route_without_token(self):
        """Test l'accès à une route protégée sans token"""
        response = self.client.get('/api/auth/profile')
        data = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['status'], 'error')
        self.assertIn('token', data['message'].lower())

    def test_protected_route_invalid_token(self):
        """Test l'accès à une route protégée avec token invalide"""
        response = self.client.get(
            '/api/auth/profile',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['status'], 'error')
        self.assertIn('token', data['message'].lower())


if __name__ == '__main__':
    unittest.main()
