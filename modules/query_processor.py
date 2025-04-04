# modules/query_processor.py
import logging
from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self, embedding_generator, vector_store):
        """Initialize query processor with required components.
        
        Args:
            embedding_generator: Instance of EmbeddingGenerator
            vector_store: Instance of VectorStore
        """
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
    
    def process_query(self, query, n_results=5):
        """Process a user query and retrieve relevant documents.
        
        Args:
            query: User's question string
            n_results: Number of document chunks to retrieve
            
        Returns:
            List of relevant document chunks
        """
        logger.info(f"Processing query: {query[:50]}...")
        
        # Generate embedding for the query
        query_embedding = self.embedding_generator.generate_query_embedding(query)
        
        # Retrieve relevant documents
        results = self.vector_store.query(query_embedding, n_results=n_results)
        logger.info(f"Retrieved {len(results)} results for query")
        
        return results
    
    def rerank_results(self, results, query):
        """Rerank results based on additional criteria (optional).
        
        This could implement more sophisticated reranking algorithms
        like BM25, cross-encoders, or other techniques.
        
        Args:
            results: Initial retrieval results
            query: Original query string
            
        Returns:
            Reranked results
        """
        # Simple implementation - could be expanded with more advanced techniques
        # For now, just sort by similarity score
        return sorted(results, key=lambda x: x["similarity"], reverse=True)

