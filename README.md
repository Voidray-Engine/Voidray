
# 🌟 VoidRay 2D Game Engine

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-GPL--3.0-red)
![Version](https://img.shields.io/badge/version-2.0.0-green)

A **lightweight**, **beginner-friendly** 2D game engine built with Python and Pygame. Perfect for learning game development, rapid prototyping, and creating indie games!

---

## 🚀 What Makes VoidRay Special?

- **🎯 Beginner-Friendly**: Clean API designed for learning
- **⚡ Rapid Development**: Create games in minutes, not hours
- **🧩 Component System**: Modern ECS-inspired architecture
- **🔬 Built-in Physics**: Realistic collisions and movement
- **🎮 Complete Input System**: Keyboard, mouse, and gamepad support
- **🎵 Audio Support**: Music and sound effects
- **📱 Cross-Platform**: Works on Windows, macOS, and Linux
- **🆓 100% Free**: Open source under GPL-3.0

---

## ✨ Engine Features

### 🎨 **Graphics & Rendering**
- Sprite rendering with rotation and scaling
- Camera system with following and smoothing
- Color utilities and drawing primitives
- Performance-optimized rendering pipeline

### ⚡ **Physics System**
- **Rigidbody Components**: Mass, velocity, forces, and drag
- **Collision Detection**: Box and circle colliders
- **Physics Events**: Collision callbacks and triggers
- **Gravity System**: Customizable world gravity

### 🎮 **Input Management**
- **Keyboard**: Key press, hold, and release detection
- **Mouse**: Position tracking and button states
- **Frame-perfect Input**: Just-pressed and just-released events

### 🎵 **Audio System**
- Music playback with looping
- Sound effects with volume control
- Multiple audio format support

### 🏗️ **Architecture**
- **Scene Management**: Easy level/menu switching
- **Component System**: Modular, reusable components
- **Asset Loading**: Automatic resource management
- **Delta Time**: Frame-rate independent movement

---

## 🎮 Quick Start Example

Create a complete game in just a few lines:

```python
import voidray
from voidray import Scene, Sprite, Vector2, Keys, BoxCollider, Rigidbody
from voidray.graphics.renderer import Color

class Player(Sprite):
    def __init__(self):
        super().__init__("Player")
        self.create_colored_rect(40, 40, Color.BLUE)
        self.speed = 300

        # Add collision detection
        self.collider = BoxCollider(40, 40)
        self.add_component(self.collider)

    def update(self, delta_time):
        super().update(delta_time)

        # Handle input
        input_manager = voidray.get_engine().input_manager
        velocity = Vector2.zero()

        if input_manager.is_key_pressed(Keys.LEFT):
            velocity.x = -self.speed
        if input_manager.is_key_pressed(Keys.RIGHT):
            velocity.x = self.speed

        # Move with smooth delta time
        self.transform.position += velocity * delta_time

class Ball(Sprite):
    def __init__(self):
        super().__init__("Ball")
        self.create_colored_circle(20, Color.RED)

        # Add realistic physics
        self.rigidbody = Rigidbody()
        self.rigidbody.set_mass(1.0)
        self.rigidbody.set_bounciness(0.8)
        self.add_component(self.rigidbody)

        # Add collision
        self.collider = CircleCollider(20)
        self.add_component(self.collider)

class GameScene(Scene):
    def on_enter(self):
        super().on_enter()

        # Create player
        player = Player()
        player.transform.position = Vector2(400, 500)
        self.add_object(player)

        # Create physics ball
        ball = Ball()
        ball.transform.position = Vector2(400, 100)
        self.add_object(ball)

def init_game():
    # Set up gravity
    voidray.get_engine().physics_system.set_gravity(500)
    
    # Create and start scene
    scene = GameScene()
    voidray.register_scene("game", scene)
    voidray.set_scene("game")

def main():
    # Configure and start engine
    voidray.configure(800, 600, "Physics Game", 60)
    voidray.on_init(init_game)
    voidray.start()

if __name__ == "__main__":
    main()
```

**Result**: A complete game with physics, collision detection, and smooth controls!

---

## 🎯 What Can You Build?

### 🕹️ **Arcade Games**
- Asteroids, Pong, Breakout
- Pac-Man style maze games
- Snake and classic puzzles

### 🏃 **Platformers**
- 2D jump-and-run games
- Physics-based puzzlers
- Metroidvania-style exploration

### 🎯 **Action Games**
- Top-down shooters
- Bullet-hell games
- Battle arena fighters

### 🧩 **Physics Games**
- Angry Birds style projectile games
- Pool/billiards simulations
- Marble rolling puzzles

### 📚 **Educational Games**
- Math and science simulations
- Interactive tutorials
- Programming learning tools

---

## 📦 Installation

**Requirements**: Python 3.8+ 

```bash
# Clone the repository
git clone https://github.com/yourusername/voidray-engine.git
cd voidray-engine

# Install dependencies (automatically handled)
python main.py
```

**That's it!** The engine auto-installs Pygame and sets everything up.

---

## 🎓 Learning Resources

- **📖 [Getting Started Guide](docs/getting_started.txt)** - Your first game in 5 minutes
- **📚 [API Reference](docs/api_reference.txt)** - Complete function documentation  
- **⚡ [Physics Guide](docs/physics_guide.txt)** - Master the physics system
- **🎮 [Basic Game Tutorial](docs/tutorial_basic_game.txt)** - Step-by-step game creation
- **💡 [Examples](examples/)** - Working code samples

---

## 🏗️ Engine Architecture

```
VoidRay Engine
├── 🎮 Core System
│   ├── Scene Management
│   ├── Game Object Hierarchy  
│   └── Component System
├── 🎨 Graphics
│   ├── Sprite Rendering
│   ├── Camera System
│   └── Performance Optimization
├── ⚡ Physics
│   ├── Rigidbody Dynamics
│   ├── Collision Detection
│   └── Physics Events
├── 🎮 Input
│   ├── Keyboard & Mouse
│   └── Event Processing
└── 🎵 Audio
    ├── Music Playback
    └── Sound Effects
```

---

## 🌟 Key Advantages

| Feature | VoidRay | Other Engines |
|---------|---------|---------------|
| **Learning Curve** | ✅ Beginner-friendly | ❌ Complex setup |
| **Code-Only** | ✅ Pure Python | ❌ Visual editors required |
| **Setup Time** | ✅ Instant | ❌ Hours of configuration |
| **Physics Built-in** | ✅ Ready to use | ❌ Separate libraries |
| **Documentation** | ✅ Extensive guides | ❌ Sparse or technical |
| **File Size** | ✅ Lightweight | ❌ Gigabytes |

---

## 🤝 Contributing

We love contributions! Whether you're:
- 🐛 **Reporting bugs**
- 💡 **Suggesting features** 
- 📝 **Improving documentation**
- 🔧 **Writing code**

Check out our [contribution guidelines](CONTRIBUTING.md) to get started!

---

## 📄 License

**GNU General Public License v3.0 (GPL-3.0)**

VoidRay is free and open source. You can:
- ✅ Use it for any purpose
- ✅ Study and modify the code  
- ✅ Distribute your changes
- ✅ Use it commercially

---

## 🚀 Try It Now!

**Ready to start creating?**

[![Run on Replit](https://replit.com/badge/github/yourusername/voidray-engine)](https://replit.com/@yourusername/voidray-engine)

Or clone locally and run:
```bash
python main.py
```

**Your first game is just minutes away!** 🎮✨

---

<div align="center">

**Made with ❤️ by the VoidRay Team**

[Documentation](docs/) • [Examples](examples/) • [Issues](https://github.com/yourusername/voidray-engine/issues) • [Discussions](https://github.com/yourusername/voidray-engine/discussions)

</div>
