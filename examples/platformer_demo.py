
"""
Platformer Demo - Side-scrolling platform game
Demonstrates gravity, jumping mechanics, and collision detection.
"""

import sys
import os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from voidray import Engine, Scene, Sprite, Vector2, InputManager, Keys
from voidray.graphics.renderer import Color
from voidray.physics.collider import RectCollider

class Player(Sprite):
    def __init__(self):
        super().__init__("Player")
        self.create_colored_rect(24, 32, Color.BLUE)
        self.transform.position = Vector2(100, 300)
        self.velocity = Vector2(0, 0)
        self.speed = 200
        self.jump_force = 400
        self.gravity = 800
        self.on_ground = False
        self.collider = RectCollider(self, 24, 32)
        
    def update(self, delta_time):
        super().update(delta_time)
        
        input_mgr = self.scene.engine.input_manager
        
        # Horizontal movement
        self.velocity.x = 0
        if input_mgr.is_key_pressed(Keys.LEFT) or input_mgr.is_key_pressed(Keys.A):
            self.velocity.x = -self.speed
        if input_mgr.is_key_pressed(Keys.RIGHT) or input_mgr.is_key_pressed(Keys.D):
            self.velocity.x = self.speed
            
        # Jumping
        if (input_mgr.is_key_pressed(Keys.SPACE) or input_mgr.is_key_pressed(Keys.UP) or 
            input_mgr.is_key_pressed(Keys.W)) and self.on_ground:
            self.velocity.y = -self.jump_force
            self.on_ground = False
            
        # Apply gravity
        self.velocity.y += self.gravity * delta_time
        
        # Move
        new_pos = self.transform.position + self.velocity * delta_time
        
        # Check platform collisions
        self.on_ground = False
        for obj in self.scene.objects:
            if isinstance(obj, Platform):
                # Simple collision detection
                if (new_pos.x < obj.transform.position.x + obj.width/2 and
                    new_pos.x + 24 > obj.transform.position.x - obj.width/2 and
                    new_pos.y + 32 > obj.transform.position.y - obj.height/2 and
                    new_pos.y < obj.transform.position.y + obj.height/2):
                    
                    # Landing on top of platform
                    if (self.velocity.y > 0 and 
                        self.transform.position.y + 32 <= obj.transform.position.y - obj.height/2 + 5):
                        new_pos.y = obj.transform.position.y - obj.height/2 - 32
                        self.velocity.y = 0
                        self.on_ground = True
                    # Hitting platform from below
                    elif (self.velocity.y < 0 and 
                          self.transform.position.y >= obj.transform.position.y + obj.height/2 - 5):
                        new_pos.y = obj.transform.position.y + obj.height/2
                        self.velocity.y = 0
                    # Hitting platform from side
                    else:
                        if self.velocity.x > 0:  # Moving right
                            new_pos.x = obj.transform.position.x - obj.width/2 - 24
                        else:  # Moving left
                            new_pos.x = obj.transform.position.x + obj.width/2
                        self.velocity.x = 0
        
        self.transform.position = new_pos
        
        # Keep player on screen
        if self.transform.position.x < 0:
            self.transform.position.x = 0
        elif self.transform.position.x > 776:
            self.transform.position.x = 776
            
        # Reset if falling off screen
        if self.transform.position.y > 700:
            self.transform.position = Vector2(100, 300)
            self.velocity = Vector2(0, 0)

class Platform(Sprite):
    def __init__(self, x, y, width, height, color=Color.GREEN):
        super().__init__("Platform")
        self.width = width
        self.height = height
        self.create_colored_rect(width, height, color)
        self.transform.position = Vector2(x, y)
        self.collider = RectCollider(self, width, height)

class Collectible(Sprite):
    def __init__(self, x, y):
        super().__init__("Collectible")
        self.create_colored_circle(8, Color.YELLOW)
        self.transform.position = Vector2(x, y)
        self.bob_timer = 0
        self.original_y = y
        self.collider = RectCollider(self, 16, 16)
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Bobbing animation
        self.bob_timer += delta_time * 3
        self.transform.position.y = self.original_y + math.sin(self.bob_timer) * 5

class PlatformerScene(Scene):
    def __init__(self):
        super().__init__("PlatformerScene")
        self.score = 0
        
    def on_enter(self):
        print("=== Platformer Demo ===")
        print("AD or Arrow keys to move")
        print("SPACE or W to jump")
        print("Collect yellow coins!")
        print("Press ESC to quit")
        
        # Create player
        self.player = Player()
        self.add_object(self.player)
        
        # Create platforms
        platforms = [
            # Ground level
            Platform(400, 580, 800, 40, Color.BROWN),
            # Jump platforms
            Platform(200, 450, 120, 20),
            Platform(500, 350, 120, 20),
            Platform(150, 250, 120, 20),
            Platform(600, 180, 120, 20),
            Platform(350, 120, 120, 20),
            # Walls
            Platform(50, 300, 20, 200),
            Platform(750, 300, 20, 200),
        ]
        
        for platform in platforms:
            self.add_object(platform)
            
        # Create collectibles
        collectibles = [
            Collectible(200, 420),
            Collectible(500, 320),
            Collectible(150, 220),
            Collectible(600, 150),
            Collectible(350, 90),
        ]
        
        for collectible in collectibles:
            self.add_object(collectible)
            # Add collision detection
            self.engine.physics_engine.add_collision_pair(
                self.player, collectible, self.on_collect_coin
            )
            
    def on_collect_coin(self, player, coin):
        self.remove_object(coin)
        self.score += 100
        print(f"Score: {self.score}")
        
        # Check win condition
        remaining_coins = [obj for obj in self.objects if isinstance(obj, Collectible)]
        if not remaining_coins:
            print("Congratulations! You collected all coins!")
            
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check for quit
        if self.engine.input_manager.is_key_pressed(Keys.ESCAPE):
            self.engine.stop()

def main():
    engine = Engine(800, 600, "Platformer Demo", 60)
    scene = PlatformerScene()
    engine.set_scene(scene)
    engine.run()

if __name__ == "__main__":
    main()
