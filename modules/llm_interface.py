# modules/llm_interface.py
import os
import logging
from llama_cpp import Llama

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMInterface:
    def __init__(self, model_path=None):
        """Initialize LLM interface.
        
        Args:
            model_path: Path to the LLM model file
        """
        self.model_path = model_path or os.environ.get("LLM_MODEL_PATH")
        if not self.model_path:
            raise ValueError("Model path must be provided or set as LLM_MODEL_PATH environment variable")
        
        try:
            logger.info(f"Loading LLM model from {self.model_path}")
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=4096,  # Context window size
                n_threads=os.cpu_count(),  # Use all available CPU threads
                use_mlock=False
            )
            logger.info("LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load LLM model: {str(e)}")
            raise
    
    def create_prompt(self, query, retrieved_docs, citation_style="APA"):
        """Create a prompt for the LLM using the query and retrieved documents.
        
        Args:
            query: User's question
            retrieved_docs: List of retrieved document chunks
            citation_style: Citation style to use (APA, MLA, IEEE)
            
        Returns:
            Formatted prompt string
        """
        # Format document context
        context_docs = []
        for i, doc in enumerate(retrieved_docs):
            source = doc["metadata"].get("source", "Unknown")
            title = doc["metadata"].get("title", os.path.basename(source))
            page = doc["metadata"].get("page", "")
            page_str = f", page {page}" if page else ""
            
            context_docs.append(f"Document[{i+1}]: {doc['content']}\nSource[{i+1}]: {title}{page_str}, {source}")
        
        context = "\n\n".join(context_docs)
        
        # Create the full prompt
        prompt = f"""You are an academic research assistant. Answer the following question based on the provided document excerpts. 
Include proper citations in {citation_style} format when using information from the documents.
If the documents don't contain enough information to answer the question, acknowledge the limitations of the provided information.

DOCUMENTS:
{context}

USER QUESTION: {query}

Please provide a well-structured answer with appropriate citations. Format citations in {citation_style} style.
"""
        return prompt
    
    def generate_response(self, prompt, max_tokens=1024, temperature=0.7):
        """Generate a response from the LLM.
        
        Args:
            prompt: Formatted prompt string
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature parameter for generation
            
        Returns:
            Generated response string
        """
        try:
            logger.info("Generating LLM response")
            output = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["USER QUESTION:"],  # Stop if the model tries to continue with another question
                echo=False
            )
            
            response = output["choices"][0]["text"].strip()
            logger.info(f"Generated response of length {len(response)}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            error_msg = "I apologize, but I encountered an error while generating a response. Please try again."
            return error_msg