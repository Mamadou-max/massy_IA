"""
Package de tests pour l'application Massy IA.
"""

import os
import tempfile
import pytest
from app import create_app, db
from backend.models import User, Conversation

# Cette ligne permet à pytest de découvrir les tests
pytest_plugins = ['app.tests.test_auth', 'app.tests.test_chatbot']