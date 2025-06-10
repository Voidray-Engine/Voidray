
"""
Sample VoidRay Script: Enhanced Player Behavior
This demonstrates advanced scripting capabilities.
"""

import voidray
from voidray import GameObject, Vector2
import math


class EnhancedPlayer(GameObject):
    """Enhanced player with scripted behaviors."""
    
    def __init__(self, name="ScriptedPlayer"):
        super().__init__(name)
        self.speed = 200
        self.jump_force = 400
        self.health = 100
        self.max_health = 100
        
        # Movement state
        self.on_ground = False
        self.velocity = Vector2(0, 0)
        
        # Animation state
        self.animation_timer = 0
        self.current_animation = "idle"
        
        # Abilities
        self.dash_cooldown = 0
        self.dash_force = 600
        self.can_double_jump = True
        
        print(f"Enhanced player '{name}' initialized via script")
    
    def update(self, delta_time):
        """Update player behavior."""
        super().update(delta_time)
        
        # Get input
        engine = voidray.get_engine()
        if not engine or not engine.input_manager:
            return
        
        input_manager = engine.input_manager
        
        # Handle movement
        self._handle_movement(input_manager, delta_time)
        
        # Handle abilities
        self._handle_abilities(input_manager, delta_time)
        
        # Update timers
        self.dash_cooldown = max(0, self.dash_cooldown - delta_time)
        self.animation_timer += delta_time
        
        # Apply velocity
        self.transform.position += self.velocity * delta_time
        
        # Simple ground detection (would be replaced with proper collision)
        if self.transform.position.y > 500:
            self.transform.position.y = 500
            self.on_ground = True
            self.velocity.y = 0
            self.can_double_jump = True
    
    def _handle_movement(self, input_manager, delta_time):
        """Handle basic movement input."""
        import pygame
        
        # Horizontal movement
        horizontal_input = 0
        if input_manager.is_key_pressed(pygame.K_a) or input_manager.is_key_pressed(pygame.K_LEFT):
            horizontal_input = -1
        if input_manager.is_key_pressed(pygame.K_d) or input_manager.is_key_pressed(pygame.K_RIGHT):
            horizontal_input = 1
        
        self.velocity.x = horizontal_input * self.speed
        
        # Jumping
        if input_manager.is_key_just_pressed(pygame.K_SPACE) or input_manager.is_key_just_pressed(pygame.K_w):
            if self.on_ground:
                self.velocity.y = -self.jump_force
                self.on_ground = False
                print("Player jumped!")
            elif self.can_double_jump:
                self.velocity.y = -self.jump_force * 0.8
                self.can_double_jump = False
                print("Player double jumped!")
        
        # Apply gravity
        if not self.on_ground:
            self.velocity.y += 980 * delta_time  # Gravity
    
    def _handle_abilities(self, input_manager, delta_time):
        """Handle special abilities."""
        import pygame
        
        # Dash ability
        if input_manager.is_key_just_pressed(pygame.K_LSHIFT) and self.dash_cooldown <= 0:
            dash_direction = Vector2(1 if self.velocity.x >= 0 else -1, 0)
            self.velocity.x = dash_direction.x * self.dash_force
            self.dash_cooldown = 1.0  # 1 second cooldown
            print("Player dashed!")
    
    def take_damage(self, amount):
        """Handle taking damage."""
        self.health = max(0, self.health - amount)
        print(f"Player took {amount} damage! Health: {self.health}/{self.max_health}")
        
        if self.health <= 0:
            self.on_death()
    
    def heal(self, amount):
        """Handle healing."""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        actual_heal = self.health - old_health
        if actual_heal > 0:
            print(f"Player healed {actual_heal} HP! Health: {self.health}/{self.max_health}")
    
    def on_death(self):
        """Handle player death."""
        print("Player died!")
        # Reset position and health
        self.health = self.max_health
        self.transform.position = Vector2(100, 100)
        self.velocity = Vector2(0, 0)
    
    def on_collision(self, other):
        """Handle collisions with other objects."""
        if hasattr(other, 'name'):
            if 'enemy' in other.name.lower():
                self.take_damage(10)
            elif 'powerup' in other.name.lower():
                self.heal(20)
        
        print(f"Player collided with {getattr(other, 'name', 'unknown object')}")


class SimpleAI(GameObject):
    """Simple AI behavior that can be attached to any object."""
    
    def __init__(self, name="AIObject"):
        super().__init__(name)
        self.target = None
        self.speed = 100
        self.detection_range = 200
        self.state = "idle"  # idle, patrol, chase, attack
        
        # Patrol points
        self.patrol_points = [
            Vector2(200, 400),
            Vector2(600, 400)
        ]
        self.current_patrol_index = 0
        
        print(f"AI object '{name}' initialized")
    
    def set_target(self, target):
        """Set the AI's target to follow."""
        self.target = target
    
    def update(self, delta_time):
        """Update AI behavior."""
        super().update(delta_time)
        
        if self.target:
            distance_to_target = (self.target.transform.position - self.transform.position).magnitude()
            
            if distance_to_target <= self.detection_range:
                self.state = "chase"
                self._chase_target(delta_time)
            else:
                self.state = "patrol"
                self._patrol(delta_time)
        else:
            self.state = "idle"
    
    def _chase_target(self, delta_time):
        """Chase the target."""
        direction = (self.target.transform.position - self.transform.position).normalized()
        self.transform.position += direction * self.speed * delta_time
    
    def _patrol(self, delta_time):
        """Patrol between waypoints."""
        if not self.patrol_points:
            return
        
        target_point = self.patrol_points[self.current_patrol_index]
        direction = target_point - self.transform.position
        
        if direction.magnitude() < 20:  # Reached waypoint
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            direction = direction.normalized()
            self.transform.position += direction * self.speed * 0.5 * delta_time


def create_scripted_objects():
    """Function to create objects with scripted behaviors."""
    print("Creating scripted game objects...")
    
    # This function can be called from the main game to set up scripted objects
    engine = voidray.get_engine()
    if not engine or not engine.current_scene:
        return
    
    # Create enhanced player
    player = EnhancedPlayer("ScriptedPlayer")
    player.transform.position = Vector2(100, 400)
    engine.current_scene.add_object(player)
    
    # Create AI enemy
    ai_enemy = SimpleAI("AIEnemy")
    ai_enemy.transform.position = Vector2(300, 400)
    ai_enemy.set_target(player)
    engine.current_scene.add_object(ai_enemy)
    
    print("Scripted objects created successfully!")


def sample_function():
    """Sample function that can be called from the game."""
    print("Sample script function called!")
    return "Hello from enhanced behavior script!"


# Script initialization
if __name__ != "__main__":
    print("Enhanced behavior script loaded successfully")
