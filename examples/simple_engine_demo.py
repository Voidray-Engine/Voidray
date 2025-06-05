
"""
Simple VoidRay Engine Demo
=========================

This demonstrates how to use VoidRay as a proper game engine.
The engine controls everything - you just define your game logic.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import voidray
from voidray import GameObject, Vector2, Keys
from voidray.graphics.renderer import Color
import random
import math


# Game objects
objects = []
score = 0


def create_enemy():
    """Create a simple enemy object."""
    enemy = GameObject("Enemy")
    enemy.transform.position = Vector2(
        random.randint(50, 750),
        random.randint(50, 150)
    )
    enemy.color = Color.RED
    enemy.size = 20
    enemy.speed = random.randint(50, 150)
    enemy.direction = Vector2(0, 1)
    return enemy


def init_game():
    """Initialize the game."""
    global objects, score
    
    print("Starting Simple Engine Demo!")
    print("Click enemies to destroy them and earn points!")
    
    # Create some enemies
    for _ in range(5):
        objects.append(create_enemy())
    
    score = 0


def update_game(delta_time):
    """Update game logic."""
    global objects, score
    
    engine = voidray.get_engine()
    
    # Update enemies
    for enemy in objects[:]:  # Copy list to avoid modification during iteration
        enemy.transform.position += enemy.direction * enemy.speed * delta_time
        
        # Remove enemies that go off screen
        if enemy.transform.position.y > engine.height + 50:
            objects.remove(enemy)
    
    # Check mouse clicks
    if engine.input_manager.is_mouse_button_just_pressed(voidray.MouseButtons.LEFT):
        mouse_pos = engine.input_manager.get_mouse_position()
        
        # Check if clicked on any enemy
        for enemy in objects[:]:
            enemy_pos = enemy.transform.position
            distance = (mouse_pos - enemy_pos).magnitude()
            
            if distance < enemy.size:
                objects.remove(enemy)
                score += 10
                break
    
    # Spawn new enemies periodically
    if random.random() < 0.005:  # Small chance each frame
        objects.append(create_enemy())
    
    # Quit on ESC
    if engine.input_manager.is_key_just_pressed(Keys.ESCAPE):
        voidray.stop()


def render_game():
    """Render the game."""
    engine = voidray.get_engine()
    renderer = engine.renderer
    
    # Draw enemies
    for enemy in objects:
        pos = enemy.transform.position
        renderer.draw_circle(pos, enemy.size, enemy.color, True)
        renderer.draw_circle(pos, enemy.size, Color.WHITE, False, 2)
    
    # Draw UI
    renderer.draw_text("VoidRay Engine Demo", Vector2(10, 10), Color.WHITE, 32)
    renderer.draw_text(f"Score: {score}", Vector2(10, 50), Color.YELLOW, 24)
    renderer.draw_text("Click the red circles to destroy them!", Vector2(10, 80), Color.LIGHT_GRAY, 18)
    renderer.draw_text("ESC to quit", Vector2(10, engine.height - 30), Color.GRAY, 16)
    
    # Draw FPS
    fps = engine.get_fps()
    renderer.draw_text(f"FPS: {fps:.1f}", Vector2(engine.width - 100, 10), Color.CYAN, 16)


def main():
    """Main function - sets up and starts the engine."""
    # Configure the engine
    voidray.configure(800, 600, "Simple VoidRay Engine Demo", 60)
    
    # Register our game functions
    voidray.on_init(init_game)
    voidray.on_update(update_game)
    voidray.on_render(render_game)
    
    # Start the engine - this runs until the game ends
    voidray.start()


if __name__ == "__main__":
    main()
