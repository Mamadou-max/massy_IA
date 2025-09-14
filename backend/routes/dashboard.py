from flask import Blueprint
from flask_jwt_extended import jwt_required
from backend.utils.helpers import create_response
from backend.models.urbanism_project import UrbanismProject
from backend.models.suspect_alert import SuspectAlert
from backend.models.research_project import ResearchProject
from sqlalchemy import desc

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/massy')


@dashboard_bp.route('/metrics', methods=['GET'])
@jwt_required(optional=True)
def metrics():
    """Retourne les KPIs réels pour le dashboard"""
    try:
        # Opportunités détectées : projets d'urbanisme ouverts
        if hasattr(UrbanismProject, 'status'):
            opportunities_count = UrbanismProject.query.filter_by(status='open').count()
        else:
            opportunities_count = UrbanismProject.query.count()  # fallback si pas de status

        # Alertes sécurité : alertes actives
        if hasattr(SuspectAlert, 'status'):
            risks_count = SuspectAlert.query.filter(SuspectAlert.status == 'new').count()
        else:
            risks_count = SuspectAlert.query.count()

        # Analyses en cours : projets de recherche en cours
        if hasattr(ResearchProject, 'status'):
            analyses_count = ResearchProject.query.filter(ResearchProject.status == 'in_progress').count()
        else:
            analyses_count = ResearchProject.query.count()

        # Résumé dynamique
        summary = f"{opportunities_count} opportunité(s) d'urbanisme, {risks_count} alerte(s) de sécurité, {analyses_count} analyse(s) en cours"

        data = {
            "opportunities": opportunities_count,
            "opportunities_count": opportunities_count,
            "risks": risks_count,
            "cache_hits": analyses_count,
            "summary": summary
        }

        return create_response({"data": data}, "KPIs récupérés avec succès")
    except Exception as e:
        return create_response({}, f"Erreur lors de la récupération des KPIs : {str(e)}", 500)


@dashboard_bp.route('/recent-activity', methods=['GET'])
@jwt_required(optional=True)
def recent_activity():
    """Retourne une liste d'activités récentes depuis la DB"""
    try:
        activities = []

        # Derniers projets Urbanism
        urban_projects = UrbanismProject.query.order_by(desc(UrbanismProject.updated_at)).limit(5).all()
        for u in urban_projects:
            activities.append({
                "title": f"Projet {getattr(u, 'title', '-')}",
                "time": u.updated_at.strftime("%H:%M") if getattr(u, 'updated_at', None) else "-",
                "description": getattr(u, 'description', '-'),
                "icon": "building",
                "type": "opportunity"
            })

        # Dernières alertes suspectes
        suspect_alerts = SuspectAlert.query.order_by(desc(SuspectAlert.reported_at)).limit(5).all()
        for s in suspect_alerts:
            activities.append({
                "title": f"Alerte {getattr(s, 'alert_type', '-')}",
                "time": s.reported_at.strftime("%H:%M") if getattr(s, 'reported_at', None) else "-",
                "description": getattr(s, 'description', '-'),
                "icon": "triangle-exclamation",
                "type": "security"
            })

        # Derniers projets de recherche
        research_projects = ResearchProject.query.order_by(desc(ResearchProject.updated_at)).limit(5).all()
        for r in research_projects:
            activities.append({
                "title": f"Analyse {getattr(r, 'title', '-')}",
                "time": r.updated_at.strftime("%H:%M") if getattr(r, 'updated_at', None) else "-",
                "description": getattr(r, 'description', '-'),
                "icon": "flask",
                "type": "info"
            })

        # Tri par heure décroissante
        activities = sorted(activities, key=lambda x: x['time'], reverse=True)

        return create_response({"activities": activities}, f"{len(activities)} activité(s) récupérée(s)")
    except Exception as e:
        return create_response({}, f"Erreur lors de la récupération des activités : {str(e)}", 500)


@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def overview():
    """Alias vers /metrics"""
    return metrics()
