"""
Space Shooter - VoidRay Game Example
A more advanced example demonstrating sprites, physics, audio, and game mechanics.
"""

import sys
import os
import math
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voidray import Engine, Scene, Sprite, InputManager, Keys, MouseButtons, Vector2
from voidray.graphics.renderer import Color
from voidray.physics.collider import RectCollider, CircleCollider


class Bullet(Sprite):
    """A projectile fired by the player or enemies."""
    
    def __init__(self, x, y, direction, speed=400, is_player_bullet=True):
        super().__init__("Bullet")
        
        # Create bullet appearance
        if is_player_bullet:
            self.create_colored_rect(4, 8, Color.CYAN)
        else:
            self.create_colored_rect(4, 6, Color.RED)
        
        self.transform.position = Vector2(x, y)
        self.velocity = direction.normalized() * speed
        self.is_player_bullet = is_player_bullet
        self.lifetime = 3.0  # Bullets last 3 seconds
        
        # Add collider
        self.collider = RectCollider(self, 4, 8 if is_player_bullet else 6)
        self.collider.is_trigger = True
        self.collider.on_collision = self.on_collision
        
        if is_player_bullet:
            self.add_tag("player_bullet")
        else:
            self.add_tag("enemy_bullet")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Move bullet
        self.transform.position += self.velocity * delta_time
        
        # Remove bullet if it goes off screen or lifetime expires
        self.lifetime -= delta_time
        screen_width = self.scene.engine.width
        screen_height = self.scene.engine.height
        
        if (self.lifetime <= 0 or 
            self.transform.position.x < -10 or self.transform.position.x > screen_width + 10 or
            self.transform.position.y < -10 or self.transform.position.y > screen_height + 10):
            self.destroy()
    
    def on_collision(self, other):
        """Handle bullet collision."""
        if self.is_player_bullet and other.game_object and other.game_object.has_tag("enemy"):
            # Player bullet hit enemy
            other.game_object.take_damage(1)
            self.destroy()
        elif not self.is_player_bullet and other.game_object and other.game_object.has_tag("player"):
            # Enemy bullet hit player
            other.game_object.take_damage(1)
            self.destroy()


class Player(Sprite):
    """The player's spaceship."""
    
    def __init__(self):
        super().__init__("Player")
        self.create_colored_rect(32, 24, Color.GREEN)
        
        # Game properties
        self.speed = 250
        self.health = 3
        self.max_health = 3
        self.shoot_cooldown = 0.0
        self.shoot_delay = 0.15  # Time between shots
        
        # Add collider
        self.collider = RectCollider(self, 32, 24)
        self.collider.on_collision = self.on_collision
        self.add_tag("player")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        input_manager = self.scene.engine.input_manager
        
        # Movement
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
        
        # Keep player on screen
        screen_width = self.scene.engine.width
        screen_height = self.scene.engine.height
        margin = 16
        
        self.transform.position.x = max(margin, min(screen_width - margin, self.transform.position.x))
        self.transform.position.y = max(margin, min(screen_height - margin, self.transform.position.y))
        
        # Shooting
        self.shoot_cooldown -= delta_time
        if (input_manager.is_key_pressed(Keys.SPACE) or 
            input_manager.is_mouse_button_pressed(MouseButtons.LEFT)) and self.shoot_cooldown <= 0:
            self.shoot()
    
    def shoot(self):
        """Fire a bullet."""
        if self.scene and self.shoot_cooldown <= 0:
            bullet = Bullet(self.transform.position.x, self.transform.position.y - 20, 
                           Vector2(0, -1), 500, True)
            self.scene.add_object(bullet)
            if hasattr(self.scene.engine, 'physics_engine'):
                self.scene.engine.physics_engine.add_collider(bullet.collider)
            
            self.shoot_cooldown = self.shoot_delay
    
    def on_collision(self, other):
        """Handle collision with other objects."""
        # Collision is handled by bullets and enemies
        pass
    
    def take_damage(self, amount):
        """Take damage."""
        self.health -= amount
        if self.health <= 0:
            self.die()
        else:
            # Flash red when hit
            self.set_color(Color.RED)
            # Note: In a real game, you'd reset color after a delay
    
    def die(self):
        """Handle player death."""
        print("Player destroyed!")
        if hasattr(self.scene, 'game_over'):
            self.scene.game_over()


