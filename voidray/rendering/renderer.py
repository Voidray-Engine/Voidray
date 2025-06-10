"""
VoidRay 2D Renderer
rendering system with texture mapping, raycasting, and advanced visual effects.
"""

import pygame
import math
import numpy as np
from typing import Optional, Tuple, List, Dict, Union
from ..math.vector2 import Vector2
from ..utils.color import Color


class TextureAtlas:
    """Manages texture atlases for efficient rendering."""

    def __init__(self):
        self.textures: Dict[str, pygame.Surface] = {}
        self.texture_coords: Dict[str, Tuple[int, int, int, int]] = {}
        self.atlas_surface: Optional[pygame.Surface] = None

    def add_texture(self, name: str, surface: pygame.Surface):
        """Add a texture to the atlas."""
        self.textures[name] = surface

    def get_texture(self, name: str) -> Optional[pygame.Surface]:
        """Get a texture by name."""
        return self.textures.get(name)


class Wall:
    """Represents a wall segment for raycasting."""

    def __init__(self, start: Vector2, end: Vector2, texture_name: str = None, height: float = 1.0):
        self.start = start
        self.end = end
        self.texture_name = texture_name
        self.height = height
        self.length = (end - start).magnitude()
        self.normal = self._calculate_normal()

    def _calculate_normal(self) -> Vector2:
        """Calculate the wall's normal vector."""
        direction = self.end - self.start
        return Vector2(-direction.y, direction.x).normalized()


class Sector:
    """Represents a sector in DOOM-style rendering."""

    def __init__(self, floor_height: float = 0, ceiling_height: float = 1, 
                 floor_texture: str = None, ceiling_texture: str = None):
        self.floor_height = floor_height
        self.ceiling_height = ceiling_height
        self.floor_texture = floor_texture
        self.ceiling_texture = ceiling_texture
        self.walls: List[Wall] = []
        self.vertices: List[Vector2] = []

    def add_wall(self, wall: Wall):
        """Add a wall to this sector."""
        self.walls.append(wall)


