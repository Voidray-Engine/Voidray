
"""
Asteroid Shooter Game - VoidRay Engine
=====================================

This is an advanced asteroid shooter that demonstrates:
- 2.5D rendering capabilities for a pseudo-3D effect
- Sprite rotation and scaling
- Particle effects simulation
- Advanced collision detection
- Object pooling for performance
- Multiple game states (playing, game over)

The player controls a spaceship that can rotate and thrust, shooting at asteroids
that break into smaller pieces. This showcases the engine's 2.5D capabilities
for creating depth and visual effects similar to classic space games.
"""

import sys
import os
import math
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voidray import Engine, Scene, GameObject, Vector2, Keys
from voidray.utils.color import Color
from voidray.physics import CircleCollider
import pygame

class Particle(GameObject):
    """
    Particle class for explosion effects.
    Demonstrates simple particle system implementation.
    """
    
    def __init__(self, position, velocity, color, lifetime):
        super().__init__("Particle")
        self.transform.position = position.copy()
        self.velocity = velocity
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.uniform(2, 5)
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Move particle
        self.transform.position += self.velocity * delta_time
        
        # Reduce lifetime
        self.lifetime -= delta_time
        
        # Mark for removal when dead
        if self.lifetime <= 0:
            self.destroy()
    
    def render(self, renderer):
        # Fade out over time
        alpha = self.lifetime / self.max_lifetime
        faded_color = Color(
            int(self.color.r * alpha),
            int(self.color.g * alpha), 
            int(self.color.b * alpha)
        )
        
        renderer.draw_circle(self.transform.position, self.size, faded_color, filled=True)


class Bullet(GameObject):
    """
    Bullet class for player projectiles.
    Demonstrates simple projectile physics and lifecycle management.
    """
    
    def __init__(self, position, direction):
        super().__init__("Bullet")
        self.transform.position = position.copy()
        self.velocity = direction * 500  # Bullet speed
        self.lifetime = 3.0  # Bullets last 3 seconds
        
        # Add small collider
        self.collider = CircleCollider(3)
        self.add_component(self.collider)
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Move bullet
        self.transform.position += self.velocity * delta_time
        
        # Reduce lifetime
        self.lifetime -= delta_time
        
        # Remove when lifetime expires or goes off screen
        if (self.lifetime <= 0 or 
            self.transform.position.x < -50 or self.transform.position.x > 850 or
            self.transform.position.y < -50 or self.transform.position.y > 650):
            self.destroy()
    
    def render(self, renderer):
        renderer.draw_circle(self.transform.position, 3, Color.YELLOW, filled=True)


