"""
Routes frontend pour l'application Massy IA.
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User
from backend.models.conversation import Message as ChatMessage
from backend.extensions import db
import os

# Chemin vers le dossier templates à partir du dossier backend/
template_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

frontend_bp = Blueprint('frontend', __name__, template_folder=template_folder)

# ------------------------------
# Filtres Jinja2 personnalisés
# ------------------------------
@frontend_bp.app_template_filter('format_datetime')
def format_datetime(value, format='%d/%m/%Y %H:%M'):
    if not value:
        return "Date inconnue"
    return value.strftime(format)

@frontend_bp.app_template_filter('time_ago')
def time_ago(value):
    if not value:
        return "Jamais"
    current_datetime = datetime.utcnow()  # utilisation now
    diff = current_datetime - value

    if diff.days > 365:
        return f"il y a {diff.days // 365} an{'s' if diff.days // 365 > 1 else ''}"
    elif diff.days > 30:
        return f"il y a {diff.days // 30} mois"
    elif diff.days > 0:
        return f"il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
    elif diff.seconds > 3600:
        return f"il y a {diff.seconds // 3600} heure{'s' if diff.seconds // 3600 > 1 else ''}"
    elif diff.seconds > 60:
        return f"il y a {diff.seconds // 60} minute{'s' if diff.seconds // 60 > 1 else ''}"
    else:
        return "à l'instant"

# ------------------------------
# Injecter des utilitaires dans tous les templates
# ------------------------------
@frontend_bp.context_processor
def inject_utils():
    return {
        'datetime': datetime,       # pour utilisation dans les templates
        'timedelta': timedelta,
        'now': datetime.utcnow(),   # timestamp actuel en UTC
        'current_year': datetime.utcnow().year
    }

# ------------------------------
# Page d'accueil / dashboard
# ------------------------------
@frontend_bp.route('/')
@frontend_bp.route('/<string:tab>')
@jwt_required(optional=True)
def index(tab='dashboard'):
    current_user = None
    if get_jwt_identity():
        current_user = User.query.get(get_jwt_identity())

    # Récupération des 10 derniers messages de l'utilisateur si connecté
    chat_messages = []
    if current_user:
        chat_messages = ChatMessage.query.filter_by(user_id=current_user.id)\
                                         .order_by(ChatMessage.timestamp.desc())\
                                         .limit(10).all()

    # Données pour le template
    context = {
        'current_user': current_user,
        'active_tab': tab,
        'current_page': tab.capitalize() if tab else 'Accueil',
        'chat_messages': chat_messages
    }

    return render_template('index.html', **context , title="Massy IA - Accueil" ,  datetime=datetime)
