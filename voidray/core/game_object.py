
"""
VoidRay GameObject System
Base class for all entities in the game world.
"""

from typing import List, Optional, Dict, Any, Type
from .component import Component
from ..math.transform import Transform


class GameObject:
    """
    Base class for all game objects.
    Uses a component-based architecture for modular functionality.
    """
    
    def __init__(self, name: str = "GameObject"):
        """
        Initialize the game object.
        
        Args:
            name: Name identifier for this object
        """
        self.name = name
        self.active = True
        self.transform = Transform()
        self.components: Dict[Type[Component], Component] = {}
        self.scene = None
        
        # Layer and rendering
        self.layer = "world"
        self.z_order = 0
        self.tags = set()
        
        # Lifecycle flags
        self._started = False
        self._destroyed = False
    
    def add_component(self, component: Component):
        """
        Add a component to this game object.
        
        Args:
            component: Component instance to add
        """
        component_type = type(component)
        
        if component_type in self.components:
            print(f"Warning: GameObject '{self.name}' already has component {component_type.__name__}")
            return
        
        self.components[component_type] = component
        component.game_object = self
        
        # Call component initialization
        if hasattr(component, 'on_add'):
            component.on_add()
    
    def remove_component(self, component_type: Type[Component]):
        """
        Remove a component from this game object.
        
        Args:
            component_type: Type of component to remove
        """
        if component_type in self.components:
            component = self.components[component_type]
            
            # Call component cleanup
            if hasattr(component, 'on_remove'):
                component.on_remove()
            
            component.game_object = None
            del self.components[component_type]
    
    def get_component(self, component_type: Type[Component]) -> Optional[Component]:
        """
        Get a component of the specified type.
        
        Args:
            component_type: Type of component to get
            
        Returns:
            Component instance or None if not found
        """
        return self.components.get(component_type)
    
    def has_component(self, component_type: Type[Component]) -> bool:
        """
        Check if this object has a component of the specified type.
        
        Args:
            component_type: Type of component to check
            
        Returns:
            True if component exists, False otherwise
        """
        return component_type in self.components
    
    def get_components(self) -> List[Component]:
        """
        Get all components attached to this game object.
        
        Returns:
            List of all components
        """
        return list(self.components.values())
    
    def add_tag(self, tag: str):
        """
        Add a tag to this game object.
        
        Args:
            tag: Tag to add
        """
        self.tags.add(tag)
    
    def remove_tag(self, tag: str):
        """
        Remove a tag from this game object.
        
        Args:
            tag: Tag to remove
        """
        self.tags.discard(tag)
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if this object has a specific tag.
        
        Args:
            tag: Tag to check for
            
        Returns:
            True if object has the tag, False otherwise
        """
        return tag in self.tags
    
    def set_layer(self, layer: str):
        """
        Set the rendering layer for this object.
        
        Args:
            layer: Layer name
        """
        old_layer = self.layer
        self.layer = layer
        
        # Update scene layer management if object is in a scene
        if self.scene:
            # Remove from old layer
            if old_layer in self.scene.layers and self in self.scene.layers[old_layer]:
                self.scene.layers[old_layer].remove(self)
            
            # Add to new layer
            if layer not in self.scene.layers:
                self.scene.layers[layer] = []
            self.scene.layers[layer].append(self)
    
    def destroy(self):
        """
        Mark this object for destruction.
        """
        self._destroyed = True
        self.active = False
        
        # Remove from scene
        if self.scene:
            self.scene.remove_object(self)
        
        # Cleanup components
        for component in list(self.components.values()):
            self.remove_component(type(component))
    
    def start(self):
        """
        Called when the object is first created and added to a scene.
        Override this method for initialization logic.
        """
        if self._started:
            return
        
        self._started = True
        
        # Start all components
        for component in self.components.values():
            if hasattr(component, 'start'):
                component.start()
    
    def update(self, delta_time: float):
        """
        Update the game object and all its components.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        if not self.active or self._destroyed:
            return
        
        # Ensure object is started
        if not self._started:
            self.start()
        
        # Update all components
        for component in self.components.values():
            if component.enabled and hasattr(component, 'update'):
                component.update(delta_time)
    
    def render(self, renderer):
        """
        Render the game object and all its components.
        
        Args:
            renderer: Renderer instance
        """
        if not self.active or self._destroyed:
            return
        
        # Render all components
        for component in self.components.values():
            if component.enabled and hasattr(component, 'render'):
                component.render(renderer)
    
    def on_scene_enter(self):
        """Called when this object's scene becomes active."""
        for component in self.components.values():
            if hasattr(component, 'on_scene_enter'):
                component.on_scene_enter()
    
    def on_scene_exit(self):
        """Called when this object's scene becomes inactive."""
        for component in self.components.values():
            if hasattr(component, 'on_scene_exit'):
                component.on_scene_exit()
    
    def find_object_by_name(self, name: str) -> Optional['GameObject']:
        """
        Find another object in the same scene by name.
        
        Args:
            name: Name to search for
            
        Returns:
            GameObject with matching name or None
        """
        if self.scene:
            return self.scene.find_object_by_name(name)
        return None
    
    def find_objects_by_tag(self, tag: str) -> List['GameObject']:
        """
        Find all objects in the same scene with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of GameObjects with matching tag
        """
        if self.scene:
            return self.scene.find_objects_by_tag(tag)
        return []
    
    def get_world_rotation(self) -> float:
        """
        Get the world rotation of this game object.
        
        Returns:
            World rotation in degrees
        """
        return self.transform.rotation
    
    def get_world_scale(self):
        """
        Get the world scale of this game object.
        
        Returns:
            World scale as Vector2
        """
        return self.transform.scale
    
    def __str__(self):
        return f"GameObject(name='{self.name}', active={self.active}, components={len(self.components)})"
    
    def __repr__(self):
        return self.__str__()
