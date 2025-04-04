# utils/evaluation.py
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Evaluator:
    """Evaluation metrics for the research assistant system."""
    
    @staticmethod
    def evaluate_retrieval(relevant_docs, retrieved_docs):
        """Evaluate retrieval performance.
        
        Args:
            relevant_docs: List of document IDs that are relevant
            retrieved_docs: List of document IDs that were retrieved
            
        Returns:
            Dict containing precision, recall, and F1 scores
        """
        # Convert to sets for easier calculation
        relevant_set = set(relevant_docs)
        retrieved_set = set(retrieved_docs)
        
        # Calculate true positives (correctly retrieved docs)
        true_positives = len(relevant_set.intersection(retrieved_set))
        
        # Calculate precision (proportion of retrieved docs that are relevant)
        precision = true_positives / len(retrieved_set) if retrieved_set else 0
        
        # Calculate recall (proportion of relevant docs that were retrieved)
        recall = true_positives / len(relevant_set) if relevant_set else 0
        
        # Calculate F1 (harmonic mean of precision and recall)
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        logger.info(f"Retrieval metrics - Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1:.2f}")
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
    
    @staticmethod
    def evaluate_citation_accuracy(expected_citations, actual_citations):
        """Evaluate citation accuracy.
        
        Args:
            expected_citations: List of expected citations
            actual_citations: List of actual citations in the response
            
        Returns:
            Dict containing citation accuracy metrics
        """
        # Calculate basic coverage
        expected_count = len(expected_citations)