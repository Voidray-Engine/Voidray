from .core.engine import Engine, configure, on_init, on_update, on_render, register_scene, set_scene, start, stop, get_engine
from .core.game_object import GameObject
from .core.scene import Scene
from .rendering.sprite import Sprite
from .rendering.camera import Camera
from .input.input_manager import InputManager, Keys, MouseButtons
from .physics.collision import Collider, BoxCollider, CircleCollider
from .physics.rigidbody import Rigidbody
from .audio.audio_manager import AudioManager
from .math.vector2 import Vector2
from .math.transform import Transform

# Enhanced features
from .core.component_registry import ComponentRegistry, register_component, create_component
from .core.debug_overlay import DebugOverlay
from .core.resource_manager import ResourceManager

# Development tools
try:
    from .tools.level_editor import LevelEditor
    from .tools.project_templates import ProjectTemplateManager, template_manager
except ImportError:
    # Tools are optional
    LevelEditor = None
    ProjectTemplateManager = None
    template_manager = None

__version__ = "2.5-stable"
__author__ = "VoidRay Team"

# Main exports for easy importing
__all__ = [
    # Engine API
    'Engine',
    'configure',
    'on_init', 
    'on_update',
    'on_render',
    'register_scene',
    'set_scene',
    'start',
    'stop',
    'get_engine',

    # Core components
    'GameObject', 
    'Scene',
    'Sprite',
    'Camera',
    'InputManager',
    'Keys',
    'MouseButtons',
    'Collider',
    'BoxCollider', 
    'CircleCollider',
    'Rigidbody',
    'AudioManager',
    'Vector2',
    'Transform'
]