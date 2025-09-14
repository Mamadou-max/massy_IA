import logging
import uuid
from typing import List, Dict, Optional
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class ChromaService:
    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialise ChromaDB et la collection 'massy_documents'"""
        try:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(allow_reset=True, anonymized_telemetry=False)
            )
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.collection = self.client.get_or_create_collection(
                name="massy_documents",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            logger.error(f"Impossible de se connecter à ChromaDB: {e}")
            self.client = None
            self.collection = None

    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None) -> bool:
        """Ajoute des documents dans la collection"""
        if not self.collection:
            logger.warning("ChromaDB non disponible")
            return False
        if not ids:
            ids = [str(uuid.uuid4()) for _ in documents]
        if not metadatas:
            metadatas = [{} for _ in documents]
        try:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des documents: {e}")
            return False

    def query_documents(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """Recherche les documents les plus similaires à une requête"""
        if not self.collection:
            return []
        try:
            results = self.collection.query(query_texts=[query_text], n_results=n_results)
            documents = []
            for i in range(len(results['ids'][0])):
                documents.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            return documents
        except Exception as e:
            logger.error(f"Erreur lors de la requête ChromaDB: {e}")
            return []

    def get_relevant_context(self, query_text: str, n_results: int = 3) -> str:
        """Retourne un contexte synthétique pour l'IA à partir des documents pertinents"""
        docs = self.query_documents(query_text, n_results)
        if not docs:
            return ""
        context = "Contexte pertinent:\n"
        for i, doc in enumerate(docs, 1):
            snippet = doc['document'][:200].replace("\n", " ")  # tronque et nettoie
            context += f"{i}. {snippet}...\n"
        return context

def get_chroma_service() -> ChromaService:
    """Factory pour récupérer le service ChromaDB"""
    return ChromaService()
