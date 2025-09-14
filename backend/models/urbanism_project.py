from backend.extensions import db
import uuid
from datetime import datetime

class UrbanismProject(db.Model):
    __tablename__ = 'urbanism_projects'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relation avec les utilisateurs si nécessaire
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
