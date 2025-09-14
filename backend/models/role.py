"""
Définition des rôles utilisateurs pour l'application Massy IA.
"""

from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

    @classmethod
    def choices(cls):
        """
        Retourne les valeurs des rôles sous forme de liste pour validation.
        """
        return [role.value for role in cls]
