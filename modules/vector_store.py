# modules/vector_store.py
import chromadb
from chromadb.config import Settings
import os
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, db_directory="./data/vector_db"):
        """Initialize ChromaDB client and collection.
        
        Args:
            db_directory: Directory to store ChromaDB files
        """
        os.makedirs(db_directory, exist_ok=True)
        logger.info(f"Initializing ChromaDB at {db_directory}")
        
        self.client = chromadb.PersistentClient(
            path=db_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        try:
            self.collection = self.client.get_or_create_collection(
                name="research_papers",
                metadata={"description": "Academic research papers"}
            )
            logger.info(f"Collection 'research_papers' ready with {self.collection.count()} documents")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB collection: {str(e)}")
            raise
    
    def add_documents(self, chunks):
        """Add document chunks to the vector store.
        
        Args:
            chunks: List of document chunks with text and metadata
        """
        if not chunks:
            logger.warning("No chunks provided to add to vector store")
            return
        
        # Prepare data for ChromaDB
        ids = [str(uuid.uuid4()) for _ in chunks]
        documents = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        # Add to collection
        try:
            logger.info(f"Adding {len(chunks)} chunks to vector store")
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Successfully added chunks. Collection now has {self.collection.count()} documents")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}")
            raise
    
    def query(self, query_embedding, n_results=5):
        """Query the vector store for similar documents.
        
        Args:
            query_embedding: Embedding vector of the query
            n_results: Number of results to return
            
        Returns:
            List of document chunks with text and metadata
        """
        try:
            logger.info(f"Querying vector store for top {n_results} results")
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Process results
            documents = results["documents"][0]  # First (and only) query results
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            
            logger.info(f"Retrieved {len(documents)} documents")
            
            # Format results
            formatted_results = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                formatted_results.append({
                    "content": doc,
                    "metadata": meta,
                    "similarity": 1.0 - dist  # Convert distance to similarity score
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            raise