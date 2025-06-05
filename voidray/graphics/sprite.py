"""
VoidRay Sprite
Enhanced sprite component with better asset loading and 2.5D support.
"""

import pygame
from typing import Optional
from ..core.game_object import GameObject
from ..math.vector2 import Vector2
from ..graphics.renderer import Color


class Sprite(GameObject):
    """
    Enhanced Sprite class with automatic asset loading and 2.5D support.
    """

    def __init__(self, name: str = "Sprite"):
        """
        Initialize a new Sprite.

        Args:
            name: Name identifier for this sprite
        """
        super().__init__(name)

        # Sprite properties
        self.surface: Optional[pygame.Surface] = None
        self.texture_name: Optional[str] = None
        self.scale = Vector2(1.0, 1.0)
        self.rotation = 0.0
        self.alpha = 255
        self.color_tint = Color.WHITE

        # Enhanced 2.5D properties
        self.depth = 0.0  # Depth for 2.5D rendering (negative = background, positive = foreground)
        self.height = 0.0  # Height above ground level for true 2.5D positioning
        self.z_order = 0  # Z-order for sorting within the same depth
        self.layer = "entities"  # Render layer
        self.billboard = False  # Always face camera (for 3D-like sprites)

        # Wall sprite properties (for DOOM-style sprites that act like walls)
        self.is_wall_sprite = False
        self.wall_height = 64.0
        self.wall_thickness = 1.0

        # Animation properties (for future use)
        self.animation_frame = 0
        self.animation_speed = 0.0
        self.animation_frames = []

    def load_texture(self, texture_name: str, asset_loader=None):
        """
        Load a texture from the asset loader with fallback support.

        Args:
            texture_name: Name or filename of the texture
            asset_loader: Asset loader instance (will use scene's if not provided)
        """
        self.texture_name = texture_name

        # Try multiple sources for asset loader
        loader = None
        if asset_loader:
            loader = asset_loader
        elif self.scene and hasattr(self.scene, 'asset_loader'):
            loader = self.scene.asset_loader
        elif self.scene and hasattr(self.scene, 'engine') and hasattr(self.scene.engine, 'asset_loader'):
            loader = self.scene.engine.asset_loader

        if loader:
            self.surface = loader.load_image(texture_name, texture_name)
            if self.surface:
                print(f"Successfully loaded texture: {texture_name}")
            else:
                print(f"Failed to load texture, using fallback: {texture_name}")
                # Create a fallback texture
                self.create_colored_rect(32, 32, (255, 0, 255))  # Magenta to indicate missing texture
        else:
            print(f"Warning: No asset loader available to load texture: {texture_name}")
            # Create a fallback texture
            self.create_colored_rect(32, 32, (255, 0, 255))

    def create_colored_rect(self, width: int, height: int, color: tuple = Color.WHITE):
        """
        Create a simple colored rectangle as the sprite texture.

        Args:
            width: Rectangle width
            height: Rectangle height
            color: RGB color tuple
        """
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface.fill(color)
        self.texture_name = f"rect_{width}x{height}_{color}"

    def create_colored_circle(self, radius: int, color: tuple = Color.WHITE):
        """
        Create a simple colored circle as the sprite texture.

        Args:
            radius: Circle radius
            color: RGB color tuple
        """
        size = radius * 2
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, color, (radius, radius), radius)
        self.texture_name = f"circle_{radius}_{color}"

    def set_scale(self, scale_x: float, scale_y: float = None):
        """
        Set the sprite scale.

        Args:
            scale_x: X scale factor
            scale_y: Y scale factor (defaults to scale_x for uniform scaling)
        """
        if scale_y is None:
            scale_y = scale_x
        self.scale = Vector2(scale_x, scale_y)

    def set_rotation(self, rotation: float):
        """
        Set the sprite rotation in degrees.

        Args:
            rotation: Rotation in degrees
        """
        self.rotation = rotation

    def set_alpha(self, alpha: int):
        """
        Set the sprite transparency.

        Args:
            alpha: Alpha value (0-255, 0 = transparent, 255 = opaque)
        """
        self.alpha = max(0, min(255, alpha))

    def set_depth(self, depth: float):
        """
        Set the depth for 2.5D rendering.

        Args:
            depth: Depth value (negative = background, positive = foreground)
        """
        self.depth = depth

    def flip(self, flip_x: bool = False, flip_y: bool = False):
        """
        Set sprite flipping.

        Args:
            flip_x: Flip horizontally
            flip_y: Flip vertically
        """
        self.flip_x = flip_x
        self.flip_y = flip_y

    def get_size(self) -> Vector2:
        """Get the sprite size."""
        if self.surface:
            return Vector2(self.surface.get_width(), self.surface.get_height())
        return Vector2(0, 0)

    def get_scaled_size(self) -> Vector2:
        """Get the sprite size after scaling."""
        size = self.get_size()
        return Vector2(size.x * self.scale.x, size.y * self.scale.y)

    def update(self, delta_time: float):
        """
        Update the sprite.

        Args:
            delta_time: Time elapsed since last frame
        """
        super().update(delta_time)

        # Handle animation (if frames are available)
        if self.animation_frames and self.animation_speed > 0:
            self.animation_frame += self.animation_speed * delta_time
            if self.animation_frame >= len(self.animation_frames):
                self.animation_frame = 0

            # Update surface to current animation frame
            frame_index = int(self.animation_frame)
            if 0 <= frame_index < len(self.animation_frames):
                self.surface = self.animation_frames[frame_index]

    def render(self, renderer):
        """
        Render this sprite using the provided renderer with enhanced 2.5D support.

        Args:
            renderer: The renderer to use for drawing
        """
        if not self.visible or not self.surface:
            return

        if self.is_wall_sprite:
            # Render as a wall segment for DOOM-style sprites
            self._render_as_wall(renderer)
        else:
            # Standard sprite rendering with height support
            renderer.draw_sprite(
                surface=self.surface,
                position=self.transform.position,
                rotation=self.rotation,
                scale=self.scale,
                z_order=self.z_order,
                layer=self.layer,
                depth=self.depth,
                alpha=self.alpha
            )

    def _render_as_wall(self, renderer):
        """Render sprite as a wall segment (DOOM-style)."""
        from ..math.vector2 import Vector2

        # Calculate wall endpoints based on sprite position and thickness
        half_thickness = self.wall_thickness / 2
        start_pos = Vector2(
            self.transform.position.x - half_thickness,
            self.transform.position.y
        )
        end_pos = Vector2(
            self.transform.position.x + half_thickness,
            self.transform.position.y
        )

        # Use surface color if available, otherwise use sprite color
        wall_color = self.color_tint
        if self.surface:
            # Sample average color from surface (simplified)
            try:
                avg_color = pygame.transform.average_color(self.surface)
                wall_color = avg_color[:3]  # Remove alpha if present
            except:
                wall_color = self.color_tint

        # Add wall segment to renderer
        renderer.add_wall_segment(
            start=start_pos,
            end=end_pos,
            height=self.wall_height,
            color=wall_color,
            texture=self.surface
        )

    def set_as_wall_sprite(self, height: float = 64.0, thickness: float = 1.0):
        """Configure this sprite to render as a wall segment."""
        self.is_wall_sprite = True
        self.wall_height = height
        self.wall_thickness = thickness
        self.layer = "walls"

    def set_height(self, height: float):
        """Set the height of this sprite above ground level."""
        self.height = height

    def set_billboard(self, billboard: bool = True):
        """Set whether this sprite should always face the camera."""
        self.billboard = billboard

    def get_bounds(self) -> tuple:
        """
        Get the sprite bounds as (x, y, width, height).

        Returns:
            Tuple of (x, y, width, height)
        """
        size = self.get_scaled_size()
        x = self.transform.position.x - size.x / 2
        y = self.transform.position.y - size.y / 2
        return (x, y, size.x, size.y)

    def contains_point(self, point: Vector2) -> bool:
        """
        Check if a point is within the sprite bounds.

        Args:
            point: Point to check

        Returns:
            True if point is within bounds
        """
        x, y, width, height = self.get_bounds()
        return (x <= point.x <= x + width and 
                y <= point.y <= y + height)