# modules/citation.py
import re
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CitationHandler:
    def __init__(self):
        """Initialize citation handler."""
        # Regular expressions for identifying in-text citations
        self.citation_patterns = {
            "apa": r'\(([^,]+),\s*(\d{4})\)',  # (Author, Year)
            "mla": r'\(([^,]+)\s+(\d+)\)',      # (Author Page)
            "ieee": r'\[(\d+)\]'                # [Number]
        }
    
    def format_citation(self, metadata, style="APA"):
        """Format a citation based on document metadata and style.
        
        Args:
            metadata: Document metadata containing source information
            style: Citation style (APA, MLA, IEEE)
            
        Returns:
            Formatted citation string
        """
        style = style.upper()
        
        # Extract metadata
        title = metadata.get("title", "Unknown Title")
        source = metadata.get("source", "Unknown Source")
        authors = metadata.get("authors", ["Unknown Author"])
        year = metadata.get("year", datetime.now().year)
        publisher = metadata.get("publisher", "Unknown Publisher")
        url = metadata.get("url", "")
        
        # Handle author formatting
        if isinstance(authors, str):
            authors = [authors]
        
        if style == "APA":
            author_text = self._format_apa_authors(authors)
            citation = f"{author_text} ({year}). {title}. {publisher}."
            if url:
                citation += f" Retrieved from {url}."
                
        elif style == "MLA":
            author_text = self._format_mla_authors(authors)
            citation = f"{author_text}. \"{title}\". {publisher}, {year}."
            if url:
                citation += f" {url}."
                
        elif style == "IEEE":
            author_text = ", ".join(authors)
            citation = f"{author_text}, \"{title},\" {publisher}, {year}."
            if url:
                citation += f" [Online]. Available: {url}."
                
        else:
            logger.warning(f"Unknown citation style: {style}, defaulting to APA")
            return self.format_citation(metadata, style="APA")
            
        return citation
    
    def _format_apa_authors(self, authors):
        """Format authors for APA style."""
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    def _format_mla_authors(self, authors):
        """Format authors for MLA style."""
        if len(authors) == 1:
            return authors[0]
        else:
            return f"{authors[0]}, et al."
    
    def extract_citations(self, text, style="APA"):
        """Extract citation references from text.
        
        Args:
            text: Text containing citations
            style: Citation style
            
        Returns:
            List of extracted citations
        """
        style = style.lower()
        if style not in self.citation_patterns:
            logger.warning(f"Unknown citation style: {style}, defaulting to APA")
            style = "apa"
            
        pattern = self.citation_patterns[style]
        matches = re.findall(pattern, text)
        
        return matches
    
    def post_process_response(self, response, retrieved_docs, style="APA"):
        """Post-process response to ensure proper citations.
        
        This function can add missing citations or correct existing ones.
        
        Args:
            response: Generated response text
            retrieved_docs: Retrieved document chunks with metadata
            style: Citation style
            
        Returns:
            Post-processed response with proper citations
        """
        # Extract existing citations
        existing_citations = self.extract_citations(response, style)
        
        # Check if response already has citations
        if existing_citations:
            logger.info(f"Response contains {len(existing_citations)} citations")
            return response
            
        # If no citations found, add a references section
        logger.info("Adding references section to response")
        
        references = []
        for i, doc in enumerate(retrieved_docs):
            ref = self.format_citation(doc["metadata"], style)
            references.append(f"[{i+1}] {ref}")
        
        if references:
            references_text = "\n\n**References:**\n" + "\n".join(references)
            processed_response = response + references_text
            return processed_response
        
        return response