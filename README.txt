VoidRay 2D Game Engine
======================

A lightweight, easy-to-use 2D game engine built with Python and Pygame.

VERSION: 1.0.0
LICENSE: Open Source
AUTHOR: VoidRay Development Team

DESCRIPTION
-----------
VoidRay is a simple yet powerful 2D game engine designed for rapid prototyping and learning game development. Built on top of Pygame, it provides a clean, object-oriented framework for creating 2D games with minimal boilerplate code.

FEATURES
--------
✓ Core 2D rendering system with sprite support
✓ Comprehensive input handling (keyboard, mouse)
✓ Physics system with collision detection
✓ Audio system for sound effects and music
✓ Scene management for organizing game states
✓ Asset loading and caching system
✓ Mathematical utilities (Vector2, Transform)
✓ Cross-platform compatibility (Windows, macOS, Linux)
✓ No external editor required - pure code approach
✓ Extensive documentation and examples

QUICK START
-----------
1. Install Python 3.8+ and Pygame:
   pip install pygame

2. Create your first game:

```python
from voidray import Engine, Scene, Sprite, Vector2
from voidray.graphics.renderer import Color

class Player(Sprite):
    def __init__(self):
        super().__init__("Player")
        self.create_colored_rect(32, 32, Color.BLUE)

class GameScene(Scene):
    def on_enter(self):
        player = Player()
        player.transform.position = Vector2(400, 300)
        self.add_object(player)

engine = Engine(800, 600, "My Game")
engine.set_scene(GameScene())
engine.run()
