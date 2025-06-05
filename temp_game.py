"""
VoidRay Game Template
Create your game here!
"""

import voidray
from voidray import Scene, GameObject, Sprite, Vector2, Keys
from voidray.graphics.renderer import Color


class Player(Sprite):
    """A simple player that can move around."""
    
    def __init__(self):
        super().__init__("Player")
        self.create_colored_rect(40, 40, Color.BLUE)
        self.speed = 300
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Get input
        input_manager = voidray.get_engine().input_manager
        
        # Move the player
        velocity = Vector2.zero()
        if input_manager.is_key_pressed(Keys.LEFT):
            velocity.x = -self.speed
        if input_manager.is_key_pressed(Keys.RIGHT):
            velocity.x = self.speed
        if input_manager.is_key_pressed(Keys.UP):
            velocity.y = -self.speed
        if input_manager.is_key_pressed(Keys.DOWN):
            velocity.y = self.speed
            
        self.transform.position += velocity * delta_time


class GameScene(Scene):
    """Main game scene."""
    
    def __init__(self):
        super().__init__("Game")
        
    def on_enter(self):
        super().on_enter()
        
        # Create player
        self.player = Player()
        self.player.transform.position = Vector2(400, 300)
        self.add_object(self.player)
        
        print("Game scene started - Use arrow keys to move!")
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check for exit
        input_manager = voidray.get_engine().input_manager
        if input_manager.is_key_just_pressed(Keys.ESCAPE):
            voidray.stop()


def init_game():
    """Initialize the game."""
    scene = GameScene()
    voidray.register_scene("game", scene)
    voidray.set_scene("game")


def main():
    """Main entry point."""
    voidray.configure(width=800, height=600, title="My VoidRay Game", fps=60)
    voidray.on_init(init_game)
    voidray.start()


if __name__ == "__main__":
    main()

