"""
Configuration pytest pour les tests de l'application Massy IA.
"""

import pytest
from app import create_app, db
from backend.models import User

@pytest.fixture(scope='module')
def test_client():
    """Fixture pour le client de test Flask"""
    app = create_app('testing')  # Assurez-vous que 'testing' est un config key valide

    # Créer un client de test
    with app.test_client() as testing_client:
        # Établir un contexte d'application
        with app.app_context():
            yield testing_client

@pytest.fixture(scope='module')
def init_database(test_client):
    """Fixture pour initialiser la base de données de test"""
    # Créer toutes les tables
    db.create_all()

    # Ajouter un utilisateur de test
    test_user = User(
        email='test@massy.fr',
        first_name='Test',
        last_name='User',
        username='testuser'  # Assurez-vous que le champ username est requis
    )
    test_user.set_password('SecurePassword123!')
    db.session.add(test_user)
    db.session.commit()

    yield db  # Fournir la session de base de données pour les tests

    # Nettoyer après les tests
    db.session.remove()
    db.drop_all()

@pytest.fixture(scope='function')
def login_default_user(test_client, init_database):
    """Fixture pour connecter l'utilisateur par défaut et récupérer le token JWT"""
    response = test_client.post(
        '/api/auth/login',
        json={
            'email': 'test@massy.fr',
            'password': 'SecurePassword123!'
        }
    )
    assert response.status_code == 200, "Impossible de se connecter avec l'utilisateur de test"

    data = response.get_json()
    token = data.get('data', {}).get('access_token')
    assert token is not None, "Token JWT non récupéré"

    return token
