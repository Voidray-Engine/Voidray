
"""
VoidRay Simple Save System
Basic save/load system for game data.
"""

import json
import os
import pickle
from typing import Any, Dict, Optional


class SaveSystem:
    """Simple save system for game data."""
    
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = save_directory
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """Ensure the save directory exists."""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def save_json(self, data: Dict[str, Any], filename: str) -> bool:
        """Save data as JSON file."""
        try:
            file_path = os.path.join(self.save_directory, f"{filename}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"Game saved to {file_path}")
            return True
        except Exception as e:
            print(f"Failed to save game to {filename}: {e}")
            return False

    def load_json(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load data from JSON file."""
        try:
            file_path = os.path.join(self.save_directory, f"{filename}.json")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Game loaded from {file_path}")
            return data
        except FileNotFoundError:
            print(f"Save file {filename} not found")
            return None
        except Exception as e:
            print(f"Failed to load game from {filename}: {e}")
            return None

    def save_binary(self, data: Any, filename: str) -> bool:
        """Save data as binary file using pickle."""
        try:
            file_path = os.path.join(self.save_directory, f"{filename}.dat")
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"Binary data saved to {file_path}")
            return True
        except Exception as e:
            print(f"Failed to save binary data to {filename}: {e}")
            return False

    def load_binary(self, filename: str) -> Optional[Any]:
        """Load data from binary file using pickle."""
        try:
            file_path = os.path.join(self.save_directory, f"{filename}.dat")
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            print(f"Binary data loaded from {file_path}")
            return data
        except FileNotFoundError:
            print(f"Binary save file {filename} not found")
            return None
        except Exception as e:
            print(f"Failed to load binary data from {filename}: {e}")
            return None
    
    def list_saves(self) -> list:
        """List all available save files."""
        saves = []
        try:
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json') or filename.endswith('.dat'):
                    saves.append(filename)
        except OSError:
            pass
        return saves
    
    def delete_save(self, filename: str) -> bool:
        """Delete a save file."""
        try:
            json_path = os.path.join(self.save_directory, f"{filename}.json")
            dat_path = os.path.join(self.save_directory, f"{filename}.dat")
            
            deleted = False
            if os.path.exists(json_path):
                os.remove(json_path)
                deleted = True
            if os.path.exists(dat_path):
                os.remove(dat_path)
                deleted = True
                
            if deleted:
                print(f"Save file {filename} deleted")
                return True
            else:
                print(f"Save file {filename} not found")
                return False
        except Exception as e:
            print(f"Failed to delete save file {filename}: {e}")
            return False


# Global save system instance
save_system = SaveSystem()


# Legacy compatibility functions
def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """Legacy function for saving JSON data."""
    filename = os.path.splitext(os.path.basename(file_path))[0]
    return save_system.save_json(data, filename)


def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Legacy function for loading JSON data."""
    filename = os.path.splitext(os.path.basename(file_path))[0]
    return save_system.load_json(filename)


def save_binary(data: Any, file_path: str) -> bool:
    """Legacy function for saving binary data."""
    filename = os.path.splitext(os.path.basename(file_path))[0]
    return save_system.save_binary(data, filename)


def load_binary(file_path: str) -> Optional[Any]:
    """Legacy function for loading binary data."""
    filename = os.path.splitext(os.path.basename(file_path))[0]
    return save_system.load_binary(filename)
