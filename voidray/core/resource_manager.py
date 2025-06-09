
"""
VoidRay Resource Manager
Centralized resource management for assets, textures, sounds, etc.
"""

from typing import Dict, Any, Optional
import os
import weakref


class ResourceManager:
    """
    Centralized resource management system for the engine.
    Handles loading, caching, and cleanup of assets.
    """
    
    def __init__(self):
        self._resources: Dict[str, Any] = {}
        self._weak_refs: Dict[str, weakref.ref] = {}
        self._resource_paths: Dict[str, str] = {}
        
    def load_resource(self, resource_id: str, file_path: str, resource_type: str = "auto") -> Any:
        """
        Load a resource and cache it.
        
        Args:
            resource_id: Unique identifier for the resource
            file_path: Path to the resource file
            resource_type: Type of resource (auto, image, sound, text)
            
        Returns:
            Loaded resource
        """
        if resource_id in self._resources:
            return self._resources[resource_id]
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resource file not found: {file_path}")
            
        # Auto-detect resource type
        if resource_type == "auto":
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                resource_type = "image"
            elif ext in ['.wav', '.mp3', '.ogg']:
                resource_type = "sound"
            else:
                resource_type = "text"
        
        # Load based on type
        resource = None
        if resource_type == "image":
            import pygame
            resource = pygame.image.load(file_path)
        elif resource_type == "sound":
            import pygame
            resource = pygame.mixer.Sound(file_path)
        elif resource_type == "text":
            with open(file_path, 'r') as f:
                resource = f.read()
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
            
        self._resources[resource_id] = resource
        self._resource_paths[resource_id] = file_path
        
        print(f"Loaded resource: {resource_id} from {file_path}")
        return resource
    
    def get_resource(self, resource_id: str) -> Optional[Any]:
        """Get a cached resource."""
        return self._resources.get(resource_id)
    
    def unload_resource(self, resource_id: str):
        """Unload a resource from cache."""
        if resource_id in self._resources:
            del self._resources[resource_id]
            if resource_id in self._resource_paths:
                del self._resource_paths[resource_id]
    
    def clear_all(self):
        """Clear all cached resources."""
        self._resources.clear()
        self._resource_paths.clear()
        print("Cleared all cached resources")
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage statistics."""
        import sys
        total_size = 0
        resource_sizes = {}
        
        for resource_id, resource in self._resources.items():
            size = sys.getsizeof(resource)
            resource_sizes[resource_id] = size
            total_size += size
            
        return {
            'total_bytes': total_size,
            'total_mb': total_size / (1024 * 1024),
            'resource_count': len(self._resources),
            'individual_sizes': resource_sizes
        }
"""
VoidRay Resource Manager
Manages game resources like textures, sounds, and data files.
"""

from typing import Dict, Any, Optional
import pygame


class ResourceManager:
    """
    Manages loading and caching of game resources.
    """
    
    def __init__(self):
        self.resources: Dict[str, Any] = {}
        self.resource_paths: Dict[str, str] = {}
    
    def load_texture(self, name: str, path: str) -> Optional[pygame.Surface]:
        """
        Load a texture from file.
        
        Args:
            name: Resource name
            path: File path
            
        Returns:
            Loaded surface or None if failed
        """
        if name in self.resources:
            return self.resources[name]
        
        try:
            surface = pygame.image.load(path)
            self.resources[name] = surface
            self.resource_paths[name] = path
            return surface
        except:
            return None
    
    def get_resource(self, name: str) -> Optional[Any]:
        """
        Get a resource by name.
        
        Args:
            name: Resource name
            
        Returns:
            Resource or None if not found
        """
        return self.resources.get(name)
    
    def unload_resource(self, name: str):
        """
        Unload a resource from memory.
        
        Args:
            name: Resource name
        """
        if name in self.resources:
            del self.resources[name]
        if name in self.resource_paths:
            del self.resource_paths[name]
    
    def clear_all(self):
        """Clear all resources."""
        self.resources.clear()
        self.resource_paths.clear()