class Asteroid(GameObject):
    """
    Asteroid class that demonstrates:
    - Sprite rotation animation
    - Size-based collision detection
    - Breaking into smaller pieces
    - Wrapping around screen edges
    """
    
    def __init__(self, position, size="large"):
        super().__init__(f"Asteroid_{size}")
        self.transform.position = position.copy()
        self.size_type = size
        
        # Size configurations
        size_config = {
            "large": {"radius": 40, "speed": 50, "health": 3, "color": Color(150, 75, 0)},
            "medium": {"radius": 25, "speed": 75, "health": 2, "color": Color(120, 60, 0)},
            "small": {"radius": 15, "speed": 100, "health": 1, "color": Color(100, 50, 0)}
        }
        
        config = size_config[size]
        self.radius = config["radius"]
        self.speed = config["speed"]
        self.health = config["health"]
        self.color = config["color"]
        
        # Random movement direction
        angle = random.uniform(0, 360)
        self.velocity = Vector2(
            math.cos(math.radians(angle)) * self.speed,
            math.sin(math.radians(angle)) * self.speed
        )
        
        # Rotation
        self.rotation_speed = random.uniform(-90, 90)  # Degrees per second
        
        # Add collider
        self.collider = CircleCollider(self.radius)
        self.add_component(self.collider)
        
        print(f"Created {size} asteroid at {position}")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Move asteroid
        self.transform.position += self.velocity * delta_time
        
        # Rotate asteroid
        self.transform.rotation += self.rotation_speed * delta_time
        
        # Wrap around screen edges
        screen_width, screen_height = 800, 600
        
        if self.transform.position.x < -self.radius:
            self.transform.position.x = screen_width + self.radius
        elif self.transform.position.x > screen_width + self.radius:
            self.transform.position.x = -self.radius
            
        if self.transform.position.y < -self.radius:
            self.transform.position.y = screen_height + self.radius
        elif self.transform.position.y > screen_height + self.radius:
            self.transform.position.y = -self.radius
    
    def take_damage(self):
        """Handle asteroid taking damage and breaking apart."""
        self.health -= 1
        
        if self.health <= 0:
            # Create explosion particles
            self.create_explosion()
            
            # Break into smaller asteroids
            if self.size_type == "large":
                self.spawn_smaller_asteroids("medium", 2)
            elif self.size_type == "medium":
                self.spawn_smaller_asteroids("small", 2)
            
            # Remove this asteroid
            self.destroy()
            return True
        return False
    
    def create_explosion(self):
        """Create particle explosion effect."""
        particle_count = random.randint(8, 15)
        
        for _ in range(particle_count):
            # Random direction and speed
            angle = random.uniform(0, 360)
            speed = random.uniform(50, 150)
            velocity = Vector2(
                math.cos(math.radians(angle)) * speed,
                math.sin(math.radians(angle)) * speed
            )
            
            # Create particle
            particle = Particle(
                self.transform.position,
                velocity,
                Color(255, random.randint(100, 255), 0),  # Orange explosion
                random.uniform(0.5, 1.5)
            )
            
            if self.scene:
                self.scene.add_object(particle)
    
    def spawn_smaller_asteroids(self, size, count):
        """Spawn smaller asteroids when this one is destroyed."""
        for _ in range(count):
            # Random offset from current position
            offset = Vector2(
                random.uniform(-20, 20),
                random.uniform(-20, 20)
            )
            new_position = self.transform.position + offset
            
            # Create new asteroid
            new_asteroid = Asteroid(new_position, size)
            
            if self.scene:
                self.scene.add_object(new_asteroid)
    
    def render(self, renderer):
        """Render asteroid with rotation and 2.5D depth effect."""
        # Draw asteroid as a rotating polygon approximation
        points = []
        num_points = 8
        
        for i in range(num_points):
            angle = (360 / num_points) * i + self.transform.rotation
            # Add some irregularity to make it look more like an asteroid
            radius_variation = self.radius + random.uniform(-5, 5)
            
            x = self.transform.position.x + math.cos(math.radians(angle)) * radius_variation
            y = self.transform.position.y + math.sin(math.radians(angle)) * radius_variation
            points.append((int(x), int(y)))
        
        # Draw filled polygon (asteroid body)
        if len(points) >= 3:
            pygame.draw.polygon(renderer.screen, self.color.to_tuple(), points)
        
        # Draw outline for better visibility
        renderer.draw_circle(self.transform.position, self.radius, Color.WHITE, filled=False, width=2)


