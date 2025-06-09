
"""
VoidRay Project Templates
Templates for quickly starting new game projects.
"""

import os
import json
from typing import Dict, Any


class ProjectTemplate:
    """
    Base class for project templates.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def create_project(self, project_path: str, **kwargs):
        """
        Create a new project from this template.
        
        Args:
            project_path: Path to create the project
            **kwargs: Template-specific parameters
        """
        raise NotImplementedError


class PlatformerTemplate(ProjectTemplate):
    """Template for a 2D platformer game."""
    
    def __init__(self):
        super().__init__("Platformer", "2D side-scrolling platformer game")
    
    def create_project(self, project_path: str, **kwargs):
        """Create a platformer project."""
        os.makedirs(project_path, exist_ok=True)
        
        # Create main.py
        main_content = '''import voidray
from voidray import Scene, GameObject, Sprite, Vector2, Keys

class Player(Sprite):
    def __init__(self):
        super().__init__("Player")
        self.create_colored_rect(32, 32, (0, 100, 255))
        self.speed = 200
        self.jump_strength = 400
        
    def update(self, delta_time):
        super().update(delta_time)
        
        engine = voidray.get_engine()
        velocity = Vector2.zero()
        
        if engine.input_manager.is_key_pressed(Keys.LEFT):
            velocity.x = -self.speed
        if engine.input_manager.is_key_pressed(Keys.RIGHT):
            velocity.x = self.speed
        if engine.input_manager.is_key_just_pressed(Keys.SPACE):
            velocity.y = -self.jump_strength
            
        self.transform.position += velocity * delta_time

class GameScene(Scene):
    def __init__(self):
        super().__init__("Game")
        
    def on_enter(self):
        super().on_enter()
        player = Player()
        player.transform.position = Vector2(400, 300)
        self.add_object(player)

def main():
    voidray.configure(800, 600, "My Platformer Game")
    
    scene = GameScene()
    voidray.register_scene("game", scene)
    voidray.set_scene("game")
    
    voidray.start()

if __name__ == "__main__":
    main()
'''
        
        with open(os.path.join(project_path, "main.py"), 'w') as f:
            f.write(main_content)
        
        print(f"Platformer project created at {project_path}")


class ShooterTemplate(ProjectTemplate):
    """Template for a top-down shooter game."""
    
    def __init__(self):
        super().__init__("Shooter", "Top-down space shooter game")
    
    def create_project(self, project_path: str, **kwargs):
        """Create a shooter project."""
        os.makedirs(project_path, exist_ok=True)
        
        # Create main.py
        main_content = '''import voidray
from voidray import Scene, GameObject, Sprite, Vector2, Keys
import random

class Player(Sprite):
    def __init__(self):
        super().__init__("Player")
        self.create_colored_triangle(20, (0, 255, 0))
        self.speed = 300
        
    def update(self, delta_time):
        super().update(delta_time)
        
        engine = voidray.get_engine()
        velocity = Vector2.zero()
        
        if engine.input_manager.is_key_pressed(Keys.W):
            velocity.y = -self.speed
        if engine.input_manager.is_key_pressed(Keys.S):
            velocity.y = self.speed
        if engine.input_manager.is_key_pressed(Keys.A):
            velocity.x = -self.speed
        if engine.input_manager.is_key_pressed(Keys.D):
            velocity.x = self.speed
            
        self.transform.position += velocity * delta_time

class GameScene(Scene):
    def __init__(self):
        super().__init__("Game")
        
    def on_enter(self):
        super().on_enter()
        player = Player()
        player.transform.position = Vector2(400, 300)
        self.add_object(player)

def main():
    voidray.configure(800, 600, "My Shooter Game")
    
    scene = GameScene()
    voidray.register_scene("game", scene)
    voidray.set_scene("game")
    
    voidray.start()

if __name__ == "__main__":
    main()
'''
        
        with open(os.path.join(project_path, "main.py"), 'w') as f:
            f.write(main_content)
        
        print(f"Shooter project created at {project_path}")


class ProjectTemplateManager:
    """Manages project templates."""
    
    def __init__(self):
        self.templates = {
            "platformer": PlatformerTemplate(),
            "shooter": ShooterTemplate()
        }
    
    def get_template(self, name: str) -> ProjectTemplate:
        """Get a template by name."""
        return self.templates.get(name)
    
    def list_templates(self):
        """List all available templates."""
        for name, template in self.templates.items():
            print(f"{name}: {template.description}")
    
    def create_project(self, template_name: str, project_path: str, **kwargs):
        """Create a project from a template."""
        template = self.get_template(template_name)
        if template:
            template.create_project(project_path, **kwargs)
        else:
            print(f"Template '{template_name}' not found")


# Global template manager
template_manager = ProjectTemplateManager()
