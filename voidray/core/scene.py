"""
VoidRay Scene Management
Manages collections of GameObjects and provides scene lifecycle methods.
"""

from typing import List, Optional, TYPE_CHECKING
from .game_object import GameObject

if TYPE_CHECKING:
    from .engine import Engine


class Scene:
    """
    A Scene contains and manages a collection of GameObjects.
    Scenes provide lifecycle methods and object management.
    """
    
    def __init__(self, name: str = "Scene"):
        """
        Initialize a new Scene.
        
        Args:
            name: Name identifier for this scene
        """
        self.name = name
        self.engine: Optional['Engine'] = None
        self.objects: List[GameObject] = []
        self.active = True
    
    def on_enter(self):
        """
        Called when this scene becomes the active scene.
        Override in subclasses for custom behavior.
        """
        print(f"Entering scene: {self.name}")
    
    def on_exit(self):
        """
        Called when this scene is no longer the active scene.
        Override in subclasses for custom behavior.
        """
        print(f"Exiting scene: {self.name}")
    
    def update(self, delta_time: float):
        """
        Update all GameObjects in this scene.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        if not self.active:
            return
        
        # Update all root objects (children will be updated recursively)
        for obj in self.objects.copy():  # Copy to avoid modification during iteration
            if obj.active and obj.parent is None:  # Only update root objects
                obj.update(delta_time)
    
    def render(self, renderer):
        """
        Render all GameObjects in this scene.
        
        Args:
            renderer: The renderer to draw with
        """
        if not self.active:
            return
        
        # Render all root objects (children will be rendered recursively)
        for obj in self.objects:
            if obj.active and obj.parent is None:  # Only render root objects
                obj.render(renderer)
    
    def add_object(self, obj: GameObject):
        """
        Add a GameObject to this scene.
        
        Args:
            obj: The GameObject to add
        """
        if obj not in self.objects:
            obj.scene = self
            self.objects.append(obj)
    
    def remove_object(self, obj: GameObject):
        """
        Remove a GameObject from this scene.
        
        Args:
            obj: The GameObject to remove
        """
        if obj in self.objects:
            obj.scene = None
            self.objects.remove(obj)
    
    def find_object(self, name: str) -> Optional[GameObject]:
        """
        Find a GameObject by name.
        
        Args:
            name: Name of the object to find
            
        Returns:
            The GameObject or None if not found
        """
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None
    
    def find_objects_with_tag(self, tag: str) -> List[GameObject]:
        """
        Find all GameObjects with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of GameObjects with the specified tag
        """
        result = []
        for obj in self.objects:
            if obj.has_tag(tag):
                result.append(obj)
        return result
    
    def get_object_count(self) -> int:
        """
        Get the total number of GameObjects in this scene.
        
        Returns:
            Number of objects
        """
        return len(self.objects)
    
    def clear(self):
        """
        Remove all GameObjects from this scene.
        """
        for obj in self.objects.copy():
            obj.destroy()
        self.objects.clear()
    
    def __str__(self) -> str:
        return f"Scene(name='{self.name}', objects={len(self.objects)})"
    
    def __repr__(self) -> str:
        return self.__str__()
