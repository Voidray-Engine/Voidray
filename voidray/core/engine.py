"""
VoidRay Engine Core
The main engine class that manages the game loop, systems, and overall execution.
"""

import pygame
import sys
from typing import Optional
from ..graphics.renderer import Renderer
from ..input.input_manager import InputManager
from ..physics.physics_engine import PhysicsEngine
from ..audio.audio_manager import AudioManager
from ..assets.asset_loader import AssetLoader
from .scene import Scene


class Engine:
    """
    The main Engine class that coordinates all engine systems and manages the game loop.
    """
    
    def __init__(self, width: int = 800, height: int = 600, title: str = "VoidRay Game", fps: int = 60):
        """
        Initialize the VoidRay engine.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels  
            title: Window title
            fps: Target frames per second
        """
        # Initialize Pygame
        pygame.init()
        
        # Engine configuration
        self.width = width
        self.height = height
        self.title = title
        self.target_fps = fps
        self.running = False
        
        # Create the display window
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        # Initialize engine systems
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.input_manager = InputManager()
        self.physics_engine = PhysicsEngine()
        self.audio_manager = AudioManager()
        self.asset_loader = AssetLoader()
        
        # Scene management
        self.current_scene: Optional[Scene] = None
        self.delta_time = 0.0
        
        # Enhanced features
        self.enable_vsync = True
        self.performance_stats = {
            'fps': 0.0,
            'frame_time': 0.0,
            'objects_rendered': 0,
            'collisions_checked': 0
        }
        
        print(f"VoidRay Engine initialized: {width}x{height} @ {fps}fps")
    
    def set_scene(self, scene: Scene):
        """
        Set the current active scene.
        
        Args:
            scene: The scene to activate
        """
        if self.current_scene:
            self.current_scene.on_exit()
        
        self.current_scene = scene
        scene.engine = self
        scene.on_enter()
        print(f"Scene changed to: {scene.__class__.__name__}")
    
    def run(self):
        """
        Start the main game loop.
        """
        if not self.current_scene:
            raise RuntimeError("No scene set! Use engine.set_scene() before calling run()")
        
        self.running = True
        print("Starting VoidRay engine...")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.target_fps)
            self.delta_time = dt / 1000.0  # Convert to seconds
            
            # Handle input events
            self._handle_events()
            
            # Update current scene
            if self.current_scene:
                self.current_scene.update(self.delta_time)
            
            # Update physics (only for collision detection, not movement)
            # Objects handle their own movement in update() methods
            self.physics_engine._check_collisions()
            
            # Render frame
            self.renderer.clear()
            if self.current_scene:
                self.current_scene.render(self.renderer)
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
        """
        Get the current frames per second.
        
        Returns:
            Current FPS as a float
        """
        return self.clock.get_fps()
    
    def get_delta_time(self) -> float:
        """
        Get the time elapsed since the last frame in seconds.
        
        Returns:
            Delta time in seconds
        """
        return self.delta_time
