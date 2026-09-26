import os
import json
from typing import List
from langchain_core.documents import Document

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")

def load_json_file(filename: str) -> List[Document]:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []

    documents = []
    
    if isinstance(data, dict):
        # Convert dictionary to a single Document (e.g. profile.json)
        content = "\n".join([f"{k}: {v}" for k, v in data.items() if v])
        if content.strip():
            documents.append(Document(
                page_content=f"--- {filename.upper()} ---\n{content}",
                metadata={"source": filename}
            ))
    elif isinstance(data, list):
        # Convert list of objects into multiple Documents (e.g. skills, experience)
        for item in data:
            if not isinstance(item, dict):
                continue
            content = "\n".join([f"{k}: {v}" for k, v in item.items() if v and k != "id"])
            if content.strip():
                documents.append(Document(
                    page_content=f"--- {filename.upper()} ITEM ---\n{content}",
                    metadata={"source": filename, "id": item.get("id", "")}
                ))
                
    return documents

def load_documents() -> List[Document]:
    """
    Loads JSON data files from the MCP data directory and converts them into LangChain Documents.
    This ensures RAG uses the exact same data source as the MCP tools.
    """
    documents = []
    
    json_files = [
        "profile.json", 
        "skills.json", 
        "experience.json", 
        "projects.json", 
        "jobs.json"
    ]
    
    for filename in json_files:
        documents.extend(load_json_file(filename))
        
    return documents
