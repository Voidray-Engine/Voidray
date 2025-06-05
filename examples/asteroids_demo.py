
"""
Asteroids Demo - Space shooter with rotation and physics
Demonstrates rotation, projectiles, and dynamic object creation/destruction.
"""

import sys
import os
import math
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from voidray import Engine, Scene, Sprite, Vector2, InputManager, Keys
from voidray.graphics.renderer import Color
from voidray.physics.collider import CircleCollider

class Ship(Sprite):
    def __init__(self):
        super().__init__("Ship")
        self.create_colored_rect(16, 16, Color.CYAN)
        self.transform.position = Vector2(400, 300)
        self.velocity = Vector2(0, 0)
        self.rotation_speed = 180  # degrees per second
        self.thrust_power = 200
        self.max_speed = 300
        self.collider = CircleCollider(self, 8)
        
    def update(self, delta_time):
        super().update(delta_time)
        
        input_mgr = self.scene.engine.input_manager
        
        # Rotation
        if input_mgr.is_key_pressed(Keys.LEFT) or input_mgr.is_key_pressed(Keys.A):
            self.transform.rotation -= self.rotation_speed * delta_time
        if input_mgr.is_key_pressed(Keys.RIGHT) or input_mgr.is_key_pressed(Keys.D):
            self.transform.rotation += self.rotation_speed * delta_time
            
        # Thrust
        if input_mgr.is_key_pressed(Keys.UP) or input_mgr.is_key_pressed(Keys.W):
            angle_rad = math.radians(self.transform.rotation)
            thrust = Vector2(math.cos(angle_rad), math.sin(angle_rad)) * self.thrust_power
            self.velocity += thrust * delta_time
            
        # Limit speed
        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed
            
        # Apply friction
        self.velocity *= 0.98
        
        # Move
        self.transform.position += self.velocity * delta_time
        
        # Wrap around screen
        if self.transform.position.x < 0:
            self.transform.position.x = 800
        elif self.transform.position.x > 800:
            self.transform.position.x = 0
        if self.transform.position.y < 0:
            self.transform.position.y = 600
        elif self.transform.position.y > 600:
            self.transform.position.y = 0
            
        # Shooting
        if input_mgr.is_key_pressed(Keys.SPACE):
            if hasattr(self.scene, 'shoot_timer'):
                self.scene.shoot_timer -= delta_time
            else:
                self.scene.shoot_timer = 0
                
            if self.scene.shoot_timer <= 0:
                self.scene.spawn_bullet(self.transform.position.copy(), self.transform.rotation)
                self.scene.shoot_timer = 0.2  # Rate limit

class Bullet(Sprite):
    def __init__(self, position, rotation):
        super().__init__("Bullet")
        self.create_colored_circle(3, Color.YELLOW)
        self.transform.position = position
        self.transform.rotation = rotation
        
        # Set velocity based on rotation
        angle_rad = math.radians(rotation)
        self.velocity = Vector2(math.cos(angle_rad), math.sin(angle_rad)) * 500
        self.lifetime = 2.0
        self.collider = CircleCollider(self, 3)
        
    def update(self, delta_time):
        super().update(delta_time)
        
        self.transform.position += self.velocity * delta_time
        self.lifetime -= delta_time
        
        # Remove when lifetime expires or off screen
        if (self.lifetime <= 0 or 
            self.transform.position.x < -10 or self.transform.position.x > 810 or
            self.transform.position.y < -10 or self.transform.position.y > 610):
            self.scene.remove_object(self)

class Asteroid(Sprite):
    def __init__(self, position=None, size=3):
        super().__init__("Asteroid")
        self.size = size
        colors = [Color.GRAY, Color.BROWN, Color.DARK_GRAY]
        sizes = [32, 24, 16]
        
        self.create_colored_circle(sizes[size-1], colors[size-1])
        
        if position:
            self.transform.position = position
        else:
            # Spawn at random edge
            edge = random.randint(0, 3)
            if edge == 0:  # Top
                self.transform.position = Vector2(random.uniform(0, 800), -20)
            elif edge == 1:  # Right
                self.transform.position = Vector2(820, random.uniform(0, 600))
            elif edge == 2:  # Bottom
                self.transform.position = Vector2(random.uniform(0, 800), 620)
            else:  # Left
                self.transform.position = Vector2(-20, random.uniform(0, 600))
        
        # Random velocity
        angle = random.uniform(0, 360)
        speed = random.uniform(50, 150)
        angle_rad = math.radians(angle)
        self.velocity = Vector2(math.cos(angle_rad), math.sin(angle_rad)) * speed
        self.rotation_speed = random.uniform(-90, 90)
        
        self.collider = CircleCollider(self, sizes[size-1] // 2)
        
    def update(self, delta_time):
        super().update(delta_time)
        
        self.transform.position += self.velocity * delta_time
        self.transform.rotation += self.rotation_speed * delta_time
        
        # Wrap around screen
        if self.transform.position.x < -50:
            self.transform.position.x = 850
        elif self.transform.position.x > 850:
            self.transform.position.x = -50
        if self.transform.position.y < -50:
            self.transform.position.y = 650
        elif self.transform.position.y > 650:
            self.transform.position.y = -50

class AsteroidsScene(Scene):
    def __init__(self):
        super().__init__("AsteroidsScene")
        self.score = 0
        self.shoot_timer = 0
        
    def on_enter(self):
        print("=== Asteroids Demo ===")
        print("WASD or Arrow keys to move and rotate")
        print("SPACE to shoot")
        print("Press ESC to quit")
        
        # Create ship
        self.ship = Ship()
        self.add_object(self.ship)
        
        # Create initial asteroids
        for _ in range(5):
            asteroid = Asteroid()
            self.add_object(asteroid)
            
    def spawn_bullet(self, position, rotation):
        bullet = Bullet(position, rotation)
        self.add_object(bullet)
        
        # Add collision with asteroids
        for obj in self.objects:
            if isinstance(obj, Asteroid):
                self.engine.physics_engine.add_collision_pair(
                    bullet, obj, self.on_bullet_asteroid_hit
                )
                
    def on_bullet_asteroid_hit(self, bullet, asteroid):
        # Remove bullet and asteroid
        self.remove_object(bullet)
        self.remove_object(asteroid)
        
        # Split asteroid if large enough
        if asteroid.size > 1:
            for _ in range(2):
                new_asteroid = Asteroid(asteroid.transform.position.copy(), asteroid.size - 1)
                self.add_object(new_asteroid)
                
        self.score += 10 * (4 - asteroid.size)
        print(f"Score: {self.score}")
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check for quit
        if self.engine.input_manager.is_key_pressed(Keys.ESCAPE):
            self.engine.stop()
            
        # Spawn new asteroids occasionally
        if random.random() < 0.01:  # 1% chance per frame
            asteroid = Asteroid()
            self.add_object(asteroid)

def main():
    engine = Engine(800, 600, "Asteroids Demo", 60)
    scene = AsteroidsScene()
    engine.set_scene(scene)
    engine.run()

if __name__ == "__main__":
    main()
