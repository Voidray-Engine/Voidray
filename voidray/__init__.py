"""
VoidRay 2D Game Engine
A lightweight, easy-to-use 2D game engine built with Python and Pygame.

Author: VoidRay Development Team
Version: 1.0.0
"""

from .core.engine import Engine
from .core.game_object import GameObject
from .core.scene import Scene
from .graphics.sprite import Sprite
from .graphics.camera import Camera
from .input.input_manager import InputManager, Keys, MouseButtons
from .physics.collider import Collider, RectCollider, CircleCollider
from .audio.audio_manager import AudioManager
from .math.vector2 import Vector2
from .math.transform import Transform

__version__ = "1.0.0"
__author__ = "VoidRay Development Team"

# Main exports for easy importing
__all__ = [
    'Engine',
    'GameObject', 
    'Scene',
    'Sprite',
    'Camera',
    'InputManager',
    'Keys',
    'MouseButtons',
    'Collider',
    'RectCollider', 
    'CircleCollider',
    'AudioManager',
    'Vector2',
    'Transform'
]
