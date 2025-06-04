"""
VoidRay Sprite Component

Handles rendering of 2D sprites and textures with support for animations,
transformations, and layering.
"""

import pygame
from typing import Optional, List
from ..core.component import Component
from ..math.vector2 import Vector2
from ..utils.color import Color


class Sprite(Component):
    """
    A component that renders a 2D sprite/texture.
    Supports basic transformations and color modulation.
    """
    
    def __init__(self, texture: Optional[pygame.Surface] = None):
        """
        Initialize the sprite component.
        
        Args:
            texture: The pygame surface to render
        """
        super().__init__()
        self.texture = texture
        self.color = Color.WHITE
        self.layer = 0  # Rendering layer (higher values render on top)
        self.flip_x = False
        self.flip_y = False
        self.visible = True
        
        # Animation support
        self.frame_width = 0
        self.frame_height = 0
        self.current_frame = 0
        self.frame_count = 1
        self.animation_speed = 10  # frames per second
        self.animation_time = 0
        self.loop_animation = True
        self.animation_playing = False
    
    def set_texture(self, texture: pygame.Surface) -> None:
        """
        Set the sprite texture.
        
        Args:
            texture: The pygame surface to use
        """
        self.texture = texture
        if texture:
            self.frame_width = texture.get_width()
            self.frame_height = texture.get_height()
    
    def set_color(self, color: Color) -> None:
        """
        Set the sprite color modulation.
        
        Args:
            color: The color to modulate with
        """
        self.color = color
    
    def set_flip(self, flip_x: bool, flip_y: bool) -> None:
        """
        Set sprite flipping.
        
        Args:
            flip_x: Whether to flip horizontally
            flip_y: Whether to flip vertically
        """
        self.flip_x = flip_x
        self.flip_y = flip_y
    
    def setup_animation(self, frame_width: int, frame_height: int, 
                       frame_count: int, animation_speed: float) -> None:
        """
        Setup sprite animation parameters.
        
        Args:
            frame_width: Width of each animation frame
            frame_height: Height of each animation frame
            frame_count: Total number of frames
            animation_speed: Animation speed in frames per second
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_count = frame_count
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.animation_time = 0
    
    def play_animation(self, loop: bool = True) -> None:
        """
        Start playing the animation.
        
        Args:
            loop: Whether to loop the animation
        """
        self.animation_playing = True
        self.loop_animation = loop
        self.current_frame = 0
        self.animation_time = 0
    
    def stop_animation(self) -> None:
        """Stop the animation."""
        self.animation_playing = False
    
    def update(self, delta_time: float) -> None:
        """
        Update sprite animation.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        if not self.animation_playing or self.frame_count <= 1:
            return
        
        self.animation_time += delta_time
        frame_duration = 1.0 / self.animation_speed
        
        if self.animation_time >= frame_duration:
            self.animation_time -= frame_duration
            self.current_frame += 1
            
            if self.current_frame >= self.frame_count:
                if self.loop_animation:
                    self.current_frame = 0
                else:
                    self.current_frame = self.frame_count - 1
                    self.animation_playing = False
    
    def render(self, renderer) -> None:
        """
        Render the sprite.
        
        Args:
            renderer: The renderer to draw with
        """
        if not self.visible or not self.texture:
            return
        
        # Get current frame surface
        surface = self._get_current_frame_surface()
        
        if not surface:
            return
        
        # Apply color modulation
        if self.color != Color.WHITE:
            surface = surface.copy()
            surface.fill(self.color.to_tuple(), special_flags=pygame.BLEND_MULT)
        
        # Apply flipping
        if self.flip_x or self.flip_y:
            surface = pygame.transform.flip(surface, self.flip_x, self.flip_y)
        
        # Render the sprite
        position = self.transform.position if self.transform else Vector2.zero()
        rotation = self.transform.rotation if self.transform else 0
        scale = self.transform.scale if self.transform else Vector2.one()
        
        renderer.draw_sprite(surface, position, rotation, scale)
    
    def _get_current_frame_surface(self) -> Optional[pygame.Surface]:
        """
        Get the surface for the current animation frame.
        
        Returns:
            The surface for the current frame
        """
        if not self.texture:
            return None
        
        if self.frame_count <= 1:
            return self.texture
        
        # Calculate frame position in sprite sheet
        frames_per_row = self.texture.get_width() // self.frame_width
        frame_x = (self.current_frame % frames_per_row) * self.frame_width
        frame_y = (self.current_frame // frames_per_row) * self.frame_height
        
        # Extract frame from sprite sheet
        frame_rect = pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
        frame_surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame_surface.blit(self.texture, (0, 0), frame_rect)
        
        return frame_surface
    
    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle of the sprite in world space.
        
        Returns:
            The bounding rectangle
        """
        if not self.texture:
            return pygame.Rect(0, 0, 0, 0)
        
        position = self.transform.position if self.transform else Vector2.zero()
        scale = self.transform.scale if self.transform else Vector2.one()
        
        width = self.frame_width * scale.x
        height = self.frame_height * scale.y
        
        return pygame.Rect(
            int(position.x - width / 2),
            int(position.y - height / 2),
            int(width),
            int(height)
        )
