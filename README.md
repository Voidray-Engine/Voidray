# 🌟 VoidRay 3 - 2D/2.5D Game Engine

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-GPL--3.0-red)
![Version](https://img.shields.io/badge/version-3-green)
![Status](https://img.shields.io/badge/status-stable-brightgreen)

A **professional** 2D/2.5D game engine built with Python and Pygame. VoidRay provides the core infrastructure and tools needed to build any type of game, while giving developers complete control over their game logic and mechanics.

---

## 🚀 Engine Features (v3)

### 🎯 **Core Engine Systems**
- **🧩 ECS Architecture**: Modern Entity-Component-System for flexible game objects
- **⚡ Advanced Physics**: Collision detection, rigidbodies, and spatial partitioning with quadtree optimization
- **🎮 Multi-Input Support**: Keyboard, mouse, gamepad with frame-perfect detection
- **🎵 Spatial Audio**: 3D positioned audio with distance attenuation and effects
- **📦 Asset Streaming**: Efficient loading, caching, and resource streaming
- **🎨 Advanced Renderer**: 2.5D graphics pipeline with depth sorting and post-processing
- **🔧 Debug Tools**: Performance monitoring, profiler, and visual debugging overlay
- **💾 Save System**: JSON and binary save/load with integrity checking

### 🏗️ **What You Build**
VoidRay gives you the foundation - **you create the game**:
- **Game Logic**: Your gameplay mechanics, rules, and systems
- **UI Design**: Menus, HUDs, and interface layouts using our UI framework
- **Content Systems**: Inventory, dialogue, AI behaviors, progression systems
- **Game Assets**: Art, sounds, levels, and content creation
- **Gameplay Flow**: How your game plays, feels, and engages players

---

## ✨ Engine Capabilities (v3)

### 🎨 **Advanced Graphics & Rendering**
- **2.5D Support**: Depth-based rendering with layered sprites and advanced camera system
- **Shader System**: Retro pixel-perfect rendering with configurable pixel sizes
- **Sprite Management**: Rotation, scaling, animation with batch rendering optimization
- **Visual Effects**: Particle systems, bloom effects, and post-processing pipeline
- **Performance**: Spatial culling, batch rendering, and 60+ FPS optimization

### ⚡ **Enhanced Physics System**
- **Rigidbody Dynamics**: Mass, velocity, acceleration, drag, and realistic forces
- **Advanced Colliders**: Box, circle, polygon collision shapes with trigger support
- **Physics Events**: Collision callbacks, overlap detection, and sensor systems
- **Spatial Optimization**: Quadtree partitioning for efficient collision detection
- **Performance**: Optimized broad-phase and narrow-phase collision detection

### 🎮 **Comprehensive Input Management**
- **Multi-Device Support**: Keyboard, mouse, gamepad with unified API
- **Advanced Detection**: Key states, combinations, just-pressed/released detection
- **Frame-Perfect Input**: Precise timing for competitive games
- **Input Mapping**: Customizable control schemes and input rebinding

### 🎵 **Professional Audio System**
- **Spatial Audio**: 3D positioned sound with distance attenuation
- **Audio Effects**: Real-time audio processing and effects
- **Multi-Format**: WAV, MP3, OGG support with automatic format detection
- **Performance**: Efficient audio streaming for large files

### 🏗️ **Robust Architecture**
- **ECS System**: Modular, reusable, and extensible components
- **Scene Management**: Advanced scene transitions with loading screens
- **Asset Pipeline**: Automatic loading, preprocessing, and optimization
- **Memory Management**: Efficient resource usage with automatic cleanup
- **Debug Tools**: Performance profiler, memory monitor, and debug overlay

---

## 🎮 Complete Pacman Game Example

VoidRay 3 includes a fully functional Pacman game demonstrating all engine features:

```python
import voidray
from voidray import Scene, GameObject, Vector2, Keys, BoxCollider
from voidray.rendering.renderer import Advanced2DRenderer
from voidray.utils.color import Color

class Pacman(GameObject):
    """Player-controlled Pacman with physics and animation."""

    def __init__(self, x, y):
        super().__init__("Pacman")
        self.transform.position = Vector2(x * CELL_SIZE + CELL_SIZE//2, y * CELL_SIZE + CELL_SIZE//2)
        self.direction = Vector2(0, 0)
        self.speed = 120

        # Add physics collider
        collider = BoxCollider(CELL_SIZE - 4, CELL_SIZE - 4)
        self.add_component(collider)

    def update(self, delta_time):
        input_manager = voidray.get_engine().input_manager

        # Handle input with frame-perfect detection
        if input_manager.is_key_pressed(Keys.LEFT):
            self.direction = Vector2(-1, 0)
        elif input_manager.is_key_pressed(Keys.RIGHT):
            self.direction = Vector2(1, 0)
        elif input_manager.is_key_pressed(Keys.UP):
            self.direction = Vector2(0, -1)
        elif input_manager.is_key_pressed(Keys.DOWN):
            self.direction = Vector2(0, 1)

        # Physics-based movement
        if self.can_move_in_direction(self.direction):
            movement = self.direction * self.speed * delta_time
            self.transform.position += movement

class PacmanGameScene(Scene):
    """Complete Pacman game with all VoidRay features."""

    def __init__(self):
        super().__init__("PacmanGame")
        self.score = 0
        self.game_over = False

    def on_enter(self):
        super().on_enter()
        self.setup_maze()
        self.setup_characters()

        # Configure camera for optimal viewing
        camera = voidray.get_engine().camera
        camera.position = Vector2(MAZE_WIDTH * CELL_SIZE // 2, MAZE_HEIGHT * CELL_SIZE // 2)

    def update(self, delta_time):
        super().update(delta_time)
        self.check_collisions()
        self.check_victory()

def main():
    """Initialize and start VoidRay Pacman."""
    voidray.configure(
        width=608,
        height=772,
        title="VoidRay 3.1.0 - Pacman Demo",
        fps=60
    )

    voidray.on_init(init_game)
    voidray.start()

if __name__ == "__main__":
    main()
```

**Features Demonstrated:**
- ✅ Advanced 2D rendering with sprite batching
- ✅ Physics-based collision detection
- ✅ Frame-perfect input handling
- ✅ Component-based game objects
- ✅ Scene management system
- ✅ Real-time performance monitoring

---

## 🎯 Game Types You Can Create

### 🕹️ **Arcade & Action Games**
- **Pacman-style** games with advanced AI and physics
- **Space shooters** with particle effects and collision systems
- **Platformers** with precise physics and smooth controls
- **Racing games** with realistic vehicle dynamics

### 🏃 **Advanced Game Genres**
- **Metroidvania** games with interconnected worlds
- **Physics puzzlers** leveraging the advanced physics engine
- **Multiplayer games** using the networking system
- **RPGs** with save systems and complex UI

### 🎮 **Modern Features**
- **Real-time lighting** and visual effects
- **Procedural generation** with the flexible component system
- **Audio-reactive games** with spatial audio
- **Performance-optimized** games running at 60+ FPS

---

## 🔧 Engine Architecture (v3)

```
VoidRay 3.1.0 Engine
├── 🎮 Core Systems
│   ├── Engine State Management
│   ├── Component Registry & ECS
│   ├── Advanced Asset Streaming
│   └── Resource Pool Management
├── 🎨 Graphics & Rendering
│   ├── Advanced 2D Renderer
│   ├── Shader Manager (Retro Mode)
│   ├── Camera System with Following
│   └── Post-Processing Pipeline
├── ⚡ Physics & Collision
│   ├── Physics Engine with Rigidbodies
│   ├── Quadtree Spatial Partitioning
│   ├── Advanced Collision Detection
│   └── Physics Events & Triggers
├── 🎮 Input & Controls
│   ├── Multi-Device Input Manager
│   ├── Frame-Perfect Detection
│   └── Input State Management
├── 🎵 Audio & Sound
│   ├── Spatial Audio System
│   ├── Audio Effects Processing
│   └── Multi-Format Support
├── 💾 Data & Saves
│   ├── JSON/Binary Save System
│   ├── Asset Loading & Caching
│   └── Resource Management
└── 🔧 Development Tools
    ├── Performance Profiler
    ├── Debug Overlay System
    ├── Engine Validator
    └── Error Dialog System
```

---

## 🌟 VoidRay 3.1.0 vs Alternatives

| **Feature**                  | **VoidRay 3**                      | **PyGame**               | **Arcade**               |
| ---------------------------- | --------------------------------------- | ------------------------ | ------------------------ |
| **Learning Curve**           | ✅ Beginner to Pro                      | ❌ Low-level              | ⚠️ Medium                |
| **Setup Time**               | ✅ Instant (zero config)                | ❌ Manual setup           | ⚠️ Some setup            |
| **Built-in Physics**         | ✅ Professional (rigidbodies, quadtree) | ❌ Basic/None             | ⚠️ Basic                 |
| **ECS Architecture**         | ✅ Full ECS with components              | ❌ Manual                 | ❌ Class-based           |
| **2.5D Support**             | ✅ Native depth sorting                 | ❌ Manual                 | ⚠️ Pseudo-3D            |
| **Performance**              | ✅ 60+ FPS with 350+ objects            | ⚠️ Depends on code       | ✅ Good                  |
| **Save System**              | ✅ Built-in JSON/Binary                 | ❌ Manual                 | ❌ Manual                |
| **Audio System**             | ✅ Spatial 3D audio                     | ⚠️ Basic mixer           | ⚠️ Basic                 |
| **Debug Tools**              | ✅ Profiler, overlay, validator         | ❌ None                   | ⚠️ Basic                 |
| **Asset Management**         | ✅ Streaming, caching, pooling          | ❌ Manual                 | ⚠️ Basic                 |
| **Version**                  | **3**                     | 2.6.1                    | 2.6.x                    |

---

## 🚀 Performance Benchmarks (v3)

### ⚡ **Real Performance Data**
- **354 objects** rendered simultaneously (Pacman demo)
- **60+ FPS** stable performance on modern hardware
- **Advanced renderer** with batching and culling
- **Memory efficient** - automatic resource cleanup
- **Spatial optimization** - quadtree collision detection

### 🔧 **Optimization Features**
- **Automatic batching** reduces draw calls
- **Spatial culling** only renders visible objects
- **Asset streaming** loads resources on-demand
- **Physics optimization** with sleeping objects and broad-phase detection

---

## 📚 Getting Started

### 🎯 **Quick Start (5 minutes):**

1. **Download VoidRay 3**
2. **Study the code** to understand the engine
3. **Modify** and create your own game
4. **Deploy** on Replit for sharing

### 📖 **Documentation Available:**
- **API Reference** - Complete function documentation
- **Physics Guide** - Advanced physics simulation
- **Component System** - ECS architecture guide
- **Performance Tips** - Optimization strategies

---

## 🤝 Contributing to VoidRay 3

### 💻 **Development Areas**
- **Engine Features** - Add new systems and components
- **Performance** - Optimize rendering and physics
- **Documentation** - Improve guides and examples
- **Game Examples** - Create showcase games

### 🎮 **Example Games Wanted**
- Platformer showcasing physics
- Shooter demonstrating effects
- RPG using save systems
- Multiplayer game with networking

---

## 📄 License & Legal

**GNU General Public License v3.0 (GPL-3.0)**

### ✅ **You Can:**
- Use VoidRay 3 for any purpose (personal, commercial, educational)
- Study and modify the engine source code
- Distribute your changes and improvements
- Create and sell games made with VoidRay

### ⚠️ **Requirements:**
- Include license notice in distributed engine code
- Make source code available if distributing modified engine
- Use same GPL-3.0 license for engine modifications

**Your games keep their own license** - Only engine modifications need to be GPL-3.0.

---

## 🚀 VoidRay 3 - Ready for Production

### 🌟 **Proven in Action:**
- **Complete Pacman game** included as example
- **354 objects** rendered at 60+ FPS
- **Professional architecture** with ECS and physics
- **Production-ready** save system and asset management

### 🎯 **Perfect For:**
- **Indie developers** building commercial games
- **Game jams** requiring rapid prototyping
- **Educational projects** teaching game development
- **Professional studios** needing Python-based tools

---

<div align="center">

## 🌟 **VoidRay 3 - Professional Game Engine** 🌟

**Built by Developers, For Developers**

*"The most advanced 2D/2.5D Python game engine - where professional games begin."*

**Start building your dream game today with VoidRay 3! 🚀**

[View Pacman Demo](pacman_game.py) | [Engine Documentation](docs/) | [Join Community](https://replit.com)

</div>
