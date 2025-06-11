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

        # Event system
        from .event_system import event_system
        self.event_system = event_system

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

        # Advanced 2D/2.5D engine features
        self.particle_systems = []
        self.animation_manager = None
        self.shader_manager = None
        self.post_processing_effects = []
        self.lighting_system = None
        self.tilemap_system = None

        # Scripting and UI systems
        self.script_manager = None
        self.ui_manager = None

        # Game creation tools
        self.game_templates = {}
        self.scripting_system = None
        self.level_streaming = False
        self.dynamic_batching = True

        # Enhanced rendering pipeline
        self.render_layers = {
            "background": -100,
            "world": 0,
            "entities": 100,
            "effects": 200,
            "ui": 1000
        }

        # Initialize profiler callback
        self.profiler.add_report_callback(self._handle_performance_report)

        # Try to load config file
        self.config.load_from_file("config/engine.json")

        # Debug overlay
        from .debug_overlay import DebugOverlay
        self.debug_overlay = DebugOverlay(self)

        # Initialize advanced 2D/2.5D systems
        self._initialize_advanced_systems()

        # Initialize advanced asset streaming
        from .asset_streaming import AssetStreamingSystem
        self.asset_streaming = AssetStreamingSystem(max_memory_mb=1024)
        self.asset_streaming.start_background_loading()
        
        # Initialize advanced quadtree system
        from ..physics.quadtree import AdvancedQuadTree
        world_size = 20000  # Large world support
        self.spatial_quadtree = AdvancedQuadTree(
            (-world_size, -world_size, world_size * 2, world_size * 2),
            max_objects=15,
            max_depth=10
        )

        # Initialize performance monitoring
        from ..tools.performance_monitor import PerformanceMonitor
        self.performance_monitor = PerformanceMonitor(self)

        # Initialize shader manager
        try:
            from ..rendering.shader_manager import ShaderManager
            self.shader_manager = ShaderManager()
            # Enable retro mode for pixel-perfect 2D games
            self.shader_manager.set_retro_mode(True, 1)
            print("Shader manager initialized with retro mode")
        except ImportError:
            self.shader_manager = None

        # Initialize spatial audio
        try:
            from ..audio.spatial_audio import SpatialAudioManager
            self.spatial_audio = SpatialAudioManager()
            print("Spatial audio system initialized")
        except ImportError:
            self.spatial_audio = None

        engine_logger.engine_start(self.width, self.height, self.target_fps)

        # Validate engine systems
        try:
            from .engine_validator import validate_engine
            if not validate_engine(self):
                print("⚠️ Engine validation found issues, but continuing...")
            else:
                print("✅ Engine validation passed - all systems healthy")
        except ImportError:
            print("Engine validator not available")

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

                # Calculate delta time with frame limiting
                dt = self.clock.tick(self.target_fps)
                self.delta_time = min(dt / 1000.0, 0.05)  # Cap at 50ms to prevent spiral of death

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

                # Update scripting system
                if self.script_manager:
                    script_profile = self.profiler.start_profile("script_update")
                    self.script_manager.update(self.delta_time)
                    self.profiler.end_profile(script_profile)

                # Update UI system
                if self.ui_manager:
                    ui_profile = self.profiler.start_profile("ui_update")
                    self.ui_manager.update(self.delta_time)
                    self.profiler.end_profile(ui_profile)

                # Debug: Check scene status
                if not self.current_scene:
                    if frame_count % 60 == 0:  # Print every second
                        print("Warning: No current scene set")
                    continue

                try:
                    # Process game events
                    event_profile = self.profiler.start_profile("event_processing")
                    self.event_system.process_events()
                    self.profiler.end_profile(event_profile)

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

                    # Update advanced systems
                    advanced_profile = self.profiler.start_profile("advanced_systems")
                    if hasattr(self, 'particle_system_manager') and self.particle_system_manager is not None:
                        self.particle_system_manager.update(self.delta_time)
                    if hasattr(self, 'animation_manager') and self.animation_manager is not None:
                        self.animation_manager.update(self.delta_time)
                    if hasattr(self, 'lighting_system') and self.lighting_system is not None:
                        self.lighting_system.update(self.delta_time)

                    # Update performance monitoring
                    if hasattr(self, 'performance_monitor'):
                        self.performance_monitor.update(self.delta_time)

                    # Update spatial audio
                    if hasattr(self, 'spatial_audio') and self.spatial_audio:
                        # Update listener position based on camera
                        if hasattr(self, 'camera') and self.camera:
                            self.spatial_audio.set_listener_position(self.camera.transform.position)
                        self.spatial_audio.update(self.delta_time)

                    self.profiler.end_profile(advanced_profile)

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

                    # Render tilemap if available
                    tilemap_profile = self.profiler.start_profile("tilemap_render")
                    if hasattr(self, 'tilemap_system') and self.tilemap_system is not None:
                        viewport = pygame.Rect(0, 0, self.width, self.height)
                        self.tilemap_system.render(self.renderer, viewport)
                    self.profiler.end_profile(tilemap_profile)

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

                    # Render particle systems
                    particles_profile = self.profiler.start_profile("particles_render")
                    if hasattr(self, 'particle_system_manager') and self.particle_system_manager is not None:
                        self.particle_system_manager.render(self.renderer)
                    self.profiler.end_profile(particles_profile)

                    # Call user render callback
                    if self.render_callback:
                        callback_render_profile = self.profiler.start_profile("user_render")
                        self.render_callback()
                        self.profiler.end_profile(callback_render_profile)

                    # Render UI system (always on top)
                    if self.ui_manager:
                        ui_render_profile = self.profiler.start_profile("ui_render")
                        self.ui_manager.render(self.renderer)
                        self.profiler.end_profile(ui_render_profile)

                    # Debug overlay (only if explicitly enabled and working)
                    if (hasattr(self, 'debug_overlay') and 
                        self.debug_overlay.visible and 
                        self.debug_overlay.debug_render_enabled):
                        try:
                            debug_profile = self.profiler.start_profile("debug_overlay")
                            self.debug_overlay.render(self.renderer)
                            self.profiler.end_profile(debug_profile)
                        except Exception as e:
                            # Disable debug overlay on error
                            self.debug_overlay.visible = False
                            print(f"Debug overlay disabled due to error: {e}")

                    # Apply post-processing shaders
                    if hasattr(self, 'shader_manager') and self.shader_manager:
                        # Process the final frame through shader pipeline
                        # Note: This would require additional surface management
                        pass

                    # Render performance overlay
                    if hasattr(self, 'performance_monitor'):
                        self.performance_monitor.render_overlay(self.renderer)

                    # Ensure the display is updated
                    present_profile = self.profiler.start_profile("present")
                    if hasattr(self, 'renderer') and hasattr(self.renderer, 'flush_sprite_batch'):
                        self.renderer.flush_sprite_batch()
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
                elif event.key == pygame.K_F12:  # F12 to take screenshot
                    self.take_screenshot()
                elif event.key == pygame.K_PAUSE or (event.key == pygame.K_p and pygame.key.get_pressed()[pygame.K_LCTRL]):
                    # Pause/Resume with Pause key or Ctrl+P
                    if self.state_manager.get_current_state() == EngineState.RUNNING:
                        self.pause_engine()
                    elif self.state_manager.get_current_state() == EngineState.PAUSED:
                        self.resume_engine()

            # Pass events to UI manager first
            if self.ui_manager:
                self.ui_manager.handle_event(event)

            # Pass events to input manager
            self.input_manager.handle_event(event)

        # Update input manager state
        self.input_manager.update()

    def _initialize_advanced_systems(self):
        """Initialize advanced 2D/2.5D engine systems."""
        # Initialize systems to None first
        self.particle_system_manager = None
        self.animation_manager = None
        self.tilemap_system = None
        self.lighting_system = None
        self.post_processing = None

        # Try to initialize particle system manager
        try:
            from ..effects.particle_system import ParticleSystemManager
            self.particle_system_manager = ParticleSystemManager()
            print("Particle system initialized")
        except (ImportError, AttributeError) as e:
            print(f"Particle system not available: {e}")
            self.particle_system_manager = None

        # Try to initialize animation system
        try:
            from ..animation.animation_manager import AnimationManager
            self.animation_manager = AnimationManager()
            print("Animation system initialized")
        except (ImportError, AttributeError) as e:
            print(f"Animation system not available: {e}")
            self.animation_manager = None

        # Try to initialize tilemap system
        try:
            from ..tilemap.tilemap_system import TilemapSystem
            self.tilemap_system = TilemapSystem()
            print("Tilemap system initialized")
        except ImportError as e:
            print(f"Tilemap system not available: {e}")

        # Try to initialize lighting system for 2.5D
        try:
            from ..lighting.lighting_system import LightingSystem
            self.lighting_system = LightingSystem()
            print("Lighting system initialized")
        except ImportError as e:
            print(f"Lighting system not available: {e}")

        # Try to initialize post-processing pipeline
        try:
            from ..effects.post_processing import PostProcessingPipeline
            self.post_processing = PostProcessingPipeline(self.screen)
            print("Post-processing initialized")
        except ImportError as e:
            print(f"Post-processing not available: {e}")

        # Initialize scripting system
        try:
            from ..scripting.script_manager import ScriptManager
            self.script_manager = ScriptManager()
            print("Scripting system initialized")
        except ImportError as e:
            print(f"Scripting system not available: {e}")
            self.script_manager = None

        # Initialize UI system
        try:
            from ..ui.ui_manager import UIManager
            self.ui_manager = UIManager()
            print("UI system initialized")
        except ImportError as e:
            print(f"UI system not available: {e}")
            self.ui_manager = None

        print("Advanced 2D/2.5D systems initialization complete")

    def _cleanup(self):
        """
        Clean up resources before shutting down.
        """
        try:
            if self.current_scene:
                self.current_scene.on_exit()

            # Generate final performance report
            if hasattr(self, 'profiler') and self.profiler:
                try:
                    self.profiler.save_report("logs/final_performance_report.json")
                except Exception as e:
                    print(f"Could not save performance report: {e}")

            # Clean up enhanced systems
            if hasattr(self, 'world_manager') and self.world_manager:
                try:
                    self.world_manager.unload_level()
                except Exception as e:
                    print(f"Error cleaning up world manager: {e}")

            if hasattr(self, 'resource_manager') and self.resource_manager:
                try:
                    self.resource_manager.cleanup()
                except Exception as e:
                    print(f"Error cleaning up resource manager: {e}")

            # Clean up particle systems
            if hasattr(self, 'particle_system_manager') and self.particle_system_manager:
                try:
                    self.particle_system_manager.clear_all_systems()
                except Exception as e:
                    print(f"Error cleaning up particle systems: {e}")

            # Clean up audio
            if hasattr(self, 'audio_manager') and self.audio_manager:
                try:
                    self.audio_manager.cleanup()
                except Exception as e:
                    print(f"Error cleaning up audio: {e}")

            # Clean up renderer
            if hasattr(self, 'renderer') and self.renderer:
                try:
                    if hasattr(self.renderer, 'cleanup'):
                        self.renderer.cleanup()
                except Exception as e:
                    print(f"Error cleaning up renderer: {e}")

        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            try:
                pygame.quit()
            except Exception:
                pass  # Ignore pygame quit errors

            # Don't call sys.exit() - let the program end naturally

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

    def take_screenshot(self, filename: str = None) -> str:
        """
        Take a screenshot of the current game window.

        Args:
            filename: Optional filename for the screenshot

        Returns:
            Path to the saved screenshot
        """
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        # Ensure screenshots directory exists
        import os
        os.makedirs("screenshots", exist_ok=True)
        filepath = os.path.join("screenshots", filename)

        # Save the current screen
        pygame.image.save(self.screen, filepath)
        print(f"Screenshot saved: {filepath}")
        return filepath

    def get_memory_usage(self) -> dict:
        """Get detailed memory usage information."""
        import psutil
        import os

        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            return {
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),  # Resident memory
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2),  # Virtual memory
                'cpu_percent': process.cpu_percent(),
                'num_threads': process.num_threads()
            }
        except ImportError:
            return {'error': 'psutil not available for memory monitoring'}

    def pause_engine(self):
        """Pause the engine execution."""
        if self.state_manager.get_current_state() == EngineState.RUNNING:
            self.state_manager.transition_to(EngineState.PAUSED)
            print("Engine paused")

    def resume_engine(self):
        """Resume the engine execution."""
        if self.state_manager.get_current_state() == EngineState.PAUSED:
            self.state_manager.transition_to(EngineState.RUNNING)
            print("Engine resumed")

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

    # Game Creation Utilities
    def create_particle_effect(self, position: Vector2, effect_type: str = "explosion", duration: float = 2.0):
        """Create a particle effect at the specified position."""
        if hasattr(self, 'particle_system_manager'):
            system = self.particle_system_manager.create_system(position, effect_type)

            if effect_type == "explosion":
                system.emit_burst(50)
                system.auto_emit = False

            # Auto-remove after duration
            def remove_system():
                system.active = False

            # Simple timer (in a full implementation, use a proper timer system)
            system._removal_timer = duration
            return system
        return None

    def create_tilemap_from_file(self, name: str, filepath: str):
        """Create a tilemap from a JSON file."""
        if hasattr(self, 'tilemap_system'):
            try:
                import json
                with open(filepath, 'r') as f:
                    data = json.load(f)
                return self.tilemap_system.load_tilemap_from_data(name, data)
            except Exception as e:
                print(f"Failed to load tilemap from {filepath}: {e}")
        return None

    def create_sprite_animation(self, name: str, sprite_sheet_path: str, 
                              frame_width: int, frame_height: int, 
                              frame_count: int, frame_rate: float = 10.0):
        """Create a sprite animation from a sprite sheet."""
        if hasattr(self, 'animation_manager'):
            try:
                sprite_sheet = pygame.image.load(sprite_sheet_path)
                self.animation_manager.load_sprite_sheet(name + "_sheet", sprite_sheet)

                frame_duration = 1.0 / frame_rate
                return self.animation_manager.create_sprite_animation(
                    name, name + "_sheet", frame_width, frame_height,
                    frame_count, frame_duration
                )
            except Exception as e:
                print(f"Failed to create sprite animation: {e}")
        return None

    def quick_setup_platformer(self, player_start: Vector2, level_data: dict = None):
        """Quick setup for a platformer game."""
        # Set up physics for platformer
        self.physics_engine.set_gravity(980)  # Standard gravity

        # Create tilemap if level data provided
        if level_data and hasattr(self, 'tilemap_system'):
            tilemap = self.tilemap_system.load_tilemap_from_data("main_level", level_data)
            self.tilemap_system.set_active_tilemap("main_level")

        # Set rendering mode
        self.set_rendering_mode("2D")

        print("Platformer setup complete!")
        return True

    def quick_setup_top_down(self, enable_lighting: bool = True):
        """Quick setup for a top-down game."""
        # Disable gravity for top-down
        self.physics_engine.set_gravity(0)

        # Set rendering mode
        if enable_lighting:
            self.set_rendering_mode("2.5D")
        else:
            self.set_rendering_mode("2D")

        print("Top-down game setup complete!")
        return True

    def add_simple_enemy_ai(self, enemy_object, target_object, speed: float = 100.0):
        """Add simple AI that follows a target."""
        def ai_update(delta_time):
            if not enemy_object.active or not target_object.active:
                return

            # Simple follow AI
            direction = target_object.transform.position - enemy_object.transform.position
            if direction.magnitude() > 50:  # Don't get too close
                direction = direction.normalized()
                enemy_object.transform.position += direction * speed * delta_time

        # In a real implementation, this would be a proper component
        if not hasattr(enemy_object, '_ai_update'):
            enemy_object._ai_update = ai_update
            enemy_object._original_update = enemy_object.update

            def combined_update(delta_time):
                enemy_object._original_update(delta_time)
                enemy_object._ai_update(delta_time)

            enemy_object.update = combined_update

        return True


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