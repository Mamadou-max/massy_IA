"""
Configuration de l'application Flask.
Les variables d'environnement surchargent les valeurs par défaut.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-me'
    SNCF_API_KEY = "8c8a44bc-dde8-4e00-89cc-1d589498cb8b"
    GOOGLE_PLACES_API_KEY="AIzaSyDSSD0AZXvKFNTyxwjTmz9zUfFJ9LkzUg4"

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY') or "XkQdYjuz1FvrHeotMKOs4UvWcf4cBXiC"
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or ''

    CHROMA_HOST = os.environ.get('CHROMA_HOST') or 'localhost'
    try:
        CHROMA_PORT = int(os.environ.get('CHROMA_PORT', 8000))
    except ValueError:
        CHROMA_PORT = 8000

    N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL') or 'http://localhost:5678/webhook'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')

    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_STRATEGY = 'fixed-window'

    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    PREFERRED_URL_SCHEME = 'https'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
