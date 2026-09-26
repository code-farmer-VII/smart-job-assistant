import uuid
import datetime
from typing import List, Dict, Any
from ..services.json_store import get_items, get_item, add_item

def list_jobs() -> List[Dict[str, Any]]:
    """Retrieve the list of saved jobs."""
    return get_items("jobs.json")

def get_job(job_id: str) -> Dict[str, Any]:
    """Retrieve details for a specific job by ID."""
    job = get_item("jobs.json", job_id)
    if not job:
        return {"error": f"Job {job_id} not found."}
    return job

def add_job(title: str, company: str, location: str, description: str, 
            requirements: List[str]) -> Dict[str, Any]:
    """Save a new job listing to track."""
    job = {
        "id": f"job-{uuid.uuid4().hex[:8]}",
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "requirements": requirements,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    return add_item("jobs.json", job)
