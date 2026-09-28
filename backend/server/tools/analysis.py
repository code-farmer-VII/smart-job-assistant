from typing import Dict, Any
from ..services.json_store import get_items, get_item, read_json

def get_job_analysis_context(job_id: str) -> Dict[str, Any]:
    """
    Retrieve all necessary context to perform a job analysis.
    This aggregates the specific job along with the user's profile, skills, 
    experience, and projects into a single payload.
    """
    job = get_item("jobs.json", job_id)
    if not job:
        return {"error": f"Job {job_id} not found."}
        
    return {
        "job": job,
        "profile": read_json("profile.json"),
        "skills": get_items("skills.json"),
        "experience": get_items("experience.json"),
        "projects": get_items("projects.json")
    }
