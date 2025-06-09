
"""
VoidRay Scene System
Core scene management for organizing game states and objects.
"""

from typing import List, Optional, Dict, Any
from .game_object import GameObject


class Scene:
    """
    Base class for all game scenes.
    Scenes represent different states of your game (menu, gameplay, pause, etc.).
    """
    
    def __init__(self, name: str = "Scene"):
        """
        Initialize the scene.
        
        Args:
            name: Scene name identifier
        """
        self.name = name
        self.objects: List[GameObject] = []
        self.active = True
        self.engine = None
        
        # Level data for 2.5D rendering
        self.level_data = None
        self.walls = []
        self.light_sources = []
        self.sprites = []
        
        # Layer management
        self.layers = {
            "background": [],
            "world": [], 
            "entities": [],
            "effects": [],
            "ui": []
        }
    
    def add_object(self, game_object: GameObject, layer: str = "world"):
        """
        Add a game object to the scene.
        
        Args:
            game_object: The GameObject to add
            layer: Layer to add the object to
        """
        if game_object not in self.objects:
            self.objects.append(game_object)
            game_object.scene = self
            
            if layer in self.layers:
                self.layers[layer].append(game_object)
            else:
                self.layers["world"].append(game_object)
    
    def remove_object(self, game_object: GameObject):
        """
        Remove a game object from the scene.
        
        Args:
            game_object: The GameObject to remove
        """
        if game_object in self.objects:
            self.objects.remove(game_object)
            game_object.scene = None
            
            # Remove from layers
            for layer_objects in self.layers.values():
                if game_object in layer_objects:
                    layer_objects.remove(game_object)
    
    def find_object_by_name(self, name: str) -> Optional[GameObject]:
        """
        Find a game object by name.
        
        Args:
            name: Name to search for
            
        Returns:
            First GameObject with matching name, or None
        """
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None
    
    def find_objects_by_tag(self, tag: str) -> List[GameObject]:
        """
        Find all game objects with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of GameObjects with matching tag
        """
        result = []
        for obj in self.objects:
            if hasattr(obj, 'tags') and tag in obj.tags:
                result.append(obj)
        return result
    
    def get_objects_in_layer(self, layer: str) -> List[GameObject]:
        """
        Get all objects in a specific layer.
        
        Args:
            layer: Layer name
            
        Returns:
            List of GameObjects in the layer
        """
        return self.layers.get(layer, [])
    
    def on_enter(self):
        """Called when the scene becomes active."""
        print(f"Entering scene: {self.name}")
        self.active = True
        
        # Initialize all objects
        for obj in self.objects:
            if hasattr(obj, 'on_scene_enter'):
                obj.on_scene_enter()
    
    def on_exit(self):
        """Called when the scene becomes inactive."""
        print(f"Exiting scene: {self.name}")
        self.active = False
        
        # Cleanup all objects
        for obj in self.objects:
            if hasattr(obj, 'on_scene_exit'):
                obj.on_scene_exit()
    
    def on_pause(self):
        """Called when the scene is paused."""
        self.active = False
    
    def on_resume(self):
        """Called when the scene is resumed from pause."""
        self.active = True
    
    def update(self, delta_time: float):
        """
        Update all objects in the scene.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        if not self.active:
            return
        
        # Update all active objects
        for obj in self.objects[:]:  # Copy list to avoid modification during iteration
            if obj.active:
                obj.update(delta_time)
    
    def render(self, renderer):
        """
        Render all objects in the scene with proper layer ordering.
        
        Args:
            renderer: Renderer instance
        """
        if not self.active:
            return
        
        # Render objects by layer order
        layer_order = ["background", "world", "entities", "effects", "ui"]
        
        for layer_name in layer_order:
            layer_objects = self.layers.get(layer_name, [])
            
            # Sort by z_order within layer
            layer_objects.sort(key=lambda obj: getattr(obj, 'z_order', 0))
            
            for obj in layer_objects:
                if obj.active and hasattr(obj, 'render'):
                    obj.render(renderer)
    
    def clear(self):
        """Remove all objects from the scene."""
        for obj in self.objects[:]:
            self.remove_object(obj)
        
        # Clear layers
        for layer in self.layers.values():
            layer.clear()
    
    def load_level(self, level_name: str, asset_loader):
        """
        Load a 2.5D level into this scene.
        
        Args:
            level_name: Name of the level to load
            asset_loader: Asset loader instance
        """
        if level_name in asset_loader.data:
            self.level_data = asset_loader.data[level_name]
            
            # Extract walls
            self.walls = self.level_data.get('walls', [])
            
            # Extract light sources
            self.light_sources = self.level_data.get('lights', [])
            
            # Extract sprites
            self.sprites = self.level_data.get('sprites', [])
            
            print(f"Level processed: {len(self.walls)} walls, {len(self.sprites)} sprites, {len(self.light_sources)} lights")
            print(f"Loaded level '{level_name}' into scene '{self.name}'")
        else:
            print(f"Level '{level_name}' not found in asset loader")
    
    def get_walls(self) -> List[Dict]:
        """Get wall data for 2.5D rendering."""
        return self.walls
    
    def get_light_sources(self) -> List[Dict]:
        """Get light source data for 2.5D rendering."""
        return self.light_sources
    
    def get_sprites(self) -> List[Dict]:
        """Get sprite data for 2.5D rendering."""
        return self.sprites
    
    def add_wall(self, start_pos, end_pos, texture="default", height=64):
        """
        Add a wall to the scene for 2.5D rendering.
        
        Args:
            start_pos: Start position (x, y)
            end_pos: End position (x, y)  
            texture: Wall texture name
            height: Wall height
        """
        wall = {
            "start": {"x": start_pos[0], "y": start_pos[1]},
            "end": {"x": end_pos[0], "y": end_pos[1]},
            "texture": texture,
            "height": height
        }
        self.walls.append(wall)
    
    def add_light_source(self, position, intensity=1.0, color=(255, 255, 255), radius=100.0):
        """
        Add a light source to the scene.
        
        Args:
            position: Light position (x, y)
            intensity: Light intensity
            color: Light color (r, g, b)
            radius: Light radius
        """
        light = {
            "x": position[0],
            "y": position[1], 
            "intensity": intensity,
            "color": list(color),
            "radius": radius
        }
        self.light_sources.append(light)
