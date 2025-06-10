
import json
import os
from typing import Dict, Any, Optional, List


class SaveSystem:
    """
    Simple save/load system for game data.
    """
    
    def __init__(self, save_directory: str = "saves"):
        """
        Initialize the save system.
        
        Args:
            save_directory: Directory to store save files
        """
        self.save_directory = save_directory
        self._ensure_save_directory()
    
    def _ensure_save_directory(self):
        """Ensure save directory exists."""
        os.makedirs(self.save_directory, exist_ok=True)
    
    def save_game(self, slot_name: str, data: Dict[str, Any]) -> bool:
        """
        Save game data to a slot.
        
        Args:
            slot_name: Name of the save slot
            data: Data to save
            
        Returns:
            True if save was successful
        """
        try:
            filepath = os.path.join(self.save_directory, f"{slot_name}.json")
            
            # Add metadata
            save_data = {
                'timestamp': None,
                'version': '1.0',
                'data': data
            }
            
            # Add timestamp if available
            try:
                import time
                save_data['timestamp'] = time.time()
            except:
                pass
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"Game saved to slot: {slot_name}")
            return True
            
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    def load_game(self, slot_name: str) -> Optional[Dict[str, Any]]:
        """
        Load game data from a slot.
        
        Args:
            slot_name: Name of the save slot
            
        Returns:
            Loaded data or None if failed
        """
        try:
            filepath = os.path.join(self.save_directory, f"{slot_name}.json")
            
            if not os.path.exists(filepath):
                print(f"Save slot '{slot_name}' does not exist")
                return None
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            print(f"Game loaded from slot: {slot_name}")
            return save_data.get('data', {})
            
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None
    
    def delete_save(self, slot_name: str) -> bool:
        """
        Delete a save slot.
        
        Args:
            slot_name: Name of the save slot
            
        Returns:
            True if deletion was successful
        """
        try:
            filepath = os.path.join(self.save_directory, f"{slot_name}.json")
            
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Deleted save slot: {slot_name}")
                return True
            else:
                print(f"Save slot '{slot_name}' does not exist")
                return False
                
        except Exception as e:
            print(f"Failed to delete save: {e}")
            return False
    
    def list_saves(self) -> List[str]:
        """
        List all available save slots.
        
        Returns:
            List of save slot names
        """
        try:
            saves = []
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json'):
                    saves.append(filename[:-5])  # Remove .json extension
            return saves
        except:
            return []
    
    def get_save_info(self, slot_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a save slot.
        
        Args:
            slot_name: Name of the save slot
            
        Returns:
            Save information or None if failed
        """
        try:
            filepath = os.path.join(self.save_directory, f"{slot_name}.json")
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            return {
                'timestamp': save_data.get('timestamp'),
                'version': save_data.get('version', 'unknown'),
                'size_bytes': os.path.getsize(filepath)
            }
            
        except Exception as e:
            print(f"Failed to get save info: {e}")
            return None


# Global save system instance
save_system = SaveSystem()