class Enemy(Sprite):
    """An enemy spaceship."""
    
    def __init__(self, x, y, enemy_type="basic"):
        super().__init__("Enemy")
        
        self.enemy_type = enemy_type
        
        if enemy_type == "basic":
            self.create_colored_rect(24, 20, Color.RED)
            self.speed = 100
            self.health = 1
            self.shoot_delay = 2.0
        elif enemy_type == "fast":
            self.create_colored_rect(20, 16, Color.YELLOW)
            self.speed = 180
            self.health = 1
            self.shoot_delay = 1.5
        elif enemy_type == "tank":
            self.create_colored_rect(32, 28, Color.MAGENTA)
            self.speed = 60
            self.health = 3
            self.shoot_delay = 1.0
        
        self.transform.position = Vector2(x, y)
        self.shoot_cooldown = random.uniform(0, self.shoot_delay)
        self.movement_pattern = random.choice(["straight", "sine", "zigzag"])
        self.time = 0
        
        # Add collider
        self.collider = RectCollider(self, 24, 20)
        self.collider.on_collision = self.on_collision
        self.add_tag("enemy")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        self.time += delta_time
        
        # Movement patterns
        if self.movement_pattern == "straight":
            self.transform.position.y += self.speed * delta_time
        elif self.movement_pattern == "sine":
            self.transform.position.y += self.speed * delta_time
            self.transform.position.x += math.sin(self.time * 3) * 50 * delta_time
        elif self.movement_pattern == "zigzag":
            self.transform.position.y += self.speed * delta_time
            if int(self.time * 2) % 2 == 0:
                self.transform.position.x += 80 * delta_time
            else:
                self.transform.position.x -= 80 * delta_time
        
        # Keep enemy on screen horizontally
        screen_width = self.scene.engine.width
        if self.transform.position.x < 0 or self.transform.position.x > screen_width:
            self.transform.position.x = max(0, min(screen_width, self.transform.position.x))
        
        # Remove enemy if it goes off bottom of screen
        if self.transform.position.y > self.scene.engine.height + 50:
            self.destroy()
        
        # Shooting
        self.shoot_cooldown -= delta_time
        if self.shoot_cooldown <= 0 and self.scene:
            self.shoot()
    
    def shoot(self):
        """Fire a bullet at the player."""
        # Find player
        player = self.scene.find_object("Player")
        if player:
            direction = (player.transform.position - self.transform.position).normalized()
            bullet = Bullet(self.transform.position.x, self.transform.position.y + 15, 
                           direction, 200, False)
            self.scene.add_object(bullet)
            if hasattr(self.scene.engine, 'physics_engine'):
                self.scene.engine.physics_engine.add_collider(bullet.collider)
            
            self.shoot_cooldown = self.shoot_delay
    
    def on_collision(self, other):
        """Handle collision with other objects."""
        # Collision is handled by bullets
        pass
    
    def take_damage(self, amount):
        """Take damage."""
        self.health -= amount
        if self.health <= 0:
            self.die()
        else:
            # Flash white when hit
            self.set_color(Color.WHITE)
    
    def die(self):
        """Handle enemy death."""
        if hasattr(self.scene, 'enemy_destroyed'):
            self.scene.enemy_destroyed(self)
        self.destroy()


