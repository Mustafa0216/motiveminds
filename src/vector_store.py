import os
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

# Data Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAQ_PATH = os.path.join(BASE_DIR, "data", "faq.txt")
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

def get_embeddings_model():
    """Initializes and returns the embedding model based on available environment keys.
    Supports Google Gemini (default) or OpenAI.
    """
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # If the user inputted an override API key in Streamlit
    if "google_api_key_override" in st.session_state and st.session_state.google_api_key_override:
        google_api_key = st.session_state.google_api_key_override
    if "openai_api_key_override" in st.session_state and st.session_state.openai_api_key_override:
        openai_api_key = st.session_state.openai_api_key_override

    if google_api_key and google_api_key != "your_api_key_here":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=google_api_key)
    elif openai_api_key and openai_api_key != "your_openai_api_key_here":
        from langchain_openai import OpenAIEmbeddings
        openai_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        return OpenAIEmbeddings(openai_api_key=openai_api_key, openai_api_base=openai_api_base)
    else:
        raise ValueError("No valid API Key (GOOGLE_API_KEY or OPENAI_API_KEY) found in environment or session state.")

def initialize_vector_store():
    """Reads faq.txt, chunks it, embeds it, and stores it in ChromaDB if not already initialized.
    No print/console statements are used to protect data exposure.
    """
    # Create data dir if needed
    os.makedirs(os.path.dirname(CHROMA_DIR), exist_ok=True)
    
    embeddings = get_embeddings_model()
    
    # Check if DB already exists and contains documents
    if os.path.exists(CHROMA_DIR) and len(os.listdir(CHROMA_DIR)) > 0:
        # DB exists, just load it
        return Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
        
    if not os.path.exists(FAQ_PATH):
        # Create a basic fallback file if faq.txt is missing
        with open(FAQ_PATH, "w", encoding="utf-8") as f:
            f.write("MotiveMinds FAQ\nNo FAQ content available.")

    # Read and split document
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        text = f.read()
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    docs = text_splitter.create_documents([text])
    
    # Build Chroma DB
    db = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    return db

def get_retriever():
    """Returns a retriever object from ChromaDB.
    Search configurations are set to retrieve top 3 matches.
    """
    db = initialize_vector_store()
    # No console print statements are executed here to prevent leaking queries/chunks
    return db.as_retriever(search_kwargs={"k": 3})