class Player(GameObject):
    """
    Player spaceship class demonstrating:
    - Rotation-based movement (like Asteroids classic game)
    - Thrust mechanics with momentum
    - Shooting mechanics
    - Screen wrapping
    - 2.5D visual effects for engine exhaust
    """
    
    def __init__(self):
        super().__init__("Player")
        self.transform.position = Vector2(400, 300)  # Center of screen
        self.transform.rotation = 0  # Facing up
        
        # Movement properties
        self.velocity = Vector2(0, 0)
        self.thrust_power = 300
        self.max_speed = 250
        self.drag = 0.98  # Momentum decay
        
        # Shooting properties
        self.shoot_cooldown = 0.0
        self.shoot_delay = 0.2  # Seconds between shots
        
        # Visual properties
        self.size = 15
        self.engine_particles = []
        
        # Add collider
        self.collider = CircleCollider(self.size)
        self.add_component(self.collider)
        
        print("Player ship created at center")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        input_manager = self.scene.engine.input_manager
        
        # Rotation controls
        if input_manager.is_key_pressed(Keys.LEFT) or input_manager.is_key_pressed(Keys.A):
            self.transform.rotation -= 180 * delta_time  # Rotate left
        if input_manager.is_key_pressed(Keys.RIGHT) or input_manager.is_key_pressed(Keys.D):
            self.transform.rotation += 180 * delta_time  # Rotate right
        
        # Thrust control
        if input_manager.is_key_pressed(Keys.UP) or input_manager.is_key_pressed(Keys.W):
            # Calculate thrust direction based on rotation
            thrust_angle = math.radians(self.transform.rotation - 90)  # -90 because 0 rotation is up
            thrust_direction = Vector2(
                math.cos(thrust_angle),
                math.sin(thrust_angle)
            )
            
            # Apply thrust
            self.velocity += thrust_direction * self.thrust_power * delta_time
            
            # Limit max speed
            if self.velocity.magnitude() > self.max_speed:
                self.velocity = self.velocity.normalized() * self.max_speed
            
            # Create engine exhaust particles
            self.create_engine_exhaust()
        
        # Apply drag (momentum decay)
        self.velocity *= self.drag
        
        # Move player
        self.transform.position += self.velocity * delta_time
        
        # Screen wrapping
        screen_width, screen_height = 800, 600
        
        if self.transform.position.x < 0:
            self.transform.position.x = screen_width
        elif self.transform.position.x > screen_width:
            self.transform.position.x = 0
            
        if self.transform.position.y < 0:
            self.transform.position.y = screen_height
        elif self.transform.position.y > screen_height:
            self.transform.position.y = 0
        
        # Shooting
        self.shoot_cooldown -= delta_time
        if (input_manager.is_key_pressed(Keys.SPACE) and self.shoot_cooldown <= 0):
            self.shoot()
            self.shoot_cooldown = self.shoot_delay
    
    def create_engine_exhaust(self):
        """Create engine exhaust particles for visual effect."""
        # Calculate exhaust position (behind ship)
        exhaust_angle = math.radians(self.transform.rotation + 90)  # Opposite of thrust direction
        exhaust_offset = Vector2(
            math.cos(exhaust_angle) * (self.size + 5),
            math.sin(exhaust_angle) * (self.size + 5)
        )
        exhaust_position = self.transform.position + exhaust_offset
        
        # Create exhaust particle
        exhaust_velocity = Vector2(
            math.cos(exhaust_angle) * random.uniform(30, 60),
            math.sin(exhaust_angle) * random.uniform(30, 60)
        )
        
        particle = Particle(
            exhaust_position,
            exhaust_velocity,
            Color(0, 100, 255),  # Blue exhaust
            random.uniform(0.2, 0.5)
        )
        
        if self.scene:
            self.scene.add_object(particle)
    
    def shoot(self):
        """Shoot a bullet in the direction the ship is facing."""
        # Calculate bullet direction
        bullet_angle = math.radians(self.transform.rotation - 90)
        bullet_direction = Vector2(
            math.cos(bullet_angle),
            math.sin(bullet_angle)
        )
        
        # Calculate bullet spawn position (front of ship)
        bullet_offset = bullet_direction * (self.size + 10)
        bullet_position = self.transform.position + bullet_offset
        
        # Create bullet
        bullet = Bullet(bullet_position, bullet_direction)
        
        if self.scene:
            self.scene.add_object(bullet)
            print("Player fired bullet")
    
    def render(self, renderer):
        """Render the player ship as a triangle pointing in the direction of rotation."""
        # Calculate triangle points based on rotation
        angle_rad = math.radians(self.transform.rotation - 90)  # -90 because 0 rotation is up
        
        # Front point (nose of ship)
        front = Vector2(
            self.transform.position.x + math.cos(angle_rad) * self.size,
            self.transform.position.y + math.sin(angle_rad) * self.size
        )
        
        # Back left point
        back_left_angle = angle_rad + math.radians(140)
        back_left = Vector2(
            self.transform.position.x + math.cos(back_left_angle) * (self.size * 0.7),
            self.transform.position.y + math.sin(back_left_angle) * (self.size * 0.7)
        )
        
        # Back right point
        back_right_angle = angle_rad - math.radians(140)
        back_right = Vector2(
            self.transform.position.x + math.cos(back_right_angle) * (self.size * 0.7),
            self.transform.position.y + math.sin(back_right_angle) * (self.size * 0.7)
        )
        
        # Draw ship triangle
        points = [
            (int(front.x), int(front.y)),
            (int(back_left.x), int(back_left.y)),
            (int(back_right.x), int(back_right.y))
        ]
        
        pygame.draw.polygon(renderer.screen, Color.WHITE.to_tuple(), points)
        
        # Draw outline for better visibility
        pygame.draw.polygon(renderer.screen, Color.CYAN.to_tuple(), points, 2)


