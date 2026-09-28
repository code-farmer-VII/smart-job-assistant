"""
Vector Store Retriever Module
=============================
Manages the ChromaDB vector store for semantic search over
the user's knowledge base documents.

Features:
- Raw-file-hash based change detection (hashes actual JSON files on disk)
- Deterministic document IDs to prevent duplicates
- Singleton embedding model for efficiency
- Hash stored outside chroma_db so DB resets don't lose change tracking
"""

import os
import hashlib
import logging
from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

# Resolve project root (4 levels up from backend/rag/retrieval/retriever.py)
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PERSIST_DIR = os.path.join(DATA_DIR, "chroma_db")

# Store hash file OUTSIDE chroma_db so it survives DB resets
HASH_FILE = os.path.join(DATA_DIR, ".kb_content_hash")

# JSON files that form the knowledge base (must match loader.py)
KNOWLEDGE_FILES = [
    "profile.json",
    "skills.json",
    "experience.json",
    "projects.json",
    "jobs.json",
    "applications.json",
]

# Singleton embedding model (expensive to load, reuse across calls)
_embeddings: Optional[HuggingFaceEmbeddings] = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Returns a cached embedding model instance."""
    global _embeddings
    if _embeddings is None:
        logger.info("Loading embedding model (all-MiniLM-L6-v2)...")
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        logger.info("Embedding model loaded.")
    return _embeddings


def _compute_raw_file_hash() -> str:
    """
    Computes a SHA-256 hash of all raw JSON knowledge base files on disk.
    
    This is more reliable than hashing formatted Document content because:
    - It catches ANY change to the source files (even whitespace or field order)
    - It's independent of formatter logic changes
    - It's fast since it reads raw bytes without parsing
    """
    hasher = hashlib.sha256()

    for filename in sorted(KNOWLEDGE_FILES):
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            # Include filename in hash so renamed files are detected
            hasher.update(filename.encode())
            with open(filepath, "rb") as f:
                hasher.update(f.read())
        else:
            # Missing file is also a "state" to track
            hasher.update(f"MISSING:{filename}".encode())

    return hasher.hexdigest()


def _read_stored_hash() -> Optional[str]:
    """Reads the previously stored content hash."""
    if os.path.exists(HASH_FILE):
        try:
            with open(HASH_FILE, "r") as f:
                return f.read().strip()
        except IOError:
            return None
    return None


def _write_stored_hash(content_hash: str) -> None:
    """Writes the current content hash to disk."""
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)
    with open(HASH_FILE, "w") as f:
        f.write(content_hash)


def _needs_reindex() -> tuple[bool, str]:
    """
    Checks whether the vector store needs to be rebuilt
    by comparing the current raw file hash with the stored hash.
    Returns (needs_reindex: bool, current_hash: str).
    """
    current_hash = _compute_raw_file_hash()
    stored_hash = _read_stored_hash()

    if stored_hash != current_hash:
        logger.info(f"Data changed! Stored hash: {stored_hash[:16] if stored_hash else 'None'}..., Current hash: {current_hash[:16]}...")
        return True, current_hash
    else:
        logger.info(f"Data unchanged (hash: {current_hash[:16]}...). Skipping re-index.")
        return False, current_hash


def reindex_vector_store(documents: List[Document], force: bool = False) -> Chroma:
    """
    Rebuilds the ChromaDB vector store from scratch when data has changed.
    
    Args:
        documents: The documents to index.
        force: If True, always re-index regardless of hash.
    
    Returns:
        The Chroma vector store instance.
    """
    embeddings = _get_embeddings()

    needs_rebuild, current_hash = _needs_reindex()

    vectorstore = Chroma(
        collection_name="smart_job_kb",
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
    )

    if not needs_rebuild and not force:
        return vectorstore

    logger.info(f"Re-indexing {len(documents)} documents into ChromaDB...")

    # Clear existing data
    existing_ids = vectorstore.get().get("ids", [])
    if existing_ids:
        vectorstore.delete(ids=existing_ids)
        logger.info(f"Cleared {len(existing_ids)} old entries")

    # Index fresh documents with deterministic IDs
    doc_ids = [
        f"doc-{i}-{hashlib.sha256(doc.page_content.encode()).hexdigest()[:12]}"
        for i, doc in enumerate(documents)
    ]
    vectorstore.add_documents(documents=documents, ids=doc_ids)

    # Save the hash so next time we skip re-indexing if nothing changed
    _write_stored_hash(current_hash)
    logger.info(f"Indexing complete. {len(documents)} documents stored.")

    return vectorstore


def get_chroma_retriever(documents: List[Document], force_reindex: bool = False) -> BaseRetriever:
    """
    Returns a LangChain retriever backed by ChromaDB.
    
    Only re-indexes if the raw data files have changed since the last index,
    or if force_reindex is True. Retrieves top-k most relevant documents
    where k is capped at 8 for focused retrieval.
    """
    if not documents:
        logger.warning("No documents provided. Retriever will return empty results.")
        embeddings = _get_embeddings()
        vectorstore = Chroma(
            collection_name="smart_job_kb",
            embedding_function=embeddings,
            persist_directory=PERSIST_DIR,
        )
        return vectorstore.as_retriever(search_kwargs={"k": 5})

    vectorstore = reindex_vector_store(documents, force=force_reindex)

    # Cap k at 8 for focused retrieval — avoids flooding the LLM context
    # with irrelevant documents from a small knowledge base
    k = min(len(documents), 8)
    return vectorstore.as_retriever(search_kwargs={"k": k})
