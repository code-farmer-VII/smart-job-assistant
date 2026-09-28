"""
RAG Pipeline Module
===================
Assembles the full Retrieval-Augmented Generation pipeline:
  1. Load JSON data from the knowledge base
  2. Deduplicate entries
  3. Chunk documents for optimal retrieval
  4. Auto-detect changes and re-index into ChromaDB vector store
  5. Retrieve relevant context via semantic search
  6. Generate LLM response with retrieved context

The pipeline always loads fresh data from disk on each request,
but only re-embeds/re-indexes when the underlying files have changed.
"""

import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from .ingestion.loader import load_documents, DATA_DIR
from .ingestion.chunker import chunk_documents
from .retrieval.retriever import get_chroma_retriever
from .prompts.interview import INTERVIEW_PREP_PROMPT

logger = logging.getLogger(__name__)

# Configure logging so we can see RAG diagnostics in the terminal
logging.basicConfig(level=logging.INFO, format="%(name)s | %(levelname)s | %(message)s")

# Cache the LLM instance — it's stateless and expensive to recreate
_cached_llm = None


def _get_llm():
    """Returns a cached LLM instance (avoids re-initializing on every request)."""
    global _cached_llm
    if _cached_llm is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set properly in .env")

        _cached_llm = ChatGoogleGenerativeAI(
            model="gemini-3.8-flash",
            google_api_key=api_key,
            temperature=0.3,
            max_output_tokens=2048
        )
        logger.info("LLM initialized and cached (Gemini 3.8 Flash)")
    return _cached_llm


def _load_pinned_profile_context() -> str:
    """
    Reads profile.json directly from disk and formats it as a pinned context block.
    This guarantees the LLM always sees the user's real profile data,
    regardless of what the semantic search retrieves.
    """
    profile_path = os.path.join(DATA_DIR, "profile.json")
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        lines = [
            "=== PINNED USER PROFILE (always use this data) ===",
            f"Name: {data.get('name', 'N/A')}",
            f"Email: {data.get('email', 'N/A')}",
            f"Location: {data.get('location', 'N/A')}",
            f"Professional Title: {data.get('professional_title', 'N/A')}",
            f"Summary: {data.get('summary', 'N/A')}",
            "===================================================",
        ]
        pinned = "\n".join(lines)
        logger.info(f"Pinned profile loaded: {data.get('name', '?')} / {data.get('email', '?')}")
        return pinned
    except Exception as e:
        logger.error(f"Failed to load pinned profile: {e}")
        return ""


def _build_chain():
    """
    Builds the LCEL chain with fresh data from disk.
    
    On every call:
    - Reloads all JSON files (instant, guarantees fresh data)
    - Deduplicates entries (handled by loader)
    - Chunks documents (instant for this dataset size)
    - Checks raw file hash — only re-embeds/re-indexes if files changed
    - Reuses cached LLM and embedding model instances
    """
    # 1. Ingest: load all JSON knowledge base files (with deduplication)
    raw_docs = load_documents()
    logger.info(f"Loaded {len(raw_docs)} documents from knowledge base")

    if not raw_docs:
        raise RuntimeError(
            "No documents loaded from data directory. "
            "Check that JSON files exist and contain data."
        )

    # 2. Chunk: split long documents, keep short ones whole
    chunks = chunk_documents(raw_docs)
    logger.info(f"Created {len(chunks)} chunks for indexing")

    # 3. Index & Retrieve: auto-detects if data changed via file hash
    retriever = get_chroma_retriever(documents=chunks)

    # 4. LLM: get cached Gemini instance
    llm = _get_llm()

    # 5. Always pin the profile at the top, then append retrieved docs
    pinned_profile = _load_pinned_profile_context()

    def format_docs_with_pinned_profile(docs):
        logger.info(f"Retrieved {len(docs)} documents for this query")
        for i, doc in enumerate(docs):
            logger.info(f"  [{i}] ({doc.metadata.get('type', '?')}) {doc.page_content[:80]}...")
        retrieved_text = "\n\n".join(doc.page_content for doc in docs)
        # Profile is always at the top regardless of retrieval
        if pinned_profile:
            return pinned_profile + "\n\n" + retrieved_text
        return retrieved_text

    # 6. Assemble the LCEL chain
    rag_chain = (
        {"context": retriever | format_docs_with_pinned_profile, "question": RunnablePassthrough()}
        | INTERVIEW_PREP_PROMPT
        | llm
        | StrOutputParser()
    )

    return rag_chain


def run_interview_prep(user_prompt: str) -> str:
    """
    Public entry point: runs the full RAG pipeline for a user query.
    
    Always loads fresh data from JSON files on each call.
    Automatically detects if knowledge base files have changed and
    re-indexes the vector store only when needed (via SHA-256 file hash).
    """
    logger.info(f"RAG query: {user_prompt[:100]}...")
    chain = _build_chain()
    result = chain.invoke(user_prompt)
    logger.info(f"RAG response generated ({len(result)} chars)")
    return result


def force_reindex() -> str:
    """
    Force re-indexes the vector store from the current data files.
    Called by the /api/reindex endpoint.
    """
    logger.info("Forcing re-index of knowledge base...")
    raw_docs = load_documents()
    chunks = chunk_documents(raw_docs)
    get_chroma_retriever(documents=chunks, force_reindex=True)
    return f"Re-indexed {len(chunks)} chunks from {len(raw_docs)} documents."


if __name__ == "__main__":
    import sys
    query = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Prepare me for a senior full stack developer interview focusing on React, Python, and system design."
    )
    print(f"Generating interview prep for: '{query}'\n")
    print("-" * 40)
    print(run_interview_prep(query))