class Powerup(Sprite):
    """A powerup that enhances the player."""
    
    def __init__(self, x, y, powerup_type="health"):
        super().__init__("Powerup")
        
        self.powerup_type = powerup_type
        
        if powerup_type == "health":
            self.create_colored_rect(16, 16, Color.GREEN)
        elif powerup_type == "rapid_fire":
            self.create_colored_rect(16, 16, Color.BLUE)
        
        self.transform.position = Vector2(x, y)
        self.bob_speed = 3
        self.bob_amount = 5
        self.start_y = y
        self.time = 0
        
        # Add collider
        self.collider = RectCollider(self, 16, 16)
        self.collider.is_trigger = True
        self.collider.on_collision = self.on_collision
        self.add_tag("powerup")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Bob animation
        self.time += delta_time
        bob_offset = math.sin(self.time * self.bob_speed) * self.bob_amount
        self.transform.position.y = self.start_y + bob_offset
        
        # Spin
        self.transform.rotation += 90 * delta_time
        
        # Move down slowly
        self.start_y += 30 * delta_time
        
        # Remove if off screen
        if self.start_y > self.scene.engine.height + 50:
            self.destroy()
    
    def on_collision(self, other):
        """Handle collision with player."""
        if other.game_object and other.game_object.has_tag("player"):
            self.apply_powerup(other.game_object)
            self.destroy()
    
    def apply_powerup(self, player):
        """Apply powerup effect to player."""
        if self.powerup_type == "health":
            player.health = min(player.max_health, player.health + 1)
            print("Health restored!")
        elif self.powerup_type == "rapid_fire":
            player.shoot_delay = max(0.05, player.shoot_delay * 0.7)
            print("Rapid fire activated!")


