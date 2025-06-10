
# 🌟 VoidRay 2D/2.5D Game Engine

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-GPL--3.0-red)
![Version](https://img.shields.io/badge/version-2.5.4--stable-green)
![Status](https://img.shields.io/badge/status-stable-brightgreen)

A **powerful**, **feature-rich** 2D/2.5D game engine built with Python and Pygame. Perfect for indie developers, game studios, and anyone wanting to create professional-quality games with ease!

---

## 🚀 What Makes VoidRay Engine Special?

### 🎯 **Professional Grade Features**
- **🧩 Advanced Component System**: Modern ECS architecture with modular components
- **⚡ High-Performance Physics**: Realistic collisions, rigidbodies, and forces
- **🎮 Complete Input System**: Keyboard, mouse, gamepad support with frame-perfect detection
- **🎵 Professional Audio**: 3D positioned audio, streaming, multiple format support
- **📦 Smart Asset Management**: Automatic loading, caching, and streaming
- **🎨 2.5D Rendering**: Advanced graphics with depth, layering, and effects
- **🔧 Visual Editor**: Built-in GUI editor with syntax highlighting and debugging tools

### 🏗️ **Engine Architecture**
- **Scene Management**: Seamless level transitions and state management
- **Resource Streaming**: Memory-efficient asset loading for large games
- **Debug Systems**: Real-time performance monitoring and debugging overlay
- **Cross-Platform**: Windows, macOS, Linux support with consistent performance

---

## ✨ Engine Capabilities

### 🎨 **Advanced Graphics & Rendering**
- **2.5D Support**: Depth-based rendering with layered sprites
- **Camera System**: Following, smoothing, shake effects, and multiple camera support
- **Sprite Management**: Rotation, scaling, animation, and batch rendering
- **Visual Effects**: Particles, lighting, and post-processing effects
- **Performance**: Optimized rendering pipeline with culling and batching

### ⚡ **Enhanced Physics System**
- **Rigidbody Dynamics**: Mass, velocity, acceleration, drag, and realistic forces
- **Advanced Colliders**: Box, circle, polygon, and custom collision shapes
- **Physics Events**: Collision callbacks, triggers, and sensor detection
- **World Physics**: Customizable gravity, air resistance, and material properties
- **Performance**: Spatial partitioning and optimized collision detection

### 🎮 **Comprehensive Input Management**
- **Multi-Device Support**: Keyboard, mouse, gamepad, and touch input
- **Advanced Detection**: Key states, combinations, and gesture recognition
- **Frame-Perfect Input**: Just-pressed, just-released, and hold detection
- **Input Mapping**: Customizable control schemes and input rebinding

### 🎵 **Professional Audio System**
- **3D Audio**: Positioned sound with distance attenuation and doppler effects
- **Streaming**: Memory-efficient audio streaming for large files
- **Multi-Format**: WAV, MP3, OGG support with automatic format detection
- **Audio Bus**: Volume mixing, effects, and real-time audio processing

### 🏗️ **Robust Architecture**
- **Component System**: Modular, reusable, and extensible components
- **Scene Management**: Advanced scene transitions with loading screens
- **Asset Pipeline**: Automatic loading, preprocessing, and optimization
- **Memory Management**: Efficient resource usage with automatic cleanup
- **Debug Tools**: Performance profiler, memory monitor, and debug overlay

---

## 🎮 Complete Game Example

Create a professional physics-based game in minutes:

```python
import voidray
from voidray import Scene, Sprite, Vector2, Keys, BoxCollider, Rigidbody
from voidray.graphics.renderer import Color

class AdvancedPlayer(Sprite):
    """Player with advanced physics and abilities."""
    
    def __init__(self):
        super().__init__("Player")
        self.create_colored_rect(40, 40, Color.BLUE)
        self.speed = 400
        self.jump_force = 600
        
        # Add physics components
        self.rigidbody = Rigidbody()
        self.rigidbody.set_mass(1.0)
        self.rigidbody.set_drag(0.1)
        self.add_component(self.rigidbody)
        
        # Add collision detection
        self.collider = BoxCollider(40, 40)
        self.collider.on_collision = self.handle_collision
        self.add_component(self.collider)
        
        self.on_ground = False
        self.double_jump_available = True

    def handle_collision(self, other, collision_info):
        """Handle collisions with other objects."""
        if collision_info.normal.y < 0:  # Hit ground
            self.on_ground = True
            self.double_jump_available = True

    def update(self, delta_time):
        super().update(delta_time)
        
        input_manager = voidray.get_engine().input_manager
        
        # Horizontal movement with acceleration
        horizontal_input = 0
        if input_manager.is_key_pressed(Keys.LEFT):
            horizontal_input = -1
        if input_manager.is_key_pressed(Keys.RIGHT):
            horizontal_input = 1
            
        # Apply horizontal force
        if horizontal_input != 0:
            force = Vector2(horizontal_input * self.speed * 10, 0)
            self.rigidbody.add_force(force)
        
        # Jumping with double jump
        if input_manager.is_key_just_pressed(Keys.SPACE):
            if self.on_ground:
                self.rigidbody.add_impulse(Vector2(0, -self.jump_force))
                self.on_ground = False
            elif self.double_jump_available:
                self.rigidbody.set_velocity(Vector2(self.rigidbody.velocity.x, 0))
                self.rigidbody.add_impulse(Vector2(0, -self.jump_force * 0.8))
                self.double_jump_available = False

class MovingPlatform(Sprite):
    """A moving platform with collision."""
    
    def __init__(self, start_pos, end_pos, speed=100):
        super().__init__("Platform")
        self.create_colored_rect(120, 20, Color.GREEN)
        
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.speed = speed
        self.direction = 1
        
        # Add collision
        self.collider = BoxCollider(120, 20)
        self.add_component(self.collider)
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Move between start and end positions
        current_pos = self.transform.position
        target = self.end_pos if self.direction == 1 else self.start_pos
        
        # Move towards target
        movement = (target - current_pos).normalized() * self.speed * delta_time
        self.transform.position += movement
        
        # Check if reached target
        if (target - current_pos).magnitude() < 10:
            self.direction *= -1

class GameScene(Scene):
    """Main game scene with advanced features."""
    
    def __init__(self):
        super().__init__("Advanced Game")
        self.player = None
        self.platforms = []
        
    def on_enter(self):
        super().on_enter()
        
        # Create player
        self.player = AdvancedPlayer()
        self.player.transform.position = Vector2(100, 400)
        self.add_object(self.player)
        
        # Create static platforms
        for i, pos in enumerate([(200, 500), (400, 400), (600, 350)]):
            platform = Sprite(f"Platform_{i}")
            platform.create_colored_rect(120, 20, Color.GRAY)
            platform.transform.position = Vector2(*pos)
            
            collider = BoxCollider(120, 20)
            platform.add_component(collider)
            self.add_object(platform)
            
        # Create moving platforms
        moving_platform = MovingPlatform(
            Vector2(300, 250), 
            Vector2(500, 250), 
            80
        )
        moving_platform.transform.position = Vector2(300, 250)
        self.add_object(moving_platform)
        self.platforms.append(moving_platform)
        
        # Set up camera to follow player
        camera = voidray.get_engine().camera
        camera.follow_target = self.player
        camera.smoothing = 0.1
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check for quit
        if voidray.get_engine().input_manager.is_key_just_pressed(Keys.ESCAPE):
            voidray.stop()
            
    def render(self, renderer):
        super().render(renderer)
        
        # Draw UI
        renderer.draw_text("VoidRay 2.5-Stable Engine Demo", Vector2(10, 10), Color.WHITE, 24)
        renderer.draw_text("Arrow keys to move, SPACE to jump (double jump available!)", 
                          Vector2(10, 40), Color.LIGHT_GRAY, 16)
        renderer.draw_text("ESC to quit", Vector2(10, 70), Color.LIGHT_GRAY, 16)
        
        # Performance info
        fps = voidray.get_engine().get_fps()
        objects_count = len(self.objects)
        renderer.draw_text(f"FPS: {fps:.1f} | Objects: {objects_count}", 
                          Vector2(10, voidray.get_engine().height - 30), Color.YELLOW, 16)

def init_game():
    """Initialize the advanced game."""
    print("Starting VoidRay 2.5-stable Advanced Demo...")
    
    # Configure physics
    engine = voidray.get_engine()
    engine.physics_system.set_gravity(800)  # Realistic gravity
    
    # Create and start scene
    scene = GameScene()
    voidray.register_scene("game", scene)
    voidray.set_scene("game")

def main():
    """Main entry point."""
    voidray.configure(
        width=1024, 
        height=768, 
        title="VoidRay 2.5-stable - Advanced Engine Demo", 
        fps=60
    )
    
    voidray.on_init(init_game)
    voidray.start()

if __name__ == "__main__":
    main()
```

**Result**: A complete game with advanced physics, moving platforms, double jumping, camera following, and professional UI!

---

## 🎯 Game Types You Can Create

### 🕹️ **Arcade & Action Games**
- Asteroids, Space Invaders, Breakout with modern physics
- Beat-em-up and fighting games with combo systems
- Racing games with realistic vehicle physics
- Bullet-hell shooters with particle effects

### 🏃 **Platformers & Adventure**
- Super Mario-style platformers with advanced movement
- Metroidvania games with interconnected worlds
- Puzzle platformers with physics-based solutions
- Sonic-style high-speed gameplay

### 🎯 **Simulation & Strategy**
- Physics simulation games (Angry Birds, World of Goo)
- Tower defense with projectile physics
- City builders and management games
- Educational simulations and interactive demos

### 🎮 **Modern Game Genres**
- Roguelike dungeons with procedural generation
- Multiplayer arena battles
- Rhythm games with audio synchronization
- Interactive storytelling with branching narratives

---

## 📦 Installation & Setup

**Requirements**: Python 3.8+ (Recommended: Python 3.12+)

### Quick Start (Replit)
1. **Fork this Repl** - Everything is pre-configured!
2. **Click Run** - The engine auto-installs dependencies
3. **Start Creating** - Use the built-in editor or modify examples

### Local Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/voidray-engine.git
cd voidray-engine

# Dependencies install automatically when you run
python main.py
```

### Using the GUI Editor
```bash
# Launch the advanced code editor
python gui_editor.py
```

---

## 🎓 Learning Resources & Documentation

### 📚 **Complete Guides**
- **[📖 Getting Started Guide](docs/getting_started.txt)** - Build your first game in 10 minutes
- **[📘 API Reference](docs/api_reference.txt)** - Complete function and class documentation  
- **[⚡ Advanced Physics Guide](docs/physics_guide.txt)** - Master realistic physics simulation
- **[🎮 Complete Game Tutorial](docs/tutorial_basic_game.txt)** - Step-by-step professional game development

### 🔧 **Development Tools**
- **Built-in GUI Editor** - Professional code editor with syntax highlighting
- **Debug Overlay** - Real-time performance monitoring
- **Asset Browser** - Visual asset management
- **Scene Inspector** - Live game object debugging

---

## 🏗️ Advanced Engine Architecture

```
VoidRay 2.5.4-stable Engine
├── 🎮 Core Systems
│   ├── Advanced Scene Management
│   ├── Component-Based Architecture (ECS)
│   ├── Professional Asset Pipeline
│   └── Multi-threaded Resource Loading
├── 🎨 Graphics & Rendering
│   ├── 2.5D Rendering Pipeline
│   ├── Advanced Camera System
│   ├── Batch Rendering & Culling
│   └── Visual Effects System
├── ⚡ Physics & Collision
│   ├── High-Performance Physics Engine
│   ├── Advanced Collision Detection
│   ├── Realistic Material Properties
│   └── Spatial Optimization
├── 🎮 Input & Controls
│   ├── Multi-Device Input System
│   ├── Gesture Recognition
│   ├── Input Mapping & Rebinding
│   └── Frame-Perfect Detection
├── 🎵 Audio & Sound
│   ├── 3D Positioned Audio
│   ├── Streaming Audio System
│   ├── Real-time Audio Effects
│   └── Audio Bus & Mixing
└── 🔧 Development Tools
    ├── Visual Code Editor
    ├── Debug & Profiling Tools
    ├── Asset Management
    └── Scene Inspector
```

---

## 🌟 VoidRay vs Other Engines

| Feature | VoidRay 2.5.4-stable | Unity 2D | Godot | PyGame |
|---------|---------------------|-----------|-------|--------|
| **Learning Curve** | ✅ Beginner to Pro | ❌ Complex | ⚠️ Moderate | ❌ Low-level |
| **Setup Time** | ✅ Instant | ❌ Hours | ⚠️ Moderate | ❌ Manual setup |
| **Built-in Physics** | ✅ Professional | ✅ Advanced | ✅ Good | ❌ Basic/None |
| **Code-First** | ✅ Pure Python | ❌ Visual editor | ⚠️ Mixed | ✅ Code only |
| **2.5D Support** | ✅ Native | ⚠️ Workarounds | ✅ Good | ❌ Manual |
| **File Size** | ✅ Lightweight | ❌ Gigabytes | ⚠️ Moderate | ✅ Small |
| **Free & Open** | ✅ GPL-3.0 | ❌ Limited free | ✅ MIT | ✅ LGPL |
| **Learning Resources** | ✅ Comprehensive | ✅ Extensive | ✅ Good | ⚠️ Scattered |

---

## 🚀 Performance & Optimization

### ⚡ **Engine Performance**
- **30/60+ FPS** stable performance on modern hardware
- **Memory Efficient** - Smart asset loading and garbage collection
- **Scalable** - Handles 1000+ objects with spatial optimization
- **Cross-Platform** - Consistent performance across all platforms

### 🔧 **Optimization Features**
- **Automatic Batching** - Reduces draw calls for better performance
- **Culling System** - Only renders visible objects
- **Asset Streaming** - Loads resources on-demand
- **Physics Optimization** - Spatial partitioning and sleeping objects

---

## 🤝 Contributing & Community

We welcome all types of contributions:

### 💻 **Code Contributions**
- Fork the repository and create feature branches
- Follow our coding standards and include tests
- Submit pull requests with detailed descriptions

### 📚 **Documentation & Examples**  
- Improve documentation and tutorials
- Create example games and demos
- Write blog posts about your VoidRay projects
- Share your games in our showcase

---

## 📄 License & Legal

**GNU General Public License v3.0 (GPL-3.0)**

### ✅ **You Can:**
- Use VoidRay for any purpose (personal, commercial, educational)
- Study and modify the source code
- Distribute your changes and improvements
- Create and sell games made with VoidRay

### ⚠️ **Requirements:**
- Include license notice in distributed code
- Make source code available if distributing modified engine
- Use same GPL-3.0 license for engine modifications

**Your games keep their own license** - Only engine modifications need to be GPL-3.0.

---

## 🚀 Get Started Today!

### 🎯 **Your First Game in 5 Minutes:**
1. **Run** `python gui_editor.py`
2. **Select** a template (Platformer, Shooter, Puzzle)
3. **Customize** with the visual editor
4. **Test** by clicking Run
5. **Share** your creation!

---

<div align="center">

## 🌟 **Built by Developers, For Developers** 🌟

**VoidRay 2.5.4-stable** - *Where Ideas Become Games*

---

*"The best game engine is the one that gets out of your way and lets you create."*

**Start building your dream game today! 🚀**

</div>
