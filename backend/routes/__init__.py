"""
Initialisation des blueprints pour l'application Flask.
Permet d'importer directement les blueprints depuis backend.routes
sans provoquer de boucles d'import.
"""

# ⚡ Importer les blueprints depuis leurs modules respectifs
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


# Liste des blueprints exportés pour les imports directs
__all__ = ["auth_bp", "frontend_bp", "dashboard_bp", "transport_bp", "shops_bp", "police_bp", "university_bp", "chatbot_bp", "media_bp", "news_bp"]