class Advanced2DRenderer:
    """
    Advanced 2.5D renderer supporting DOOM-style rendering with textures.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.camera_offset = Vector2(0, 0)
        self.background_color = Color.BLACK

        # 2.5D rendering properties
        self.camera_height = 32.0
        self.camera_pitch = 0.0
        self.field_of_view = 60.0
        self.render_distance = 1000.0
        self.fog_distance = 500.0

        # Texture management
        self.texture_atlas = TextureAtlas()
        self.sprite_textures: Dict[str, pygame.Surface] = {}

        # Rendering buffers
        self.z_buffer = np.full(self.width, float('inf'))
        self.floor_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.wall_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # World geometry
        self.sectors: List[Sector] = []
        self.walls: List[Wall] = []

        # Lighting system
        self.ambient_light = 0.3
        self.light_sources: List[Dict] = []

        # Effects
        self.enable_fog = True
        self.enable_lighting = True
        self.enable_shadows = True

        print("Advanced 2.5D renderer initialized")
        
        # Disable debug rendering by default
        self.debug_mode = False
        self.show_debug_cubes = False

    def clear(self, color: Optional[Tuple[int, int, int]] = None):
        """Clear the screen and buffers."""
        if color is None:
            color = self.background_color
        self.screen.fill(color)
        self.z_buffer.fill(float('inf'))
        self.floor_buffer.fill(0)
        self.wall_buffer.fill(0)

    def present(self):
        """Present the rendered frame."""
        pygame.display.flip()

    def load_texture(self, name: str, image_path: str) -> bool:
        """Load a texture for 2.5D rendering."""
        try:
            surface = pygame.image.load(image_path).convert_alpha()
            self.texture_atlas.add_texture(name, surface)
            print(f"Loaded texture: {name}")
            return True
        except pygame.error as e:
            print(f"Failed to load texture {name}: {e}")
            return False

    def create_procedural_texture(self, name: str, width: int, height: int, 
                                pattern: str = "brick") -> pygame.Surface:
        """Create procedural textures for testing."""
        surface = pygame.Surface((width, height))

        if pattern == "brick":
            # Create brick pattern
            brick_width = width // 8
            brick_height = height // 4

            for y in range(0, height, brick_height):
                offset = (brick_width // 2) if (y // brick_height) % 2 else 0
                for x in range(-offset, width + offset, brick_width):
                    rect = pygame.Rect(x, y, brick_width - 2, brick_height - 2)
                    color = (180 + (x + y) % 40, 100 + (x + y) % 30, 80)
                    pygame.draw.rect(surface, color, rect)

        elif pattern == "stone":
            # Create stone pattern
            for y in range(height):
                for x in range(width):
                    noise = (x * 7 + y * 13) % 100
                    gray = 120 + noise // 4
                    surface.set_at((x, y), (gray, gray - 10, gray - 20))

        elif pattern == "metal":
            # Create metal pattern
            for y in range(height):
                for x in range(width):
                    if x % 4 == 0 or y % 8 == 0:
                        surface.set_at((x, y), (100, 100, 120))
                    else:
                        surface.set_at((x, y), (140, 140, 160))

        self.texture_atlas.add_texture(name, surface)
        return surface

    def add_sector(self, sector: Sector):
        """Add a sector to the world."""
        self.sectors.append(sector)
        self.walls.extend(sector.walls)

    def add_wall(self, start: Vector2, end: Vector2, texture_name: str = None, height: float = 64.0):
        """Add a wall to the world."""
        wall = Wall(start, end, texture_name, height)
        self.walls.append(wall)

    def add_light_source(self, position: Vector2, intensity: float = 1.0, 
                        color: Tuple[int, int, int] = (255, 255, 255), radius: float = 100.0):
        """Add a dynamic light source."""
        self.light_sources.append({
            'position': position,
            'intensity': intensity,
            'color': color,
            'radius': radius
        })

    def cast_ray(self, origin: Vector2, direction: Vector2) -> Tuple[float, Wall, float]:
        """Cast a ray and return distance, wall hit, and texture coordinate."""
        min_distance = float('inf')
        hit_wall = None
        texture_coord = 0.0

        for wall in self.walls:
            # Line intersection math
            wall_vec = wall.end - wall.start
            to_start = origin - wall.start

            # Calculate intersection using cross products
            wall_cross_ray = wall_vec.x * direction.y - wall_vec.y * direction.x

            if abs(wall_cross_ray) < 1e-10:  # Parallel lines
                continue

            t = (to_start.x * direction.y - to_start.y * direction.x) / wall_cross_ray
            u = (to_start.x * wall_vec.y - to_start.y * wall_vec.x) / wall_cross_ray

            if 0 <= t <= 1 and u > 0:  # Valid intersection
                distance = u
                if distance < min_distance:
                    min_distance = distance
                    hit_wall = wall
                    texture_coord = t  # Position along wall for texture mapping

        return min_distance, hit_wall, texture_coord

    def render_2_5d_view(self, camera_pos: Vector2, camera_angle: float):
        """Render the 2.5D view using raycasting."""
        half_fov = math.radians(self.field_of_view / 2)

        for x in range(self.width):
            # Calculate ray angle
            screen_x = (2 * x / self.width) - 1
            ray_angle = camera_angle + screen_x * half_fov
            ray_direction = Vector2(math.cos(ray_angle), math.sin(ray_angle))

            # Cast ray
            distance, wall, texture_coord = self.cast_ray(camera_pos, ray_direction)

            if wall and distance < self.render_distance:
                # Calculate wall height on screen
                wall_height = int(wall.height * self.height / distance)
                wall_top = (self.height - wall_height) // 2
                wall_bottom = wall_top + wall_height

                # Apply camera pitch
                pitch_offset = int(self.camera_pitch * self.height / 100)
                wall_top += pitch_offset
                wall_bottom += pitch_offset

                # Get wall texture
                texture = None
                if wall.texture_name:
                    texture = self.texture_atlas.get_texture(wall.texture_name)

                # Calculate lighting
                light_factor = self._calculate_lighting(camera_pos, wall, distance)

                # Render wall column
                self._render_wall_column(x, wall_top, wall_bottom, texture, 
                                       texture_coord, light_factor, distance)

                # Update z-buffer
                self.z_buffer[x] = distance

            # Render floor and ceiling
            self._render_floor_ceiling_column(x, camera_pos, ray_direction, camera_angle)

    def _calculate_lighting(self, camera_pos: Vector2, wall: Wall, distance: float) -> float:
        """Calculate lighting factor for a wall."""
        if not self.enable_lighting:
            return 1.0

        light_factor = self.ambient_light

        # Distance-based lighting falloff
        distance_factor = max(0, 1.0 - distance / self.render_distance)
        light_factor += distance_factor * 0.3

        # Dynamic light sources
        wall_center = (wall.start + wall.end) * 0.5
        for light in self.light_sources:
            light_distance = (light['position'] - wall_center).magnitude()
            if light_distance < light['radius']:
                light_contribution = light['intensity'] * (1.0 - light_distance / light['radius'])
                light_factor += light_contribution * 0.5

        # Fog effect
        if self.enable_fog and distance > self.fog_distance:
            fog_factor = 1.0 - (distance - self.fog_distance) / (self.render_distance - self.fog_distance)
            light_factor *= max(0.1, fog_factor)

        return min(1.0, light_factor)

    def _render_wall_column(self, x: int, wall_top: int, wall_bottom: int, 
                          texture: pygame.Surface, texture_coord: float, 
                          light_factor: float, distance: float):
        """Render a single wall column with texture mapping."""
        wall_top = max(0, wall_top)
        wall_bottom = min(self.height, wall_bottom)

        if wall_top >= wall_bottom:
            return

        # Default color if no texture
        wall_color = (100, 100, 100)

        if texture:
            texture_width = texture.get_width()
            texture_height = texture.get_height()
            texture_x = int(texture_coord * texture_width) % texture_width

            # Render textured wall
            for y in range(wall_top, wall_bottom):
                # Calculate texture Y coordinate
                wall_progress = (y - wall_top) / max(1, wall_bottom - wall_top)
                texture_y = int(wall_progress * texture_height) % texture_height

                # Get pixel color from texture
                try:
                    pixel_color = texture.get_at((texture_x, texture_y))[:3]

                    # Apply lighting
                    final_color = tuple(int(c * light_factor) for c in pixel_color)

                    self.screen.set_at((x, y), final_color)
                except IndexError:
                    # Fallback color
                    final_color = tuple(int(c * light_factor) for c in wall_color)
                    self.screen.set_at((x, y), final_color)
        else:
            # Render solid color wall
            final_color = tuple(int(c * light_factor) for c in wall_color)
            pygame.draw.line(self.screen, final_color, (x, wall_top), (x, wall_bottom))

    def _render_floor_ceiling_column(self, x: int, camera_pos: Vector2, 
                                   ray_direction: Vector2, camera_angle: float):
        """Render floor and ceiling for a column using texture mapping."""
        # Simple floor/ceiling rendering
        horizon = self.height // 2 + int(self.camera_pitch * self.height / 100)

        # Floor
        if horizon < self.height:
            floor_color = (64, 64, 64)  # Dark gray
            pygame.draw.line(self.screen, floor_color, (x, horizon), (x, self.height))

        # Ceiling
        if horizon > 0:
            ceiling_color = (32, 32, 64)  # Dark blue
            pygame.draw.line(self.screen, ceiling_color, (x, 0), (x, horizon))

    def render_sprite_2_5d(self, sprite_pos: Vector2, sprite_texture: str, 
                         camera_pos: Vector2, camera_angle: float, scale: float = 1.0):
        """Render a sprite in 2.5D space with proper depth sorting."""
        # Calculate sprite position relative to camera
        sprite_rel = sprite_pos - camera_pos
        distance = sprite_rel.magnitude()

        if distance > self.render_distance:
            return

        # Transform to camera space
        cos_angle = math.cos(camera_angle)
        sin_angle = math.sin(camera_angle)

        sprite_x = sprite_rel.x * cos_angle + sprite_rel.y * sin_angle
        sprite_y = -sprite_rel.x * sin_angle + sprite_rel.y * cos_angle

        if sprite_y <= 0:  # Behind camera
            return

        # Project to screen
        screen_x = int(self.width / 2 * (1 + sprite_x / sprite_y))
        sprite_height = int(abs(self.height / sprite_y) * scale)
        sprite_width = sprite_height  # Assume square sprites

        # Get texture
        texture = self.texture_atlas.get_texture(sprite_texture)
        if not texture:
            return

        # Calculate sprite bounds
        sprite_top = (self.height - sprite_height) // 2
        sprite_bottom = sprite_top + sprite_height
        sprite_left = screen_x - sprite_width // 2
        sprite_right = sprite_left + sprite_width

        # Clip to screen bounds
        sprite_left = max(0, sprite_left)
        sprite_right = min(self.width, sprite_right)
        sprite_top = max(0, sprite_top)
        sprite_bottom = min(self.height, sprite_bottom)

        # Render sprite with z-buffer testing
        for screen_x in range(sprite_left, sprite_right):
            if distance < self.z_buffer[screen_x]:
                # Calculate texture coordinates
                tex_x = int((screen_x - sprite_left) / sprite_width * texture.get_width())

                for screen_y in range(sprite_top, sprite_bottom):
                    tex_y = int((screen_y - sprite_top) / sprite_height * texture.get_height())

                    try:
                        pixel_color = texture.get_at((tex_x, tex_y))
                        if pixel_color[3] > 128:  # Alpha threshold
                            # Apply lighting
                            light_factor = self._calculate_sprite_lighting(sprite_pos, distance)
                            final_color = tuple(int(c * light_factor) for c in pixel_color[:3])
                            self.screen.set_at((screen_x, screen_y), final_color)
                    except IndexError:
                        continue

    def _calculate_sprite_lighting(self, sprite_pos: Vector2, distance: float) -> float:
        """Calculate lighting for sprites."""
        light_factor = self.ambient_light

        # Distance falloff
        distance_factor = max(0, 1.0 - distance / self.render_distance)
        light_factor += distance_factor * 0.4

        # Dynamic lights
        for light in self.light_sources:
            light_distance = (light['position'] - sprite_pos).magnitude()
            if light_distance < light['radius']:
                light_contribution = light['intensity'] * (1.0 - light_distance / light['radius'])
                light_factor += light_contribution * 0.6

        return min(1.0, light_factor)

    def set_camera_properties(self, height: float = None, pitch: float = None, fov: float = None):
        """Set 2.5D camera properties."""
        if height is not None:
            self.camera_height = height
        if pitch is not None:
            self.camera_pitch = max(-45, min(45, pitch))
        if fov is not None:
            self.field_of_view = max(30, min(120, fov))

    def enable_effects(self, fog: bool = None, lighting: bool = None, shadows: bool = None):
        """Enable or disable rendering effects."""
        if fog is not None:
            self.enable_fog = fog
        if lighting is not None:
            self.enable_lighting = lighting
        if shadows is not None:
            self.enable_shadows = shadows

    def clear_sprite_cache(self):
        """Clear sprite cache to free memory."""
        self.sprite_textures.clear()
        print("Sprite cache cleared")

    # Standard 2D rendering methods (enhanced)
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """Convert world coordinates to screen coordinates."""
        return world_pos - self.camera_offset

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """Convert screen coordinates to world coordinates."""
        return screen_pos + self.camera_offset

    def draw_sprite(self, surface: pygame.Surface, position: Vector2, 
                   rotation: float = 0, scale: Vector2 = None):
        """Draw a sprite with enhanced features."""
        if scale is None:
            scale = Vector2(1, 1)

        # Apply transformations
        transformed_surface = surface

        # Scale
        if scale.x != 1 or scale.y != 1:
            new_width = int(surface.get_width() * scale.x)
            new_height = int(surface.get_height() * scale.y)
            transformed_surface = pygame.transform.scale(transformed_surface, (new_width, new_height))

        # Rotate
        if rotation != 0:
            transformed_surface = pygame.transform.rotate(transformed_surface, rotation)

        # Convert to screen coordinates
        screen_pos = self.world_to_screen(position)

        # Center the sprite on the position
        rect = transformed_surface.get_rect()
        rect.center = (screen_pos.x, screen_pos.y)

        self.screen.blit(transformed_surface, rect)

    def draw_textured_rect(self, position: Vector2, size: Vector2, texture_name: str, 
                          tiling: Tuple[float, float] = (1.0, 1.0)):
        """Draw a textured rectangle with tiling support."""
        texture = self.texture_atlas.get_texture(texture_name)
        if not texture:
            # Fallback to colored rectangle
            self.draw_rect(position, size, (128, 128, 128))
            return

        screen_pos = self.world_to_screen(position)

        # Calculate tiling
        tile_width = int(texture.get_width() * tiling[0])
        tile_height = int(texture.get_height() * tiling[1])

        if tile_width > 0 and tile_height > 0:
            scaled_texture = pygame.transform.scale(texture, (tile_width, tile_height))

            # Tile the texture across the rectangle
            for x in range(int(screen_pos.x), int(screen_pos.x + size.x), tile_width):
                for y in range(int(screen_pos.y), int(screen_pos.y + size.y), tile_height):
                    # Clip to rectangle bounds
                    clip_width = min(tile_width, int(screen_pos.x + size.x - x))
                    clip_height = min(tile_height, int(screen_pos.y + size.y - y))

                    if clip_width > 0 and clip_height > 0:
                        clipped_texture = scaled_texture.subsurface(0, 0, clip_width, clip_height)
                        self.screen.blit(clipped_texture, (x, y))

    def draw_rect(self, position: Vector2, size: Vector2, 
                  color: Tuple[int, int, int], filled: bool = True):
        """Draw a rectangle."""
        screen_pos = self.world_to_screen(position)
        rect = pygame.Rect(screen_pos.x, screen_pos.y, size.x, size.y)

        if filled:
            pygame.draw.rect(self.screen, color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, 1)

    def draw_circle(self, center: Vector2, radius: float, 
                   color: Tuple[int, int, int], filled: bool = True):
        """Draw a circle."""
        screen_pos = self.world_to_screen(center)

        if filled:
            pygame.draw.circle(self.screen, color, (int(screen_pos.x), int(screen_pos.y)), int(radius))
        else:
            pygame.draw.circle(self.screen, color, (int(screen_pos.x), int(screen_pos.y)), int(radius), 1)

    def draw_line(self, start: Vector2, end: Vector2, 
                  color: Tuple[int, int, int], width: int = 1):
        """Draw a line."""
        screen_start = self.world_to_screen(start)
        screen_end = self.world_to_screen(end)

        pygame.draw.line(self.screen, color, 
                        (screen_start.x, screen_start.y), 
                        (screen_end.x, screen_end.y), width)

    def draw_text(self, text: str, position: Vector2, 
                  color: Tuple[int, int, int] = Color.WHITE, 
                  font_size: int = 24, font_name: Optional[str] = None):
        """Draw text."""
        font = pygame.font.Font(font_name, font_size)
        text_surface = font.render(text, True, color)

        screen_pos = self.world_to_screen(position)
        self.screen.blit(text_surface, (screen_pos.x, screen_pos.y))

    def get_text_size(self, text: str, font_size: int = 24, 
                     font_name: Optional[str] = None) -> Tuple[int, int]:
        """
        Get the size of rendered text.

        Args:
            text: Text string to measure
            font_size: Font size in pixels
            font_name: Font name (None for default)

        Returns:
            (width, height) tuple
        """
        font = pygame.font.Font(font_name, font_size)
        return font.size(text)

    def get_memory_usage(self) -> Dict[str, int]:
        """Get renderer memory usage statistics."""
        return {
            'textures': len(self.texture_atlas.textures),
            'sprites': len(self.sprite_textures),
            'walls': len(self.walls),
            'sectors': len(self.sectors),
            'lights': len(self.light_sources)
        }

    # Standard 2D rendering methods (backward compatibility)
    def draw_rect(self, position: Vector2, size: Vector2, 
                  color: Tuple[int, int, int], filled: bool = True):
        """Draw a rectangle."""
        screen_pos = self.world_to_screen(position)
        rect = pygame.Rect(screen_pos.x, screen_pos.y, size.x, size.y)

        if filled:
            pygame.draw.rect(self.screen, color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, 1)

    def draw_circle(self, center: Vector2, radius: float, 
                   color: Tuple[int, int, int], filled: bool = True):
        """Draw a circle."""
        screen_pos = self.world_to_screen(center)

        if filled:
            pygame.draw.circle(self.screen, color, (int(screen_pos.x), int(screen_pos.y)), int(radius))
        else:
            pygame.draw.circle(self.screen, color, (int(screen_pos.x), int(screen_pos.y)), int(radius), 1)

    def draw_line(self, start: Vector2, end: Vector2, 
                  color: Tuple[int, int, int], width: int = 1):
        """Draw a line."""
        screen_start = self.world_to_screen(start)
        screen_end = self.world_to_screen(end)

        pygame.draw.line(self.screen, color, 
                        (screen_start.x, screen_start.y), 
                        (screen_end.x, screen_end.y), width)

    def draw_text(self, text: str, position: Vector2, 
                  color: Tuple[int, int, int] = (255, 255, 255), 
                  font_size: int = 24, font_name: Optional[str] = None):
        """Draw text."""
        font = pygame.font.Font(font_name, font_size)
        text_surface = font.render(text, True, color)

        screen_pos = self.world_to_screen(position)
        self.screen.blit(text_surface, (screen_pos.x, screen_pos.y))

    def get_text_size(self, text: str, font_size: int = 24, 
                     font_name: Optional[str] = None) -> Tuple[int, int]:
        """Get the size of rendered text."""
        font = pygame.font.Font(font_name, font_size)
        return font.size(text)


# Alias for backward compatibility
Renderer = Advanced2DRenderer