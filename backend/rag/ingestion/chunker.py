"""
Document Chunker Module
=======================
Splits loaded documents into smaller, semantically meaningful chunks
for optimal vector search retrieval.
"""

import logging
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Splits documents into retrieval-friendly chunks.
    
    Strategy:
    - Short documents (< 500 chars) like skills, profile entries are kept whole.
    - Longer documents like experience descriptions are split with overlap
      to preserve context across chunk boundaries.
    """
    if not documents:
        logger.warning("No documents to chunk.")
        return []

    short_docs = []
    long_docs = []

    for doc in documents:
        if len(doc.page_content) < 500:
            short_docs.append(doc)
        else:
            long_docs.append(doc)

    # Only split longer documents
    chunks = list(short_docs)  # Keep short docs intact

    if long_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        split_chunks = text_splitter.split_documents(long_docs)
        chunks.extend(split_chunks)

    logger.info(
        f"Chunking complete: {len(short_docs)} kept whole, "
        f"{len(long_docs)} split into {len(chunks) - len(short_docs)} chunks. "
        f"Total: {len(chunks)}"
    )

    return chunks
