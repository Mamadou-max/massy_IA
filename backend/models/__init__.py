from .user import User, UserRole
from .conversation import Conversation
from .research_project import ResearchProject
from .suspect_alert import SuspectAlert
from .urbanism_project import UrbanismProject  # <- ajouter ici

__all__ = [
    'User', 'UserRole',
    'Conversation',
    'ResearchProject',
    'SuspectAlert',
    'UrbanismProject'
]
