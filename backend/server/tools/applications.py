import uuid
import datetime
from typing import List, Dict, Any
from ..services.json_store import get_items, add_item, update_item

def get_applications() -> List[Dict[str, Any]]:
    """Retrieve the list of job applications."""
    return get_items("applications.json")

def update_application_status(job_id: str, status: str) -> Dict[str, Any]:
    """
    Update the status of an application.
    Allowed statuses: SAVED, APPLIED, ASSESSMENT, INTERVIEW, OFFER, REJECTED, WITHDRAWN.
    If the application doesn't exist for the job_id, it is created.
    """
    valid_statuses = ["SAVED", "APPLIED", "ASSESSMENT", "INTERVIEW", "OFFER", "REJECTED", "WITHDRAWN"]
    if status not in valid_statuses:
        return {"error": f"Invalid status. Must be one of {valid_statuses}"}
        
    apps = get_items("applications.json")
    for app in apps:
        if app.get("job_id") == job_id:
            # Update existing
            return update_item("applications.json", app["id"], {
                "status": status,
                "updated_at": datetime.datetime.utcnow().isoformat()
            })
            
    # Create new if it doesn't exist
    new_app = {
        "id": f"application-{uuid.uuid4().hex[:8]}",
        "job_id": job_id,
        "status": status,
        "updated_at": datetime.datetime.utcnow().isoformat()
    }
    return add_item("applications.json", new_app)