class SpaceShooterScene(Scene):
    """The main space shooter scene."""
    
    def __init__(self):
        super().__init__("SpaceShooter")
        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.enemies_per_wave = 5
        self.spawn_timer = 0
        self.spawn_delay = 2.0
        self.powerup_timer = 0
        self.powerup_delay = 15.0
        self.game_over_flag = False
    
    def on_enter(self):
        super().on_enter()
        
        # Create player
        self.player = Player()
        self.player.transform.position = Vector2(400, 500)
        self.add_object(self.player)
        
        # Add player collider to physics
        if hasattr(self.engine, 'physics_engine'):
            self.engine.physics_engine.add_collider(self.player.collider)
        
        print("Space Shooter started!")
        print("WASD/Arrows: Move, SPACE/Click: Shoot, ESC: Quit")
        print("Survive the waves of enemies!")
    
    def update(self, delta_time):
        super().update(delta_time)
        
        if self.game_over_flag:
            # Check for restart
            if self.engine.input_manager.is_key_just_pressed(Keys.R):
                self.restart_game()
            return
        
        # Manual collision detection - fix the collision system
        self._check_collisions()
        
        # Spawn enemies
        self.spawn_timer -= delta_time
        if self.spawn_timer <= 0 and self.enemies_spawned < self.enemies_per_wave:
            self.spawn_enemy()
            self.spawn_timer = self.spawn_delay
        
        # Check for wave completion
        enemies = self.find_objects_with_tag("enemy")
        if len(enemies) == 0 and self.enemies_spawned >= self.enemies_per_wave:
            self.next_wave()
        
        # Spawn powerups
        self.powerup_timer -= delta_time
        if self.powerup_timer <= 0:
            self.spawn_powerup()
            self.powerup_timer = self.powerup_delay
        
        # Check for quit
        if self.engine.input_manager.is_key_just_pressed(Keys.ESCAPE):
            self.engine.stop()
    
    def spawn_enemy(self):
        """Spawn a new enemy."""
        x = random.uniform(50, self.engine.width - 50)
        y = random.uniform(-100, -50)
        
        # Choose enemy type based on wave
        if self.wave == 1:
            enemy_type = "basic"
        elif self.wave <= 3:
            enemy_type = random.choice(["basic", "fast"])
        else:
            enemy_type = random.choice(["basic", "fast", "tank"])
        
        enemy = Enemy(x, y, enemy_type)
        self.add_object(enemy)
        
        if hasattr(self.engine, 'physics_engine'):
            self.engine.physics_engine.add_collider(enemy.collider)
        
        self.enemies_spawned += 1
    
    def _check_collisions(self):
        """Manual collision detection to fix the collision system."""
        # Get all game objects
        player_bullets = self.find_objects_with_tag("player_bullet")
        enemy_bullets = self.find_objects_with_tag("enemy_bullet")
        enemies = self.find_objects_with_tag("enemy")
        players = self.find_objects_with_tag("player")
        
        # Player bullets vs enemies
        for bullet in player_bullets:
            for enemy in enemies:
                if self._objects_colliding(bullet, enemy):
                    enemy.take_damage(1)
                    bullet.destroy()
                    break
        
        # Enemy bullets vs player
        for bullet in enemy_bullets:
            for player in players:
                if self._objects_colliding(bullet, player):
                    player.take_damage(1)
                    bullet.destroy()
                    break
        
        # Enemies vs player (direct collision)
        for enemy in enemies:
            for player in players:
                if self._objects_colliding(enemy, player):
                    player.take_damage(1)
                    enemy.take_damage(999)  # Destroy enemy on collision
                    break
    
    def _objects_colliding(self, obj1, obj2):
        """Simple rectangle collision detection."""
        if not (obj1.active and obj2.active):
            return False
        
        # Get positions
        pos1 = obj1.transform.position
        pos2 = obj2.transform.position
        
        # Simple distance-based collision (can be improved with proper rect collision)
        distance = pos1.distance_to(pos2)
        collision_threshold = 20  # Adjust based on object sizes
        
        return distance < collision_threshold
    
    def spawn_powerup(self):
        """Spawn a powerup."""
        x = random.uniform(50, self.engine.width - 50)
        y = random.uniform(-50, -20)
        powerup_type = random.choice(["health", "rapid_fire"])
        
        powerup = Powerup(x, y, powerup_type)
        self.add_object(powerup)
        
        if hasattr(self.engine, 'physics_engine'):
            self.engine.physics_engine.add_collider(powerup.collider)
    
    def next_wave(self):
        """Start the next wave."""
        self.wave += 1
        self.enemies_spawned = 0
        self.enemies_per_wave += 2
        self.spawn_delay = max(0.5, self.spawn_delay * 0.9)
        print(f"Wave {self.wave} started!")
    
    def enemy_destroyed(self, enemy):
        """Called when an enemy is destroyed."""
        points = {"basic": 10, "fast": 15, "tank": 25}
        self.score += points.get(enemy.enemy_type, 10)
    
    def game_over(self):
        """Handle game over."""
        self.game_over_flag = True
        print(f"Game Over! Final Score: {self.score}")
        print("Press R to restart or ESC to quit")
    
    def restart_game(self):
        """Restart the game."""
        # Clear all objects
        self.clear()
        
        # Reset game state
        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.enemies_per_wave = 5
        self.spawn_timer = 0
        self.spawn_delay = 2.0
        self.powerup_timer = 0
        self.game_over_flag = False
        
        # Recreate player
        self.on_enter()
    
    def render(self, renderer):
        super().render(renderer)
        
        # Draw UI
        renderer.draw_text(f"Score: {self.score}", Vector2(10, 10), Color.WHITE, 24)
        renderer.draw_text(f"Wave: {self.wave}", Vector2(10, 40), Color.WHITE, 20)
        
        # Draw health
        if hasattr(self, 'player') and self.player:
            for i in range(self.player.health):
                renderer.draw_rect(Vector2(10 + i * 25, 70), Vector2(20, 10), Color.GREEN)
        
        # Draw controls
        renderer.draw_text("WASD: Move, SPACE: Shoot", Vector2(10, self.engine.height - 30), 
                          Color.LIGHT_GRAY, 16)
        
        if self.game_over_flag:
            # Draw game over screen
            screen_center = Vector2(self.engine.width / 2, self.engine.height / 2)
            renderer.draw_text("GAME OVER", screen_center - Vector2(100, 50), Color.RED, 48)
            renderer.draw_text(f"Final Score: {self.score}", screen_center - Vector2(80, 0), 
                              Color.WHITE, 24)
            renderer.draw_text("Press R to restart", screen_center - Vector2(70, -30), 
                              Color.WHITE, 20)


def main():
    """Main entry point for the space shooter example."""
    # Create engine
    engine = Engine(800, 600, "VoidRay Space Shooter", 60)
    
    # Create and set the game scene
    game_scene = SpaceShooterScene()
    engine.set_scene(game_scene)
    
    # Run the game
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")


if __name__ == "__main__":
    main()
