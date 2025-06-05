
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
        # Initialize Pygame with enhanced settings
        pygame.init()
        
        # Initialize audio mixer with better settings
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Audio initialization failed: {e}")
        
        # Engine configuration
        self.width = width
        self.height = height
        self.title = title
        self.target_fps = fps
        self.running = False
        
        # Create the display window with optimized flags
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption(title)
        
        # Initialize engine systems
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.input_manager = InputManager()
        self.physics_engine = PhysicsEngine()
        self.audio_manager = AudioManager()
        self.asset_loader = AssetLoader()
        
        # Add common asset search paths
        self.asset_loader.add_search_path("image", "examples/assets/")
        self.asset_loader.add_search_path("sound", "examples/assets/")
        
        # Scene management
        self.current_scene: Optional[Scene] = None
        self.delta_time = 0.0
        
        # Enhanced features
        self.enable_vsync = True
        self.performance_stats = {
            'fps': 0.0,
            'frame_time': 0.0,
            'objects_rendered': 0,
            'collisions_checked': 0,
            'draw_calls': 0
        }
        
        # 2.5D rendering settings
        self.enable_2_5d = False
        self.depth_layers = {}
        
        print(f"VoidRay Engine initialized: {width}x{height} @ {fps}fps")
        print(f"Available image files: {len(self.asset_loader.list_available_files('image'))}")
    
    def enable_2_5d_rendering(self, enabled: bool = True):
        """Enable or disable 2.5D rendering features."""
        self.enable_2_5d = enabled
        self.renderer.enable_depth_sorting = enabled
        self.renderer.enable_perspective(enabled)
        print(f"2.5D rendering {'enabled' if enabled else 'disabled'}")
    
    def configure_2_5d_mode(self, mode: str = "doom"):
        """Configure 2.5D rendering for specific game styles.
        
        Args:
            mode: "doom" for DOOM-style, "gta" for GTA 1-style, "isometric" for isometric view
        """
        if mode.lower() == "doom":
            # DOOM-style configuration
            self.renderer.set_perspective_settings(fov=90.0, horizon=0.5, strength=1.5)
            self.renderer.set_height_bounds(floor=0.0, ceiling=128.0)
            self.renderer.enable_walls(True)
            self.renderer.fog_strength = 0.3
            print("Configured for DOOM-style 2.5D rendering")
            
        elif mode.lower() == "gta":
            # GTA 1-style top-down with perspective
            self.renderer.set_perspective_settings(fov=60.0, horizon=0.3, strength=0.8)
            self.renderer.set_height_bounds(floor=0.0, ceiling=64.0)
            self.renderer.enable_walls(True)
            self.renderer.fog_strength = 0.1
            print("Configured for GTA 1-style 2.5D rendering")
            
        elif mode.lower() == "isometric":
            # Isometric-style perspective
            self.renderer.set_perspective_settings(fov=45.0, horizon=0.6, strength=0.5)
            self.renderer.set_height_bounds(floor=0.0, ceiling=32.0)
            self.renderer.enable_walls(False)
            self.renderer.fog_strength = 0.0
            print("Configured for isometric-style 2.5D rendering")
            
        else:
            print(f"Unknown 2.5D mode: {mode}. Available modes: 'doom', 'gta', 'isometric'")
    
    def set_perspective_view(self, fov: float = 60.0, horizon: float = 0.5):
        """Set perspective view parameters."""
        self.renderer.set_perspective_settings(fov=fov, horizon=horizon)
        
    def add_wall(self, start_pos, end_pos, height: float = 64.0, color: tuple = (128, 128, 128)):
        """Add a wall segment to the current scene."""
        self.renderer.add_wall_segment(start_pos, end_pos, height, color)
        
    def clear_walls(self):
        """Clear all wall segments."""
        self.renderer.clear_walls()
    
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
        scene.asset_loader = self.asset_loader  # Provide asset loader access
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
        total_frame_time = 0
        
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
            self.physics_engine._check_collisions()
            
            # Render frame
            self.renderer.clear()
            if self.current_scene:
                self.current_scene.render(self.renderer)
            self.renderer.present()
            
            # Update performance stats
            frame_count += 1
            total_frame_time += dt
            
            if frame_count % 60 == 0:  # Update stats every second
                self.performance_stats.update({
                    'fps': self.clock.get_fps(),
                    'frame_time': dt,
                    'objects_rendered': self.renderer.get_stats()['objects_rendered'],
                    'draw_calls': self.renderer.get_stats()['draw_calls']
                })
        
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
        self.asset_loader.clear_all()
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
    
    def get_performance_stats(self) -> dict:
        """Get comprehensive performance statistics."""
        stats = self.performance_stats.copy()
        stats.update(self.renderer.get_stats())
        stats.update(self.asset_loader.get_loading_stats())
        return stats
    
    def preload_scene_assets(self, asset_config: dict):
        """Preload assets for a scene to avoid loading stutters."""
        self.asset_loader.preload_assets(asset_config)
    
    def optimize_memory(self):
        """Optimize memory usage by clearing unnecessary caches."""
        self.renderer.clear_caches()
        self.asset_loader.cleanup_unused_assets()
        print("Memory optimization complete")
    
    def get_cache_info(self):
        """Get information about engine cache usage."""
        renderer_cache = self.renderer.get_cache_info()
        asset_cache = self.asset_loader.get_loading_stats()
        return {
            'renderer': renderer_cache,
            'assets': asset_cache
        }
