
"""
VoidRay Serialization Utilities
Basic serialization helpers for game data persistence.
"""

import json
import pickle
import os
from typing import Dict, Any, Optional


class SerializationUtils:
    """Basic serialization utilities for game data."""
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str) -> bool:
        """Save data as JSON file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save JSON to {file_path}: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Optional[Dict[str, Any]]:
        """Load data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load JSON from {file_path}: {e}")
            return None
    
    @staticmethod
    def save_binary(data: Any, file_path: str) -> bool:
        """Save data as binary file using pickle."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Failed to save binary to {file_path}: {e}")
            return False
    
    @staticmethod
    def load_binary(file_path: str) -> Optional[Any]:
        """Load data from binary file using pickle."""
        try:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Failed to load binary from {file_path}: {e}")
            return None


# Global save system instance for easy access
save_system = SerializationUtils()
    
    
