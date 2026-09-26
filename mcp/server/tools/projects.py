import uuid
from typing import List, Dict, Any
from ..services.json_store import get_items, add_item

def get_projects() -> List[Dict[str, Any]]:
    """Retrieve the user's projects."""
    return get_items("projects.json")

def add_project(name: str, description: str, technologies: List[str], 
                github_url: str = "", project_url: str = "") -> Dict[str, Any]:
    """Add a new project to the user's profile."""
    proj = {
        "id": f"project-{uuid.uuid4().hex[:8]}",
        "name": name,
        "description": description,
        "technologies": technologies,
        "github_url": github_url,
        "project_url": project_url
    }
    return add_item("projects.json", proj)
