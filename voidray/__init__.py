"""
VoidRay Game Engine

A powerful 2D/2.5D game engine built with Python and Pygame.
Provides comprehensive tools for game development including physics,
graphics, audio, input handling, and more.
"""

# Core engine components
from .core.engine import VoidRayEngine, Engine
from .core.scene import Scene
from .core.game_object import GameObject
from .core.component import Component

# Graphics and rendering
from .graphics.sprite import Sprite
from .graphics.camera import Camera
from .graphics.renderer import Color

# Math utilities
from .math.vector2 import Vector2
from .math.transform import Transform

# Input handling
from .input.input_manager import InputManager, Keys

# Physics system
from .physics.physics_engine import PhysicsEngine
from .physics.physics_system import PhysicsSystem
from .physics.collider import Collider, RectCollider, CircleCollider, BoxCollider
from .physics.rigidbody import Rigidbody

# Audio
from .audio.audio_manager import AudioManager

# Utilities
from .utils.color import Color as UtilColor
from .utils.time import Time
from .utils.save_system import save_system

# Core systems
from .core.event_system import event_system, EventType, GameEvent
from .core.scene_transitions import SceneTransition, TransitionType

# Global engine instance
_engine = None


def configure(width: int = 800,
              height: int = 600,
              title: str = "VoidRay Game",
              fps: int = 60):
    """Configure the game engine with basic settings."""
    global _engine
    _engine = VoidRayEngine()
    _engine.configure(width, height, title, fps)
    return _engine


def start():
    """Start the game engine."""
    if _engine:
        _engine.start()
    else:
        print("Error: Engine not configured. Call voidray.configure() first.")


def stop():
    """Stop the game engine."""
    if _engine:
        _engine.stop()


def get_engine():
    """Get the current engine instance."""
    return _engine


def on_init(callback):
    """Register initialization callback."""
    if _engine:
        _engine.on_init(callback)


def on_update(callback):
    """Register update callback."""
    if _engine:
        _engine.on_update(callback)


def on_render(callback):
    """Register render callback."""
    if _engine:
        _engine.on_render(callback)


def register_scene(name: str, scene):
    """Register a scene with the engine."""
    if _engine:
        _engine.register_scene(name, scene)


def set_scene(name_or_scene):
    """Set the active scene."""
    if _engine:
        _engine.set_scene(name_or_scene)


def get_scene():
    """Get the current active scene."""
    if _engine:
        return _engine.scene_manager.get_current_scene()
    return None


# Version info
__version__ = "3.0.5"
__author__ = "VoidRay Team"

# Main exports
__all__ = [
    # Core
    'Engine',
    'VoidRayEngine',
    'Scene',
    'GameObject',
    'Component',

    # Graphics
    'Sprite',
    'Camera',
    'Color',

    # Math
    'Vector2',
    'Transform',

    # Input
    'InputManager',
    'Keys',

    # Physics
    'PhysicsEngine',
    'PhysicsSystem',
    'Collider',
    'RectCollider',
    'CircleCollider',
    'BoxCollider',
    'Rigidbody',

    # Audio
    'AudioManager',

    # Utilities
    'UtilColor',
    'Time',
    'save_system',

    # Core systems
    'event_system',
    'EventType',
    'GameEvent',
    'SceneTransition',
    'TransitionType',

    # Engine functions
    'configure',
    'start',
    'stop',
    'get_engine',
    'on_init',
    'on_update',
    'on_render',
    'register_scene',
    'set_scene',
    'get_scene'
]
# Error handling
from .core.error_dialog import show_fatal_error
