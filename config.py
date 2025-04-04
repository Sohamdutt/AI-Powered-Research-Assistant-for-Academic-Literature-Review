# config.py
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
PAPERS_DIR = DATA_DIR / "papers"
MODEL_DIR = BASE_DIR / "models"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(PAPERS_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Default configurations
DEFAULT_CONFIG = {
    # Document processing
    "CHUNK_SIZE": 1000,
    "CHUNK_OVERLAP": 200,
    
    # Embeddings
    "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
    
    # LLM
    "DEFAULT_LLM_PATH": str(MODEL_DIR / "llama-2-7b.gguf"),
    "MAX_TOKENS": 1024,
    "TEMPERATURE": 0.7,
    
    # Retrieval
    "DEFAULT_NUM_RESULTS": 5,
    
    # Citation
    "DEFAULT_CITATION_STYLE": "APA",
    
    # UI
    "PAGE_TITLE": "Academic Research Assistant",
    "PAGE_ICON": "📚"
}

# Environment variable overrides
for key, default_value in DEFAULT_CONFIG.items():
    env_var = f"RESEARCH_ASSISTANT_{key}"
    if env_var in os.environ:
        DEFAULT_CONFIG[key] = os.environ[env_var]
