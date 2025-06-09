"""
VoidRay Engine - Complete Pong Game
===================================

A complete Pong implementation featuring:
- Main menu screen
- Gameplay with proper Pong mechanics
- Game over screen with winner announcement
- Score tracking (first to 5 wins)
- Smooth transitions between states

Controls:
- Player 1: W/S keys
- Player 2: UP/DOWN arrow keys
- SPACE: Start game / Continue
- ESC: Quit game
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import voidray
from voidray import Scene, GameObject, Vector2
from voidray.utils.color import Color
from voidray.physics import RectCollider
import pygame
import math
import random


class Ball(GameObject):
    """Game ball that bounces around the screen."""

    def __init__(self):
        super().__init__("Ball")

        # Ball properties
        self.size = Vector2(15, 15)
        self.velocity = Vector2(0, 0)
        self.base_speed = 350
        self.max_speed = 600

        # Set initial position to center
        self.transform.position = Vector2(400, 300)

        # Add collider
        self.collider = RectCollider(self.size.x, self.size.y)
        self.add_component(self.collider)

        self.reset()

    def reset(self):
        """Reset ball to center with random direction."""
        self.transform.position = Vector2(400, 300)

        # Random direction
        angle = random.uniform(-math.pi/6, math.pi/6)  # 30 degree max angle
        direction = 1 if random.random() > 0.5 else -1

        self.velocity.x = direction * self.base_speed * math.cos(angle)
        self.velocity.y = self.base_speed * math.sin(angle)

    def update(self, delta_time):
        super().update(delta_time)

        # Move ball
        self.transform.position += self.velocity * delta_time

        # Bounce off top and bottom walls
        if self.transform.position.y <= self.size.y/2:
            self.transform.position.y = self.size.y/2
            self.velocity.y = -self.velocity.y

        if self.transform.position.y >= 600 - self.size.y/2:
            self.transform.position.y = 600 - self.size.y/2
            self.velocity.y = -self.velocity.y

    def render(self, renderer):
        # Draw ball as white square
        renderer.draw_rect(
            self.transform.position - self.size/2,
            self.size,
            (255, 255, 255),
            filled=True
        )

    def bounce_off_paddle(self, paddle_y, paddle_height):
        """Bounce off paddle with angle based on hit position."""
        # Calculate hit position relative to paddle center (-1 to 1)
        hit_pos = (self.transform.position.y - paddle_y) / (paddle_height/2)
        hit_pos = max(-1, min(1, hit_pos))

        # Calculate new velocity with angle based on hit position
        speed = self.velocity.magnitude()
        angle = hit_pos * math.pi/3  # Max 60 degree angle

        # Reverse X direction and apply angle
        if self.velocity.x > 0:
            self.velocity.x = -speed * math.cos(angle)
        else:
            self.velocity.x = speed * math.cos(angle)

        self.velocity.y = speed * math.sin(angle)

        # Increase speed slightly
        speed_increase = 1.02
        self.velocity *= speed_increase
        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed


class Paddle(GameObject):
    """Player paddle that moves up and down."""

    def __init__(self, name, x_position, up_key, down_key):
        super().__init__(name)

        # Paddle properties
        self.size = Vector2(15, 80)
        self.speed = 450
        self.up_key = up_key
        self.down_key = down_key

        # Set position
        self.transform.position = Vector2(x_position, 300)

        # Add collider
        self.collider = RectCollider(self.size.x, self.size.y)
        self.add_component(self.collider)

    def update(self, delta_time):
        super().update(delta_time)

        # Get input manager from engine
        engine = voidray.get_engine()
        if not engine or not engine.input_manager:
            return

        input_manager = engine.input_manager

        # Handle movement
        if input_manager.is_key_pressed(self.up_key):
            self.transform.position.y -= self.speed * delta_time
        if input_manager.is_key_pressed(self.down_key):
            self.transform.position.y += self.speed * delta_time

        # Keep paddle on screen
        half_height = self.size.y / 2
        if self.transform.position.y < half_height:
            self.transform.position.y = half_height
        if self.transform.position.y > 600 - half_height:
            self.transform.position.y = 600 - half_height

    def render(self, renderer):
        # Draw paddle as white rectangle
        renderer.draw_rect(
            self.transform.position - self.size/2,
            self.size,
            (255, 255, 255),
            filled=True
        )


class MenuScene(Scene):
    """Main menu scene."""

    def __init__(self):
        super().__init__("MainMenu")
        self.blink_timer = 0
        self.show_text = True

    def update(self, delta_time):
        super().update(delta_time)

        # Blinking text effect
        self.blink_timer += delta_time
        if self.blink_timer >= 0.8:
            self.show_text = not self.show_text
            self.blink_timer = 0

        # Check for input
        engine = voidray.get_engine()
        if engine and engine.input_manager:
            if engine.input_manager.is_key_just_pressed(pygame.K_SPACE):
                voidray.set_scene("gameplay")
            elif engine.input_manager.is_key_just_pressed(pygame.K_ESCAPE):
                engine.stop()

    def render(self, renderer):
        super().render(renderer)

        # Draw title
        self.draw_text(renderer, "PONG", 400, 200, 72, (255, 255, 255))

        # Draw instructions
        self.draw_text(renderer, "Player 1: W/S", 400, 320, 32, (200, 200, 200))
        self.draw_text(renderer, "Player 2: UP/DOWN", 400, 360, 32, (200, 200, 200))

        # Draw start instruction (blinking)
        if self.show_text:
            self.draw_text(renderer, "PRESS SPACE TO START", 400, 450, 36, (255, 255, 0))

        self.draw_text(renderer, "ESC to quit", 400, 520, 24, (150, 150, 150))

    def draw_text(self, renderer, text, x, y, size, color):
        """Draw text centered at position."""
        # Get text size to manually center it
        text_width, text_height = renderer.get_text_size(text, size)
        centered_x = x - text_width // 2
        centered_y = y - text_height // 2

        renderer.draw_text(
            text,
            Vector2(centered_x, centered_y),
            color,
            font_size=size
        )


class GameplayScene(Scene):
    """Main gameplay scene for Pong."""

    def __init__(self):
        super().__init__("PongGameplay")

        # Game objects
        self.player1 = None
        self.player2 = None
        self.ball = None

        # Game state
        self.score1 = 0
        self.score2 = 0
        self.max_score = 5

    def on_enter(self):
        """Called when scene becomes active."""
        super().on_enter()
        self.setup_game()

    def setup_game(self):
        """Setup the game objects."""
        # Create paddles
        self.player1 = Paddle("Player1", 50, pygame.K_w, pygame.K_s)
        self.player2 = Paddle("Player2", 750, pygame.K_UP, pygame.K_DOWN)

        # Create ball
        self.ball = Ball()

        # Add to scene
        self.add_object(self.player1)
        self.add_object(self.player2)
        self.add_object(self.ball)

    def update(self, delta_time):
        super().update(delta_time)

        # Check ball-paddle collisions
        self.check_collisions()

        # Check scoring
        self.check_scoring()

        # Check for quit
        engine = voidray.get_engine()
        if engine and engine.input_manager:
            if engine.input_manager.is_key_just_pressed(pygame.K_ESCAPE):
                voidray.set_scene("menu")

    def check_collisions(self):
        """Check for ball-paddle collisions."""
        ball_rect = pygame.Rect(
            self.ball.transform.position.x - self.ball.size.x/2,
            self.ball.transform.position.y - self.ball.size.y/2,
            self.ball.size.x,
            self.ball.size.y
        )

        # Player 1 paddle collision
        p1_rect = pygame.Rect(
            self.player1.transform.position.x - self.player1.size.x/2,
            self.player1.transform.position.y - self.player1.size.y/2,
            self.player1.size.x,
            self.player1.size.y
        )

        if ball_rect.colliderect(p1_rect) and self.ball.velocity.x < 0:
            self.ball.bounce_off_paddle(
                self.player1.transform.position.y,
                self.player1.size.y
            )
            # Move ball away from paddle to prevent sticking
            self.ball.transform.position.x = self.player1.transform.position.x + self.player1.size.x/2 + self.ball.size.x/2

        # Player 2 paddle collision
        p2_rect = pygame.Rect(
            self.player2.transform.position.x - self.player2.size.x/2,
            self.player2.transform.position.y - self.player2.size.y/2,
            self.player2.size.x,
            self.player2.size.y
        )

        if ball_rect.colliderect(p2_rect) and self.ball.velocity.x > 0:
            self.ball.bounce_off_paddle(
                self.player2.transform.position.y,
                self.player2.size.y
            )
            # Move ball away from paddle to prevent sticking
            self.ball.transform.position.x = self.player2.transform.position.x - self.player2.size.x/2 - self.ball.size.x/2

    def check_scoring(self):
        """Check if someone scored."""
        if self.ball.transform.position.x < 0:
            # Player 2 scores
            self.score2 += 1
            self.ball.reset()
            if self.score2 >= self.max_score:
                voidray.set_scene("gameover")

        elif self.ball.transform.position.x > 800:
            # Player 1 scores
            self.score1 += 1
            self.ball.reset()
            if self.score1 >= self.max_score:
                voidray.set_scene("gameover")

    def render(self, renderer):
        # Call base class render to draw all objects
        super().render(renderer)

        # Draw center line
        for y in range(0, 600, 30):
            renderer.draw_rect(Vector2(395, y), Vector2(10, 15), (100, 100, 100), filled=True)

        # Draw score as simple blocks
        score_y = 50
        # Player 1 score
        for i in range(self.score1):
            renderer.draw_rect(Vector2(300 + i*25, score_y), Vector2(20, 20), (255, 255, 255), filled=True)

        # Player 2 score
        for i in range(self.score2):
            renderer.draw_rect(Vector2(480 + i*25, score_y), Vector2(20, 20), (255, 255, 255), filled=True)

        # Draw score divider
        renderer.draw_rect(Vector2(395, score_y), Vector2(10, 20), (100, 100, 100), filled=True)


class GameOverScene(Scene):
    """Game over scene showing the winner."""

    def __init__(self):
        super().__init__("GameOver")
        self.winner = ""
        self.blink_timer = 0
        self.show_text = True

    def on_enter(self):
        """Determine the winner when entering the scene."""
        super().on_enter()
        # Get the gameplay scene to check scores
        engine = voidray.get_engine()
        if engine and "gameplay" in engine.scenes:
            gameplay_scene = engine.scenes["gameplay"]
            if gameplay_scene.score1 >= gameplay_scene.max_score:
                self.winner = "PLAYER 1 WINS!"
            elif gameplay_scene.score2 >= gameplay_scene.max_score:
                self.winner = "PLAYER 2 WINS!"
            else:
                self.winner = "GAME OVER"

    def update(self, delta_time):
        super().update(delta_time)

        # Blinking text effect
        self.blink_timer += delta_time
        if self.blink_timer >= 0.6:
            self.show_text = not self.show_text
            self.blink_timer = 0

        # Check for input
        engine = voidray.get_engine()
        if engine and engine.input_manager:
            if engine.input_manager.is_key_just_pressed(pygame.K_SPACE):
                # Reset scores and go back to menu
                if "gameplay" in engine.scenes:
                    gameplay_scene = engine.scenes["gameplay"]
                    gameplay_scene.score1 = 0
                    gameplay_scene.score2 = 0
                voidray.set_scene("menu")
            elif engine.input_manager.is_key_just_pressed(pygame.K_ESCAPE):
                engine.stop()

    def render(self, renderer):
        super().render(renderer)

        # Draw winner text (blinking)
        if self.show_text:
            self.draw_text(renderer, self.winner, 400, 250, 48, (255, 255, 0))

        # Draw instructions
        self.draw_text(renderer, "PRESS SPACE FOR MENU", 400, 350, 32, (200, 200, 200))
        self.draw_text(renderer, "ESC to quit", 400, 420, 24, (150, 150, 150))

    def draw_text(self, renderer, text, x, y, size, color):
        """Draw text centered at position."""
        # Get text size to manually center it
        text_width, text_height = renderer.get_text_size(text, size)
        centered_x = x - text_width // 2
        centered_y = y - text_height // 2

        renderer.draw_text(
            text,
            Vector2(centered_x, centered_y),
            color,
            font_size=size
        )


def init_game():
    """Initialize the complete Pong game with all scenes."""
    print("Initializing Complete Pong Game...")

    try:
        # Create all scenes
        menu_scene = MenuScene()
        gameplay_scene = GameplayScene()
        gameover_scene = GameOverScene()

        # Register scenes
        voidray.register_scene("menu", menu_scene)
        voidray.register_scene("gameplay", gameplay_scene)
        voidray.register_scene("gameover", gameover_scene)

        # Start with menu
        voidray.set_scene("menu")

        print("✓ Complete Pong game initialized successfully!")

    except Exception as e:
        print(f"❌ Error during game initialization: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    print("🎮 VoidRay Engine - Complete Pong Game")
    print("=====================================")

    try:
        # Configure the engine
        engine = voidray.configure(
            width=800, 
            height=600, 
            title="Complete Pong Game", 
            fps=60
        )

        # Register initialization callback
        voidray.on_init(init_game)

        # Start the engine
        voidray.start()

    except Exception as e:
        print(f"❌ Error running Pong game: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()