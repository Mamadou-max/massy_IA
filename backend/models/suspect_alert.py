from backend.extensions import db
from datetime import datetime
import uuid

class SuspectAlert(db.Model):
    """Modèle pour les alertes de comportements suspects"""

    __tablename__ = 'suspect_alerts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.Integer, nullable=False)  # De 1 à 10
    status = db.Column(db.String(20), default='new', nullable=False)  # new, in_progress, resolved
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    additional_data = db.Column(db.JSON)  # Pour stocker des données supplémentaires (ex: images, vidéos)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.alert_type,
            'description': self.description,
            'location': {'lat': self.latitude, 'lng': self.longitude},
            'risk_level': self.risk_level,
            'status': self.status,
            'reported_at': self.reported_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'reporter': self.reporter.to_public_dict() if self.reporter else None,
            'additional_data': self.additional_data
        }
