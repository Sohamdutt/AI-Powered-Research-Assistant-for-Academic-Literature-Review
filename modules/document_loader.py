# modules/document_loader.py
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        """Initialize document processor with chunking parameters.
        
        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
    
    def load_document(self, file_path):
        """Load document from file path."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                logger.info(f"Loading PDF document: {file_path}")
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                metadata = self._extract_pdf_metadata(file_path)
                
                # Add metadata to each page
                for page in pages:
                    page.metadata.update(metadata)
                    page.metadata["page"] = page.metadata.get("page", 0) + 1  # 1-indexed page numbers
                
                return pages
            
            elif file_extension in ['.txt', '.md', '.rst']:
                logger.info(f"Loading text document: {file_path}")
                loader = TextLoader(file_path)
                documents = loader.load()
                
                # Add basic metadata
                for doc in documents:
                    doc.metadata["source"] = file_path
                    doc.metadata["file_type"] = file_extension[1:]
                
                return documents
            
            else:
                logger.error(f"Unsupported file type: {file_extension}")
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise
    
    def chunk_documents(self, documents):
        """Split documents into chunks."""
        logger.info(f"Chunking {len(documents)} documents")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _extract_pdf_metadata(self, file_path):
        """Extract metadata from PDF file."""
        # This could be expanded with PyPDF2 or other libraries
        # to extract more detailed metadata
        return {
            "source": file_path,
            "file_type": "pdf",
            "title": os.path.basename(file_path).replace('.pdf', '')
        }
    
    def process_file(self, file_path):
        """Load and chunk a document file."""
        documents = self.load_document(file_path)
        chunks = self.chunk_documents(documents)
        return chunks