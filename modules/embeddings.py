# modules/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """Initialize embedding generator with a specific model.
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def generate_embeddings(self, texts):
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of strings to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            logger.warning("Empty text list provided for embedding generation")
            return []
        
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts)
        return embeddings.tolist()  # Convert numpy arrays to lists for storage
    
    def generate_query_embedding(self, query):
        """Generate embedding for a single query string.
        
        Args:
            query: String query
            
        Returns:
            Embedding vector
        """
        logger.info(f"Generating embedding for query: {query[:50]}...")
        embedding = self.model.encode(query)
        return embedding.tolist()
