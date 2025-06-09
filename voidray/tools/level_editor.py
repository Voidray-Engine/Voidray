
"""
VoidRay Level Editor
Visual editor for creating 2.5D levels.
"""

import pygame
from typing import List, Dict, Any, Optional, Tuple
from ..math.vector2 import Vector2
from ..utils.color import Color


class LevelEditor:
    """
    Visual level editor for creating 2.5D levels.
    """
    
    def __init__(self, width: int = 1024, height: int = 768):
        """
        Initialize the level editor.
        
        Args:
            width: Editor window width
            height: Editor window height
        """
        self.width = width
        self.height = height
        self.running = False
        
        # Editor state
        self.walls: List[Dict[str, Any]] = []
        self.lights: List[Dict[str, Any]] = []
        self.sprites: List[Dict[str, Any]] = []
        
        # Tool state
        self.current_tool = "wall"  # wall, light, sprite, select
        self.wall_start = None
        self.selected_object = None
        
        # Grid
        self.grid_size = 32
        self.show_grid = True
        
        # Camera
        self.camera_offset = Vector2(0, 0)
        self.zoom = 1.0
        
        # UI
        self.font = None
        
    def init_pygame(self):
        """Initialize pygame for the editor."""
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("VoidRay Level Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
    def run(self):
        """Run the level editor."""
        self.init_pygame()
        self.running = True
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.render()
            
        pygame.quit()
    
    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_1:
                    self.current_tool = "wall"
                elif event.key == pygame.K_2:
                    self.current_tool = "light"
                elif event.key == pygame.K_3:
                    self.current_tool = "sprite"
                elif event.key == pygame.K_4:
                    self.current_tool = "select"
                elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.save_level()
                elif event.key == pygame.K_o and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.load_level()
                elif event.key == pygame.K_n and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.new_level()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_left_click(event.pos)
                elif event.button == 3:  # Right click
                    self.handle_right_click(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.current_tool == "wall" and self.wall_start:
                    self.finish_wall(event.pos)
    
    def handle_left_click(self, pos: Tuple[int, int]):
        """Handle left mouse click."""
        world_pos = self.screen_to_world(Vector2(pos[0], pos[1]))
        grid_pos = self.snap_to_grid(world_pos)
        
        if self.current_tool == "wall":
            if self.wall_start is None:
                self.wall_start = grid_pos
            else:
                self.add_wall(self.wall_start, grid_pos)
                self.wall_start = None
        
        elif self.current_tool == "light":
            self.add_light(grid_pos)
        
        elif self.current_tool == "sprite":
            self.add_sprite(grid_pos)
    
    def handle_right_click(self, pos: Tuple[int, int]):
        """Handle right mouse click."""
        if self.current_tool == "wall" and self.wall_start:
            self.wall_start = None
    
    def finish_wall(self, pos: Tuple[int, int]):
        """Finish placing a wall."""
        if self.wall_start:
            world_pos = self.screen_to_world(Vector2(pos[0], pos[1]))
            grid_pos = self.snap_to_grid(world_pos)
            self.add_wall(self.wall_start, grid_pos)
            self.wall_start = None
    
    def add_wall(self, start: Vector2, end: Vector2):
        """Add a wall to the level."""
        wall = {
            "start": {"x": start.x, "y": start.y},
            "end": {"x": end.x, "y": end.y},
            "texture": "brick",
            "height": 64
        }
        self.walls.append(wall)
    
    def add_light(self, position: Vector2):
        """Add a light to the level."""
        light = {
            "x": position.x,
            "y": position.y,
            "intensity": 1.0,
            "radius": 100.0,
            "color": [255, 255, 200]
        }
        self.lights.append(light)
    
    def add_sprite(self, position: Vector2):
        """Add a sprite to the level."""
        sprite = {
            "x": position.x,
            "y": position.y,
            "texture": "default",
            "scale": 1.0
        }
        self.sprites.append(sprite)
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """Convert screen coordinates to world coordinates."""
        return (screen_pos - self.camera_offset) / self.zoom
    
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """Convert world coordinates to screen coordinates."""
        return world_pos * self.zoom + self.camera_offset
    
    def snap_to_grid(self, pos: Vector2) -> Vector2:
        """Snap position to grid."""
        if self.show_grid:
            x = round(pos.x / self.grid_size) * self.grid_size
            y = round(pos.y / self.grid_size) * self.grid_size
            return Vector2(x, y)
        return pos
    
    def update(self, delta_time: float):
        """Update editor state."""
        # Handle camera movement
        keys = pygame.key.get_pressed()
        camera_speed = 300
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera_offset.x += camera_speed * delta_time
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_offset.x -= camera_speed * delta_time
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera_offset.y += camera_speed * delta_time
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_offset.y -= camera_speed * delta_time
    
    def render(self):
        """Render the editor."""
        self.screen.fill((50, 50, 50))
        
        # Draw grid
        if self.show_grid:
            self.draw_grid()
        
        # Draw level objects
        self.draw_walls()
        self.draw_lights()
        self.draw_sprites()
        
        # Draw current tool preview
        if self.current_tool == "wall" and self.wall_start:
            mouse_pos = pygame.mouse.get_pos()
            world_pos = self.screen_to_world(Vector2(mouse_pos[0], mouse_pos[1]))
            grid_pos = self.snap_to_grid(world_pos)
            self.draw_wall_preview(self.wall_start, grid_pos)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_grid(self):
        """Draw the grid."""
        for x in range(0, self.width, self.grid_size):
            start = self.world_to_screen(Vector2(x, 0))
            end = self.world_to_screen(Vector2(x, self.height))
            pygame.draw.line(self.screen, (70, 70, 70), start.tuple(), end.tuple())
        
        for y in range(0, self.height, self.grid_size):
            start = self.world_to_screen(Vector2(0, y))
            end = self.world_to_screen(Vector2(self.width, y))
            pygame.draw.line(self.screen, (70, 70, 70), start.tuple(), end.tuple())
    
    def draw_walls(self):
        """Draw all walls."""
        for wall in self.walls:
            start = Vector2(wall["start"]["x"], wall["start"]["y"])
            end = Vector2(wall["end"]["x"], wall["end"]["y"])
            
            screen_start = self.world_to_screen(start)
            screen_end = self.world_to_screen(end)
            
            pygame.draw.line(self.screen, (255, 255, 255), 
                           screen_start.tuple(), screen_end.tuple(), 3)
    
    def draw_lights(self):
        """Draw all lights."""
        for light in self.lights:
            pos = Vector2(light["x"], light["y"])
            screen_pos = self.world_to_screen(pos)
            
            pygame.draw.circle(self.screen, (255, 255, 0), 
                             screen_pos.tuple(), 8)
    
    def draw_sprites(self):
        """Draw all sprites."""
        for sprite in self.sprites:
            pos = Vector2(sprite["x"], sprite["y"])
            screen_pos = self.world_to_screen(pos)
            
            pygame.draw.rect(self.screen, (0, 255, 0),
                           (screen_pos.x - 8, screen_pos.y - 8, 16, 16))
    
    def draw_wall_preview(self, start: Vector2, end: Vector2):
        """Draw wall preview while placing."""
        screen_start = self.world_to_screen(start)
        screen_end = self.world_to_screen(end)
        
        pygame.draw.line(self.screen, (128, 128, 128), 
                       screen_start.tuple(), screen_end.tuple(), 2)
    
    def draw_ui(self):
        """Draw the user interface."""
        # Tool info
        tool_text = f"Tool: {self.current_tool.title()}"
        text_surface = self.font.render(tool_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))
        
        # Instructions
        instructions = [
            "1: Wall Tool",
            "2: Light Tool", 
            "3: Sprite Tool",
            "4: Select Tool",
            "G: Toggle Grid",
            "Ctrl+S: Save",
            "Ctrl+O: Open",
            "Ctrl+N: New"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = self.font.render(instruction, True, (200, 200, 200))
            self.screen.blit(text_surface, (10, 40 + i * 20))
    
    def save_level(self, filename: str = "level.json"):
        """Save the current level."""
        import json
        
        level_data = {
            "name": "custom_level",
            "walls": self.walls,
            "lights": self.lights,
            "sprites": self.sprites
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(level_data, f, indent=2)
            print(f"Level saved to {filename}")
        except Exception as e:
            print(f"Error saving level: {e}")
    
    def load_level(self, filename: str = "level.json"):
        """Load a level from file."""
        import json
        
        try:
            with open(filename, 'r') as f:
                level_data = json.load(f)
            
            self.walls = level_data.get("walls", [])
            self.lights = level_data.get("lights", [])
            self.sprites = level_data.get("sprites", [])
            
            print(f"Level loaded from {filename}")
        except Exception as e:
            print(f"Error loading level: {e}")
    
    def new_level(self):
        """Create a new empty level."""
        self.walls.clear()
        self.lights.clear()
        self.sprites.clear()
        print("New level created")


if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
