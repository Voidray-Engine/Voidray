"""
VoidRay Engine Core
The main engine class that manages the game loop, systems, and overall execution.
"""

import pygame
import sys
from typing import Optional, Dict, Any, Callable
from ..graphics.renderer import Renderer
from ..input.input_manager import InputManager
from ..physics.physics_engine import PhysicsEngine
from ..audio.audio_manager import AudioManager
from ..assets.asset_loader import AssetLoader
from .scene import Scene
from .resource_manager import ResourceManager
from .engine_state import EngineStateManager, EngineState
from .config import EngineConfig
from .logger import engine_logger
from .error_dialog import show_fatal_error
from pygame import Vector2


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
        self.resource_manager = None
        self.state_manager = EngineStateManager()  # Initialize immediately
        self.config = None

        # Enhanced scene management
        from .scene_manager import SceneManager
        self.scene_manager = SceneManager()
        self.current_scene: Optional[Scene] = None
        self.scenes: Dict[str, Scene] = {}
        self.delta_time = 0.0
        
        # World management for large-scale games
        from .world_manager import WorldManager
        self.world_manager = WorldManager()
        
        # Performance profiling
        from .profiler import PerformanceProfiler
        self.profiler = PerformanceProfiler()

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

        # Create the display window with explicit flags
        flags = pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption(self.title)
        
        # Fill screen with black initially to ensure it's visible
        self.screen.fill((0, 0, 0))
        pygame.display.flip()
        
        # Initialize the clock
        self.clock = pygame.time.Clock()

        # Initialize systems
        try:
            from ..rendering.renderer import Advanced2DRenderer
            self.renderer = Advanced2DRenderer(self.screen)
            print("Advanced 2.5D renderer initialized")
        except (ImportError, AttributeError) as e:
            # Fallback to basic renderer
            from ..graphics.renderer import Renderer
            self.renderer = Renderer(self.screen)
            print("Basic renderer initialized")
        self.input_manager = InputManager()
        self.asset_loader = AssetLoader(cache_size=500, enable_streaming=True)
        self.audio_manager = AudioManager(channels=32)

        # Initialize physics systems
        self.physics_engine = PhysicsEngine()
        try:
            from ..physics.physics_system import PhysicsSystem
            self.physics_system = PhysicsSystem()
            # Connect the systems
            self.physics_system.physics_engine = self.physics_engine
        except ImportError:
            self.physics_system = self.physics_engine

        # Create default camera
        from ..rendering.camera import Camera
        self.camera = Camera()

        # 2.5D rendering mode
        self.rendering_mode = "2D"  # Can be "2D" or "2.5D"
        self.camera_position = Vector2(0, 0)
        self.camera_angle = 0.0

        # Initialize renderer attributes
        self.renderer.rendering_mode = "2D"
        self.renderer.render_distance = 1000
        self.renderer.fog_distance = 800

        # Enhanced features for demanding games
        self.performance_mode = False
        self.vsync_enabled = True
        self.multithreading_enabled = True

        # Enhanced resource management with streaming
        self.resource_manager = ResourceManager(max_memory_mb=1024, enable_streaming=True)
        self.config = EngineConfig()
        
        # Initialize profiler callback
        self.profiler.add_report_callback(self._handle_performance_report)

        # Try to load config file
        self.config.load_from_file("config/engine.json")

        # Debug overlay
        from .debug_overlay import DebugOverlay
        self.debug_overlay = DebugOverlay(self)

        engine_logger.engine_start(self.width, self.height, self.target_fps)

        # Call user initialization
        if self.init_callback:
            print("Calling user initialization callback...")
            try:
                self.init_callback()
                print("User initialization completed successfully")
            except Exception as e:
                print(f"Error in user initialization: {e}")
                import traceback
                traceback.print_exc()
                
                # Show error dialog for initialization errors
                try:
                    show_fatal_error(
                        "Game Initialization Error",
                        f"Failed to initialize the game.\n\nError: {str(e)}",
                        e
                    )
                except Exception as dialog_error:
                    print(f"Error dialog failed: {dialog_error}")
                
                # Stop the engine
                self.stop()
                return
        else:
            print("No initialization callback registered")

    def start(self):
        """
        Start the game engine.
        """
        if self.running:
            return

        self.state_manager.transition_to(EngineState.INITIALIZING)
        self._initialize_systems()
        self.state_manager.transition_to(EngineState.RUNNING)
        self._run_main_loop()

    def _run_main_loop(self):
        """
        Run the main game loop.
        """
        self.running = True
        print("Starting VoidRay engine...")

        # Performance tracking and statistics
        frame_count = 0
        performance_timer = 0
        self.engine_stats = {
            'frames_rendered': 0,
            'objects_rendered': 0,
            'physics_objects': 0,
            'memory_usage': 0,
            'rendering_mode': self.rendering_mode,
            'performance_mode': self.performance_mode
        }

        try:
            while self.running:
                # Start frame profiling
                self.profiler.start_frame()
                profile_id = self.profiler.start_profile("main_loop")
                
                # Calculate delta time
                dt = self.clock.tick(self.target_fps)
                self.delta_time = dt / 1000.0  # Convert to seconds

            # Performance monitoring and statistics
                frame_count += 1
                performance_timer += self.delta_time
                self.engine_stats['frames_rendered'] += 1

                if performance_timer >= 1.0:  # Every second
                    actual_fps = frame_count / performance_timer
                    self.engine_stats['objects_rendered'] = len(self.current_scene.objects) if self.current_scene else 0
                    self.engine_stats['physics_objects'] = len(self.physics_engine.colliders)

                    if actual_fps < self.target_fps * 0.8:  # If FPS drops below 80% of target
                        engine_logger.warning(f"Performance warning: FPS dropped to {actual_fps:.1f}")
                        self._optimize_performance()

                    frame_count = 0
                    performance_timer = 0

                # Handle input events
                self._handle_events()
                
                # Debug: Check scene status
                if not self.current_scene:
                    if frame_count % 60 == 0:  # Print every second
                        print("Warning: No current scene set")
                    continue

                try:
                    # Update current scene
                    update_profile = self.profiler.start_profile("scene_update")
                    if self.current_scene:
                        self.current_scene.update(self.delta_time)
                    self.profiler.end_profile(update_profile)

                    # Call user update callback
                    if self.update_callback:
                        callback_profile = self.profiler.start_profile("user_update")
                        self.update_callback(self.delta_time)
                        self.profiler.end_profile(callback_profile)

                    # Update physics with optimization
                    physics_profile = self.profiler.start_profile("physics_update")
                    self.physics_engine.update(self.delta_time)
                    if hasattr(self, 'physics_system'):
                        self.physics_system.update(self.delta_time)
                    self.profiler.end_profile(physics_profile)
                    
                    # Update world manager
                    world_profile = self.profiler.start_profile("world_update")
                    # Update player position for streaming (would get from player object)
                    # self.world_manager.update_player_position(player_position)
                    self.profiler.end_profile(world_profile)

                except Exception as e:
                    engine_logger.error(f"Update error: {e}")
                    # Continue running instead of crashing

                try:
                    # Render frame
                    render_profile = self.profiler.start_profile("render_frame")
                    self.renderer.clear()

                    # Render current scene
                    scene_render_profile = self.profiler.start_profile("scene_render")
                    if self.current_scene:
                        self.current_scene.render(self.renderer)
                        if frame_count % 60 == 0:  # Debug output every second
                            print(f"Rendering scene with {len(self.current_scene.objects)} objects")
                    else:
                        # Draw a debug message if no scene
                        font = pygame.font.Font(None, 24)
                        text = font.render("No Scene Loaded", True, (255, 255, 255))
                        self.screen.blit(text, (10, 10))
                    self.profiler.end_profile(scene_render_profile)

                    # Call user render callback
                    if self.render_callback:
                        callback_render_profile = self.profiler.start_profile("user_render")
                        self.render_callback()
                        self.profiler.end_profile(callback_render_profile)

                    # Debug overlay completely disabled
                    # if hasattr(self, 'debug_overlay') and self.debug_overlay.visible:
                    #     debug_profile = self.profiler.start_profile("debug_overlay")
                    #     self.debug_overlay.render(self.renderer)
                    #     self.profiler.end_profile(debug_profile)

                    # Ensure the display is updated
                    present_profile = self.profiler.start_profile("present")
                    self.renderer.present()
                    self.profiler.end_profile(present_profile)
                    
                    self.profiler.end_profile(render_profile)
                    
                    # Force pygame event processing to keep window responsive
                    pygame.event.pump()
                    
                    # End frame profiling
                    self.profiler.end_profile(profile_id)
                    self.profiler.end_frame()

                except Exception as e:
                    engine_logger.error(f"Render error: {e}")
                    print(f"Render error details: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # For critical render errors, show dialog and stop
                    if "get_text_size" in str(e) or "AttributeError" in str(type(e).__name__):
                        try:
                            show_fatal_error(
                                "Rendering System Error",
                                f"A critical rendering error has occurred.\n\nError: {str(e)}",
                                e
                            )
                        except Exception as dialog_error:
                            print(f"Error dialog failed: {dialog_error}")
                        self.stop()
                        break
                    # Continue running for non-critical errors

        except KeyboardInterrupt:
            print("Engine stopped by user")
        except Exception as e:
            engine_logger.error(f"Critical engine error: {e}")
            print(f"Engine crashed with error: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error dialog
            try:
                show_fatal_error(
                    "VoidRay Engine Fatal Error",
                    f"The game engine has encountered a critical error and must close.\n\nError: {str(e)}",
                    e
                )
            except Exception as dialog_error:
                print(f"Error dialog failed: {dialog_error}")
        finally:
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:  # F3 to toggle debug overlay
                    self.debug_overlay.toggle()

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

        # Generate final performance report
        if hasattr(self, 'profiler'):
            self.profiler.save_report("logs/final_performance_report.json")
            
        # Clean up enhanced systems
        if hasattr(self, 'world_manager'):
            self.world_manager.unload_level()
            
        if hasattr(self, 'resource_manager'):
            self.resource_manager.cleanup()

        self.audio_manager.cleanup()
        pygame.quit()
        sys.exit()
    
    def _handle_performance_report(self, report: Dict[str, Any]):
        """Handle performance reports for optimization."""
        # Auto-optimize based on performance
        frame_stats = report.get('frame_stats', {})
        avg_fps = frame_stats.get('avg_fps', 60)
        
        if avg_fps < self.target_fps * 0.8:  # If FPS drops below 80% of target
            print(f"Performance degradation detected (FPS: {avg_fps:.1f})")
            self._auto_optimize()
    
    def _auto_optimize(self):
        """Automatically optimize performance when needed."""
        # Reduce render distance
        if hasattr(self, 'renderer') and hasattr(self.renderer, 'render_distance'):
            self.renderer.render_distance *= 0.9
        
        # Free memory
        if hasattr(self, 'resource_manager'):
            self.resource_manager._free_memory()
        
        # Optimize physics
        self.physics_engine.optimize_performance()
        
        print("Auto-optimization applied")

    def get_fps(self) -> float:
        """Get the current frames per second."""
        return self.clock.get_fps() if self.clock else 0

    def get_delta_time(self) -> float:
        """Get the time elapsed since the last frame in seconds."""
        return self.delta_time

    def get_engine_stats(self) -> dict:
        """Get engine performance statistics."""
        stats = self.engine_stats.copy()
        if hasattr(self, 'audio_manager'):
            stats['audio_info'] = self.audio_manager.get_audio_info()
        if hasattr(self, 'asset_loader'):
            stats['asset_usage'] = self.asset_loader.get_memory_usage()
        return stats

    def get_scene_object_count(self) -> int:
        """Get the number of objects in the current scene."""
        return len(self.current_scene.objects) if self.current_scene else 0

    def set_rendering_mode(self, mode: str):
        """
        Set rendering mode for 2D or 2.5D games.

        Args:
            mode: "2D" for traditional 2D, "2.5D" for pseudo-3D
        """
        if mode in ["2D", "2.5D"]:
            self.rendering_mode = mode
            self.renderer.set_rendering_mode(mode)
            print(f"Rendering mode set to {mode}")

    def enable_performance_mode(self, enabled: bool = True):
        """
        Enable performance mode for demanding games.

        Args:
            enabled: Whether to enable performance optimizations
        """
        self.performance_mode = enabled

        if enabled:
            # Reduce some quality settings for better performance
            self.renderer.set_render_distance(800)
            self.physics_engine.set_spatial_grid_size(150)
            print("Performance mode enabled")
        else:
            # Restore quality settings
            self.renderer.set_render_distance(1000)
            self.physics_engine.set_spatial_grid_size(200)
            print("Performance mode disabled")

    def preload_game_assets(self, asset_packs: Dict[str, Dict]):
        """
        Preload assets for demanding games.

        Args:
            asset_packs: Dictionary of asset pack configurations
        """
        print("Preloading game assets for better performance...")

        for pack_name, pack_config in asset_packs.items():
            self.asset_loader.preload_asset_pack(pack_name, pack_config)

        print("Asset preloading complete")

    def set_audio_quality(self, quality: str):
        """
        Set audio quality level.

        Args:
            quality: "low", "medium", "high"
        """
        if quality == "low":
            frequency, channels = 22050, 16
        elif quality == "medium":
            frequency, channels = 44100, 24
        else:  # high
            frequency, channels = 48000, 32

        # Note: Would require audio system restart in full implementation
        print(f"Audio quality set to {quality}")

    def optimize_for_mobile(self):
        """Optimize engine settings for mobile/low-end devices."""
        self.enable_performance_mode(True)
        self.set_audio_quality("medium")
        self.renderer.set_fog_distance(600)
        self.asset_loader.cache.max_size = 100
        print("Mobile optimizations applied")

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

    

    def load_level(self, level_name: str, scene_name: str = None):
        """Load a 2.5D level into the current or specified scene."""
        target_scene = self.current_scene
        if scene_name and scene_name in self.scenes:
            target_scene = self.scenes[scene_name]

        if target_scene:
            target_scene.load_level(level_name, self.asset_loader)

            # Set up renderer with level data
            if self.rendering_mode == "2.5D":
                self._setup_2_5d_level(target_scene)
        else:
            print("No scene available to load level into")

    def _setup_2_5d_level(self, scene):
        """Set up the 2.5D renderer with level data."""
        # Clear existing geometry
        self.renderer.walls.clear()
        self.renderer.sectors.clear()
        self.renderer.light_sources.clear()

        # Add walls from scene
        for wall_data in scene.get_walls():
            start = Vector2(wall_data['start']['x'], wall_data['start']['y'])
            end = Vector2(wall_data['end']['x'], wall_data['end']['y'])
            texture = wall_data.get('texture')
            height = wall_data.get('height', 64)

            self.renderer.add_wall(start, end, texture, height)

        # Add light sources
        for light_data in scene.get_light_sources():
            position = Vector2(light_data['x'], light_data['y'])
            intensity = light_data.get('intensity', 1.0)
            radius = light_data.get('radius', 100.0)
            color = tuple(light_data.get('color', [255, 255, 255]))

            self.renderer.add_light_source(position, intensity, color, radius)

        print(f"Set up 2.5D level with {len(self.renderer.walls)} walls and {len(self.renderer.light_sources)} lights")

    def create_sample_textures(self):
        """Create sample procedural textures for testing."""
        textures_to_create = [
            ("brick", "brick"),
            ("stone", "stone"), 
            ("metal", "metal")
        ]

        for name, pattern in textures_to_create:
            self.renderer.create_procedural_texture(name, 64, 64, pattern)

        print("Created sample procedural textures")

    def set_camera_2_5d(self, position: Vector2, angle: float):
        """Set 2.5D camera position and angle."""
        self.camera_position = position
        self.camera_angle = angle


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