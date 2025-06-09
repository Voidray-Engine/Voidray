
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
        
        # Add physics components
        self.rigidbody = Rigidbody()
        self.rigidbody.set_mass(1.0)
        self.rigidbody.set_bounciness(0.8)
        self.rigidbody.set_drag(0.1)
        self.add_component(self.rigidbody)
        
        # Add collision
        self.collider = CircleCollider(radius)
        self.collider.on_collision = self.on_collision_callback
        self.add_component(self.collider)
        
        # Give it some initial velocity
        initial_velocity = Vector2(
            random.uniform(-200, 200),
            random.uniform(-300, -100)
        )
        self.rigidbody.set_velocity(initial_velocity)

    def on_collision_callback(self, other, collision_info):
        """Handle collision with other objects."""
        # Add some visual feedback or sound here
        pass

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
        
        # Add collision detection
        self.collider = BoxCollider(40, 40)
        self.collider.on_collision = self.on_collision_callback
        self.add_component(self.collider)

    def on_collision_callback(self, other, collision_info):
        """Handle collision with other objects."""
        if hasattr(other.game_object, 'name') and 'Ball' in other.game_object.name:
            # Push the ball away
            ball_rb = other.game_object.get_component(Rigidbody)
            if ball_rb:
                push_force = (other.game_object.transform.position - self.transform.position).normalized() * 500
                ball_rb.add_impulse(push_force)

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
    """Initialize the game - called once when engine starts."""
    print("Initializing VoidRay physics demo...")

    # Enable gravity for a more realistic feel
    engine = voidray.get_engine()
    engine.physics_system.set_gravity(500)  # Positive for downward gravity

    # Create and register our scene
    physics_scene = PhysicsScene()
    voidray.register_scene("physics", physics_scene)
    voidray.set_scene("physics")


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
