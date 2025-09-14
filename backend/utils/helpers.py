from flask import jsonify
from typing import Dict, Optional, Union, Tuple, Any
import re

import re
from typing import Optional
from flask import jsonify
import PyPDF2

def extract_text_from_pdf(file) -> str:
    """
    Extrait le texte d'un fichier PDF.
    `file` doit être un objet FileStorage (Flask `request.files['file']`)
    """
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction du texte du PDF: {e}")


def create_response(
    data: Optional[Union[Dict, list, str, Any]] = None,
    message: str = "Succès",
    status_code: int = 200
) -> Tuple[Any, int]:
    """
    Crée une réponse JSON standardisée pour les succès.

    Args:
        data: Données à inclure dans la réponse (optionnel).
        message: Message à renvoyer (par défaut "Succès").
        status_code: Code HTTP (par défaut 200).

    Returns:
        Tuple contenant la réponse JSON et le code HTTP.
    """
    response = {
        'success': True,
        'message': message,
        'status': status_code
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def error_response(
    message: str,
    status_code: int = 400,
    errors: Optional[Dict] = None
) -> Tuple[Any, int]:
    """
    Crée une réponse JSON standardisée pour les erreurs.

    Args:
        message: Message d'erreur.
        status_code: Code HTTP (par défaut 400).
        errors: Détails supplémentaires sur l'erreur (optionnel).

    Returns:
        Tuple contenant la réponse JSON et le code HTTP.
    """
    response = {
        'success': False,
        'message': message,
        'status': status_code
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code


def sanitize_input(input_string: str) -> str:
    """
    Nettoie une chaîne de caractères pour éviter les injections ou caractères non désirés.
    Ne conserve que les lettres, chiffres, espaces et traits d'union.

    Args:
        input_string: Chaîne à nettoyer.

    Returns:
        Chaîne nettoyée.
    """
    if not isinstance(input_string, str):
        return ""
    return re.sub(r'[^\w\s-]', '', input_string).strip()
