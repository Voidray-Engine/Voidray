
"""
VoidRay Scene Manager
Advanced scene management with state machines, transitions, and performance optimization.
"""

from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import time
from .scene import Scene
from .game_object import GameObject


class SceneTransition:
    """Represents a scene transition with effects and duration."""
    
    def __init__(self, transition_type: str = "fade", duration: float = 0.5, 
                 color: tuple = (0, 0, 0), custom_callback: Callable = None):
        self.transition_type = transition_type
        self.duration = duration
        self.color = color
        self.custom_callback = custom_callback
        self.progress = 0.0
        self.is_active = False


class SceneState(Enum):
    """Scene lifecycle states."""
    INACTIVE = "inactive"
    LOADING = "loading"
    ACTIVE = "active"
    PAUSED = "paused"
    TRANSITIONING = "transitioning"
    UNLOADING = "unloading"


class SceneManager:
    """
    Advanced scene manager with state machines, transitions, and performance optimizations.
    """
    
    def __init__(self):
        """Initialize the scene manager."""
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.scene_stack: List[Scene] = []
        self.scene_states: Dict[str, SceneState] = {}
        
        # Layer management
        self.global_layers: List[str] = ["background", "world", "entities", "effects", "ui", "debug"]
        self.layer_visibility: Dict[str, bool] = {}
        self.layer_z_orders: Dict[str, int] = {
            "background": 0,
            "world": 100,
            "entities": 200,
            "effects": 300,
            "ui": 400,
            "debug": 500
        }
        
        # Initialize layer visibility
        for layer in self.global_layers:
            self.layer_visibility[layer] = True
            
        # Transition system
        self.current_transition: Optional[SceneTransition] = None
        self.transition_callbacks: Dict[str, List[Callable]] = {}
        
        # Performance tracking
        self.scene_metrics: Dict[str, Dict[str, Any]] = {}
        self.last_performance_check = time.time()
        
        # Scene preloading
        self.preloaded_scenes: Dict[str, Scene] = {}
        self.preload_queue: List[str] = []
        
        # Scene pooling for frequently used scenes
        self.scene_pools: Dict[str, List[Scene]] = {}
    
    def register_scene(self, name: str, scene: Scene, preload: bool = False):
        """
        Register a scene with the manager.
        
        Args:
            name: Scene identifier
            scene: Scene instance
            preload: Whether to preload this scene
        """
        self.scenes[name] = scene
        self.scene_states[name] = SceneState.INACTIVE
        self.scene_metrics[name] = {
            'load_time': 0.0,
            'object_count': 0,
            'memory_usage': 0,
            'last_accessed': time.time()
        }
        
        if preload:
            self.preload_scene(name)
    
    def preload_scene(self, name: str):
        """Preload a scene for faster transitions."""
        if name in self.scenes and name not in self.preloaded_scenes:
            scene = self.scenes[name]
            self.scene_states[name] = SceneState.LOADING
            
            start_time = time.time()
            scene.preload()  # Assuming scenes have a preload method
            load_time = time.time() - start_time
            
            self.preloaded_scenes[name] = scene
            self.scene_states[name] = SceneState.INACTIVE
            self.scene_metrics[name]['load_time'] = load_time
            
            print(f"Preloaded scene '{name}' in {load_time:.3f}s")
    
    def load_scene(self, name: str, transition: SceneTransition = None) -> bool:
        """
        Load a scene by name with optional transition.
        
        Args:
            name: Scene identifier
            transition: Optional transition effect
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.scenes:
            print(f"Scene '{name}' not found")
            return False
        
        # Start transition if provided
        if transition:
            self._start_transition(transition, lambda: self._perform_scene_load(name))
        else:
            self._perform_scene_load(name)
        
        return True
    
    def _perform_scene_load(self, name: str):
        """Internal scene loading logic."""
        old_scene = self.current_scene
        
        # Exit current scene
        if old_scene:
            self.scene_states[old_scene.name] = SceneState.TRANSITIONING
            old_scene.on_exit()
            self.scene_states[old_scene.name] = SceneState.INACTIVE
        
        # Load new scene
        new_scene = self.scenes[name]
        self.scene_states[name] = SceneState.LOADING
        
        start_time = time.time()
        new_scene.on_enter()
        load_time = time.time() - start_time
        
        self.current_scene = new_scene
        self.scene_states[name] = SceneState.ACTIVE
        self.scene_metrics[name]['last_accessed'] = time.time()
        self.scene_metrics[name]['load_time'] = load_time
        
        # Call transition callbacks
        self._call_transition_callbacks('scene_loaded', old_scene, new_scene)
        
        print(f"Loaded scene '{name}' in {load_time:.3f}s")
    
    def push_scene(self, name: str, transition: SceneTransition = None) -> bool:
        """
        Push current scene to stack and load new scene.
        
        Args:
            name: Scene identifier
            transition: Optional transition effect
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.scenes:
            return False
        
        if self.current_scene:
            self.scene_stack.append(self.current_scene)
            self.scene_states[self.current_scene.name] = SceneState.PAUSED
            self.current_scene.on_pause()
        
        if transition:
            self._start_transition(transition, lambda: self._perform_scene_push(name))
        else:
            self._perform_scene_push(name)
        
        return True
    
    def _perform_scene_push(self, name: str):
        """Internal scene push logic."""
        new_scene = self.scenes[name]
        self.scene_states[name] = SceneState.LOADING
        new_scene.on_enter()
        self.current_scene = new_scene
        self.scene_states[name] = SceneState.ACTIVE
    
    def pop_scene(self, transition: SceneTransition = None) -> bool:
        """
        Pop scene from stack and return to it.
        
        Args:
            transition: Optional transition effect
            
        Returns:
            True if successful, False if stack is empty
        """
        if not self.scene_stack:
            return False
        
        if transition:
            self._start_transition(transition, self._perform_scene_pop)
        else:
            self._perform_scene_pop()
        
        return True
    
    def _perform_scene_pop(self):
        """Internal scene pop logic."""
        if self.current_scene:
            self.scene_states[self.current_scene.name] = SceneState.INACTIVE
            self.current_scene.on_exit()
        
        previous_scene = self.scene_stack.pop()
        self.current_scene = previous_scene
        self.scene_states[previous_scene.name] = SceneState.ACTIVE
        previous_scene.on_resume()
    
    def _start_transition(self, transition: SceneTransition, completion_callback: Callable):
        """Start a scene transition."""
        transition.is_active = True
        transition.progress = 0.0
        transition.completion_callback = completion_callback
        self.current_transition = transition
    
    def set_layer_visibility(self, layer: str, visible: bool):
        """Set visibility of a specific layer."""
        if layer in self.layer_visibility:
            self.layer_visibility[layer] = visible
    
    def set_layer_z_order(self, layer: str, z_order: int):
        """Set the z-order for a layer."""
        if layer in self.layer_z_orders:
            self.layer_z_orders[layer] = z_order
            # Re-sort layers by z-order
            self.global_layers.sort(key=lambda l: self.layer_z_orders.get(l, 0))
    
    def get_objects_by_layer(self, layer: str) -> List[GameObject]:
        """Get all objects in a specific layer from current scene."""
        if not self.current_scene:
            return []
        
        result = []
        for obj in self.current_scene.objects:
            if hasattr(obj, 'layer') and obj.layer == layer:
                result.append(obj)
        
        return result
    
    def add_transition_callback(self, event: str, callback: Callable):
        """Add a callback for transition events."""
        if event not in self.transition_callbacks:
            self.transition_callbacks[event] = []
        self.transition_callbacks[event].append(callback)
    
    def _call_transition_callbacks(self, event: str, *args):
        """Call callbacks for a transition event."""
        if event in self.transition_callbacks:
            for callback in self.transition_callbacks[event]:
                try:
                    callback(*args)
                except Exception as e:
                    print(f"Error in transition callback: {e}")
    
    def update(self, delta_time: float):
        """Update the scene manager and current scene."""
        # Update transition
        if self.current_transition and self.current_transition.is_active:
            self._update_transition(delta_time)
        
        # Update current scene
        if self.current_scene and self.scene_states.get(self.current_scene.name) == SceneState.ACTIVE:
            self.current_scene.update(delta_time)
            self._update_scene_metrics()
    
    def _update_transition(self, delta_time: float):
        """Update the current transition effect."""
        transition = self.current_transition
        transition.progress += delta_time / transition.duration
        
        if transition.progress >= 1.0:
            transition.progress = 1.0
            transition.is_active = False
            
            # Call completion callback
            if hasattr(transition, 'completion_callback'):
                transition.completion_callback()
            
            self.current_transition = None
    
    def _update_scene_metrics(self):
        """Update performance metrics for the current scene."""
        if not self.current_scene:
            return
        
        current_time = time.time()
        if current_time - self.last_performance_check > 1.0:  # Update every second
            scene_name = self.current_scene.name
            self.scene_metrics[scene_name]['object_count'] = len(self.current_scene.objects)
            # Memory usage would require more complex tracking
            self.last_performance_check = current_time
    
    def render(self, renderer):
        """Render the current scene with layer ordering and transitions."""
        if not self.current_scene:
            return
        
        # Render scene layers in order
        for layer in self.global_layers:
            if not self.layer_visibility.get(layer, True):
                continue
                
            layer_objects = self.get_objects_by_layer(layer)
            # Sort by z_order within layer
            layer_objects.sort(key=lambda obj: getattr(obj, 'z_order', 0))
            
            for obj in layer_objects:
                if hasattr(obj, 'active') and obj.active:
                    obj.render(renderer)
        
        # Render transition effect
        if self.current_transition and self.current_transition.is_active:
            self._render_transition(renderer)
    
    def _render_transition(self, renderer):
        """Render the current transition effect."""
        transition = self.current_transition
        
        if transition.transition_type == "fade":
            alpha = int(255 * abs(transition.progress - 0.5) * 2)
            overlay = renderer.create_surface((renderer.screen.get_width(), renderer.screen.get_height()))
            overlay.fill(transition.color)
            overlay.set_alpha(alpha)
            renderer.screen.blit(overlay, (0, 0))
        elif transition.custom_callback:
            transition.custom_callback(renderer, transition.progress)
    
    def get_scene_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics for all scenes."""
        return self.scene_metrics.copy()
    
    def cleanup_unused_scenes(self, max_idle_time: float = 300.0):
        """Clean up scenes that haven't been used recently."""
        current_time = time.time()
        scenes_to_cleanup = []
        
        for scene_name, metrics in self.scene_metrics.items():
            if (current_time - metrics['last_accessed'] > max_idle_time and 
                scene_name != self.current_scene.name if self.current_scene else True):
                scenes_to_cleanup.append(scene_name)
        
        for scene_name in scenes_to_cleanup:
            if scene_name in self.preloaded_scenes:
                del self.preloaded_scenes[scene_name]
                print(f"Cleaned up unused scene: {scene_name}")
    
    def get_current_scene(self) -> Optional[Scene]:
        """Get the current active scene."""
        return self.current_scene
