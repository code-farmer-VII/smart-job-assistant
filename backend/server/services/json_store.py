import json
import os
from typing import Dict, List, Any, Union

# Define the data directory relative to this file
# This assumes the file is in mcp/server/services/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, "data")

def _get_file_path(filename: str) -> str:
    """Returns the absolute path to the JSON data file."""
    return os.path.join(DATA_DIR, filename)

def read_json(filename: str) -> Union[Dict, List]:
    """
    Reads a JSON file and returns its contents.
    
    This abstraction ensures we can easily swap JSON storage for a 
    database (like PostgreSQL) later without changing the MCP tools.
    """
    path = _get_file_path(filename)
    if not os.path.exists(path):
        # We assume empty list as default, except for profile which is an object.
        # But to be safe, returning an empty dict if the filename is profile.json
        if filename == "profile.json":
            return {}
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {} if filename == "profile.json" else []

def write_json(filename: str, data: Union[Dict, List]) -> None:
    """
    Writes data back to a JSON file.
    """
    path = _get_file_path(filename)
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_items(filename: str) -> List[Dict]:
    """Retrieves all items from a list-based JSON file."""
    data = read_json(filename)
    if isinstance(data, list):
        return data
    return []

def get_item(filename: str, item_id: str) -> Any:
    """Retrieves a specific item by ID from a list-based JSON file."""
    items = get_items(filename)
    for item in items:
        if item.get("id") == item_id:
            return item
    return None

def add_item(filename: str, item: Dict) -> Dict:
    """
    Adds a new item to a list-based JSON file.
    """
    items = get_items(filename)
    items.append(item)
    write_json(filename, items)
    return item

def update_item(filename: str, item_id: str, item_data: Dict) -> Any:
    """
    Updates an existing item by ID in a list-based JSON file.
    """
    items = get_items(filename)
    for i, item in enumerate(items):
        if item.get("id") == item_id:
            items[i].update(item_data)
            write_json(filename, items)
            return items[i]
    return None

def delete_item(filename: str, item_id: str) -> bool:
    """
    Deletes an item by ID from a list-based JSON file.
    """
    items = get_items(filename)
    initial_length = len(items)
    items = [item for item in items if item.get("id") != item_id]
    
    if len(items) < initial_length:
        write_json(filename, items)
        return True
    return False
