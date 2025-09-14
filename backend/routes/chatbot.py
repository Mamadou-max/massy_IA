"""
Routes pour le chatbot IA des élections municipales.
"""

from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.conversation import  Conversation, Message
from backend.models.user import User
from backend.services import ai_service, n8n_service
from backend.services.chroma_service import ChromaService
from backend.utils.helpers import create_response, error_response, sanitize_input

chatbot_bp = Blueprint('chatbot', __name__, url_prefix="/api/chatbot")

def get_chroma_service():
    """Crée et retourne le service Chroma à la demande"""
    return ChromaService()


@chatbot_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """Endpoint pour discuter avec le chatbot"""
    try:
        data = request.get_json() or {}
        user_message = sanitize_input(data.get('message', '').strip())
        if not user_message:
            return error_response("Message requis", 400)

        # Récupération de l'utilisateur
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return error_response("Utilisateur non trouvé", 404)

        # Récupération du contexte pertinent
        chroma_service = get_chroma_service()
        context = chroma_service.get_relevant_context(user_message)

        # Génération de la réponse AI
        response = ai_service.generate_election_response(user_message, context)

        # Déclenchement du workflow N8N
        n8n_service.trigger_election_workflow(user_message, user.to_dict())

        # Gestion de la conversation
        conversation = Conversation.query.filter_by(user_id=user.id)\
                                        .order_by(Conversation.updated_at.desc())\
                                        .first()

        if conversation:
            # Ajouter les messages existants
            user_msg = Message(conversation_id=conversation.id, sender='user', content=user_message)
            bot_msg = Message(conversation_id=conversation.id, sender='bot', content=response)
            db.session.add_all([user_msg, bot_msg])
            conversation.updated_at = datetime.utcnow()
        else:
            # Créer une nouvelle conversation
            conversation = Conversation(
                user_id=user.id,
                title=(user_message[:50] + "...") if len(user_message) > 50 else user_message,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(conversation)
            db.session.flush()  # pour récupérer conversation.id avant d'ajouter les messages

            user_msg = Message(conversation_id=conversation.id, sender='user', content=user_message)
            bot_msg = Message(conversation_id=conversation.id, sender='bot', content=response)
            db.session.add_all([user_msg, bot_msg])

        db.session.commit()

        return create_response({
            'response': response,
            'conversation_id': conversation.id,
            'context_used': bool(context)
        }, "Réponse générée avec succès")

    except Exception as e:
        db.session.rollback()
        return error_response(f"Erreur lors de la génération de la réponse : {str(e)}", 500)


@chatbot_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Récupération des conversations de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        conversations = Conversation.query.filter_by(user_id=current_user_id)\
                                          .order_by(Conversation.updated_at.desc())\
                                          .all()
        return create_response({
            'conversations': [conv.to_dict() for conv in conversations]
        }, "Conversations récupérées avec succès")
    except Exception as e:
        return error_response(f"Erreur lors de la récupération des conversations : {str(e)}", 500)


@chatbot_bp.route('/conversations/<conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """Récupération d'une conversation spécifique"""
    try:
        current_user_id = get_jwt_identity()
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user_id).first()
        if not conversation:
            return error_response("Conversation non trouvée", 404)
        return create_response({'conversation': conversation.to_dict()}, "Conversation récupérée avec succès")
    except Exception as e:
        return error_response(f"Erreur lors de la récupération de la conversation : {str(e)}", 500)


@chatbot_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conversation_id):
    """Suppression d'une conversation"""
    try:
        current_user_id = get_jwt_identity()
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user_id).first()
        if not conversation:
            return error_response("Conversation non trouvée", 404)

        db.session.delete(conversation)
        db.session.commit()
        return create_response(None, "Conversation supprimée avec succès")
    except Exception as e:
        db.session.rollback()
        return error_response(f"Erreur lors de la suppression de la conversation : {str(e)}", 500)
