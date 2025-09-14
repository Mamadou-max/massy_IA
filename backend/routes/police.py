"""
Routes pour la gestion policière : détection de comportements suspects et optimisation des patrouilles.
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import User, SuspectAlert, UserRole
from backend.extensions import db
from backend.utils.helpers import create_response, error_response
from datetime import datetime, timedelta
import random
import uuid

police_bp = Blueprint('police', __name__, url_prefix='/api/police')


def check_police_access():
    """Vérifie que l'utilisateur connecté est un membre de la police"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.has_role(UserRole.POLICE):
        return None, error_response("Accès refusé. Réservé aux forces de l'ordre.", 403)
    return user, None


@police_bp.route('/detect-suspects', methods=['GET'])
@jwt_required()
def detect_suspects():
    """Détecte les comportements suspects (simulation avec données réalistes)"""
    user, error = check_police_access()
    if error:
        return error

    try:
        alerts = []
        alert_types = [
            'Comportement erratique', 'Vol à la tire', 'Agression verbale',
            'Objet abandonné', 'Rassemblement illégal', 'Véhicule suspect'
        ]
        locations = [
            {'name': 'Gare de Massy TGV', 'lat': 48.735, 'lng': 2.29},
            {'name': 'Centre commercial Vilgénis', 'lat': 48.732, 'lng': 2.295},
            {'name': 'Place de France', 'lat': 48.738, 'lng': 2.289},
            {'name': 'Parc Georges Brassens', 'lat': 48.729, 'lng': 2.301}
        ]

        for _ in range(5):
            location = random.choice(locations)
            alert_type = random.choice(alert_types)
            risk_level = random.randint(5, 10)
            time_delta = random.randint(1, 120)

            alert = SuspectAlert(
                id=str(uuid.uuid4()),
                alert_type=alert_type,
                description=f"{alert_type} détecté près de {location['name']}. "
                            f"Témoins rapportent un individu {random.choice(['agité', 'masqué', 'armé', 'en fuite'])}.",
                latitude=location['lat'] + random.uniform(-0.001, 0.001),
                longitude=location['lng'] + random.uniform(-0.001, 0.001),
                risk_level=risk_level,
                status='new',
                reported_at=datetime.utcnow() - timedelta(minutes=time_delta),
                user_id=user.id,
                additional_data={
                    'witnesses': random.randint(1, 5),
                    'evidence': random.choice(['video', 'photo', 'témoignage']),
                    'priority': 'high' if risk_level > 7 else 'medium'
                }
            )
            db.session.add(alert)
            alerts.append(alert.to_dict())

        db.session.commit()
        return create_response({'alerts': alerts}, "Alertes simulées générées avec succès")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur détection suspects: {str(e)}")
        return error_response("Erreur interne lors de la détection de suspects", 500)


@police_bp.route('/optimize-patrols', methods=['GET'])
@jwt_required()
def optimize_patrols():
    """Optimise les patrouilles en fonction des alertes (simulation)"""
    user, error = check_police_access()
    if error:
        return error

    try:
        alerts = SuspectAlert.query.filter_by(status='new').order_by(SuspectAlert.risk_level.desc()).all()
        if not alerts:
            return create_response({'routes': []}, "Aucune alerte récente. Patrouilles standard recommandées.")

        routes = []
        for alert in alerts[:3]:
            path = [{'lat': alert.latitude + random.uniform(-0.0005, 0.0005) * j,
                     'lng': alert.longitude + random.uniform(-0.0005, 0.0005) * j} for j in range(5)]
            routes.append({
                'id': str(uuid.uuid4()),
                'alert_id': alert.id,
                'alert_type': alert.alert_type,
                'path': path,
                'duration': random.randint(20, 60),
                'priority': 'high' if alert.risk_level > 7 else 'medium',
                'recommended_actions': [
                    'Surveillance renforcée',
                    'Contact avec les témoins',
                    'Vérification des caméras à proximité'
                ]
            })

        return create_response({
            'optimized_routes': len(routes),
            'routes': routes
        }, f"{len(routes)} itinéraire(s) optimisé(s) basé(s) sur {len(alerts)} alerte(s).")

    except Exception as e:
        current_app.logger.error(f"Erreur optimisation patrouilles: {str(e)}")
        return error_response("Erreur interne lors de l'optimisation des patrouilles", 500)


@police_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """Récupère toutes les alertes (avec filtres)"""
    user, error = check_police_access()
    if error:
        return error

    try:
        status = request.args.get('status', 'new')
        risk_level = request.args.get('risk_level')

        query = SuspectAlert.query
        if status != 'all':
            query = query.filter_by(status=status)
        if risk_level:
            query = query.filter_by(risk_level=int(risk_level))

        alerts = query.order_by(SuspectAlert.reported_at.desc()).all()
        return create_response({'alerts': [alert.to_dict() for alert in alerts]}, "Alertes récupérées avec succès")

    except Exception as e:
        current_app.logger.error(f"Erreur récupération alertes: {str(e)}")
        return error_response("Erreur interne lors de la récupération des alertes", 500)


@police_bp.route('/alerts/<alert_id>', methods=['PUT'])
@jwt_required()
def update_alert(alert_id):
    """Met à jour le statut d'une alerte"""
    user, error = check_police_access()
    if error:
        return error

    try:
        alert = SuspectAlert.query.get(alert_id)
        if not alert:
            return error_response("Alerte non trouvée", 404)

        data = request.get_json() or {}
        if 'status' in data:
            alert.status = data['status']
            if data['status'] == 'resolved':
                alert.resolved_at = datetime.utcnow()

        db.session.commit()
        return create_response({'alert': alert.to_dict()}, "Alerte mise à jour avec succès")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur mise à jour alerte: {str(e)}")
        return error_response("Erreur interne lors de la mise à jour de l'alerte", 500)
