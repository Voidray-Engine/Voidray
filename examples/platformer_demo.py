
"""
VoidRay Platformer Demo
A simple platformer game demonstrating physics, jumping, and collision detection.
"""

import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voidray import Engine, Scene, Sprite, Vector2, Keys
from voidray.graphics.renderer import Color
from voidray.physics.collider import RectCollider
import random


class Platform(Sprite):
    """A static platform that the player can jump on."""
    
    def __init__(self, x, y, width, height, color=Color.BROWN):
        super().__init__("Platform")
        self.width = width
        self.height = height
        self.create_colored_rect(width, height, color)
        self.transform.position = Vector2(x, y)
        
        # Add collider
        self.collider = RectCollider(self, width, height)
        self.collider.is_static = True
        self.add_tag("platform")


class Player(Sprite):
    """The player character with physics-based movement."""
    
    def __init__(self):
        super().__init__("Player")
        self.create_colored_rect(32, 32, Color.BLUE)
        
        # Physics properties
        self.velocity = Vector2(0, 0)
        self.gravity = 800  # pixels per second squared
        self.jump_force = -400  # negative is up
        self.speed = 200
        self.max_fall_speed = 600
        
        # State
        self.is_grounded = False
        self.can_jump = True
        
        # Add collider
        self.collider = RectCollider(self, 32, 32)
        self.collider.on_collision = self.on_collision
        self.add_tag("player")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        input_manager = self.scene.engine.input_manager
        
        # Horizontal movement
        horizontal_input = 0
        if input_manager.is_key_pressed(Keys.A) or input_manager.is_key_pressed(Keys.LEFT):
            horizontal_input = -1
        if input_manager.is_key_pressed(Keys.D) or input_manager.is_key_pressed(Keys.RIGHT):
            horizontal_input = 1
        
        self.velocity.x = horizontal_input * self.speed
        
        # Jumping
        if (input_manager.is_key_just_pressed(Keys.SPACE) or 
            input_manager.is_key_just_pressed(Keys.W) or 
            input_manager.is_key_just_pressed(Keys.UP)) and self.can_jump and self.is_grounded:
            self.velocity.y = self.jump_force
            self.is_grounded = False
            self.can_jump = False
        
        # Apply gravity
        if not self.is_grounded:
            self.velocity.y += self.gravity * delta_time
            self.velocity.y = min(self.velocity.y, self.max_fall_speed)
        
        # Apply velocity
        self.transform.position += self.velocity * delta_time
        
        # Keep player on screen horizontally
        screen_width = self.scene.engine.width
        margin = 16
        self.transform.position.x = max(margin, min(screen_width - margin, self.transform.position.x))
        
        # Check if player fell off the world
        if self.transform.position.y > self.scene.engine.height + 100:
            self.respawn()
        
        # Reset jump ability when not pressing jump
        if not (input_manager.is_key_pressed(Keys.SPACE) or 
                input_manager.is_key_pressed(Keys.W) or 
                input_manager.is_key_pressed(Keys.UP)):
            self.can_jump = True
    
    def on_collision(self, other):
        """Handle collision with platforms."""
        if other.game_object and other.game_object.has_tag("platform"):
            # Simple collision response - land on top of platform
            platform = other.game_object
            player_bottom = self.transform.position.y + 16
            platform_top = platform.transform.position.y - 16
            
            # If player is falling and close to landing on platform
            if self.velocity.y > 0 and abs(player_bottom - platform_top) < 20:
                self.transform.position.y = platform_top - 16
                self.velocity.y = 0
                self.is_grounded = True
    
    def respawn(self):
        """Respawn the player at the starting position."""
        self.transform.position = Vector2(100, 200)
        self.velocity = Vector2(0, 0)
        self.is_grounded = False


