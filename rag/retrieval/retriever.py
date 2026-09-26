import os
from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_chroma_retriever(documents: List[Document]) -> BaseRetriever:
    """
    Creates or updates a Chroma vector database from the provided documents.
    Returns a LangChain retriever interface for LCEL chaining.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is not set properly in .env")

    # Initialize Gemini Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", 
        google_api_key=api_key
    )
    
    # Persist directory for ChromaDB
    persist_directory = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "chroma_db"
    )
    
    # Create vector store and ingest documents
    # If no documents are passed, it will just load the existing DB
    if documents:
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_directory
        )
    else:
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        
    # Return a retriever that fetches the top 5 most similar chunks
    return vectorstore.as_retriever(search_kwargs={"k": 5})
