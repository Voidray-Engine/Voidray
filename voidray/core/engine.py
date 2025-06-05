"""
VoidRay Engine Core
The main engine class that manages the game loop, systems, and overall execution.
"""

import pygame
import sys
from typing import Optional
from ..rendering.renderer import Renderer
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
            
            # Update physics with optimization
            self.physics_engine.update(self.delta_time)
            
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
    
    def set_rendering_mode(self, mode: str) -> None:
        """
        Set the rendering mode for the engine.
        
        Args:
            mode: "2D" for traditional 2D, "2.5D" for pseudo-3D rendering
        """
        self.renderer.set_rendering_mode(mode)
        print(f"Rendering mode set to: {mode}")
    
    def _optimize_performance(self) -> None:
        """
        Optimize performance when FPS drops.
        """
        # Clear sprite cache to free memory
        self.renderer.clear_sprite_cache()
        
        # Reduce render distance in 2.5D mode
        if self.renderer.rendering_mode == "2.5D":
            current_distance = self.renderer.render_distance
            self.renderer.set_render_distance(current_distance * 0.8)
            print(f"Performance optimization: Reduced render distance to {self.renderer.render_distance}")
        
        # Optimize physics
        self.physics_engine.optimize_performance()
    
    def set_target_fps(self, fps: int) -> None:
        """
        Set the target FPS.
        
        Args:
            fps: Target frames per second
        """
        self.target_fps = fps
        print(f"Target FPS set to: {fps}")
    
    def get_performance_info(self) -> dict:
        """
        Get performance information.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'fps': self.get_fps(),
            'delta_time': self.delta_time,
            'target_fps': self.target_fps,
            'rendering_mode': self.renderer.rendering_mode,
            'active_objects': len(self.current_scene.game_objects) if self.current_scene else 0,
            'colliders': len(self.physics_engine.colliders)
        }