class Enemy(Sprite):
    """A simple enemy that patrols platforms."""
    
    def __init__(self, x, y, patrol_distance=100):
        super().__init__("Enemy")
        self.create_colored_rect(24, 24, Color.RED)
        self.transform.position = Vector2(x, y)
        
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.speed = 80
        self.direction = 1  # 1 for right, -1 for left
        
        # Physics
        self.velocity = Vector2(self.speed * self.direction, 0)
        self.gravity = 800
        
        # Add collider
        self.collider = RectCollider(self, 24, 24)
        self.collider.on_collision = self.on_collision
        self.add_tag("enemy")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Patrol logic
        if self.transform.position.x <= self.start_x - self.patrol_distance:
            self.direction = 1
        elif self.transform.position.x >= self.start_x + self.patrol_distance:
            self.direction = -1
        
        self.velocity.x = self.speed * self.direction
        
        # Apply gravity
        self.velocity.y += self.gravity * delta_time
        self.velocity.y = min(self.velocity.y, 600)
        
        # Apply velocity
        self.transform.position += self.velocity * delta_time
        
        # Remove if fell off world
        if self.transform.position.y > self.scene.engine.height + 100:
            self.destroy()
    
    def on_collision(self, other):
        """Handle collision with platforms and player."""
        if other.game_object and other.game_object.has_tag("platform"):
            # Land on platform
            platform = other.game_object
            enemy_bottom = self.transform.position.y + 12
            platform_top = platform.transform.position.y - 12
            
            if self.velocity.y > 0 and abs(enemy_bottom - platform_top) < 20:
                self.transform.position.y = platform_top - 12
                self.velocity.y = 0
        elif other.game_object and other.game_object.has_tag("player"):
            # Player touched enemy - respawn player
            other.game_object.respawn()


class Collectible(Sprite):
    """A collectible item that gives points."""
    
    def __init__(self, x, y):
        super().__init__("Collectible")
        self.create_colored_rect(16, 16, Color.YELLOW)
        self.transform.position = Vector2(x, y)
        
        # Animation properties
        self.bob_time = 0
        self.start_y = y
        
        # Add collider
        self.collider = RectCollider(self, 16, 16)
        self.collider.is_trigger = True
        self.collider.on_collision = self.on_collision
        self.add_tag("collectible")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Bob animation
        self.bob_time += delta_time * 3
        bob_offset = 5 * (0.5 + 0.5 * math.sin(self.bob_time))
        self.transform.position.y = self.start_y + bob_offset
        
        # Rotate
        self.transform.rotation += 90 * delta_time
    
    def on_collision(self, other):
        """Handle collision with player."""
        if other.game_object and other.game_object.has_tag("player"):
            # Player collected this item
            if hasattr(self.scene, 'collect_item'):
                self.scene.collect_item(self)
            self.destroy()


