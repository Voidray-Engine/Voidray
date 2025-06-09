
"""
Pong Game Example - VoidRay Engine
==================================

This is a classic Pong implementation that demonstrates:
- Basic 2D rendering with rectangles
- Keyboard input handling
- Simple physics and collision detection
- Game state management
- Score tracking

The game features two paddles controlled by players and a ball that bounces around.
Player 1 uses W/S keys, Player 2 uses UP/DOWN arrow keys.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voidray import Engine, Scene, GameObject, Vector2, Keys
from voidray.utils.color import Color
from voidray.physics import RectCollider
import pygame

class Ball(GameObject):
    """
    The Ball class represents the game ball that bounces around the screen.
    It demonstrates:
    - Custom GameObject creation
    - Velocity-based movement
    - Collision detection with screen boundaries
    - Simple physics (bouncing)
    """
    
    def __init__(self):
        super().__init__("Ball")
        
        # Ball properties
        self.size = Vector2(15, 15)
        self.velocity = Vector2(300, 200)  # Pixels per second
        self.max_speed = 500
        
        # Set initial position to center of screen
        self.transform.position = Vector2(400, 300)
        
        # Add collider for collision detection
        self.collider = RectCollider(self.size.x, self.size.y)
        self.add_component(self.collider)
        
        print("Ball created at center with initial velocity")
    
    def update(self, delta_time):
        """
        Update the ball's position and handle bouncing off walls.
        
        Args:
            delta_time: Time since last frame in seconds
        """
        super().update(delta_time)
        
        # Move ball based on velocity
        self.transform.position += self.velocity * delta_time
        
        # Get screen bounds (assuming 800x600 screen)
        screen_width = 800
        screen_height = 600
        
        # Bounce off top and bottom walls
        if self.transform.position.y <= self.size.y/2:
            self.transform.position.y = self.size.y/2
            self.velocity.y = -self.velocity.y
            print("Ball bounced off top wall")
        elif self.transform.position.y >= screen_height - self.size.y/2:
            self.transform.position.y = screen_height - self.size.y/2
            self.velocity.y = -self.velocity.y
            print("Ball bounced off bottom wall")
        
        # Check if ball goes off left or right side (scoring)
        if self.transform.position.x < 0:
            # Right player scores
            self.scene.right_score += 1
            self.reset_ball()
            print(f"Right player scores! Score: {self.scene.left_score} - {self.scene.right_score}")
        elif self.transform.position.x > screen_width:
            # Left player scores
            self.scene.left_score += 1
            self.reset_ball()
            print(f"Left player scores! Score: {self.scene.left_score} - {self.scene.right_score}")
    
    def reset_ball(self):
        """Reset ball to center with random direction."""
        self.transform.position = Vector2(400, 300)
        # Reverse horizontal direction and add some randomness
        self.velocity.x = -self.velocity.x + (200 if self.velocity.x > 0 else -200)
        self.velocity.y = 200 if self.velocity.y > 0 else -200
    
    def render(self, renderer):
        """
        Render the ball as a white rectangle.
        
        Args:
            renderer: The renderer to draw with
        """
        # Draw ball as a white rectangle
        ball_rect_pos = Vector2(
            self.transform.position.x - self.size.x/2,
            self.transform.position.y - self.size.y/2
        )
        renderer.draw_rect(ball_rect_pos, self.size, Color.WHITE, filled=True)


class Paddle(GameObject):
    """
    The Paddle class represents player-controlled paddles.
    It demonstrates:
    - Input-based movement
    - Boundary constraints
    - Collision detection with the ball
    """
    
    def __init__(self, name, x_position, up_key, down_key):
        super().__init__(name)
        
        # Paddle properties
        self.size = Vector2(20, 100)
        self.speed = 400  # Pixels per second
        self.up_key = up_key
        self.down_key = down_key
        
        # Set position (left or right side)
        self.transform.position = Vector2(x_position, 300)
        
        # Add collider for ball collision
        self.collider = RectCollider(self.size.x, self.size.y)
        self.add_component(self.collider)
        
        print(f"Paddle '{name}' created at x={x_position}")
    
    def update(self, delta_time):
        """
        Update paddle position based on input.
        
        Args:
            delta_time: Time since last frame in seconds
        """
        super().update(delta_time)
        
        # Get input manager from engine
        input_manager = self.scene.engine.input_manager
        
        # Handle movement input
        movement = 0
        if input_manager.is_key_pressed(self.up_key):
            movement = -1  # Up (negative Y)
        elif input_manager.is_key_pressed(self.down_key):
            movement = 1   # Down (positive Y)
        
        # Apply movement
        if movement != 0:
            new_y = self.transform.position.y + movement * self.speed * delta_time
            
            # Constrain to screen bounds
            half_height = self.size.y / 2
            screen_height = 600
            
            new_y = max(half_height, min(screen_height - half_height, new_y))
            self.transform.position.y = new_y
    
    def render(self, renderer):
        """
        Render the paddle as a white rectangle.
        
        Args:
            renderer: The renderer to draw with
        """
        # Draw paddle as a white rectangle
        paddle_rect_pos = Vector2(
            self.transform.position.x - self.size.x/2,
            self.transform.position.y - self.size.y/2
        )
        renderer.draw_rect(paddle_rect_pos, self.size, Color.WHITE, filled=True)


class PongScene(Scene):
    """
    The main game scene that manages all game objects and game logic.
    It demonstrates:
    - Scene management
    - Object creation and organization
    - Game state tracking (scores)
    - Collision handling between ball and paddles
    """
    
    def __init__(self):
        super().__init__("PongGame")
        
        # Game state
        self.left_score = 0
        self.right_score = 0
        self.max_score = 5  # First to 5 wins
        
        # Game objects
        self.ball = None
        self.left_paddle = None
        self.right_paddle = None
    
    def on_enter(self):
        """Called when scene becomes active - initialize game objects."""
        super().on_enter()
        
        print("Starting Pong Game!")
        print("Controls:")
        print("  Player 1 (Left): W/S keys")
        print("  Player 2 (Right): UP/DOWN arrow keys")
        print("  First to 5 points wins!")
        print()
        
        # Create game objects
        self.ball = Ball()
        self.left_paddle = Paddle("LeftPaddle", 50, Keys.W, Keys.S)
        self.right_paddle = Paddle("RightPaddle", 750, Keys.UP, Keys.DOWN)
        
        # Add objects to scene
        self.add_object(self.ball)
        self.add_object(self.left_paddle)
        self.add_object(self.right_paddle)
        
        # Register for physics callbacks to handle ball-paddle collisions
        if self.engine:
            self.engine.physics_engine.add_collision_callback(self.on_collision)
    
    def on_collision(self, collider1, collider2):
        """
        Handle collisions between game objects.
        
        Args:
            collider1: First collider in collision
            collider2: Second collider in collision
        """
        # Check if ball collided with a paddle
        ball_collider = None
        paddle_collider = None
        
        if collider1.game_object == self.ball:
            ball_collider = collider1
            paddle_collider = collider2
        elif collider2.game_object == self.ball:
            ball_collider = collider2
            paddle_collider = collider1
        
        if ball_collider and paddle_collider:
            # Ball hit a paddle - reverse horizontal velocity and add some angle
            self.ball.velocity.x = -self.ball.velocity.x
            
            # Add vertical velocity based on where ball hit paddle
            paddle_center = paddle_collider.game_object.transform.position.y
            ball_center = ball_collider.game_object.transform.position.y
            hit_offset = (ball_center - paddle_center) / (paddle_collider.game_object.size.y / 2)
            
            # Add spin based on hit location
            self.ball.velocity.y += hit_offset * 150
            
            # Increase ball speed slightly (up to max)
            speed = self.ball.velocity.magnitude()
            if speed < self.ball.max_speed:
                speed_multiplier = min(1.1, self.ball.max_speed / speed)
                self.ball.velocity *= speed_multiplier
            
            print(f"Ball hit paddle! New velocity: {self.ball.velocity}")
    
    def update(self, delta_time):
        """Update game logic and check win conditions."""
        super().update(delta_time)
        
        # Manual collision detection for ball-paddle collisions
        self.check_ball_paddle_collisions()
        
        # Check for win condition
        if self.left_score >= self.max_score:
            print(f"\nPlayer 1 (Left) WINS! Final Score: {self.left_score} - {self.right_score}")
            self.restart_game()
        elif self.right_score >= self.max_score:
            print(f"\nPlayer 2 (Right) WINS! Final Score: {self.left_score} - {self.right_score}")
            self.restart_game()
        
        # Check for exit
        if self.engine.input_manager.is_key_just_pressed(Keys.ESCAPE):
            print("Game ended by player")
            self.engine.stop()
    
    def check_ball_paddle_collisions(self):
        """Manually check for ball-paddle collisions."""
        if not self.ball or not self.left_paddle or not self.right_paddle:
            return
        
        ball_pos = self.ball.transform.position
        ball_size = self.ball.size
        
        # Check collision with left paddle
        left_pos = self.left_paddle.transform.position
        left_size = self.left_paddle.size
        
        if (ball_pos.x - ball_size.x/2 <= left_pos.x + left_size.x/2 and
            ball_pos.x + ball_size.x/2 >= left_pos.x - left_size.x/2 and
            ball_pos.y - ball_size.y/2 <= left_pos.y + left_size.y/2 and
            ball_pos.y + ball_size.y/2 >= left_pos.y - left_size.y/2 and
            self.ball.velocity.x < 0):  # Only if ball is moving left
            
            self.handle_paddle_collision(self.left_paddle)
        
        # Check collision with right paddle
        right_pos = self.right_paddle.transform.position
        right_size = self.right_paddle.size
        
        if (ball_pos.x - ball_size.x/2 <= right_pos.x + right_size.x/2 and
            ball_pos.x + ball_size.x/2 >= right_pos.x - right_size.x/2 and
            ball_pos.y - ball_size.y/2 <= right_pos.y + right_size.y/2 and
            ball_pos.y + ball_size.y/2 >= right_pos.y - right_size.y/2 and
            self.ball.velocity.x > 0):  # Only if ball is moving right
            
            self.handle_paddle_collision(self.right_paddle)
    
    def handle_paddle_collision(self, paddle):
        """Handle ball collision with a paddle."""
        # Ball hit a paddle - reverse horizontal velocity and add some angle
        self.ball.velocity.x = -self.ball.velocity.x
        
        # Add vertical velocity based on where ball hit paddle
        paddle_center = paddle.transform.position.y
        ball_center = self.ball.transform.position.y
        hit_offset = (ball_center - paddle_center) / (paddle.size.y / 2)
        
        # Add spin based on hit location
        self.ball.velocity.y += hit_offset * 150
        
        # Increase ball speed slightly (up to max)
        speed = self.ball.velocity.magnitude()
        if speed < self.ball.max_speed:
            speed_multiplier = min(1.1, self.ball.max_speed / speed)
            self.ball.velocity *= speed_multiplier
        
        print(f"Ball hit paddle! New velocity: {self.ball.velocity}")
    
    def restart_game(self):
        """Restart the game after someone wins."""
        print("Press SPACE to play again or ESC to quit")
        
        # Wait for input
        if self.engine.input_manager.is_key_just_pressed(Keys.SPACE):
            self.left_score = 0
            self.right_score = 0
            self.ball.reset_ball()
            print("New game started!")
    
    def render(self, renderer):
        """Render all game objects and UI."""
        super().render(renderer)
        
        # Draw center line
        for y in range(0, 600, 20):
            renderer.draw_rect(Vector2(395, y), Vector2(10, 10), Color.WHITE, filled=True)
        
        # Draw scores
        renderer.draw_text(str(self.left_score), Vector2(350, 50), Color.WHITE, 48)
        renderer.draw_text(str(self.right_score), Vector2(450, 50), Color.WHITE, 48)
        
        # Draw instructions
        if self.left_score >= self.max_score or self.right_score >= self.max_score:
            renderer.draw_text("Press SPACE to play again", Vector2(250, 500), Color.WHITE, 24)
            renderer.draw_text("Press ESC to quit", Vector2(300, 530), Color.WHITE, 24)


def main():
    """Main function to run the Pong game."""
    print("VoidRay Engine - Pong Game Example")
    print("==================================")
    
    try:
        # Create engine with 800x600 resolution
        engine = Engine(800, 600, "VoidRay Pong", 60)
        
        # Create and set the game scene
        pong_scene = PongScene()
        engine.set_scene(pong_scene)
        
        # Run the game
        engine.run()
        
    except Exception as e:
        print(f"Error running Pong game: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

