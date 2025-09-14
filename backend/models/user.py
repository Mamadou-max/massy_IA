from backend.extensions import db
from backend.utils.security import hash_password, check_password
from datetime import datetime
import uuid
from enum import Enum

class UserRole(Enum):
    """Rôles disponibles pour les utilisateurs"""
    CITIZEN = 'citizen'       # Citoyen standard
    POLICE = 'police'         # Forces de l'ordre
    UNIVERSITY = 'university' # Chercheurs / universités

class User(db.Model):
    """Modèle utilisateur avec gestion des rôles et relations pour alertes et projets"""

    __tablename__ = 'users'

    # Colonnes principales
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.CITIZEN, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    profile_picture = db.Column(db.String(256))  # URL ou chemin vers l'image de profil

    # Relations
    suspect_alerts = db.relationship(
        'SuspectAlert',
        backref='reporter',
        lazy=True,
        cascade='all, delete-orphan'
    )
    research_projects = db.relationship(
        'ResearchProject',
        backref='researcher',
        lazy=True,
        cascade='all, delete-orphan'
    )
    conversations = db.relationship(
        'Conversation',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):
        """Initialisation avec gestion du rôle si fourni"""
        super().__init__(**kwargs)
        role_value = kwargs.get('role')
        if role_value:
            try:
                self.role = UserRole(role_value) if isinstance(role_value, str) else role_value
            except ValueError:
                self.role = UserRole.CITIZEN

    # --- Méthodes de mot de passe ---
    def set_password(self, password: str):
        """Hash et définit le mot de passe"""
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Vérifie le mot de passe"""
        return check_password(self.password_hash, password)

    # --- Méthode pour le suivi du dernier login ---
    def update_last_login(self):
        """Met à jour la date du dernier login"""
        self.last_login = datetime.utcnow()

    # --- Vérification des rôles ---
    def has_role(self, *roles) -> bool:
        """Vérifie si l'utilisateur a l'un des rôles spécifiés"""
        role_values = [r.value if isinstance(r, UserRole) else r for r in roles]
        return self.role.value in role_values

    # --- Sérialisation pour API ---
    def to_dict(self) -> dict:
        """Convertit l'utilisateur en dictionnaire complet pour JSON"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile_picture': self.profile_picture
        }

    def to_public_dict(self) -> dict:
        """Version publique (sans email et mot de passe)"""
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'profile_picture': self.profile_picture
        }

    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"
