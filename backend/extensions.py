"""
Extensions Flask utilisées dans l'application.
Centralisé pour éviter les imports circulaires et garantir l'initialisation correcte.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Création des instances des extensions (non attachées à l'application)
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def init_extensions(app):
    """
    Initialise toutes les extensions avec l'application Flask.
    À appeler depuis create_app() dans app/__init__.py.
    """
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
