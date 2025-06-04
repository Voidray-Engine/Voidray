
"""
VoidRay Scene Manager
Advanced scene management with layer support and render optimization.
"""

from typing import Dict, List, Optional
from .scene import Scene
from .game_object import GameObject


class SceneManager:
    """
    Advanced scene manager with layer and performance optimizations.
    """
    
    def __init__(self):
        """
        Initialize the scene manager.
        """
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.scene_stack: List[Scene] = []
        
        # Layer management
        self.global_layers: List[str] = ["background", "world", "entities", "effects", "ui"]
        self.layer_visibility: Dict[str, bool] = {}
        
        # Initialize layer visibility
        for layer in self.global_layers:
            self.layer_visibility[layer] = True
    
    def register_scene(self, name: str, scene: Scene):
        """
        Register a scene with the manager.
        
        Args:
            name: Scene identifier
            scene: Scene instance
        """
        self.scenes[name] = scene
    
    def load_scene(self, name: str) -> bool:
        """
        Load a scene by name.
        
        Args:
            name: Scene identifier
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.scenes:
            return False
        
        if self.current_scene:
            self.current_scene.on_exit()
        
        self.current_scene = self.scenes[name]
        self.current_scene.on_enter()
        return True
    
    def push_scene(self, name: str) -> bool:
        """
        Push current scene to stack and load new scene.
        
        Args:
            name: Scene identifier
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.scenes:
            return False
        
        if self.current_scene:
            self.scene_stack.append(self.current_scene)
            self.current_scene.on_pause()
        
        self.current_scene = self.scenes[name]
        self.current_scene.on_enter()
        return True
    
    def pop_scene(self) -> bool:
        """
        Pop scene from stack and return to it.
        
        Returns:
            True if successful, False if stack is empty
        """
        if not self.scene_stack:
            return False
        
        if self.current_scene:
            self.current_scene.on_exit()
        
        self.current_scene = self.scene_stack.pop()
        self.current_scene.on_resume()
        return True
    
    def set_layer_visibility(self, layer: str, visible: bool):
        """
        Set visibility of a specific layer.
        
        Args:
            layer: Layer name
            visible: Whether layer should be visible
        """
        if layer in self.layer_visibility:
            self.layer_visibility[layer] = visible
    
    def get_objects_by_layer(self, layer: str) -> List[GameObject]:
        """
        Get all objects in a specific layer from current scene.
        
        Args:
            layer: Layer name
            
        Returns:
            List of GameObjects in the layer
        """
        if not self.current_scene:
            return []
        
        result = []
        for obj in self.current_scene.game_objects:
            if obj.layer == layer:
                result.append(obj)
        
        return result
    
    def update(self, delta_time: float):
        """
        Update the current scene.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        if self.current_scene:
            self.current_scene.update(delta_time)
    
    def render(self, renderer):
        """
        Render the current scene with layer ordering.
        
        Args:
            renderer: Renderer instance
        """
        if not self.current_scene:
            return
        
        # Render objects by layer order
        for layer in self.global_layers:
            if not self.layer_visibility.get(layer, True):
                continue
                
            layer_objects = self.get_objects_by_layer(layer)
            # Sort by z_order within layer
            layer_objects.sort(key=lambda obj: obj.z_order)
            
            for obj in layer_objects:
                if obj.active:
                    obj.render(renderer)
