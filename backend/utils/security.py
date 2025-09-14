import re
import bcrypt
from typing import Tuple


def validate_email(email: str) -> bool:
    """
    Valide le format d'un email.

    Args:
        email: Adresse email à valider.

    Returns:
        True si le format est valide, False sinon.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Valide la complexité d'un mot de passe.

    Critères :
        - Minimum 8 caractères
        - Au moins une majuscule
        - Au moins une minuscule
        - Au moins un chiffre
        - Au moins un caractère spécial (!@#$%^&*(),.?":{}|<>)

    Args:
        password: Mot de passe à valider.

    Returns:
        Tuple contenant un booléen indiquant si le mot de passe est valide et un message.
    """
    if len(password) < 8:
        return False, "Le mot de passe doit faire au moins 8 caractères"
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    if not re.search(r'[0-9]', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial"
    return True, "Mot de passe valide"


def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt.

    Args:
        password: Mot de passe en clair.

    Returns:
        Mot de passe hashé en string UTF-8.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(hashed_password: str, password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond à un hash bcrypt.

    Args:
        hashed_password: Mot de passe hashé.
        password: Mot de passe en clair à vérifier.

    Returns:
        True si le mot de passe correspond au hash, False sinon.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
