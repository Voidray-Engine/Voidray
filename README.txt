# VoidRay 2D Game Engine

A lightweight and beginner-friendly 2D game engine built with **Python** and **Pygame**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-GPL--3.0-red)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## 🚀 About

**VoidRay** is a clean and minimal 2D game engine designed for rapid development and learning. It’s built with Python and Pygame and offers the essential components to start building 2D games right away — without needing a visual editor.

VoidRay is fully open-source under the **GNU General Public License v3.0 (GPL-3.0)**, encouraging freedom to study, modify, and distribute.

---

## ✨ Features

- ✅ Basic 2D rendering system with sprite support
- ✅ Keyboard and mouse input handling
- ✅ Physics and collision system
- ✅ Scene and game state management
- ✅ Audio playback (music & sound effects)
- ✅ Vector math utilities (`Vector2`, `Transform`)
- ✅ Asset loading and caching
- ✅ Pure code workflow – no editor required
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Beginner-friendly examples and docs

---

## 📦 Installation

Requires **Python 3.8+** and [Pygame](https://www.pygame.org/).

```bash
pip install pygame

---

## 🕹 Quick Start

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
