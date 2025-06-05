
from .core.engine import Engine, configure, on_init, on_update, on_render, register_scene, set_scene, start, stop, get_engine
from .core.game_object import GameObject
from .core.scene import Scene
from .graphics.sprite import Sprite
from .graphics.camera import Camera
from .input.input_manager import InputManager, Keys, MouseButtons
from .physics.collision import Collider, BoxCollider, CircleCollider
from .physics.rigidbody import Rigidbody
from .audio.audio_manager import AudioManager
from .math.vector2 import Vector2
from .math.transform import Transform

__version__ = "2.0.0"
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
