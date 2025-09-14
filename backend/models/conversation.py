from backend.extensions import db
from datetime import datetime
import uuid

class Conversation(db.Model):
    """Modèle pour les conversations avec le chatbot"""
    __tablename__ = 'conversations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relation avec les messages
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')

    def get_messages(self):
        """Retourne les messages sous forme de liste de dicts triés par date"""
        return [msg.to_dict() for msg in self.messages.order_by(Message.created_at.asc()).all()]

    def to_dict(self):
        """Retourne un dict représentant la conversation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'messages': self.get_messages()
        }


class Message(db.Model):
    """Modèle pour les messages dans une conversation"""
    __tablename__ = 'messages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # 'user' ou 'bot'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    meta_info = db.Column(db.String(200))  # anciennement 'metadata', facultatif

    def to_dict(self):
        """Retourne un dict représentant le message"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender': self.sender,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'meta_info': self.meta_info
        }