class AsteroidShooterScene(Scene):
    """
    Main game scene for the asteroid shooter.
    Demonstrates advanced game state management, collision handling,
    and 2.5D rendering setup.
    """
    
    def __init__(self):
        super().__init__("AsteroidShooter")
        
        # Game state
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.wave = 1
        self.asteroids_remaining = 0
        
        # Game objects
        self.player = None
        self.asteroids = []
        self.bullets = []
        self.particles = []
        
        # Timing
        self.respawn_timer = 0.0
        self.wave_transition_timer = 0.0
    
    def on_enter(self):
        """Initialize the game when scene starts."""
        super().on_enter()
        
        print("Starting Asteroid Shooter!")
        print("Controls:")
        print("  A/D or LEFT/RIGHT - Rotate ship")
        print("  W or UP - Thrust")
        print("  SPACE - Shoot")
        print("  ESC - Quit")
        print()
        
        # Set 2.5D rendering mode for enhanced visual effects
        if self.engine:
            self.engine.set_rendering_mode("2.5D")
            print("2.5D rendering mode enabled for enhanced effects")
        
        # Create player
        self.player = Player()
        self.add_object(self.player)
        
        # Start first wave
        self.start_wave(1)
        
        # Register collision callback
        if self.engine:
            self.engine.physics_engine.add_collision_callback(self.on_collision)
    
    def start_wave(self, wave_number):
        """Start a new wave of asteroids."""
        self.wave = wave_number
        asteroid_count = 3 + wave_number  # More asteroids each wave
        
        print(f"Starting Wave {wave_number} with {asteroid_count} asteroids")
        
        # Create asteroids at random positions (not too close to player)
        for _ in range(asteroid_count):
            while True:
                position = Vector2(
                    random.uniform(50, 750),
                    random.uniform(50, 550)
                )
                
                # Make sure asteroid doesn't spawn too close to player
                if self.player and (position - self.player.transform.position).magnitude() > 100:
                    break
            
            asteroid = Asteroid(position, "large")
            self.add_object(asteroid)
        
        self.asteroids_remaining = asteroid_count
    
    def on_collision(self, collider1, collider2):
        """Handle collisions between different object types."""
        obj1 = collider1.game_object
        obj2 = collider2.game_object
        
        # Bullet hits asteroid
        if isinstance(obj1, Bullet) and isinstance(obj2, Asteroid):
            self.handle_bullet_asteroid_collision(obj1, obj2)
        elif isinstance(obj1, Asteroid) and isinstance(obj2, Bullet):
            self.handle_bullet_asteroid_collision(obj2, obj1)
        
        # Player hits asteroid
        elif isinstance(obj1, Player) and isinstance(obj2, Asteroid):
            self.handle_player_asteroid_collision(obj1, obj2)
        elif isinstance(obj1, Asteroid) and isinstance(obj2, Player):
            self.handle_player_asteroid_collision(obj2, obj1)
    
    def handle_bullet_asteroid_collision(self, bullet, asteroid):
        """Handle bullet hitting an asteroid."""
        # Destroy bullet
        bullet.destroy()
        
        # Damage asteroid
        if asteroid.take_damage():
            # Asteroid was destroyed - award points
            points = {"large": 20, "medium": 50, "small": 100}
            self.score += points.get(asteroid.size_type, 10)
            
            print(f"Asteroid destroyed! Score: {self.score}")
            
            self.asteroids_remaining -= 1
            
            # Check if wave is complete
            if self.asteroids_remaining <= 0:
                self.wave_transition_timer = 2.0  # 2 second delay before next wave
    
    def handle_player_asteroid_collision(self, player, asteroid):
        """Handle player colliding with an asteroid."""
        if not self.game_over:
            self.lives -= 1
            print(f"Player hit! Lives remaining: {self.lives}")
            
            # Create explosion effect
            asteroid.create_explosion()
            
            if self.lives <= 0:
                self.game_over = True
                print("GAME OVER!")
            else:
                # Respawn player after brief delay
                self.respawn_timer = 2.0
                player.transform.position = Vector2(400, 300)
                player.velocity = Vector2(0, 0)
    
    def update(self, delta_time):
        """Update game logic."""
        super().update(delta_time)
        
        # Handle timers
        if self.respawn_timer > 0:
            self.respawn_timer -= delta_time
        
        if self.wave_transition_timer > 0:
            self.wave_transition_timer -= delta_time
            if self.wave_transition_timer <= 0:
                self.start_wave(self.wave + 1)
        
        # Check for restart
        if self.game_over and self.engine.input_manager.is_key_just_pressed(Keys.R):
            self.restart_game()
        
        # Check for quit
        if self.engine.input_manager.is_key_just_pressed(Keys.ESCAPE):
            self.engine.stop()
        
        # Count remaining asteroids
        self.asteroids_remaining = len([obj for obj in self.objects if isinstance(obj, Asteroid)])
    
    def restart_game(self):
        """Restart the game."""
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.wave = 1
        
        # Clear all objects except player
        for obj in self.objects.copy():
            if not isinstance(obj, Player):
                obj.destroy()
        
        # Reset player
        if self.player:
            self.player.transform.position = Vector2(400, 300)
            self.player.velocity = Vector2(0, 0)
        
        # Start first wave
        self.start_wave(1)
        
        print("Game restarted!")
    
    def render(self, renderer):
        """Render game objects and UI."""
        super().render(renderer)
        
        # Draw UI
        renderer.draw_text(f"Score: {self.score}", Vector2(10, 10), Color.WHITE, 24)
        renderer.draw_text(f"Lives: {self.lives}", Vector2(10, 40), Color.WHITE, 24)
        renderer.draw_text(f"Wave: {self.wave}", Vector2(10, 70), Color.WHITE, 24)
        
        # Draw game over screen
        if self.game_over:
            renderer.draw_text("GAME OVER", Vector2(300, 250), Color.RED, 48)
            renderer.draw_text(f"Final Score: {self.score}", Vector2(320, 300), Color.WHITE, 24)
            renderer.draw_text("Press R to restart", Vector2(320, 330), Color.WHITE, 24)
            renderer.draw_text("Press ESC to quit", Vector2(320, 360), Color.WHITE, 24)
        
        # Draw wave transition
        elif self.wave_transition_timer > 0:
            renderer.draw_text(f"Wave {self.wave} Complete!", Vector2(280, 280), Color.GREEN, 36)
            renderer.draw_text("Next wave incoming...", Vector2(300, 320), Color.WHITE, 24)


def main():
    """Main function to run the Asteroid Shooter game."""
    print("VoidRay Engine - Asteroid Shooter Example")
    print("=========================================")
    
    try:
        # Create engine with 800x600 resolution
        engine = Engine(800, 600, "VoidRay Asteroid Shooter", 60)
        
        # Create and set the game scene
        game_scene = AsteroidShooterScene()
        engine.set_scene(game_scene)
        
        # Run the game
        engine.run()
        
    except Exception as e:
        print(f"Error running Asteroid Shooter: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
