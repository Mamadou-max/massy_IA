"""
Routes pour l'analyse et la gestion de projets de recherche universitaire.
"""

from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import User, UserRole, ResearchProject
from backend.extensions import db
from backend.utils.helpers import create_response, error_response
import random
import uuid

university_bp = Blueprint('university', __name__, url_prefix='/api/university')


@university_bp.route('/research', methods=['POST'])
@jwt_required()
def perform_research():
    """Effectue une recherche universitaire"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.has_role(UserRole.UNIVERSITY):
            return error_response("Accès refusé. Réservé aux universités.", 403)

        data = request.get_json() or {}
        query = data.get('query', '').strip()
        if not query:
            return error_response("Veuillez fournir un sujet de recherche.", 400)

        # Simulation de résultats de recherche
        summaries = []
        research_areas = [
            {'title': 'Impact économique', 'tags': ['économie', 'transport', 'emploi']},
            {'title': 'Analyse sociologique', 'tags': ['sociologie', 'population', 'comportement']},
            {'title': 'Optimisation urbaine', 'tags': ['urbanisme', 'infrastructure', 'mobilité']}
        ]

        for i in range(1, 4):
            area = random.choice(research_areas)
            summaries.append({
                'id': str(uuid.uuid4()),
                'title': f"Étude {i}: {query} — {area['title']}",
                'content': (
                    f"Cette étude analyse {query.lower()} sous l'angle de {area['title'].lower()}. "
                    f"Basée sur {random.randint(500, 5000)} échantillons collectés entre 2020 et 2025, "
                    f"l'analyse révèle une {random.choice(['augmentation', 'stabilisation', 'diminution'])} "
                    f"de {random.randint(5, 50)}% du phénomène étudié. "
                    f"Recommandations: {random.choice(['Investir dans les infrastructures', 'Renforcer la surveillance', 'Lancer une campagne de sensibilisation'])}."
                ),
                'tags': area['tags'] + [f"massy_{random.randint(1, 5)}"],
                'data_points': random.randint(100, 1000),
                'trend': random.choice(['positive', 'neutral', 'negative'])
            })

        statistics = [
            {'label': 'Échantillons analysés', 'value': random.randint(1000, 10000)},
            {'label': 'Impact économique (k€)', 'value': random.randint(50, 500)},
            {'label': 'Satisfaction citoyenne (%)', 'value': random.randint(60, 95)},
            {'label': 'Risque identifié (1-10)', 'value': random.randint(1, 10)},
            {'label': 'Potentiel d\'amélioration (%)', 'value': random.randint(10, 80)}
        ]

        # Sauvegarde du projet
        project = ResearchProject(
            id=str(uuid.uuid4()),
            title=f"Recherche: {query}",
            description=f"Analyse approfondie de {query} et ses impacts sur Massy. "
                        f"Méthodologie: {random.choice(['Enquête terrain', 'Analyse de données', 'Modélisation'])}.",
            user_id=user.id,
            status='in_progress',
            results={
                'summaries': summaries,
                'statistics': statistics,
                'methodology': random.choice(['quantitative', 'qualitative', 'mixte']),
                'data_sources': ['INSEE', 'RATP', 'Enquêtes locales', 'OpenStreetMap']
            },
            tags=[tag for summary in summaries for tag in summary['tags']]
        )

        db.session.add(project)
        db.session.commit()

        return create_response({
            'project_id': project.id,
            'summaries': summaries,
            'statistics': statistics
        }, f"Recherche '{query}' lancée avec succès. {len(summaries)} résultats préliminaires générés.")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur recherche universitaire: {str(e)}")
        return error_response("Erreur interne lors de la création du projet de recherche.", 500)


@university_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """Récupère tous les projets de recherche de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.has_role(UserRole.UNIVERSITY):
            return error_response("Accès refusé.", 403)

        projects = ResearchProject.query.filter_by(user_id=user.id).order_by(ResearchProject.updated_at.desc()).all()
        return create_response({
            'projects': [project.to_dict() for project in projects]
        }, f"{len(projects)} projet(s) récupéré(s).")

    except Exception as e:
        current_app.logger.error(f"Erreur récupération projets universitaires: {str(e)}")
        return error_response("Erreur interne lors de la récupération des projets.", 500)


@university_bp.route('/projects/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Récupère un projet spécifique avec ses résultats"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.has_role(UserRole.UNIVERSITY):
            return error_response("Accès refusé.", 403)

        project = ResearchProject.query.get(project_id)
        if not project or project.user_id != user.id:
            return error_response("Projet non trouvé.", 404)

        return create_response({
            **project.to_dict(),
            'full_results': project.results
        }, f"Projet '{project.title}' récupéré avec succès.")

    except Exception as e:
        current_app.logger.error(f"Erreur récupération projet universitaire: {str(e)}")
        return error_response("Erreur interne lors de la récupération du projet.", 500)
