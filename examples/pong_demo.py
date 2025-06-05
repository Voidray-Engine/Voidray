
"""
Pong Demo - Classic paddle game
Demonstrates input handling, collision detection, and basic game logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from voidray import Engine, Scene, Sprite, Vector2, InputManager, Keys
from voidray.graphics.renderer import Color
from voidray.physics.collider import RectCollider, CircleCollider

class Ball(Sprite):
    def __init__(self):
        super().__init__("Ball")
        self.create_colored_circle(8, Color.WHITE)
        self.velocity = Vector2(300, 200)
        self.collider = CircleCollider(self, 8)
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Move ball
        self.transform.position += self.velocity * delta_time
        
        # Bounce off top/bottom walls
        if self.transform.position.y <= 8 or self.transform.position.y >= 592:
            self.velocity.y = -self.velocity.y
            
        # Reset if ball goes off screen
        if self.transform.position.x < -20 or self.transform.position.x > 820:
            self.transform.position = Vector2(400, 300)
            self.velocity.x = -self.velocity.x

class Paddle(Sprite):
    def __init__(self, name, x, controls):
        super().__init__(name)
        self.create_colored_rect(20, 80, Color.WHITE)
        self.transform.position = Vector2(x, 300)
        self.speed = 400
        self.controls = controls  # (up_key, down_key)
        self.collider = RectCollider(self, 20, 80)
        
    def update(self, delta_time):
        super().update(delta_time)
        
        input_mgr = self.scene.engine.input_manager
        
        # Move paddle
        if input_mgr.is_key_pressed(self.controls[0]):  # Up
            self.transform.position.y -= self.speed * delta_time
        if input_mgr.is_key_pressed(self.controls[1]):  # Down
            self.transform.position.y += self.speed * delta_time
            
        # Keep paddle on screen
        self.transform.position.y = max(40, min(560, self.transform.position.y))

class PongScene(Scene):
    def __init__(self):
        super().__init__("PongScene")
        
    def on_enter(self):
        print("=== Pong Demo ===")
        print("Player 1: W/S keys")
        print("Player 2: Up/Down arrows")
        print("Press ESC to quit")
        
        # Create paddles
        self.paddle1 = Paddle("Player1", 50, (Keys.W, Keys.S))
        self.paddle2 = Paddle("Player2", 750, (Keys.UP, Keys.DOWN))
        self.add_object(self.paddle1)
        self.add_object(self.paddle2)
        
        # Create ball
        self.ball = Ball()
        self.add_object(self.ball)
        
        # Add collision detection
        self.engine.physics_engine.add_collision_pair(
            self.ball, self.paddle1, self.on_paddle_hit
        )
        self.engine.physics_engine.add_collision_pair(
            self.ball, self.paddle2, self.on_paddle_hit
        )
        
    def on_paddle_hit(self, ball, paddle):
        # Reverse ball direction and add some randomness
        ball.velocity.x = -ball.velocity.x
        ball.velocity.y += (ball.transform.position.y - paddle.transform.position.y) * 2
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check for quit
        if self.engine.input_manager.is_key_pressed(Keys.ESCAPE):
            self.engine.stop()

def main():
    engine = Engine(800, 600, "Pong Demo", 60)
    scene = PongScene()
    engine.set_scene(scene)
    engine.run()

if __name__ == "__main__":
    main()
