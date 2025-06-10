
"""
VoidRay Tilemap System
Efficient tile-based rendering and collision system for 2D games.
"""

import pygame
from typing import List, Dict, Optional, Tuple, Any
from ..math.vector2 import Vector2


class Tile:
    """Individual tile with properties."""
    
    def __init__(self, tile_id: int, surface: pygame.Surface = None):
        self.tile_id = tile_id
        self.surface = surface
        self.solid = False
        self.properties: Dict[str, Any] = {}
        
    def set_property(self, key: str, value: Any):
        """Set a custom tile property."""
        self.properties[key] = value
        
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a custom tile property."""
        return self.properties.get(key, default)


class TileLayer:
    """Layer of tiles in a tilemap."""
    
    def __init__(self, name: str, width: int, height: int):
        self.name = name
        self.width = width
        self.height = height
        self.tiles: List[List[Optional[Tile]]] = [[None for _ in range(width)] for _ in range(height)]
        self.visible = True
        self.opacity = 255
        self.parallax_factor = Vector2(1.0, 1.0)
        
    def set_tile(self, x: int, y: int, tile: Optional[Tile]):
        """Set a tile at the given coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile
            
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get a tile at the given coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
        
    def fill_area(self, start_x: int, start_y: int, end_x: int, end_y: int, tile: Tile):
        """Fill an area with a specific tile."""
        for y in range(max(0, start_y), min(self.height, end_y + 1)):
            for x in range(max(0, start_x), min(self.width, end_x + 1)):
                self.set_tile(x, y, tile)


