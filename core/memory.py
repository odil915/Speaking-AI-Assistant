import json
import os

MEMORY_FILE = "chat_history.json"

def load_memory():
    """
    Loads chat history from the JSON file.
    Returns an empty list if file doesn't exist.
    """
    if not os.path.exists(MEMORY_FILE):
        return []
        
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading memory: {e}")
        return []

def save_memory(history):
    """
    Saves the current chat history list to JSON file.
    """
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving memory: {e}")

def clear_memory():
    """
    Wipes the memory file by saving an empty list.
    """
    save_memory([])
