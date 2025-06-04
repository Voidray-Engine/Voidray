"""
VoidRay Camera

Handles view transformations and provides different camera modes
for 2D rendering including following objects and screen bounds.
"""

from typing import Optional
from ..core.component import Component
from ..math.vector2 import Vector2


class Camera(Component):
    """
    A camera component that defines the view area and handles
    coordinate transformations between world and screen space.
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize the camera.
        
        Args:
            width: Screen width
            height: Screen height
        """
        super().__init__()
        self.screen_width = width
        self.screen_height = height
        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        
        # Follow target
        self.follow_target: Optional['GameObject'] = None
        self.follow_smoothing = 5.0
        self.follow_offset = Vector2.zero()
        
        # Camera bounds
        self.use_bounds = False
        self.bounds_min = Vector2.zero()
        self.bounds_max = Vector2.zero()
    
    def set_screen_size(self, width: int, height: int) -> None:
        """
        Set the screen dimensions.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.screen_width = width
        self.screen_height = height
    
    def set_zoom(self, zoom: float) -> None:
        """
        Set the camera zoom level.
        
        Args:
            zoom: The zoom level (1.0 = normal, > 1.0 = zoomed in, < 1.0 = zoomed out)
        """
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom))
    
    def set_zoom_limits(self, min_zoom: float, max_zoom: float) -> None:
        """
        Set the zoom limits.
        
        Args:
            min_zoom: Minimum zoom level
            max_zoom: Maximum zoom level
        """
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.zoom = max(min_zoom, min(max_zoom, self.zoom))
    
    def set_follow_target(self, target: 'GameObject', smoothing: float = 5.0, 
                         offset: Vector2 = Vector2.zero()) -> None:
        """
        Set a target for the camera to follow.
        
        Args:
            target: The game object to follow
            smoothing: How smoothly to follow (higher = more responsive)
            offset: Offset from the target position
        """
        self.follow_target = target
        self.follow_smoothing = smoothing
        self.follow_offset = offset
    
    def clear_follow_target(self) -> None:
        """Stop following any target."""
        self.follow_target = None
    
    def set_bounds(self, min_pos: Vector2, max_pos: Vector2) -> None:
        """
        Set camera bounds to limit movement.
        
        Args:
            min_pos: Minimum world position the camera can view
            max_pos: Maximum world position the camera can view
        """
        self.use_bounds = True
        self.bounds_min = min_pos
        self.bounds_max = max_pos
    
    def clear_bounds(self) -> None:
        """Remove camera bounds."""
        self.use_bounds = False
    
    def update(self, delta_time: float) -> None:
        """
        Update camera logic including following targets.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        if self.follow_target and self.transform:
            # Calculate target position
            target_pos = self.follow_target.transform.position + self.follow_offset
            
            # Smoothly move towards target
            current_pos = self.transform.position
            diff = target_pos - current_pos
            move_amount = diff * self.follow_smoothing * delta_time
            new_pos = current_pos + move_amount
            
            # Apply bounds if enabled
            if self.use_bounds:
                new_pos = self._clamp_to_bounds(new_pos)
            
            self.transform.position = new_pos
    
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: Position in world space
            
        Returns:
            Position in screen space
        """
        camera_pos = self.transform.position if self.transform else Vector2.zero()
        
        # Apply camera transformation
        relative_pos = world_pos - camera_pos
        screen_pos = relative_pos * self.zoom
        
        # Center on screen
        screen_center = Vector2(self.screen_width / 2, self.screen_height / 2)
        return screen_center + screen_pos
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_pos: Position in screen space
            
        Returns:
            Position in world space
        """
        camera_pos = self.transform.position if self.transform else Vector2.zero()
        
        # Remove screen centering
        screen_center = Vector2(self.screen_width / 2, self.screen_height / 2)
        relative_pos = screen_pos - screen_center
        
        # Apply inverse camera transformation
        world_offset = relative_pos / self.zoom
        return camera_pos + world_offset
    
    def get_view_bounds(self) -> tuple:
        """
        Get the world space bounds of what the camera can see.
        
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        camera_pos = self.transform.position if self.transform else Vector2.zero()
        
        half_width = (self.screen_width / 2) / self.zoom
        half_height = (self.screen_height / 2) / self.zoom
        
        return (
            camera_pos.x - half_width,
            camera_pos.y - half_height,
            camera_pos.x + half_width,
            camera_pos.y + half_height
        )
    
    def is_visible(self, position: Vector2, size: Vector2 = Vector2.zero()) -> bool:
        """
        Check if a position or area is visible by the camera.
        
        Args:
            position: World position to check
            size: Size of the area (optional)
            
        Returns:
            True if visible, False otherwise
        """
        min_x, min_y, max_x, max_y = self.get_view_bounds()
        
        # Add size padding
        obj_min_x = position.x - size.x / 2
        obj_min_y = position.y - size.y / 2
        obj_max_x = position.x + size.x / 2
        obj_max_y = position.y + size.y / 2
        
        # Check if rectangles overlap
        return not (obj_max_x < min_x or obj_min_x > max_x or 
                   obj_max_y < min_y or obj_min_y > max_y)
    
    def _clamp_to_bounds(self, position: Vector2) -> Vector2:
        """
        Clamp camera position to defined bounds.
        
        Args:
            position: The position to clamp
            
        Returns:
            The clamped position
        """
        if not self.use_bounds:
            return position
        
        # Calculate view size in world space
        view_width = self.screen_width / self.zoom
        view_height = self.screen_height / self.zoom
        
        # Calculate the actual bounds the camera center can be in
        actual_min_x = self.bounds_min.x + view_width / 2
        actual_min_y = self.bounds_min.y + view_height / 2
        actual_max_x = self.bounds_max.x - view_width / 2
        actual_max_y = self.bounds_max.y - view_height / 2
        
        # Clamp position
        clamped_x = max(actual_min_x, min(actual_max_x, position.x))
        clamped_y = max(actual_min_y, min(actual_max_y, position.y))
        
        return Vector2(clamped_x, clamped_y)
