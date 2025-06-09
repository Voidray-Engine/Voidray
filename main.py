"""
The code has been updated to include 2.5D rendering capabilities and a mode selection feature.
"""
"""
VoidRay Game Engine - Physics & Components Demo
==============================================

This demonstrates the physics system and component-based architecture
with collisions, rigidbodies, and proper component usage.
"""

import voidray
from voidray import Scene, GameObject, Sprite, Vector2, Keys, BoxCollider, CircleCollider, Rigidbody
from voidray.utils.color import Color
import random


class Ball(Sprite):
    """A bouncing ball with physics."""

    def __init__(self, radius=15):
        super().__init__("Ball")
        self.create_colored_circle(radius, (255, 255, 0))  # Yellow
        self.radius = radius

        # Add physics components
        self.rigidbody = Rigidbody()
        self.rigidbody.set_mass(1.0)
        self.rigidbody.set_bounciness(0.8)
        self.rigidbody.set_drag(0.1)
        self.add_component(self.rigidbody)

        # Add collision using the newer collision system
        self.collider = CircleCollider(radius)
        self.add_component(self.collider)

        # Give it some initial velocity
        initial_velocity = Vector2(
            random.uniform(-200, 200),
            random.uniform(-300, -100)
        )
        self.rigidbody.set_velocity(initial_velocity)

    

    def update(self, delta_time):
        super().update(delta_time)

        # Keep ball on screen with bouncing
        engine = voidray.get_engine()
        pos = self.transform.position
        vel = self.rigidbody.velocity

        # Bounce off walls
        if pos.x <= 15 or pos.x >= engine.width - 15:
            vel.x = -vel.x * 0.8
            pos.x = max(15, min(engine.width - 15, pos.x))

        if pos.y <= 15:
            vel.y = -vel.y * 0.8
            pos.y = 15

        if pos.y >= engine.height - 15:
            vel.y = -vel.y * 0.8
            pos.y = engine.height - 15

        self.rigidbody.set_velocity(vel)


class Player(Sprite):
    """A player that can move around and has collision."""

    def __init__(self):
        super().__init__("Player")
        self.create_colored_rect(40, 40, (0, 0, 255))  # Blue
        self.speed = 300

        # Add collision detection using the newer collision system
        self.collider = BoxCollider(40, 40)
        self.add_component(self.collider)

    def update(self, delta_time):
        super().update(delta_time)

        # Get input from the engine
        input_manager = voidray.get_engine().input_manager

        # Move the player
        velocity = Vector2.zero()
        if input_manager.is_key_pressed(Keys.LEFT):
            velocity.x = -self.speed
        if input_manager.is_key_pressed(Keys.RIGHT):
            velocity.x = self.speed
        if input_manager.is_key_pressed(Keys.UP):
            velocity.y = -self.speed
        if input_manager.is_key_pressed(Keys.DOWN):
            velocity.y = self.speed

        # Apply movement
        self.transform.position += velocity * delta_time

        # Keep player on screen
        engine = voidray.get_engine()
        self.transform.position.x = max(20, min(engine.width - 20, self.transform.position.x))
        self.transform.position.y = max(20, min(engine.height - 20, self.transform.position.y))


class PhysicsScene(Scene):
    """A scene that demonstrates physics and components."""

    def __init__(self):
        super().__init__("Physics Demo")
        self.player = None
        self.balls = []

    def on_enter(self):
        super().on_enter()

        # Create player
        self.player = Player()
        self.player.transform.position = Vector2(400, 300)
        self.add_object(self.player)

        # Create some bouncing balls
        for i in range(5):
            ball = Ball(random.randint(10, 20))
            ball.transform.position = Vector2(
                random.randint(50, 750),
                random.randint(50, 200)
            )
            self.balls.append(ball)
            self.add_object(ball)

        print("VoidRay Physics & Components Demo")
        print("Use arrow keys to move the blue square")
        print("Collide with balls to push them around")
        print("Press SPACE to add more balls")
        print("Press ESC to quit")

    def update(self, delta_time):
        super().update(delta_time)

        # Check for input
        input_manager = voidray.get_engine().input_manager

        if input_manager.is_key_just_pressed(Keys.ESCAPE):
            voidray.stop()

        if input_manager.is_key_just_pressed(Keys.SPACE):
            # Add a new ball
            ball = Ball(random.randint(10, 20))
            ball.transform.position = Vector2(
                random.randint(50, 750),
                random.randint(50, 200)
            )
            self.balls.append(ball)
            self.add_object(ball)

    def render(self, renderer):
        super().render(renderer)

        # Draw some UI
        renderer.draw_text("VoidRay Physics & Components Demo", Vector2(10, 10), (255, 255, 255), 24)  # White
        renderer.draw_text("Arrow keys to move, SPACE for more balls, ESC to quit", Vector2(10, 40), (192, 192, 192), 16)  # Light Gray
        renderer.draw_text(f"Balls: {len(self.balls)}", Vector2(10, 70), (255, 255, 0), 16)  # Yellow

        # Show FPS
        fps = voidray.get_engine().get_fps()
        renderer.draw_text(f"FPS: {fps:.1f}", Vector2(10, voidray.get_engine().height - 30), (255, 255, 0), 16)  # Yellow


