"""
VoidRay Asteroids Example

A classic asteroids-style game demonstrating VoidRay engine features
including player controls, projectiles, and collision detection.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voidray import Engine, Scene, Sprite, Vector2, Keys
from voidray.graphics.renderer import Color
from voidray.physics.collider import CircleCollider
import random
import math


class Ship(Sprite):
    """Player ship that can move and shoot."""
    
    def __init__(self):
        super().__init__("Ship")
        # Create triangular ship appearance
        self.create_colored_rect(16, 16, Color.CYAN)
        
        self.velocity = Vector2(0, 0)
        self.thrust_force = 300.0
        self.rotation_speed = 180.0
        self.max_speed = 200.0
        self.shoot_cooldown = 0.0
        self.shoot_interval = 0.2
        
        # Add collider
        self.collider = CircleCollider(self, 8)
        self.add_tag("player")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        input_manager = self.scene.engine.input_manager
        
        # Rotation
        if input_manager.is_key_pressed(Keys.A) or input_manager.is_key_pressed(Keys.LEFT):
            self.transform.rotation -= self.rotation_speed * delta_time
        if input_manager.is_key_pressed(Keys.D) or input_manager.is_key_pressed(Keys.RIGHT):
            self.transform.rotation += self.rotation_speed * delta_time
        
        # Thrust
        if input_manager.is_key_pressed(Keys.W) or input_manager.is_key_pressed(Keys.UP):
            thrust_direction = Vector2.from_angle_degrees(self.transform.rotation)
            self.velocity += thrust_direction * self.thrust_force * delta_time
        
        # Limit max speed
        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed
        
        # Apply movement
        self.transform.position += self.velocity * delta_time
        
        # Apply drag
        self.velocity *= 0.98
        
        # Wrap around screen
        self.wrap_around_screen()
        
        # Shooting
        self.shoot_cooldown -= delta_time
        if input_manager.is_key_pressed(Keys.SPACE) and self.shoot_cooldown <= 0:
            self.shoot()
    
    def shoot(self):
        """Create a bullet."""
        bullet_direction = Vector2.from_angle_degrees(self.transform.rotation)
        bullet_pos = self.transform.position + bullet_direction * 20
        
        bullet = Bullet(bullet_pos.x, bullet_pos.y, bullet_direction)
        self.scene.add_object(bullet)
        if hasattr(self.scene.engine, 'physics_engine'):
            self.scene.engine.physics_engine.add_collider(bullet.collider)
        
        self.shoot_cooldown = self.shoot_interval
    
    def wrap_around_screen(self):
        """Wrap ship position around screen edges."""
        screen_width = self.scene.engine.width
        screen_height = self.scene.engine.height
        
        if self.transform.position.x < 0:
            self.transform.position.x = screen_width
        elif self.transform.position.x > screen_width:
            self.transform.position.x = 0
            
        if self.transform.position.y < 0:
            self.transform.position.y = screen_height
        elif self.transform.position.y > screen_height:
            self.transform.position.y = 0


class Bullet(Sprite):
    """Bullet projectile."""
    
    def __init__(self, x, y, direction):
        super().__init__("Bullet")
        self.create_colored_rect(3, 8, Color.WHITE)
        
        self.transform.position = Vector2(x, y)
        self.velocity = direction.normalized() * 400
        self.lifetime = 3.0
        
        # Add collider
        self.collider = CircleCollider(self, 2)
        self.collider.is_trigger = True
        self.add_tag("bullet")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Move bullet
        self.transform.position += self.velocity * delta_time
        
        # Update lifetime
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.destroy()
            return
        
        # Wrap around screen
        self.wrap_around_screen()
    
    def wrap_around_screen(self):
        """Wrap bullet position around screen edges."""
        screen_width = self.scene.engine.width
        screen_height = self.scene.engine.height
        
        if self.transform.position.x < 0:
            self.transform.position.x = screen_width
        elif self.transform.position.x > screen_width:
            self.transform.position.x = 0
            
        if self.transform.position.y < 0:
            self.transform.position.y = screen_height
        elif self.transform.position.y > screen_height:
            self.transform.position.y = 0


class Asteroid(Sprite):
    """Asteroid enemy."""
    
    def __init__(self, x, y, size=3):
        super().__init__("Asteroid")
        
        self.size = size
        asteroid_sizes = {1: 12, 2: 20, 3: 32}
        asteroid_colors = {1: Color.GRAY, 2: Color.LIGHT_GRAY, 3: Color.DARK_GRAY}
        
        radius = asteroid_sizes[size]
        color = asteroid_colors[size]
        
        self.create_colored_rect(radius, radius, color)
        self.transform.position = Vector2(x, y)
        
        # Random velocity
        angle = random.uniform(0, 360)
        speed = random.uniform(20, 60)
        self.velocity = Vector2.from_angle_degrees(angle, speed)
        
        # Add collider
        self.collider = CircleCollider(self, radius // 2)
        self.add_tag("asteroid")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Move asteroid
        self.transform.position += self.velocity * delta_time
        
        # Slow rotation
        self.transform.rotation += 30 * delta_time
        
        # Wrap around screen
        self.wrap_around_screen()
    
    def wrap_around_screen(self):
        """Wrap asteroid position around screen edges."""
        screen_width = self.scene.engine.width
        screen_height = self.scene.engine.height
        
        if self.transform.position.x < -50:
            self.transform.position.x = screen_width + 50
        elif self.transform.position.x > screen_width + 50:
            self.transform.position.x = -50
            
        if self.transform.position.y < -50:
            self.transform.position.y = screen_height + 50
        elif self.transform.position.y > screen_height + 50:
            self.transform.position.y = -50
    
    def split(self):
        """Split asteroid into smaller pieces."""
        if self.size > 1:
            # Create two smaller asteroids
            for i in range(2):
                new_asteroid = Asteroid(
                    self.transform.position.x + random.uniform(-20, 20),
                    self.transform.position.y + random.uniform(-20, 20),
                    self.size - 1
                )
                self.scene.add_object(new_asteroid)
                if hasattr(self.scene.engine, 'physics_engine'):
                    self.scene.engine.physics_engine.add_collider(new_asteroid.collider)


class AsteroidsScene(Scene):
    """Main asteroids game scene."""
    
    def __init__(self):
        super().__init__("Asteroids")
        self.score = 0
        self.asteroids_destroyed = 0
        self.wave = 1
    
    def on_enter(self):
        super().on_enter()
        
        # Create player ship
        self.ship = Ship()
        self.ship.transform.position = Vector2(400, 300)
        self.add_object(self.ship)
        
        if hasattr(self.engine, 'physics_engine'):
            self.engine.physics_engine.add_collider(self.ship.collider)
        
        # Create initial asteroids
        for i in range(5):
            self.spawn_asteroid()
        
        print("Asteroids game started!")
        print("Controls: A/D or Left/Right to rotate, W/Up to thrust, SPACE to shoot")
        print("Destroy all asteroids to advance to the next wave!")
    
    def spawn_asteroid(self):
        """Spawn a new asteroid at the edge of the screen."""
        # Choose a random edge
        edge = random.randint(0, 3)
        
        if edge == 0:  # Top
            x = random.uniform(0, self.engine.width)
            y = -50
        elif edge == 1:  # Right
            x = self.engine.width + 50
            y = random.uniform(0, self.engine.height)
        elif edge == 2:  # Bottom
            x = random.uniform(0, self.engine.width)
            y = self.engine.height + 50
        else:  # Left
            x = -50
            y = random.uniform(0, self.engine.height)
        
        asteroid = Asteroid(x, y, 3)
        self.add_object(asteroid)
        
        if hasattr(self.engine, 'physics_engine'):
            self.engine.physics_engine.add_collider(asteroid.collider)
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check for collisions manually (simple version)
        bullets = self.find_objects_with_tag("bullet")
        asteroids = self.find_objects_with_tag("asteroid")
        
        # Bullet-asteroid collisions
        for bullet in bullets:
            for asteroid in asteroids:
                if self.check_collision(bullet, asteroid):
                    bullet.destroy()
                    asteroid.split()
                    asteroid.destroy()
                    self.score += 10
                    self.asteroids_destroyed += 1
                    break
        
        # Ship-asteroid collisions
        if hasattr(self, 'ship') and self.ship.active:
            for asteroid in asteroids:
                if self.check_collision(self.ship, asteroid):
                    print(f"Game Over! Final Score: {self.score}")
                    self.engine.stop()
                    return
        
        # Check if all asteroids destroyed
        if len(asteroids) == 0:
            self.next_wave()
        
        # Quit on escape
        if self.engine.input_manager.is_key_just_pressed(Keys.ESCAPE):
            self.engine.stop()
    
    def check_collision(self, obj1, obj2):
        """Simple distance-based collision detection."""
        if not (obj1.active and obj2.active):
            return False
        
        distance = obj1.transform.position.distance_to(obj2.transform.position)
        return distance < 20  # Simple collision threshold
    
    def next_wave(self):
        """Start next wave with more asteroids."""
        self.wave += 1
        asteroids_count = 4 + self.wave
        
        for i in range(asteroids_count):
            self.spawn_asteroid()
        
        print(f"Wave {self.wave} started! {asteroids_count} asteroids incoming!")
    
    def render(self, renderer):
        super().render(renderer)
        
        # Draw UI
        renderer.draw_text(f"Score: {self.score}", Vector2(10, 10), Color.WHITE, 24)
        renderer.draw_text(f"Wave: {self.wave}", Vector2(10, 40), Color.WHITE, 20)
        
        # Draw controls
        renderer.draw_text("A/D: Rotate | W: Thrust | SPACE: Shoot | ESC: Quit", 
                          Vector2(10, self.engine.height - 30), Color.LIGHT_GRAY, 16)


def main():
    """Main function to run the asteroids example."""
    engine = Engine(800, 600, "VoidRay Asteroids", 60)
    scene = AsteroidsScene()
    engine.set_scene(scene)
    
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")


if __name__ == "__main__":
    main()