class Tilemap:
    """Complete tilemap with multiple layers."""
    
    def __init__(self, tile_width: int, tile_height: int):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.layers: List[TileLayer] = []
        self.tileset: Dict[int, Tile] = {}
        self.collision_layer: Optional[TileLayer] = None
        
    def add_layer(self, layer: TileLayer):
        """Add a tile layer."""
        self.layers.append(layer)
        
    def get_layer(self, name: str) -> Optional[TileLayer]:
        """Get a layer by name."""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None
        
    def add_tile_to_tileset(self, tile_id: int, surface: pygame.Surface, solid: bool = False):
        """Add a tile to the tileset."""
        tile = Tile(tile_id, surface)
        tile.solid = solid
        self.tileset[tile_id] = tile
        
    def world_to_tile(self, world_pos: Vector2) -> Tuple[int, int]:
        """Convert world position to tile coordinates."""
        tile_x = int(world_pos.x // self.tile_width)
        tile_y = int(world_pos.y // self.tile_height)
        return tile_x, tile_y
        
    def tile_to_world(self, tile_x: int, tile_y: int) -> Vector2:
        """Convert tile coordinates to world position."""
        world_x = tile_x * self.tile_width
        world_y = tile_y * self.tile_height
        return Vector2(world_x, world_y)
        
    def is_tile_solid(self, tile_x: int, tile_y: int) -> bool:
        """Check if a tile is solid (for collision)."""
        if self.collision_layer:
            tile = self.collision_layer.get_tile(tile_x, tile_y)
            return tile and tile.solid
        return False
        
    def get_tiles_in_area(self, world_rect: pygame.Rect) -> List[Tuple[int, int, Tile]]:
        """Get all tiles that intersect with a world rectangle."""
        tiles = []
        
        # Convert world rectangle to tile coordinates
        start_x = max(0, int(world_rect.left // self.tile_width))
        start_y = max(0, int(world_rect.top // self.tile_height))
        end_x = int((world_rect.right - 1) // self.tile_width)
        end_y = int((world_rect.bottom - 1) // self.tile_height)
        
        for layer in self.layers:
            if not layer.visible:
                continue
                
            for y in range(start_y, min(layer.height, end_y + 1)):
                for x in range(start_x, min(layer.width, end_x + 1)):
                    tile = layer.get_tile(x, y)
                    if tile:
                        tiles.append((x, y, tile))
                        
        return tiles


class TilemapSystem:
    """System for rendering and managing tilemaps."""
    
    def __init__(self):
        self.tilemaps: Dict[str, Tilemap] = {}
        self.active_tilemap: Optional[str] = None
        self.camera_offset = Vector2.zero()
        
    def create_tilemap(self, name: str, tile_width: int, tile_height: int) -> Tilemap:
        """Create a new tilemap."""
        tilemap = Tilemap(tile_width, tile_height)
        self.tilemaps[name] = tilemap
        return tilemap
        
    def set_active_tilemap(self, name: str):
        """Set the active tilemap for rendering."""
        if name in self.tilemaps:
            self.active_tilemap = name
            
    def get_active_tilemap(self) -> Optional[Tilemap]:
        """Get the currently active tilemap."""
        if self.active_tilemap and self.active_tilemap in self.tilemaps:
            return self.tilemaps[self.active_tilemap]
        return None
        
    def set_camera_offset(self, offset: Vector2):
        """Set camera offset for tilemap rendering."""
        self.camera_offset = offset
        
    def render(self, renderer, viewport: pygame.Rect):
        """Render the active tilemap."""
        tilemap = self.get_active_tilemap()
        if not tilemap:
            return
            
        # Calculate visible tile range
        camera_rect = pygame.Rect(
            viewport.x + self.camera_offset.x,
            viewport.y + self.camera_offset.y,
            viewport.width,
            viewport.height
        )
        
        # Render each layer
        for layer in tilemap.layers:
            if not layer.visible:
                continue
                
            self._render_layer(renderer, tilemap, layer, camera_rect)
            
    def _render_layer(self, renderer, tilemap: Tilemap, layer: TileLayer, camera_rect: pygame.Rect):
        """Render a single tile layer."""
        # Apply parallax offset
        parallax_offset = Vector2(
            self.camera_offset.x * layer.parallax_factor.x,
            self.camera_offset.y * layer.parallax_factor.y
        )
        
        # Calculate tile range to render
        start_x = max(0, int((camera_rect.left - parallax_offset.x) // tilemap.tile_width))
        start_y = max(0, int((camera_rect.top - parallax_offset.y) // tilemap.tile_height))
        end_x = min(layer.width - 1, int((camera_rect.right - parallax_offset.x) // tilemap.tile_width) + 1)
        end_y = min(layer.height - 1, int((camera_rect.bottom - parallax_offset.y) // tilemap.tile_height) + 1)
        
        # Render visible tiles
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                tile = layer.get_tile(x, y)
                if tile and tile.surface:
                    # Calculate screen position
                    screen_x = x * tilemap.tile_width - parallax_offset.x
                    screen_y = y * tilemap.tile_height - parallax_offset.y
                    
                    # Apply layer opacity
                    if layer.opacity < 255:
                        tile_surface = tile.surface.copy()
                        tile_surface.set_alpha(layer.opacity)
                        renderer.screen.blit(tile_surface, (screen_x, screen_y))
                    else:
                        renderer.screen.blit(tile.surface, (screen_x, screen_y))
                        
    def check_collision_at_position(self, world_pos: Vector2, size: Vector2) -> bool:
        """Check if there's a collision at the given world position."""
        tilemap = self.get_active_tilemap()
        if not tilemap or not tilemap.collision_layer:
            return False
            
        # Create collision rectangle
        collision_rect = pygame.Rect(world_pos.x, world_pos.y, size.x, size.y)
        
        # Check tiles that intersect with the collision rectangle
        tiles = tilemap.get_tiles_in_area(collision_rect)
        
        for tile_x, tile_y, tile in tiles:
            if tile.solid:
                # Check if the tile actually intersects with the collision rectangle
                tile_rect = pygame.Rect(
                    tile_x * tilemap.tile_width,
                    tile_y * tilemap.tile_height,
                    tilemap.tile_width,
                    tilemap.tile_height
                )
                
                if collision_rect.colliderect(tile_rect):
                    return True
                    
        return False
        
    def get_tile_at_world_position(self, world_pos: Vector2, layer_name: str = None) -> Optional[Tile]:
        """Get the tile at a world position."""
        tilemap = self.get_active_tilemap()
        if not tilemap:
            return None
            
        tile_x, tile_y = tilemap.world_to_tile(world_pos)
        
        if layer_name:
            layer = tilemap.get_layer(layer_name)
            if layer:
                return layer.get_tile(tile_x, tile_y)
        else:
            # Check all layers (return first non-None tile)
            for layer in tilemap.layers:
                tile = layer.get_tile(tile_x, tile_y)
                if tile:
                    return tile
                    
        return None
        
    def load_tilemap_from_data(self, name: str, data: Dict[str, Any]) -> Tilemap:
        """Load a tilemap from data dictionary."""
        tilemap = self.create_tilemap(
            name,
            data.get('tile_width', 32),
            data.get('tile_height', 32)
        )
        
        # Load tileset
        if 'tileset' in data:
            for tile_data in data['tileset']:
                tile_id = tile_data['id']
                # In a real implementation, you'd load the surface from a file
                # For now, create a colored rectangle
                surface = pygame.Surface((tilemap.tile_width, tilemap.tile_height))
                color = tile_data.get('color', (255, 255, 255))
                surface.fill(color)
                
                tilemap.add_tile_to_tileset(
                    tile_id, 
                    surface, 
                    tile_data.get('solid', False)
                )
        
        # Load layers
        if 'layers' in data:
            for layer_data in data['layers']:
                layer = TileLayer(
                    layer_data['name'],
                    layer_data['width'],
                    layer_data['height']
                )
                
                # Load tile data
                if 'tiles' in layer_data:
                    tiles_data = layer_data['tiles']
                    for y in range(layer.height):
                        for x in range(layer.width):
                            tile_id = tiles_data[y * layer.width + x]
                            if tile_id != 0 and tile_id in tilemap.tileset:
                                layer.set_tile(x, y, tilemap.tileset[tile_id])
                
                tilemap.add_layer(layer)
                
                # Set as collision layer if specified
                if layer_data.get('collision', False):
                    tilemap.collision_layer = layer
        
        return tilemap
