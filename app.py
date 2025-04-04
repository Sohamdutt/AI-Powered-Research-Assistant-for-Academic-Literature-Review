# app.py
import streamlit as st
import os
import tempfile
from modules.document_loader import DocumentProcessor
from modules.embeddings import EmbeddingGenerator
from modules.vector_store import VectorStore
from modules.query_processor import QueryProcessor
from modules.llm_interface import LLMInterface
from modules.citation import CitationHandler
import sys
sys.modules['torch'].__path__ = []

# Set page configuration
st.set_page_config(
    page_title="Academic Research Assistant",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.papers_added = 0
    st.session_state.chat_history = []

# App title and description
st.title("📚 AI-Powered Academic Research Assistant")
st.markdown("""
This tool helps researchers find and summarize academic literature with proper citations.
Upload papers, ask questions, and get cited answers based on the literature.
""")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # LLM model selection
    model_path = st.text_input(
        "LLM Model Path", 
        value=os.environ.get("LLM_MODEL_PATH", "models\mistral-7b.gguf"),
        help="Path to the LLM model file (Llama or Mistral)"
    )
    
    # Citation style
    citation_style = st.selectbox(
        "Citation Style",
        options=["APA", "MLA", "IEEE"],
        index=0,
        help="Select your preferred citation style"
    )
    
    # Document processing parameters
    st.subheader("Document Processing")
    chunk_size = st.slider(
        "Chunk Size", 
        min_value=500, 
        max_value=2000, 
        value=1000,
        help="Size of text chunks for processing"
    )
    
    chunk_overlap = st.slider(
        "Chunk Overlap", 
        min_value=0, 
        max_value=500, 
        value=200,
        help="Overlap between consecutive chunks"
    )
    
    # Number of results to retrieve
    n_results = st.slider(
        "Retrieved Documents", 
        min_value=3, 
        max_value=10, 
        value=5,
        help="Number of document chunks to retrieve per query"
    )
    
    # Initialize or reinitialize system
    if st.button("Initialize System"):
        with st.spinner("Initializing system components..."):
            # Create temporary or persistent directories
            os.makedirs("data/papers", exist_ok=True)
            os.makedirs("data/vector_db", exist_ok=True)
            
            # Initialize components
            st.session_state.doc_processor = DocumentProcessor(
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap
            )
            
            st.session_state.embedding_generator = EmbeddingGenerator()
            st.session_state.vector_store = VectorStore(db_directory="./data/vector_db")
            
            st.session_state.query_processor = QueryProcessor(
                embedding_generator=st.session_state.embedding_generator,
                vector_store=st.session_state.vector_store
            )
            
            try:
                st.session_state.llm_interface = LLMInterface(model_path=model_path)
                st.session_state.citation_handler = CitationHandler()
                st.session_state.initialized = True
                st.success("System initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing LLM: {str(e)}")
    
    st.markdown("---")
    st.markdown("### Paper Upload")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload Academic Papers", 
        type=["pdf", "txt"], 
        accept_multiple_files=True
    )
    
    # Process uploaded files
    if uploaded_files and st.session_state.initialized:
        process_button = st.button("Process Papers")
        if process_button:
            with st.spinner("Processing papers..."):
                for uploaded_file in uploaded_files:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name
                    
                    try:
                        # Process the document
                        chunks = st.session_state.doc_processor.process_file(temp_path)
                        
                        # Generate embeddings
                        texts = [chunk.page_content for chunk in chunks]
                        
                        # Add to vector store
                        st.session_state.vector_store.add_documents(chunks)
                        st.session_state.papers_added += 1
                        
                        # Clean up
                        os.unlink(temp_path)
                        
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                
                st.success(f"Processed {len(uploaded_files)} papers successfully!")
    
    # Display stats
    if st.session_state.initialized:
        st.markdown(f"Papers added: {st.session_state.papers_added}")

# Main area: Chat interface
if not st.session_state.initialized:
    st.warning("Please initialize the system using the sidebar controls.")
else:
    # Display chat history
    for i, (query, response) in enumerate(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(query)
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Query input
    user_query = st.chat_input("Ask a research question...")
    
    if user_query:
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)
        
        # Process query and generate response
        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                # Process query
                retrieved_docs = st.session_state.query_processor.process_query(
                    user_query, 
                    n_results=n_results
                )
                
                # Create prompt
                prompt = st.session_state.llm_interface.create_prompt(
                    query=user_query,
                    retrieved_docs=retrieved_docs,
                    citation_style=citation_style
                )
                
                # Generate response
                response = st.session_state.llm_interface.generate_response(prompt)
                
                # Post-process to ensure citations
                final_response = st.session_state.citation_handler.post_process_response(
                    response=response,
                    retrieved_docs=retrieved_docs,
                    style=citation_style
                )
                
                # Display response
                st.markdown(final_response)
                
                # Add to chat history
                st.session_state.chat_history.append((user_query, final_response))