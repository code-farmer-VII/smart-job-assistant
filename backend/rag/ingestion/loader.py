"""
Data Loader Module
==================
Loads structured JSON data files from the project's data directory
and converts them into LangChain Document objects for RAG ingestion.
"""

import os
import json
import logging
from typing import List, Dict, Any
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Resolve project root: smart-job-assistant/
# loader.py is at: backend/rag/ingestion/loader.py
# So we need 4 levels up to reach project root
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# JSON files that form the RAG knowledge base
KNOWLEDGE_FILES = [
    "profile.json",
    "skills.json",
    "experience.json",
    "projects.json",
    "jobs.json",
    "applications.json",
]


def _format_profile(data: Dict[str, Any]) -> str:
    """Formats profile.json (a single dict) into a human-readable text block."""
    lines = [
        f"Name: {data.get('name', 'N/A')}",
        f"Email: {data.get('email', 'N/A')}",
        f"Location: {data.get('location', 'N/A')}",
        f"Professional Title: {data.get('professional_title', 'N/A')}",
        f"Summary: {data.get('summary', 'N/A')}",
    ]
    return "USER PROFILE INFORMATION\n" + "\n".join(lines)


def _format_skill(item: Dict[str, Any]) -> str:
    """Formats a single skill entry."""
    return f"Skill: {item.get('name', 'N/A')} | Level: {item.get('level', 'N/A')}"


def _format_experience(item: Dict[str, Any]) -> str:
    """Formats a single experience entry."""
    techs = ", ".join(item.get("technologies", []))
    lines = [
        f"Company: {item.get('company', 'N/A')}",
        f"Position: {item.get('position', 'N/A')}",
        f"Period: {item.get('start_date', '?')} to {item.get('end_date', '?')}",
        f"Description: {item.get('description', 'N/A')}",
        f"Technologies: {techs}" if techs else "",
    ]
    return "WORK EXPERIENCE\n" + "\n".join(l for l in lines if l)


def _format_project(item: Dict[str, Any]) -> str:
    """Formats a single project entry."""
    techs = ", ".join(item.get("technologies", []))
    lines = [
        f"Project: {item.get('name', 'N/A')}",
        f"Description: {item.get('description', 'N/A')}",
        f"Technologies: {techs}" if techs else "",
        f"GitHub: {item.get('github_url', '')}" if item.get("github_url") else "",
        f"Live URL: {item.get('project_url', '')}" if item.get("project_url") else "",
    ]
    return "PROJECT\n" + "\n".join(l for l in lines if l)


def _format_job(item: Dict[str, Any]) -> str:
    """Formats a single job listing entry."""
    reqs = ", ".join(item.get("requirements", []))
    lines = [
        f"Job Title: {item.get('title', 'N/A')}",
        f"Company: {item.get('company', 'N/A')}",
        f"Location: {item.get('location', 'N/A')}",
        f"Description: {item.get('description', 'N/A')}",
        f"Requirements: {reqs}" if reqs else "",
    ]
    return "JOB LISTING\n" + "\n".join(l for l in lines if l)


def _format_application(item: Dict[str, Any]) -> str:
    """Formats a single application entry."""
    lines = [
        f"Application ID: {item.get('id', 'N/A')}",
        f"Job ID: {item.get('job_id', 'N/A')}",
        f"Status: {item.get('status', 'N/A')}",
        f"Last Updated: {item.get('updated_at', 'N/A')}",
    ]
    return "APPLICATION STATUS\n" + "\n".join(lines)


# Map each file to its formatting strategy
_FORMATTERS = {
    "skills.json": ("SKILL", _format_skill),
    "experience.json": ("EXPERIENCE", _format_experience),
    "projects.json": ("PROJECT", _format_project),
    "jobs.json": ("JOB", _format_job),
    "applications.json": ("APPLICATION", _format_application),
}


def load_json_file(filename: str) -> List[Document]:
    """
    Loads a single JSON file and converts it into LangChain Documents.
    Uses structured formatting so the LLM receives clean, labeled context.
    """
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        logger.warning(f"Data file not found: {path}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load {filename}: {e}")
        return []

    documents = []

    if filename == "profile.json" and isinstance(data, dict):
        # Profile is a single object — always include it
        content = _format_profile(data)
        documents.append(Document(
            page_content=content,
            metadata={"source": filename, "type": "profile", "id": data.get("id", "")}
        ))

    elif isinstance(data, list):
        formatter_info = _FORMATTERS.get(filename)
        for item in data:
            if not isinstance(item, dict):
                continue
            # Skip items with all empty values (placeholder entries)
            has_content = any(
                v for k, v in item.items()
                if k != "id" and v and v != [] and v != ""
            )
            if not has_content:
                continue

            if formatter_info:
                doc_type, formatter = formatter_info
                content = formatter(item)
            else:
                # Generic fallback
                content = "\n".join(f"{k}: {v}" for k, v in item.items() if v and k != "id")

            documents.append(Document(
                page_content=content,
                metadata={"source": filename, "type": doc_type if formatter_info else "unknown", "id": item.get("id", "")}
            ))

    logger.info(f"Loaded {len(documents)} documents from {filename}")
    return documents


def _deduplicate_documents(documents: List[Document]) -> List[Document]:
    """
    Removes duplicate documents based on their page_content.
    
    Keeps the first occurrence of each unique content string.
    This handles cases like:
    - Same skill listed multiple times with different IDs
    - Identical experience entries appearing more than once
    """
    seen_content = set()
    unique_docs = []
    duplicates_removed = 0

    for doc in documents:
        # Normalize content for comparison (strip whitespace)
        content_key = doc.page_content.strip()
        if content_key not in seen_content:
            seen_content.add(content_key)
            unique_docs.append(doc)
        else:
            duplicates_removed += 1
            logger.debug(
                f"Removed duplicate: {doc.metadata.get('type', '?')} "
                f"(id={doc.metadata.get('id', '?')})"
            )

    if duplicates_removed > 0:
        logger.info(
            f"Deduplication: removed {duplicates_removed} duplicates, "
            f"{len(unique_docs)} unique documents remain"
        )

    return unique_docs


def load_documents() -> List[Document]:
    """
    Loads all JSON data files from the knowledge base directory
    and converts them into LangChain Documents for RAG ingestion.
    Automatically deduplicates entries with identical content.
    """
    documents = []

    logger.info(f"Loading knowledge base from: {DATA_DIR}")

    for filename in KNOWLEDGE_FILES:
        docs = load_json_file(filename)
        documents.extend(docs)

    logger.info(f"Total documents loaded (before dedup): {len(documents)}")

    # Remove duplicate entries (e.g. same skill listed multiple times)
    documents = _deduplicate_documents(documents)

    logger.info(f"Total documents after dedup: {len(documents)}")

    if not documents:
        logger.warning(
            f"No documents were loaded! Check that data files exist in: {DATA_DIR}"
        )

    return documents

