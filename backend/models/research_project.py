from backend.extensions import db
from datetime import datetime
import uuid

class ResearchProject(db.Model):
    """Modèle pour les projets de recherche universitaires"""

    __tablename__ = 'research_projects'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='draft', nullable=False)  # draft, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    results = db.Column(db.JSON)  # Pour stocker les résultats de la recherche
    tags = db.Column(db.JSON)  # Mots-clés associés

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'researcher': self.researcher.to_public_dict() if self.researcher else None,
            'tags': self.tags,
            'has_results': bool(self.results)
        }
