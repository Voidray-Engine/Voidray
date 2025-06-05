
"""
VoidRay Engine Core
The main engine class that manages the game loop, systems, and overall execution.
"""

import pygame
import sys
from typing import Optional, Dict, Any, Callable
from ..rendering.renderer import Renderer
from ..input.input_manager import InputManager
from ..physics.physics_engine import PhysicsEngine
from ..audio.audio_manager import AudioManager
from ..assets.asset_loader import AssetLoader
from .scene import Scene


class VoidRayEngine:
    """
    The VoidRay Game Engine - A self-contained game engine that manages everything.
    Users register their game logic and the engine handles the rest.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoidRayEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Engine configuration
        self.width = 800
        self.height = 600
        self.title = "VoidRay Game"
        self.target_fps = 60
        self.running = False
        self.auto_start = True
        
        # Engine systems (will be initialized when configure() is called)
        self.screen = None
        self.clock = None
        self.renderer = None
        self.input_manager = None
        self.physics_engine = None
        self.audio_manager = None
        self.asset_loader = None
        
        # Scene management
        self.current_scene: Optional[Scene] = None
        self.scenes: Dict[str, Scene] = {}
        self.delta_time = 0.0
        
        # User callbacks
        self.init_callback: Optional[Callable] = None
        self.update_callback: Optional[Callable[[float], None]] = None
        self.render_callback: Optional[Callable] = None
        
        self._initialized = True
    
    def configure(self, width: int = 800, height: int = 600, title: str = "VoidRay Game", 
                 fps: int = 60, auto_start: bool = True):
        """
        Configure the engine settings.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels  
            title: Window title
            fps: Target frames per second
            auto_start: Whether to start the engine automatically
        """
        self.width = width
        self.height = height
        self.title = title
        self.target_fps = fps
        self.auto_start = auto_start
        
        return self
    
    def on_init(self, callback: Callable):
        """
        Register initialization callback.
        
        Args:
            callback: Function to call during engine initialization
        """
        self.init_callback = callback
        return self
    
    def on_update(self, callback: Callable[[float], None]):
        """
        Register update callback.
        
        Args:
            callback: Function to call every frame with delta_time
        """
        self.update_callback = callback
        return self
    
    def on_render(self, callback: Callable):
        """
        Register render callback.
        
        Args:
            callback: Function to call for custom rendering
        """
        self.render_callback = callback
        return self
    
    def register_scene(self, name: str, scene: Scene):
        """
        Register a scene with the engine.
        
        Args:
            name: Scene identifier
            scene: Scene instance
        """
        self.scenes[name] = scene
        scene.engine = self
        return self
    
    def set_scene(self, name_or_scene):
        """
        Set the current active scene.
        
        Args:
            name_or_scene: Scene name string or Scene instance
        """
        if isinstance(name_or_scene, str):
            if name_or_scene not in self.scenes:
                raise ValueError(f"Scene '{name_or_scene}' not found")
            scene = self.scenes[name_or_scene]
        else:
            scene = name_or_scene
            scene.engine = self
        
        if self.current_scene:
            self.current_scene.on_exit()
        
        self.current_scene = scene
        scene.on_enter()
        print(f"Scene changed to: {scene.__class__.__name__}")
        return self
    
    def _initialize_systems(self):
        """Initialize all engine systems."""
        # Initialize Pygame
        pygame.init()
        
        # Create the display window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        
        # Initialize engine systems
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.input_manager = InputManager()
        self.physics_engine = PhysicsEngine()
        self.audio_manager = AudioManager()
        self.asset_loader = AssetLoader()
        
        # Initialize physics system for collision detection
        from ..physics.physics_system import PhysicsSystem
        self.physics_system = PhysicsSystem()
        
        print(f"VoidRay Engine initialized: {self.width}x{self.height} @ {self.target_fps}fps")
        
        # Call user initialization
        if self.init_callback:
            self.init_callback()
    
    def start(self):
        """
        Start the game engine.
        """
        if self.running:
            return
            
        self._initialize_systems()
        self._run_main_loop()
    
    def _run_main_loop(self):
        """
        Run the main game loop.
        """
        self.running = True
        print("Starting VoidRay engine...")
        
        # Performance tracking
        frame_count = 0
        performance_timer = 0
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.target_fps)
            self.delta_time = dt / 1000.0  # Convert to seconds
            
            # Performance monitoring
            frame_count += 1
            performance_timer += self.delta_time
            
            if performance_timer >= 1.0:  # Every second
                actual_fps = frame_count / performance_timer
                if actual_fps < self.target_fps * 0.8:  # If FPS drops below 80% of target
                    self._optimize_performance()
                frame_count = 0
                performance_timer = 0
            
            # Handle input events
            self._handle_events()
            
            # Update current scene
            if self.current_scene:
                self.current_scene.update(self.delta_time)
            
            # Call user update callback
            if self.update_callback:
                self.update_callback(self.delta_time)
            
            # Update physics with optimization
            self.physics_engine.update(self.delta_time)
            self.physics_system.update(self.delta_time)
            
            # Render frame
            self.renderer.clear()
            
            # Render current scene
            if self.current_scene:
                self.current_scene.render(self.renderer)
            
            # Call user render callback
            if self.render_callback:
                self.render_callback()
            
            self.renderer.present()
        
        self._cleanup()
    
    def stop(self):
        """
        Stop the engine and exit the game loop.
        """
        self.running = False
        print("Stopping VoidRay engine...")
    
    def _handle_events(self):
        """
        Process pygame events and update input manager.
        """
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.stop()
            
            # Pass events to input manager
            self.input_manager.handle_event(event)
        
        # Update input manager state
        self.input_manager.update()
    
    def _cleanup(self):
        """
        Clean up resources before shutting down.
        """
        if self.current_scene:
            self.current_scene.on_exit()
        
        self.audio_manager.cleanup()
        pygame.quit()
        sys.exit()
    
    def get_fps(self) -> float:
        """Get the current frames per second."""
        return self.clock.get_fps() if self.clock else 0
    
    def get_delta_time(self) -> float:
        """Get the time elapsed since the last frame in seconds."""
        return self.delta_time
    
    def _optimize_performance(self) -> None:
        """Optimize performance when FPS drops."""
        # Clear sprite cache to free memory
        self.renderer.clear_sprite_cache()
        
        # Reduce render distance in 2.5D mode
        if self.renderer.rendering_mode == "2.5D":
            current_distance = self.renderer.render_distance
            self.renderer.set_render_distance(current_distance * 0.8)
            print(f"Performance optimization: Reduced render distance to {self.renderer.render_distance}")
        
        # Optimize physics
        self.physics_engine.optimize_performance()


# Global engine instance
Engine = VoidRayEngine()


# Convenience functions for quick setup
def configure(width: int = 800, height: int = 600, title: str = "VoidRay Game", 
             fps: int = 60, auto_start: bool = True):
    """Configure the VoidRay engine."""
    return Engine.configure(width, height, title, fps, auto_start)


def on_init(callback: Callable):
    """Register initialization callback."""
    return Engine.on_init(callback)


def on_update(callback: Callable[[float], None]):
    """Register update callback."""
    return Engine.on_update(callback)


def on_render(callback: Callable):
    """Register render callback."""
    return Engine.on_render(callback)


def register_scene(name: str, scene: Scene):
    """Register a scene."""
    return Engine.register_scene(name, scene)


def set_scene(name_or_scene):
    """Set the current scene."""
    return Engine.set_scene(name_or_scene)


def start():
    """Start the engine."""
    Engine.start()


def stop():
    """Stop the engine."""
    Engine.stop()


def get_engine():
    """Get the engine instance."""
    return Engine
