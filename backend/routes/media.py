"""
Routes pour la gestion des médias avec IA : génération d'images et analyse de vidéos.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from backend.services import ai_service
from backend.utils.helpers import create_response, error_response

# Blueprint pour le module "media"
media_bp = Blueprint('media', __name__, url_prefix='/api/media')


@media_bp.route('/generate-image', methods=['POST'])
@jwt_required()
def generate_image():
    """
    Génère une image à partir d'un prompt fourni via l'IA.
    Reçoit JSON : {"prompt": "description de l'image"}
    """
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', '').strip()
        if not prompt:
            return error_response("Prompt requis", 400)

        image_url = ai_service.generate_image(prompt)
        return create_response({"image_url": image_url}, "Image générée avec succès")
    
    except Exception as e:
        return error_response(f"Erreur lors de la génération de l'image : {str(e)}", 500)


@media_bp.route('/analyze-video', methods=['POST'])
@jwt_required()
def analyze_video():
    """
    Analyse une vidéo fournie par l'utilisateur.
    Reçoit un fichier via form-data : key="video"
    """
    try:
        video = request.files.get('video')
        if not video:
            return error_response("Fichier vidéo requis", 400)

        report = ai_service.analyze_video(video)
        return create_response({"report": report}, "Analyse vidéo effectuée avec succès")
    
    except Exception as e:
        return error_response(f"Erreur lors de l'analyse de la vidéo : {str(e)}", 500)
