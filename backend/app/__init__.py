"""
Factory pour créer et configurer l'application Flask.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
from datetime import datetime
from backend.scripts.auto_sync import auto_sync_all, start_scheduler 

# Imports absolus depuis backend
from backend.extensions import db, jwt, migrate

def create_app(config_class):
    """Crée et configure l'application Flask."""

    # Création de l'application
    app = Flask(__name__)
    app.config.from_object(config_class)
    auto_sync_all()  # Lance immédiatement une première synchro
    start_scheduler(app)  # 
    
    app.jinja_env.globals['datetime'] = datetime

    # Initialisation des extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Configuration CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', "*"))

    # Correction : JWT identity loader
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """
        Si on passe user.id à create_access_token(identity=...),
        alors 'user' est déjà un ID (str/int), donc on le renvoie tel quel.
        """
        return str(user)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Récupère l'objet User complet à partir de l'ID stocké dans le JWT.
        """
        from backend.models.user import User
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    # Enregistrement des blueprints
    try:
        from backend.routes.auth import auth_bp 
        from backend.routes.frontend import frontend_bp
        from backend.routes.dashboard import dashboard_bp
        from backend.routes.transport import transport_bp
        from backend.routes.shops import shops_bp
        from backend.routes.police import police_bp
        from backend.routes.university import university_bp
        from backend.routes.chatbot import chatbot_bp
        from backend.routes.media import media_bp
        from backend.routes.news import news_bp
        

        

        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(frontend_bp)
        app.register_blueprint(dashboard_bp, url_prefix='/api/massy')
        app.register_blueprint(transport_bp, url_prefix='/api/transport')
        app.register_blueprint(shops_bp, url_prefix='/api/shops')
        app.register_blueprint(police_bp, url_prefix='/api/police')
        app.register_blueprint(university_bp, url_prefix='/api/university')
        app.register_blueprint(chatbot_bp , url_prefix='/api/chatbot')
        app.register_blueprint(media_bp , url_prefix='/api/media')
        app.register_blueprint(news_bp , url_prefix='/api/news')

    except Exception as e:
        app.logger.error(f"Erreur lors du chargement des blueprints: {str(e)}")
        raise

    # Logging
    if not app.debug and not app.testing:
        try:
            logs_path = os.path.join(os.getcwd(), 'logs')
            os.makedirs(logs_path, exist_ok=True)
            file_handler = RotatingFileHandler(
                os.path.join(logs_path, 'massy_ia.log'),
                maxBytes=10240,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Massy IA Platform startup')
        except Exception as e:
            app.logger.error(f"Erreur lors de la configuration du logging: {str(e)}")

    # Gestion des erreurs HTTP globales
    @app.errorhandler(404)
    def page_not_found(e):
        return {"success": False, "message": "Ressource non trouvée", "status": 404}, 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return {"success": False, "message": "Erreur interne du serveur", "status": 500}, 500

    return app