class PlatformerScene(Scene):
    """The main platformer scene."""
    
    def __init__(self):
        super().__init__("Platformer")
        self.score = 0
        self.total_collectibles = 0
    
    def on_enter(self):
        super().on_enter()
        
        # Create player
        self.player = Player()
        self.player.transform.position = Vector2(100, 200)
        self.add_object(self.player)
        
        # Create platforms
        self.create_level()
        
        # Add all colliders to physics
        if hasattr(self.engine, 'physics_engine'):
            for obj in self.objects:
                if hasattr(obj, 'collider') and obj.collider:
                    self.engine.physics_engine.add_collider(obj.collider)
        
        print("Platformer Demo started!")
        print("WASD/Arrows: Move, SPACE/W/UP: Jump")
        print("Collect all yellow items and avoid red enemies!")
        print("Press ESC to quit")
    
    def create_level(self):
        """Create the level platforms and objects."""
        # Ground platforms
        self.add_object(Platform(0, 550, 200, 50))
        self.add_object(Platform(300, 550, 200, 50))
        self.add_object(Platform(600, 550, 200, 50))
        
        # Middle platforms
        self.add_object(Platform(150, 450, 150, 20))
        self.add_object(Platform(400, 400, 100, 20))
        self.add_object(Platform(600, 350, 120, 20))
        
        # Upper platforms
        self.add_object(Platform(100, 300, 100, 20))
        self.add_object(Platform(300, 250, 80, 20))
        self.add_object(Platform(500, 200, 100, 20))
        self.add_object(Platform(700, 150, 80, 20))
        
        # Small jumping platforms
        self.add_object(Platform(250, 350, 60, 15))
        self.add_object(Platform(450, 300, 60, 15))
        
        # Add enemies
        self.add_object(Enemy(350, 380, 80))
        self.add_object(Enemy(650, 330, 60))
        self.add_object(Enemy(120, 280, 70))
        
        # Add collectibles
        collectible_positions = [
            (175, 420), (425, 370), (630, 320),
            (125, 270), (320, 220), (525, 170),
            (730, 120), (275, 320), (475, 270)
        ]
        
        for x, y in collectible_positions:
            self.add_object(Collectible(x, y))
            self.total_collectibles += 1
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Manual collision detection
        self._check_collisions()
        
        # Check for quit
        if self.engine.input_manager.is_key_just_pressed(Keys.ESCAPE):
            self.engine.stop()
        
        # Check win condition
        if self.score >= self.total_collectibles:
            print("Congratulations! You collected all items!")
    
    def _check_collisions(self):
        """Manual collision detection."""
        # Get all game objects with colliders
        player = self.find_object("Player")
        platforms = self.find_objects_with_tag("platform")
        enemies = self.find_objects_with_tag("enemy")
        collectibles = self.find_objects_with_tag("collectible")
        
        if not player:
            return
        
        # Reset grounded state
        player.is_grounded = False
        
        # Player vs platforms
        for platform in platforms:
            if self._objects_colliding(player, platform):
                self._handle_platform_collision(player, platform)
        
        # Player vs enemies
        for enemy in enemies:
            if self._objects_colliding(player, enemy):
                player.respawn()
                break
        
        # Player vs collectibles
        for collectible in collectibles:
            if self._objects_colliding(player, collectible):
                self.collect_item(collectible)
                collectible.destroy()
        
        # Enemies vs platforms
        for enemy in enemies:
            for platform in platforms:
                if self._objects_colliding(enemy, platform):
                    self._handle_platform_collision(enemy, platform)
    
    def _objects_colliding(self, obj1, obj2):
        """Simple rectangle collision detection."""
        if not (obj1.active and obj2.active):
            return False
        
        # Get positions and sizes
        pos1 = obj1.transform.position
        pos2 = obj2.transform.position
        
        # Get object sizes
        if obj1.name == "Player":
            size1_w, size1_h = 32, 32
        elif obj1.name == "Enemy":
            size1_w, size1_h = 24, 24
        else:  # Collectible
            size1_w, size1_h = 16, 16
            
        if hasattr(obj2, 'width') and hasattr(obj2, 'height'):
            size2_w, size2_h = obj2.width, obj2.height
        elif obj2.name == "Player":
            size2_w, size2_h = 32, 32
        elif obj2.name == "Enemy":
            size2_w, size2_h = 24, 24
        else:
            size2_w, size2_h = 16, 16
        
        return (abs(pos1.x - pos2.x) < (size1_w + size2_w) / 2 and 
                abs(pos1.y - pos2.y) < (size1_h + size2_h) / 2)
    
    def _handle_platform_collision(self, obj, platform):
        """Handle collision between an object and a platform."""
        obj_bottom = obj.transform.position.y + 16
        platform_top = platform.transform.position.y - platform.height // 2
        
        # If object is falling and close to landing on platform
        if obj.velocity.y > 0 and abs(obj_bottom - platform_top) < 25:
            obj.transform.position.y = platform_top - 16
            obj.velocity.y = 0
            if obj.name == "Player":
                obj.is_grounded = True
    
    def collect_item(self, item):
        """Called when player collects an item."""
        self.score += 1
        print(f"Collected! Score: {self.score}/{self.total_collectibles}")
    
    def render(self, renderer):
        super().render(renderer)
        
        # Draw UI
        renderer.draw_text(f"Score: {self.score}/{self.total_collectibles}", 
                          Vector2(10, 10), Color.WHITE, 24, layer="ui")
        
        # Draw controls
        renderer.draw_text("WASD: Move, SPACE: Jump", 
                          Vector2(10, self.engine.height - 30), Color.LIGHT_GRAY, 16, layer="ui")


def main():
    """Main entry point for the platformer demo."""
    # Create engine
    engine = Engine(800, 600, "VoidRay Platformer Demo", 60)
    
    # Create and set the game scene
    game_scene = PlatformerScene()
    engine.set_scene(game_scene)
    
    # Run the game
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")


if __name__ == "__main__":
    main()
