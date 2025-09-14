"""
Routes pour l'analyse des projets et documents d'urbanisme avec l'IA.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services import ai_service, n8n_service
from backend.models import User, UrbanismProject
from backend.extensions import db
from backend.utils.helpers import create_response, error_response, extract_text_from_pdf
import datetime

urbanism_bp = Blueprint('urbanism', __name__, url_prefix='/api/urbanism')


@urbanism_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_urbanism_document():
    """Analyse d'un document ou projet d'urbanisme via l'IA et sauvegarde dans la base"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return error_response("Utilisateur non trouvé", 404)

        offer_text = ""

        # Vérification si un fichier PDF est fourni
        if 'file' in request.files:
            pdf_file = request.files['file']
            if not pdf_file.filename:
                return error_response("Aucun fichier sélectionné", 400)
            if not pdf_file.filename.lower().endswith('.pdf'):
                return error_response("Le fichier doit être au format PDF", 400)
            
            offer_text = extract_text_from_pdf(pdf_file)
        else:
            data = request.get_json() or {}
            offer_text = data.get('text', '').strip()
            if not offer_text:
                return error_response("Texte ou fichier PDF requis", 400)

        # Analyse IA
        analysis = ai_service.analyze_market_offer(offer_text)

        # Déclenchement workflow N8N
        n8n_service.trigger_market_analysis_workflow({
            'user': user.to_dict(),
            'text': offer_text,
            'analysis': analysis
        })

        # Sauvegarde dans la base
        project = UrbanismProject(
            user_id=user.id,
            title=f"Analyse Urbanisme {datetime.datetime.utcnow().isoformat()}",
            content=offer_text,
            analysis=analysis,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()

        return create_response({
            'project_id': project.id,
            'analysis': analysis,
            'text_length': len(offer_text)
        }, "Analyse effectuée et sauvegardée avec succès")

    except Exception as e:
        db.session.rollback()
        return error_response(f"Erreur lors de l'analyse : {str(e)}", 500)


@urbanism_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_urbanism_templates():
    """Récupération des modèles de documents d'urbanisme"""
    try:
        templates = [
            {
                'id': '1',
                'name': 'Modèle de plan local d\'urbanisme',
                'description': 'Modèle standard pour un PLU',
                'category': 'Urbanisme',
                'file_url': '/templates/plu.docx'
            },
            {
                'id': '2',
                'name': 'Modèle de permis de construire',
                'description': 'Modèle standard pour permis de construire',
                'category': 'Urbanisme',
                'file_url': '/templates/permis-construire.docx'
            },
            {
                'id': '3',
                'name': 'Modèle de règlement de lotissement',
                'description': 'Modèle standard pour règlement de lotissement',
                'category': 'Urbanisme',
                'file_url': '/templates/reglement-lotissement.docx'
            }
        ]
        return create_response({'templates': templates}, "Modèles récupérés avec succès")
    except Exception as e:
        return error_response(f"Erreur lors de la récupération des modèles : {str(e)}", 500)
