import datetime
import logging
import requests
from typing import Dict, Any, Optional
from backend.config import Config

logger = logging.getLogger(__name__)

class N8NIntegration:
    """
    Service pour déclencher les workflows N8N.
    Compatible avec :
      - Analyse d'offres de marchés publics
      - Analyse de documents urbanisme
      - Chatbot élections
    """
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url.rstrip("/")
        self.timeout = 10  # Timeout par défaut des requêtes HTTP

    def trigger_election_workflow(self, user_query: str, user_info: Dict[str, Any]) -> bool:
        """Déclenche le workflow N8N pour le chatbot élections"""
        payload = {
            "query": user_query,
            "user": user_info,
            "timestamp": int(datetime.datetime.utcnow().timestamp() * 1000)
        }
        try:
            url = f"{self.webhook_url}/election-bot"
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Erreur lors du déclenchement du workflow élections: {e}")
            return False

    def trigger_market_analysis_workflow(self, offer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Déclenche le workflow N8N pour l'analyse de marché ou document urbanisme"""
        try:
            url = f"{self.webhook_url}/market-analysis"
            response = requests.post(url, json=offer_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erreur lors du déclenchement du workflow marché/urbanisme: {e}")
            return None

    def trigger_custom_workflow(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Déclenche un workflow N8N arbitraire"""
        try:
            url = f"{self.webhook_url}/{endpoint.lstrip('/')}"
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erreur lors du déclenchement du workflow {endpoint}: {e}")
            return None

# Instance globale réutilisable par les routes et services
n8n_service = N8NIntegration(Config.N8N_WEBHOOK_URL)