def init_game():
    """Initialize the advanced game."""
    print("============================================================")
    print("VoidRay 2.5-stable Advanced Demo - Choose Your Experience:")
    print("============================================================")
    print("This demo showcases:")
    print("• Advanced 2.5D rendering with texture mapping")
    print("• DOOM-style raycasting and lighting")
    print("• Enhanced physics and components")
    print("• PNG texture loading and asset management")
    print("• Rich environment building tools")
    print("")
    print("Press SPACE during demo to see available modes!")

    # Configure physics
    engine = voidray.get_engine()
    engine.physics_system.set_gravity(800)  # Realistic gravity

    # Create sample textures for 2.5D rendering
    engine.create_sample_textures()

    # Create and start scene
    scene = GameScene()
    voidray.register_scene("game", scene)
    voidray.set_scene("game")


class GameScene(Scene):
    """Main game scene with advanced features and 2.5D capabilities."""

    def __init__(self):
        super().__init__("Advanced Game")
        self.player = None
        self.platforms = []
        self.demo_mode = "2D"  # Can be "2D" or "2.5D"
        self.mode_switch_timer = 0.0
        
        # Initialize 2D physics demo objects
        self.balls = []
        self._setup_2d_demo()

    def update(self, delta_time):
        super().update(delta_time)

        # Check for exit
        engine = voidray.get_engine()
        if engine.input_manager.is_key_pressed(Keys.ESCAPE):
            engine.stop()

        # Mode switching
        self.mode_switch_timer += delta_time
        if engine.input_manager.is_key_just_pressed(Keys.SPACE) and self.mode_switch_timer > 0.5:
            self._switch_demo_mode()
            self.mode_switch_timer = 0.0

        # 2.5D specific controls
        if self.demo_mode == "2.5D":
            self._handle_2_5d_controls(engine, delta_time)

    def _setup_2d_demo(self):
        """Set up the 2D physics demo."""
        # Create player
        self.player = Player()
        self.player.transform.position = Vector2(400, 300)
        self.add_object(self.player)

        # Create some bouncing balls
        for i in range(3):
            ball = Ball(random.randint(10, 20))
            ball.transform.position = Vector2(
                random.randint(50, 750),
                random.randint(50, 200)
            )
            self.balls.append(ball)
            self.add_object(ball)
    
    def _switch_demo_mode(self):
        """Switch between 2D and 2.5D demo modes."""
        engine = voidray.get_engine()

        if self.demo_mode == "2D":
            self.demo_mode = "2.5D"
            engine.set_rendering_mode("2.5D")
            self._setup_2_5d_demo()
            print("\n=== Switched to 2.5D DOOM-Style Mode ===")
            print("Use WASD to move in first-person view")
            print("Mouse look coming soon!")
        else:
            self.demo_mode = "2D"
            engine.set_rendering_mode("2D")
            print("\n=== Switched to 2D Physics Mode ===")
            print("Use arrow keys to control the blue square")

    def _setup_2_5d_demo(self):
        """Set up the 2.5D demo environment."""
        engine = voidray.get_engine()

        # Create a simple level for 2.5D demonstration
        level_data = {
            "name": "demo_2_5d",
            "spawn_point": {"x": 100, "y": 100},
            "walls": [
                # Outer walls
                {"start": {"x": 50, "y": 50}, "end": {"x": 350, "y": 50}, "texture": "brick", "height": 64},
                {"start": {"x": 350, "y": 50}, "end": {"x": 350, "y": 350}, "texture": "stone", "height": 64},
                {"start": {"x": 350, "y": 350}, "end": {"x": 50, "y": 350}, "texture": "brick", "height": 64},
                {"start": {"x": 50, "y": 350}, "end": {"x": 50, "y": 50}, "texture": "stone", "height": 64},

                # Inner structure
                {"start": {"x": 150, "y": 150}, "end": {"x": 250, "y": 150}, "texture": "metal", "height": 48},
                {"start": {"x": 250, "y": 150}, "end": {"x": 250, "y": 250}, "texture": "metal", "height": 48},
                {"start": {"x": 250, "y": 250}, "end": {"x": 150, "y": 250}, "texture": "metal", "height": 48},
            ],
            "lights": [
                {"x": 200, "y": 200, "intensity": 1.2, "radius": 120, "color": [255, 255, 200]},
                {"x": 100, "y": 300, "intensity": 0.8, "radius": 80, "color": [255, 200, 200]}
            ]
        }

        # Store level data
        engine.asset_loader.data["demo_2_5d"] = level_data

        # Load into scene
        self.load_level("demo_2_5d", engine.asset_loader)

        # Set initial camera position
        engine.set_camera_2_5d(Vector2(100, 100), 0)

    def _handle_2_5d_controls(self, engine, delta_time):
        """Handle 2.5D movement controls."""
        import math

        # Get current camera state
        camera_pos = engine.camera_position
        camera_angle = engine.camera_angle

        # Movement speed
        move_speed = 100.0  # units per second
        turn_speed = 90.0   # degrees per second

        # Calculate movement vectors
        forward = Vector2(math.cos(math.radians(camera_angle)), 
                         math.sin(math.radians(camera_angle)))
        right = Vector2(-forward.y, forward.x)

        # Movement
        new_pos = camera_pos

        if engine.input_manager.is_key_pressed(Keys.W):
            new_pos += forward * move_speed * delta_time
        if engine.input_manager.is_key_pressed(Keys.S):
            new_pos -= forward * move_speed * delta_time
        if engine.input_manager.is_key_pressed(Keys.A):
            new_pos -= right * move_speed * delta_time
        if engine.input_manager.is_key_pressed(Keys.D):
            new_pos += right * move_speed * delta_time

        # Rotation
        new_angle = camera_angle
        if engine.input_manager.is_key_pressed(Keys.LEFT):
            new_angle -= turn_speed * delta_time
        if engine.input_manager.is_key_pressed(Keys.RIGHT):
            new_angle += turn_speed * delta_time

        # Update camera
        engine.set_camera_2_5d(new_pos, new_angle % 360)

    def render(self, renderer):
        super().render(renderer)

        engine = voidray.get_engine()

        # Render based on current mode
        if self.demo_mode == "2.5D" and hasattr(self, 'level_data') and self.level_data:
            # Render 2.5D view
            import math
            renderer.render_2_5d_view(engine.camera_position, math.radians(engine.camera_angle))

            # 2.5D UI
            self._render_2_5d_ui(renderer)
        else:
            # 2D UI
            self._render_2d_ui(renderer)

    def _render_2d_ui(self, renderer):
        """Render 2D mode UI."""
        # Draw instructions
        renderer.draw_text("VoidRay Advanced Demo - 2D Physics Mode", Vector2(10, 10), Color.WHITE, 24)
        renderer.draw_text("Use arrow keys to move the blue square", Vector2(10, 40), Color.YELLOW, 16)
        renderer.draw_text("Collide with balls to push them around", Vector2(10, 60), Color.YELLOW, 16)
        renderer.draw_text("Press SPACE to switch to 2.5D DOOM-style mode", Vector2(10, 80), Color.CYAN, 16)
        renderer.draw_text("Press ESC to quit", Vector2(10, 100), Color.YELLOW, 16)

        # Draw stats
        engine = voidray.get_engine()
        fps = engine.get_fps()

        renderer.draw_text(f"FPS: {fps:.1f}", Vector2(10, renderer.height - 50), Color.GREEN, 16)
        renderer.draw_text(f"Mode: {self.demo_mode}", Vector2(10, renderer.height - 30), Color.CYAN, 16)

    def _render_2_5d_ui(self, renderer):
        """Render 2.5D mode UI."""
        # Crosshair
        center_x, center_y = renderer.width // 2, renderer.height // 2
        crosshair_size = 8

        renderer.draw_line(
            Vector2(center_x - crosshair_size, center_y), 
            Vector2(center_x + crosshair_size, center_y),
            Color.WHITE, 2
        )
        renderer.draw_line(
            Vector2(center_x, center_y - crosshair_size), 
            Vector2(center_x, center_y + crosshair_size),
            Color.WHITE, 2
        )

        # Stats and instructions
        engine = voidray.get_engine()
        fps = engine.get_fps()

        renderer.draw_text("VoidRay 2.5D DOOM-Style Mode", Vector2(10, 10), Color.WHITE, 20)
        renderer.draw_text("WASD - Move | Arrow Keys - Turn", Vector2(10, 35), Color.YELLOW, 14)
        renderer.draw_text("SPACE - Switch to 2D Mode", Vector2(10, 55), Color.CYAN, 14)
        renderer.draw_text("ESC - Quit", Vector2(10, 75), Color.YELLOW, 14)

        renderer.draw_text(f"FPS: {fps:.1f}", Vector2(10, renderer.height - 70), Color.GREEN, 16)
        renderer.draw_text(f"Mode: {self.demo_mode}", Vector2(10, renderer.height - 50), Color.CYAN, 16)
        renderer.draw_text(f"Pos: ({engine.camera_position.x:.1f}, {engine.camera_position.y:.1f})", 
                         Vector2(10, renderer.height - 30), Color.YELLOW, 16)


def update_game(delta_time):
    """Called every frame - for global game logic."""
    pass  # Scene handles everything in this demo


def render_game():
    """Called every frame for custom rendering."""
    pass  # Scene handles everything in this demo


def main():
    """
    Main entry point using the physics and component system.
    """
    print("=" * 60)
    print("VoidRay Game Engine - Physics & Components Demo")
    print("=" * 60)

    # Configure the engine
    voidray.configure(
        width=800, 
        height=600, 
        title="VoidRay Physics & Components Demo", 
        fps=60
    )

    # Register callbacks
    voidray.on_init(init_game)
    voidray.on_update(update_game)
    voidray.on_render(render_game)

    # Start the engine (this will run until the game ends)
    voidray.start()


if __name__ == "__main__":
    main()