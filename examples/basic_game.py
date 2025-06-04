"""
Basic VoidRay Game Example
A simple example demonstrating basic VoidRay features.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voidray import Engine, Scene, Sprite, InputManager, Keys, Vector2
from voidray.graphics.renderer import Color


class Player(Sprite):
    """A simple player character that can move around."""
    
    def __init__(self):
        super().__init__("Player")
        # Create a blue square for the player
        self.create_colored_rect(32, 32, Color.BLUE)
        self.speed = 200  # pixels per second
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Get input from engine
        input_manager = self.scene.engine.input_manager
        
        # Calculate movement
        movement = Vector2(0, 0)
        if input_manager.is_key_pressed(Keys.A) or input_manager.is_key_pressed(Keys.LEFT):
            movement.x -= 1
        if input_manager.is_key_pressed(Keys.D) or input_manager.is_key_pressed(Keys.RIGHT):
            movement.x += 1
        if input_manager.is_key_pressed(Keys.W) or input_manager.is_key_pressed(Keys.UP):
            movement.y -= 1
        if input_manager.is_key_pressed(Keys.S) or input_manager.is_key_pressed(Keys.DOWN):
            movement.y += 1
        
        # Normalize diagonal movement
        if movement.magnitude() > 0:
            movement = movement.normalized()
            
        # Apply movement
        self.transform.position += movement * self.speed * delta_time


class Enemy(Sprite):
    """A simple enemy that bounces around the screen."""
    
    def __init__(self, x, y):
        super().__init__("Enemy")
        # Create a red square for the enemy
        self.create_colored_rect(24, 24, Color.RED)
        self.transform.position = Vector2(x, y)
        self.velocity = Vector2(100, 150)  # pixels per second
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Move the enemy
        self.transform.position += self.velocity * delta_time
        
        # Bounce off screen edges
        screen_width = self.scene.engine.width
        screen_height = self.scene.engine.height
        
        if self.transform.position.x < 0 or self.transform.position.x > screen_width:
            self.velocity.x *= -1
        if self.transform.position.y < 0 or self.transform.position.y > screen_height:
            self.velocity.y *= -1
        
        # Keep within bounds
        self.transform.position.x = max(0, min(screen_width, self.transform.position.x))
        self.transform.position.y = max(0, min(screen_height, self.transform.position.y))


class BasicGameScene(Scene):
    """The main game scene."""
    
    def __init__(self):
        super().__init__("BasicGame")
        
    def on_enter(self):
        super().on_enter()
        
        # Create player
        self.player = Player()
        self.player.transform.position = Vector2(400, 300)
        self.add_object(self.player)
        
        # Create some enemies
        enemies_data = [
            (100, 100), (700, 100), (100, 500), (700, 500), (400, 200)
        ]
        
        for x, y in enemies_data:
            enemy = Enemy(x, y)
            self.add_object(enemy)
        
        print("Basic game started!")
        print("Use WASD or Arrow Keys to move the blue player")
        print("Avoid the red enemies!")
        print("Press ESC to quit")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check collisions between player and enemies
        self._check_collisions()
        
        # Check for quit
        if self.engine.input_manager.is_key_just_pressed(Keys.ESCAPE):
            self.engine.stop()
    
    def _check_collisions(self):
        """Check for collisions between player and enemies."""
        if not hasattr(self, 'player') or not self.player.active:
            return
            
        enemies = self.find_objects_with_tag("enemy")
        
        for enemy in enemies:
            if self._objects_colliding(self.player, enemy):
                print("Player hit by enemy! Game Over!")
                self.engine.stop()
                break
    
    def _objects_colliding(self, obj1, obj2):
        """Simple distance-based collision detection."""
        if not (obj1.active and obj2.active):
            return False
        
        pos1 = obj1.transform.position
        pos2 = obj2.transform.position
        distance = pos1.distance_to(pos2)
        
        return distance < 30  # Collision threshold


def main():
    """Main entry point for the basic game example."""
    # Create engine
    engine = Engine(800, 600, "VoidRay Basic Game Example", 60)
    
    # Create and set the game scene
    game_scene = BasicGameScene()
    engine.set_scene(game_scene)
    
    # Run the game
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")


if __name__ == "__main__":
    main()
