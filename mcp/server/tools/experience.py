import uuid
from typing import List, Dict, Any
from ..services.json_store import get_items, add_item

def get_experience() -> List[Dict[str, Any]]:
    """Retrieve the user's work experience history."""
    return get_items("experience.json")

def add_experience(company: str, position: str, start_date: str, end_date: str, 
                   description: str, technologies: List[str]) -> Dict[str, Any]:
    """Add a new work experience entry."""
    exp = {
        "id": f"experience-{uuid.uuid4().hex[:8]}",
        "company": company,
        "position": position,
        "start_date": start_date,
        "end_date": end_date,
        "description": description,
        "technologies": technologies
    }
    return add_item("experience.json", exp)
