from typing import Dict, Any
from ..services.json_store import read_json, write_json

def get_profile() -> Dict[str, Any]:
    """Retrieve the user's profile information."""
    return read_json("profile.json")

def update_profile(name: str = None, email: str = None, location: str = None, 
                  professional_title: str = None, summary: str = None) -> Dict[str, Any]:
    """Update the user's profile information. Only provided fields are updated."""
    profile_data = read_json("profile.json")
    
    if name is not None: profile_data["name"] = name
    if email is not None: profile_data["email"] = email
    if location is not None: profile_data["location"] = location
    if professional_title is not None: profile_data["professional_title"] = professional_title
    if summary is not None: profile_data["summary"] = summary
    
    write_json("profile.json", profile_data)
    return profile_data
