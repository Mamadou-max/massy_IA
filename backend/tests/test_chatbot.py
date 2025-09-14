"""
Tests unitaires et d'intégration pour les routes du chatbot.
"""

import unittest
import json
from unittest.mock import patch
from app import create_app, db
from backend.models import User, Conversation


class ChatbotTestCase(unittest.TestCase):
    """Test case pour les routes du chatbot"""

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

        # Enregistrer et connecter l'utilisateur
        response = self.register_user()
        data = response.get_json()
        self.access_token = data['data']['access_token']
        self.user_id = data['data']['user']['id']

    def tearDown(self):
        """Nettoyage après chaque test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --- Helpers ---
    def register_user(self, user_data=None):
        if user_data is None:
            user_data = self.test_user
        return self.client.post(
            '/api/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )

    def login_user(self, email=None, password=None):
        if email is None:
            email = self.test_user['email']
        if password is None:
            password = self.test_user['password']
        return self.client.post(
            '/api/auth/login',
            data=json.dumps({'email': email, 'password': password}),
            content_type='application/json'
        )

    # --- Tests ---
    @patch('app.routes.chatbot.ai_service.generate_election_response')
    @patch('app.routes.chatbot.chroma_service.get_relevant_context')
    @patch('app.routes.chatbot.n8n_service.trigger_election_workflow')
    def test_chat_endpoint(self, mock_n8n, mock_context, mock_ai_response):
        """Test l'endpoint de chat du chatbot"""
        mock_context.return_value = "Contexte pertinent sur les élections"
        mock_ai_response.return_value = "Réponse générée par l'IA"
        mock_n8n.return_value = True

        chat_data = {'message': 'Où sont les bureaux de vote ?'}
        response = self.client.post(
            '/api/chatbot/chat',
            data=json.dumps(chat_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['response'], "Réponse générée par l'IA")

        mock_context.assert_called_once_with(chat_data['message'])
        mock_ai_response.assert_called_once_with(chat_data['message'], "Contexte pertinent sur les élections")
        mock_n8n.assert_called_once()

    def test_chat_endpoint_without_message(self):
        """Test l'endpoint de chat sans message"""
        response = self.client.post(
            '/api/chatbot/chat',
            data=json.dumps({}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'error')
        self.assertIn('message requis', data['message'].lower())

    def test_chat_endpoint_without_authentication(self):
        """Test l'endpoint de chat sans authentification"""
        chat_data = {'message': 'Où sont les bureaux de vote ?'}
        response = self.client.post(
            '/api/chatbot/chat',
            data=json.dumps(chat_data),
            content_type='application/json'
        )
        data = response.get_json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['status'], 'error')
        self.assertIn('token', data['message'].lower())

    @patch('app.routes.chatbot.ai_service.generate_election_response')
    @patch('app.routes.chatbot.chroma_service.get_relevant_context')
    def test_chat_creates_conversation(self, mock_context, mock_ai_response):
        """Vérifie que l'endpoint crée une conversation"""
        mock_context.return_value = "Contexte pertinent sur les élections"
        mock_ai_response.return_value = "Réponse générée par l'IA"

        self.assertEqual(Conversation.query.filter_by(user_id=self.user_id).count(), 0)

        chat_data = {'message': 'Où sont les bureaux de vote ?'}
        response = self.client.post(
            '/api/chatbot/chat',
            data=json.dumps(chat_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        data = response.get_json()
        self.assertEqual(response.status_code, 200)

        conv = Conversation.query.filter_by(user_id=self.user_id).first()
        self.assertIsNotNone(conv)
        self.assertIn(chat_data['message'], conv.title)
        messages = conv.get_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'user')
        self.assertEqual(messages[0]['content'], chat_data['message'])
        self.assertEqual(messages[1]['role'], 'assistant')
        self.assertEqual(messages[1]['content'], "Réponse générée par l'IA")

    def test_get_conversations(self):
        """Récupération des conversations de l'utilisateur"""
        # Créer 2 conversations
        for i in range(2):
            conv = Conversation(
                user_id=self.user_id,
                title=f"Test conversation {i+1}",
                messages=[{"role": "user", "content": f"Message {i+1}", "timestamp": "2023-01-01T00:00:00"}]
            )
            db.session.add(conv)
        db.session.commit()

        response = self.client.get(
            '/api/chatbot/conversations',
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['data']['conversations']), 2)
        self.assertEqual(data['data']['conversations'][0]['title'], "Test conversation 2")  # plus récent

    # Autres tests: get specific conversation, delete, etc.
    # On peut ajouter les tests pour conversation inexistante ou autre utilisateur ici

if __name__ == '__main__':
    unittest.main()
