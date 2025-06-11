
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
"""
VoidRay Level Editor
Advanced level editing tools for creating game worlds.
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any
from ..math.vector2 import Vector2
from ..tilemap.tilemap_system import Tilemap, TileLayer
from ..input.input_manager import InputManager, Keys, MouseButtons


class LevelEditor:
    """
    Advanced level editor with multi-layer support, undo/redo, and real-time preview.
    """
    
    def __init__(self, renderer, input_manager: InputManager):
        self.renderer = renderer
        self.input_manager = input_manager
        
        # Editor state
        self.active = False
        self.current_tilemap: Optional[Tilemap] = None
        self.current_layer = 0
        self.selected_tile_id = 1
        
        # Tools
        self.current_tool = "paint"  # paint, erase, fill, select, move
        self.brush_size = 1
        
        # Camera/viewport
        self.camera_position = Vector2.zero()
        self.zoom_level = 1.0
        self.grid_visible = True
        
        # Selection
        self.selection_start: Optional[Vector2] = None
        self.selection_end: Optional[Vector2] = None
        self.clipboard: List[List[int]] = []
        
        # Undo/Redo system
        self.history: List[Dict[str, Any]] = []
        self.history_index = -1
        self.max_history = 50
        
        # UI
        self.ui_panels = {
            'tileset': {'visible': True, 'position': Vector2(10, 10), 'size': Vector2(200, 300)},
            'layers': {'visible': True, 'position': Vector2(220, 10), 'size': Vector2(150, 200)},
            'properties': {'visible': True, 'position': Vector2(380, 10), 'size': Vector2(200, 150)}
        }
        
        # Performance
        self.dirty_regions: List[Tuple[int, int, int, int]] = []
        self.last_paint_pos: Optional[Vector2] = None
    
    def activate(self, tilemap: Tilemap):
        """Activate the level editor with a tilemap."""
        self.active = True
        self.current_tilemap = tilemap
        self.camera_position = Vector2.zero()
        self.zoom_level = 1.0
        print("Level Editor activated")
    
    def deactivate(self):
        """Deactivate the level editor."""
        self.active = False
        self.current_tilemap = None
        print("Level Editor deactivated")
    
    def update(self, delta_time: float):
        """Update the level editor."""
        if not self.active or not self.current_tilemap:
            return
        
        self._handle_input()
        self._update_camera(delta_time)
    
    def _handle_input(self):
        """Handle editor input."""
        # Tool switching
        if self.input_manager.is_key_just_pressed(Keys.NUM_1):
            self.current_tool = "paint"
        elif self.input_manager.is_key_just_pressed(Keys.NUM_2):
            self.current_tool = "erase"
        elif self.input_manager.is_key_just_pressed(Keys.NUM_3):
            self.current_tool = "fill"
        elif self.input_manager.is_key_just_pressed(Keys.NUM_4):
            self.current_tool = "select"
        
        # Undo/Redo
        if self.input_manager.is_key_pressed(Keys.CTRL):
            if self.input_manager.is_key_just_pressed(Keys.Z):
                self.undo()
            elif self.input_manager.is_key_just_pressed(Keys.Y):
                self.redo()
        
        # Layer switching
        if self.input_manager.is_key_just_pressed(Keys.UP):
            self.change_layer(1)
        elif self.input_manager.is_key_just_pressed(Keys.DOWN):
            self.change_layer(-1)
        
        # Mouse input
        mouse_pos = self.input_manager.get_mouse_position()
        world_pos = self.screen_to_world(mouse_pos)
        tile_pos = self.world_to_tile(world_pos)
        
        if self.input_manager.is_mouse_button_pressed(MouseButtons.LEFT):
            self._handle_mouse_action(tile_pos, True)
        elif self.input_manager.is_mouse_button_pressed(MouseButtons.RIGHT):
            self._handle_mouse_action(tile_pos, False)
    
    def _handle_mouse_action(self, tile_pos: Vector2, primary: bool):
        """Handle mouse actions on tiles."""
        if not self.current_tilemap:
            return
        
        layer = self.get_current_layer()
        if not layer:
            return
        
        tile_x, tile_y = int(tile_pos.x), int(tile_pos.y)
        
        if self.current_tool == "paint" and primary:
            self._paint_tile(layer, tile_x, tile_y, self.selected_tile_id)
        elif self.current_tool == "erase" or (self.current_tool == "paint" and not primary):
            self._paint_tile(layer, tile_x, tile_y, None)
        elif self.current_tool == "fill" and primary:
            self._flood_fill(layer, tile_x, tile_y, self.selected_tile_id)
        elif self.current_tool == "select":
            self._handle_selection(tile_pos, primary)
    
    def _paint_tile(self, layer: TileLayer, x: int, y: int, tile_id: Optional[int]):
        """Paint a single tile."""
        if not (0 <= x < layer.width and 0 <= y < layer.height):
            return
        
        # Check if we need to record this action
        current_pos = Vector2(x, y)
        if self.last_paint_pos != current_pos:
            self._record_action("paint", layer, x, y, layer.get_tile(x, y), tile_id)
        
        # Set the tile
        tile = self.current_tilemap.tileset.get(tile_id) if tile_id else None
        layer.set_tile(x, y, tile)
        
        # Mark region as dirty
        self._mark_dirty_region(x, y, 1, 1)
        self.last_paint_pos = current_pos
    
    def _flood_fill(self, layer: TileLayer, start_x: int, start_y: int, new_tile_id: int):
        """Flood fill algorithm for painting areas."""
        if not (0 <= start_x < layer.width and 0 <= start_y < layer.height):
            return
        
        start_tile = layer.get_tile(start_x, start_y)
        start_tile_id = start_tile.tile_id if start_tile else None
        
        if start_tile_id == new_tile_id:
            return
        
        # Record action for undo
        affected_tiles = []
        
        # Flood fill using stack
        stack = [(start_x, start_y)]
        visited = set()
        
        while stack:
            x, y = stack.pop()
            
            if (x, y) in visited or not (0 <= x < layer.width and 0 <= y < layer.height):
                continue
            
            current_tile = layer.get_tile(x, y)
            current_tile_id = current_tile.tile_id if current_tile else None
            
            if current_tile_id != start_tile_id:
                continue
            
            visited.add((x, y))
            affected_tiles.append((x, y, current_tile, new_tile_id))
            
            # Set new tile
            tile = self.current_tilemap.tileset.get(new_tile_id)
            layer.set_tile(x, y, tile)
            
            # Add neighbors
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                stack.append((x + dx, y + dy))
        
        # Record for undo
        if affected_tiles:
            self._record_action("flood_fill", layer, affected_tiles=affected_tiles)
            
            # Mark dirty regions
            min_x = min(tile[0] for tile in affected_tiles)
            max_x = max(tile[0] for tile in affected_tiles)
            min_y = min(tile[1] for tile in affected_tiles)
            max_y = max(tile[1] for tile in affected_tiles)
            self._mark_dirty_region(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    
    def _record_action(self, action_type: str, layer: TileLayer, x: int = 0, y: int = 0, 
                      old_tile=None, new_tile_id=None, **kwargs):
        """Record an action for undo/redo."""
        action = {
            'type': action_type,
            'layer': layer,
            'x': x,
            'y': y,
            'old_tile': old_tile,
            'new_tile_id': new_tile_id,
            **kwargs
        }
        
        # Remove future history if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # Add new action
        self.history.append(action)
        self.history_index += 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
    
    def undo(self):
        """Undo the last action."""
        if self.history_index >= 0:
            action = self.history[self.history_index]
            self._revert_action(action)
            self.history_index -= 1
            print("Undo")
    
    def redo(self):
        """Redo the next action."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            action = self.history[self.history_index]
            self._apply_action(action)
            print("Redo")
    
    def _revert_action(self, action: Dict[str, Any]):
        """Revert a recorded action."""
        if action['type'] == "paint":
            layer = action['layer']
            layer.set_tile(action['x'], action['y'], action['old_tile'])
            self._mark_dirty_region(action['x'], action['y'], 1, 1)
        
        elif action['type'] == "flood_fill":
            for x, y, old_tile, _ in action['affected_tiles']:
                action['layer'].set_tile(x, y, old_tile)
    
    def _apply_action(self, action: Dict[str, Any]):
        """Apply a recorded action."""
        if action['type'] == "paint":
            layer = action['layer']
            tile = self.current_tilemap.tileset.get(action['new_tile_id']) if action['new_tile_id'] else None
            layer.set_tile(action['x'], action['y'], tile)
            self._mark_dirty_region(action['x'], action['y'], 1, 1)
        
        elif action['type'] == "flood_fill":
            for x, y, _, new_tile_id in action['affected_tiles']:
                tile = self.current_tilemap.tileset.get(new_tile_id)
                action['layer'].set_tile(x, y, tile)
    
    def get_current_layer(self) -> Optional[TileLayer]:
        """Get the currently selected layer."""
        if self.current_tilemap and 0 <= self.current_layer < len(self.current_tilemap.layers):
            return self.current_tilemap.layers[self.current_layer]
        return None
    
    def change_layer(self, direction: int):
        """Change the active layer."""
        if self.current_tilemap:
            new_layer = self.current_layer + direction
            if 0 <= new_layer < len(self.current_tilemap.layers):
                self.current_layer = new_layer
                print(f"Switched to layer {self.current_layer}")
    
    def world_to_tile(self, world_pos: Vector2) -> Vector2:
        """Convert world position to tile coordinates."""
        if self.current_tilemap:
            return self.current_tilemap.world_to_tile(world_pos)
        return Vector2.zero()
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """Convert screen position to world coordinates."""
        return (screen_pos / self.zoom_level) + self.camera_position
    
    def _update_camera(self, delta_time: float):
        """Update camera movement."""
        move_speed = 300.0 / self.zoom_level
        
        if self.input_manager.is_key_pressed(Keys.A):
            self.camera_position.x -= move_speed * delta_time
        if self.input_manager.is_key_pressed(Keys.D):
            self.camera_position.x += move_speed * delta_time
        if self.input_manager.is_key_pressed(Keys.W):
            self.camera_position.y -= move_speed * delta_time
        if self.input_manager.is_key_pressed(Keys.S):
            self.camera_position.y += move_speed * delta_time
        
        # Zoom
        wheel_delta = self.input_manager.get_mouse_wheel_delta()
        if wheel_delta != 0:
            zoom_factor = 1.1 if wheel_delta > 0 else 0.9
            self.zoom_level = max(0.1, min(5.0, self.zoom_level * zoom_factor))
    
    def _mark_dirty_region(self, x: int, y: int, width: int, height: int):
        """Mark a region as dirty for optimized rendering."""
        self.dirty_regions.append((x, y, width, height))
    
    def render(self):
        """Render the level editor."""
        if not self.active or not self.current_tilemap:
            return
        
        # Render tilemap layers
        self._render_tilemap()
        
        # Render grid
        if self.grid_visible:
            self._render_grid()
        
        # Render selection
        self._render_selection()
        
        # Render cursor
        self._render_cursor()
        
        # Render UI
        self._render_ui()
    
    def _render_tilemap(self):
        """Render the tilemap with editor-specific features."""
        # Render layers with transparency for non-active layers
        for i, layer in enumerate(self.current_tilemap.layers):
            alpha = 255 if i == self.current_layer else 128
            # Render layer with modified alpha...
    
    def _render_grid(self):
        """Render the tile grid."""
        if not self.current_tilemap:
            return
        
        # Calculate visible tile range
        screen_bounds = pygame.Rect(0, 0, self.renderer.width, self.renderer.height)
        world_bounds = pygame.Rect(
            self.camera_position.x,
            self.camera_position.y,
            screen_bounds.width / self.zoom_level,
            screen_bounds.height / self.zoom_level
        )
        
        tile_width = self.current_tilemap.tile_width
        tile_height = self.current_tilemap.tile_height
        
        start_x = int(world_bounds.left // tile_width)
        end_x = int(world_bounds.right // tile_width) + 1
        start_y = int(world_bounds.top // tile_height)
        end_y = int(world_bounds.bottom // tile_height) + 1
        
        # Draw grid lines
        grid_color = (100, 100, 100)
        for x in range(start_x, end_x + 1):
            screen_x = (x * tile_width - self.camera_position.x) * self.zoom_level
            pygame.draw.line(self.renderer.screen, grid_color, 
                           (screen_x, 0), (screen_x, self.renderer.height))
        
        for y in range(start_y, end_y + 1):
            screen_y = (y * tile_height - self.camera_position.y) * self.zoom_level
            pygame.draw.line(self.renderer.screen, grid_color, 
                           (0, screen_y), (self.renderer.width, screen_y))
    
    def _render_cursor(self):
        """Render the cursor/brush preview."""
        mouse_pos = self.input_manager.get_mouse_position()
        world_pos = self.screen_to_world(mouse_pos)
        tile_pos = self.world_to_tile(world_pos)
        
        if self.current_tilemap:
            tile_x, tile_y = int(tile_pos.x), int(tile_pos.y)
            screen_x = (tile_x * self.current_tilemap.tile_width - self.camera_position.x) * self.zoom_level
            screen_y = (tile_y * self.current_tilemap.tile_height - self.camera_position.y) * self.zoom_level
            
            # Draw cursor rectangle
            cursor_color = (255, 255, 0) if self.current_tool == "paint" else (255, 0, 0)
            cursor_rect = pygame.Rect(
                screen_x, screen_y,
                self.current_tilemap.tile_width * self.zoom_level,
                self.current_tilemap.tile_height * self.zoom_level
            )
            pygame.draw.rect(self.renderer.screen, cursor_color, cursor_rect, 2)
    
    def _render_selection(self):
        """Render selection area."""
        if self.selection_start and self.selection_end:
            # Draw selection rectangle
            pass
    
    def _render_ui(self):
        """Render editor UI panels."""
        # Render tileset panel
        if self.ui_panels['tileset']['visible']:
            self._render_tileset_panel()
        
        # Render layers panel
        if self.ui_panels['layers']['visible']:
            self._render_layers_panel()
        
        # Render properties panel
        if self.ui_panels['properties']['visible']:
            self._render_properties_panel()
    
    def _render_tileset_panel(self):
        """Render the tileset selection panel."""
        panel = self.ui_panels['tileset']
        pos = panel['position']
        size = panel['size']
        
        # Draw panel background
        panel_rect = pygame.Rect(pos.x, pos.y, size.x, size.y)
        pygame.draw.rect(self.renderer.screen, (50, 50, 50), panel_rect)
        pygame.draw.rect(self.renderer.screen, (100, 100, 100), panel_rect, 2)
        
        # Draw tileset tiles
        if self.current_tilemap:
            tile_size = 32
            cols = int(size.x // tile_size) - 1
            
            for tile_id, tile in self.current_tilemap.tileset.items():
                if tile.surface:
                    col = (tile_id - 1) % cols
                    row = (tile_id - 1) // cols
                    
                    tile_x = pos.x + 10 + col * tile_size
                    tile_y = pos.y + 30 + row * tile_size
                    
                    # Scale tile to fit
                    scaled_surface = pygame.transform.scale(tile.surface, (tile_size, tile_size))
                    self.renderer.screen.blit(scaled_surface, (tile_x, tile_y))
                    
                    # Highlight selected tile
                    if tile_id == self.selected_tile_id:
                        highlight_rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)
                        pygame.draw.rect(self.renderer.screen, (255, 255, 0), highlight_rect, 2)
    
    def _render_layers_panel(self):
        """Render the layers panel."""
        panel = self.ui_panels['layers']
        pos = panel['position']
        size = panel['size']
        
        # Draw panel background
        panel_rect = pygame.Rect(pos.x, pos.y, size.x, size.y)
        pygame.draw.rect(self.renderer.screen, (50, 50, 50), panel_rect)
        pygame.draw.rect(self.renderer.screen, (100, 100, 100), panel_rect, 2)
        
        # Draw layer list
        if self.current_tilemap:
            font = pygame.font.Font(None, 24)
            for i, layer in enumerate(self.current_tilemap.layers):
                y_offset = pos.y + 30 + i * 25
                
                # Highlight current layer
                if i == self.current_layer:
                    highlight_rect = pygame.Rect(pos.x + 5, y_offset - 2, size.x - 10, 20)
                    pygame.draw.rect(self.renderer.screen, (80, 80, 120), highlight_rect)
                
                # Draw layer name
                text_color = (255, 255, 255) if layer.visible else (128, 128, 128)
                text = font.render(layer.name, True, text_color)
                self.renderer.screen.blit(text, (pos.x + 10, y_offset))
    
    def _render_properties_panel(self):
        """Render the properties panel."""
        panel = self.ui_panels['properties']
        pos = panel['position']
        size = panel['size']
        
        # Draw panel background
        panel_rect = pygame.Rect(pos.x, pos.y, size.x, size.y)
        pygame.draw.rect(self.renderer.screen, (50, 50, 50), panel_rect)
        pygame.draw.rect(self.renderer.screen, (100, 100, 100), panel_rect, 2)
        
        # Draw properties
        font = pygame.font.Font(None, 20)
        y_offset = pos.y + 25
        
        properties = [
            f"Tool: {self.current_tool}",
            f"Layer: {self.current_layer}",
            f"Tile: {self.selected_tile_id}",
            f"Zoom: {self.zoom_level:.1f}x",
            f"Pos: ({int(self.camera_position.x)}, {int(self.camera_position.y)})"
        ]
        
        for prop in properties:
            text = font.render(prop, True, (255, 255, 255))
            self.renderer.screen.blit(text, (pos.x + 10, y_offset))
            y_offset += 20
