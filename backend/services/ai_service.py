import logging
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from backend.config import Config

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, config):
        self.config = config
        self.mistral_api_key = config.MISTRAL_API_KEY
        self.timeout = 30
        self.mistral_base_url = "https://api.mistral.ai/v1"  # API Mistral

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=retry_if_exception_type(requests.exceptions.RequestException))
    def mistral_chat_completion(self, messages, model="mistral-medium-latest", temperature=0.3):
        if not self.mistral_api_key:
            logger.error("Mistral API key not configured")
            return None
        headers = {"Authorization": f"Bearer {self.mistral_api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages, "temperature": temperature}
        try:
            response = requests.post(f"{self.mistral_base_url}/chat/completions", headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            return None

    # ================= Chatbot / FAQ =================
    def generate_election_response(self, user_query, context=None):
        """Réponse pour le chatbot municipal"""
        system_message = "Vous êtes un assistant officiel de la Ville de Massy."
        if context:
            system_message += f"\nContexte: {context}"
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_query}
        ]
        try:
            return self.mistral_chat_completion(messages) or "Désolé, problème technique. Contactez la mairie."
        except Exception as e:
            logger.error(f"Error generating election response: {e}")
            return "Désolé, problème technique. Contactez la mairie."

    # ================= Analyse d'offres / urbanisme =================
    def analyze_market_offer(self, offer_text):
        """Analyse une offre de marché public"""
        system_message = "Vous êtes un expert en analyse d'offres de marchés publics pour la ville de Massy."
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Analyse: {offer_text}"}
        ]
        try:
            return self.mistral_chat_completion(messages) or "Erreur lors de l'analyse de l'offre."
        except Exception as e:
            logger.error(f"Error analyzing market offer: {e}")
            return "Erreur lors de l'analyse de l'offre."

    def analyze_urbanism_document(self, document_text):
        """Analyse un document ou projet d'urbanisme"""
        system_message = "Vous êtes un expert en urbanisme et projets municipaux de la ville de Massy."
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Analyse: {document_text}"}
        ]
        try:
            return self.mistral_chat_completion(messages) or "Erreur lors de l'analyse du document."
        except Exception as e:
            logger.error(f"Error analyzing urbanism document: {e}")
            return "Erreur lors de l'analyse du document."

    # ================= Génération média =================
    def generate_image(self, prompt):
        """Génère une image via IA"""
        try:
            # Simulation / placeholder
            return f"https://dummyimage.com/512x512/000/fff&text={prompt.replace(' ', '+')}"
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None

    def analyze_video(self, video_file):
        """Analyse une vidéo via IA"""
        try:
            # Simulation / placeholder
            return {"summary": "Vidéo analysée avec succès", "duration_seconds": 120}
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            return {"error": "Erreur lors de l'analyse vidéo"}

# Instance globale pour toutes les routes
ai_service = AIService(Config)
