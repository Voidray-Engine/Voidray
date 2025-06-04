"""
VoidRay GameObject
Base class for all game objects in the VoidRay engine.
"""

from typing import List, Optional, TYPE_CHECKING
from ..math.vector2 import Vector2
from ..math.transform import Transform

if TYPE_CHECKING:
    from .scene import Scene


class GameObject:
    """
    Base class for all game objects. Provides basic functionality for
    position, rotation, scale, and hierarchical relationships.
    """
    
    def __init__(self, name: str = "GameObject"):
        """
        Initialize a new GameObject.
        
        Args:
            name: Name identifier for this object
        """
        self.name = name
        self.active = True
        
        # Transform component
        self.transform = Transform()
        
        # 2.5D properties
        self.z_order = 0  # Higher values render on top
        self.layer = "default"  # Layer for grouping and sorting
        self.depth_scale = 1.0  # Scale factor based on depth for 2.5D effect
        
        # Hierarchy
        self.parent: Optional['GameObject'] = None
        self.children: List['GameObject'] = []
        
        # Scene reference
        self.scene: Optional['Scene'] = None
        
        # Component system (simple tag-based for now)
        self.tags: List[str] = []
    
    def update(self, delta_time: float):
        """
        Update this game object. Override in subclasses.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        if not self.active:
            return
        
        # Update all children
        for child in self.children:
            child.update(delta_time)
    
    def render(self, renderer):
        """
        Render this game object. Override in subclasses.
        
        Args:
            renderer: The renderer to draw with
        """
        if not self.active:
            return
        
        # Render all children
        for child in self.children:
            child.render(renderer)
    
    def add_child(self, child: 'GameObject'):
        """
        Add a child object to this GameObject.
        
        Args:
            child: The child GameObject to add
        """
        if child.parent:
            child.parent.remove_child(child)
        
        child.parent = self
        child.scene = self.scene
        self.children.append(child)
    
    def remove_child(self, child: 'GameObject'):
        """
        Remove a child object from this GameObject.
        
        Args:
            child: The child GameObject to remove
        """
        if child in self.children:
            child.parent = None
            self.children.remove(child)
    
    def get_child(self, name: str) -> Optional['GameObject']:
        """
        Find a child by name.
        
        Args:
            name: Name of the child to find
            
        Returns:
            The child GameObject or None if not found
        """
        for child in self.children:
            if child.name == name:
                return child
        return None
    
    def get_children_with_tag(self, tag: str) -> List['GameObject']:
        """
        Get all children with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of GameObjects with the specified tag
        """
        return [child for child in self.children if tag in child.tags]
    
    def add_tag(self, tag: str):
        """
        Add a tag to this GameObject.
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """
        Remove a tag from this GameObject.
        
        Args:
            tag: Tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if this GameObject has a specific tag.
        
        Args:
            tag: Tag to check for
            
        Returns:
            True if the object has the tag, False otherwise
        """
        return tag in self.tags
    
    def get_world_position(self) -> Vector2:
        """
        Get the world position of this GameObject.
        
        Returns:
            World position as Vector2
        """
        if self.parent:
            return self.parent.get_world_position() + self.transform.position
        return self.transform.position.copy()
    
    def get_world_scale(self) -> Vector2:
        """
        Get the world scale of this GameObject.
        
        Returns:
            World scale as Vector2
        """
        if self.parent:
            parent_scale = self.parent.get_world_scale()
            return Vector2(
                self.transform.scale.x * parent_scale.x,
                self.transform.scale.y * parent_scale.y
            )
        return self.transform.scale.copy()
    
    def get_world_rotation(self) -> float:
        """
        Get the world rotation of this GameObject.
        
        Returns:
            World rotation in degrees
        """
        if self.parent:
            return self.parent.get_world_rotation() + self.transform.rotation
        return self.transform.rotation
    
    def get_depth_scale(self) -> float:
        """
        Get the depth-based scale for 2.5D effects.
        
        Returns:
            Scale factor based on depth
        """
        if self.parent:
            return self.parent.get_depth_scale() * self.depth_scale
        return self.depth_scale
    
    def set_z_order(self, z_order: int):
        """
        Set the Z-order (depth) of this object.
        
        Args:
            z_order: Higher values render on top
        """
        self.z_order = z_order
    
    def set_layer(self, layer: str):
        """
        Set the rendering layer of this object.
        
        Args:
            layer: Layer name
        """
        self.layer = layer
    
    def destroy(self):
        """
        Mark this GameObject for destruction and remove from parent.
        """
        if self.parent:
            self.parent.remove_child(self)
        
        if self.scene:
            self.scene.remove_object(self)
        
        # Destroy all children
        for child in self.children.copy():
            child.destroy()
        
        self.active = False
    
    def __str__(self) -> str:
        return f"GameObject(name='{self.name}', active={self.active})"
    
    def __repr__(self) -> str:
        return self.__str__()
