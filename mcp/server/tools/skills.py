import uuid
from typing import List, Dict, Any
from ..services.json_store import get_items, add_item

def get_skills() -> List[Dict[str, Any]]:
    """Retrieve the user's list of skills."""
    return get_items("skills.json")

def add_skill(name: str, level: str) -> Dict[str, Any]:
    """Add a new skill to the user's profile."""
    skill = {
        "id": f"skill-{uuid.uuid4().hex[:8]}",
        "name": name,
        "level": level
    }
    return add_item("skills.json", skill)
