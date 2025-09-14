"""
Routes pour l'analyse des marchés publics avec l'IA.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from backend.services import ai_service, n8n_service
from backend.utils.helpers import create_response, error_response, extract_text_from_pdf

# Blueprint pour le module "market"
market_bp = Blueprint('market', __name__, url_prefix='/api/market')


@market_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_market_offer():
    """
    Analyse d'une offre de marché public avec l'IA.
    Accepte soit un fichier PDF, soit du texte brut dans le corps de la requête.
    """
    try:
        offer_text = ""

        # Si un fichier PDF est fourni
        if 'file' in request.files:
            pdf_file = request.files['file']
            if not pdf_file.filename:
                return error_response("Aucun fichier sélectionné", 400)
            if not pdf_file.filename.lower().endswith('.pdf'):
                return error_response("Le fichier doit être au format PDF", 400)
            
            # Extraction du texte du PDF
            offer_text = extract_text_from_pdf(pdf_file)

        else:
            # Si du texte est fourni directement
            data = request.get_json() or {}
            offer_text = data.get('text', '').strip()
            if not offer_text:
                return error_response("Texte ou fichier PDF requis", 400)
        
        # Analyse de l'offre avec l'IA
        analysis = ai_service.analyze_market_offer(offer_text)
        
        # Déclenchement du workflow N8N pour suivi
        n8n_service.trigger_market_analysis_workflow({
            'text': offer_text,
            'analysis': analysis
        })
        
        return create_response({
            'analysis': analysis,
            'text_length': len(offer_text)
        }, "Analyse effectuée avec succès")
    
    except Exception as e:
        return error_response(f"Erreur lors de l'analyse: {str(e)}", 500)


@market_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_market_templates():
    """
    Récupération des modèles de marchés publics.
    Pour l'instant, renvoie des modèles statiques.
    """
    try:
        templates = [
            {
                'id': '1',
                'name': 'Modèle de marché de services',
                'description': 'Modèle standard pour les marchés de services',
                'category': 'Services',
                'file_url': '/templates/marche-services.docx'
            },
            {
                'id': '2',
                'name': 'Modèle de marché de travaux',
                'description': 'Modèle standard pour les marchés de travaux',
                'category': 'Travaux',
                'file_url': '/templates/marche-travaux.docx'
            },
            {
                'id': '3',
                'name': 'Modèle de marché de fournitures',
                'description': 'Modèle standard pour les marchés de fournitures',
                'category': 'Fournitures',
                'file_url': '/templates/marche-fournitures.docx'
            }
        ]
        
        return create_response({'templates': templates}, "Modèles récupérés avec succès")
    
    except Exception as e:
        return error_response(f"Erreur lors de la récupération des modèles: {str(e)}", 500)
