"""
VoidRay Engine Configuration
Centralized configuration management for the engine.
"""

import json
import os
from typing import Dict, Any, Optional


class EngineConfig:
    """
    Engine configuration management.
    """

    def __init__(self):
        self.config_data: Dict[str, Any] = {
            'graphics': {
                'vsync': True,
                'fullscreen': False,
                'show_fps': False
            },
            'audio': {
                'master_volume': 1.0,
                'music_volume': 0.8,
                'sfx_volume': 1.0
            },
            'physics': {
                'gravity': 0,
                'time_scale': 1.0,
                'max_velocity': 2000
            },
            'performance': {
                'performance_mode': False,
                'render_distance': 1000,
                'max_objects': 1000
            }
        }

    def load_from_file(self, filepath: str) -> bool:
        """
        Load configuration from JSON file.

        Args:
            filepath: Path to config file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self._merge_config(loaded_config)
                return True
        except Exception as e:
            print(f"Failed to load config from {filepath}: {e}")
        return False

    def save_to_file(self, filepath: str) -> bool:
        """
        Save configuration to JSON file.

        Args:
            filepath: Path to save config file

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save config to {filepath}: {e}")
            return False

    def get(self, section: str, key: str, default=None) -> Any:
        """
        Get a configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        return self.config_data.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any):
        """
        Set a configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self.config_data:
            self.config_data[section] = {}
        self.config_data[section][key] = value

    def _merge_config(self, loaded_config: Dict[str, Any]):
        """Merge loaded config with defaults."""
        for section, values in loaded_config.items():
            if section in self.config_data:
                self.config_data[section].update(values)
            else:
                self.config_data[section] = values