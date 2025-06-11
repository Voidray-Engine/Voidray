
"""
VoidRay Engine Compatibility Layer
Ensures backward compatibility with older versions of games.
"""

import warnings
from typing import Any, Dict, Optional


class CompatibilityManager:
    """
    Manages backward compatibility for different engine versions.
    """
    
    def __init__(self):
        self.version_warnings = set()
    
    def check_deprecated_method(self, method_name: str, version: str = "3.0", replacement: str = None):
        """Check if a method is deprecated and show warning."""
        warning_key = f"{method_name}_{version}"
        if warning_key not in self.version_warnings:
            self.version_warnings.add(warning_key)
            replacement_text = f" Use {replacement} instead." if replacement else ""
            warnings.warn(
                f"{method_name} is deprecated since version {version}.{replacement_text}",
                DeprecationWarning,
                stacklevel=3
            )
    
    def wrap_legacy_method(self, old_method: Any, new_method: Any, method_name: str):
        """Wrap legacy methods to maintain compatibility."""
        def wrapper(*args, **kwargs):
            self.check_deprecated_method(method_name, replacement=new_method.__name__)
            return new_method(*args, **kwargs)
        return wrapper


# Global compatibility manager
compatibility_manager = CompatibilityManager()


def ensure_backward_compatibility(engine):
    """
    Ensure the engine maintains backward compatibility.
    
    Args:
        engine: The VoidRay engine instance
    """
    # Add legacy method aliases
    if not hasattr(engine, 'get_current_fps'):
        engine.get_current_fps = compatibility_manager.wrap_legacy_method(
            None, engine.get_fps, 'get_current_fps'
        )
    
    if not hasattr(engine, 'get_object_count'):
        engine.get_object_count = compatibility_manager.wrap_legacy_method(
            None, engine.get_scene_object_count, 'get_object_count'
        )
    
    # Ensure scene compatibility
    if hasattr(engine, 'current_scene') and engine.current_scene:
        scene = engine.current_scene
        if not hasattr(scene, 'game_objects'):
            scene.game_objects = scene.objects  # Alias for older games
    
    # Physics compatibility
    if hasattr(engine, 'physics_engine'):
        physics = engine.physics_engine
        if not hasattr(physics, 'world'):
            physics.world = physics  # Self-reference for older physics calls
    
    print("Backward compatibility ensured")


def get_compatible_engine_api():
    """
    Get a dictionary of compatible API methods for older games.
    """
    return {
        'version': '3.1.0',
        'compatible_versions': ['2.0', '2.1', '2.5', '3.0'],
        'deprecated_methods': {
            'get_current_fps': 'get_fps',
            'get_object_count': 'get_scene_object_count',
            'engine.world': 'engine.physics_engine',
            'scene.game_objects': 'scene.objects'
        }
    }
