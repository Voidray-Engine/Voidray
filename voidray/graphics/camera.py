"""
VoidRay Camera System
Handles camera positioning, following, and viewport management.
"""

from ..core.game_object import GameObject
from ..math.vector2 import Vector2
import math


class Camera(GameObject):
    """
    A Camera controls the view of the game world.
    """

    def __init__(self, name: str = "Camera"):
        """
        Initialize a new Camera.

        Args:
            name: Name identifier for this camera
        """
        super().__init__(name)

        self.target: GameObject = None
        self.follow_speed = 5.0
        self.offset = Vector2(0, 0)
        self.bounds_min = Vector2(float('-inf'), float('-inf'))
        self.bounds_max = Vector2(float('inf'), float('inf'))
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.shake_timer = 0.0

        # Enhanced camera features
        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_speed = 2.0
        self.target_zoom = 1.0
        self.smooth_zoom = True
        self.rotation = 0.0

        # 2.5D perspective
        self.perspective_factor = 0.1  # How much depth affects position
        self.fov_height = 600  # Field of view height for depth calculations

    def set_target(self, target: GameObject, offset: Vector2 = None):
        """
        Set a target GameObject for the camera to follow.

        Args:
            target: The GameObject to follow
            offset: Offset from the target position
        """
        self.target = target
        if offset:
            self.offset = offset

    def set_bounds(self, min_pos: Vector2, max_pos: Vector2):
        """
        Set camera movement bounds.

        Args:
            min_pos: Minimum camera position
            max_pos: Maximum camera position
        """
        self.bounds_min = min_pos
        self.bounds_max = max_pos

    def shake(self, intensity: float, duration: float):
        """
        Add camera shake effect.

        Args:
            intensity: Shake intensity in pixels
            duration: Shake duration in seconds
        """
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = duration

    def set_zoom(self, zoom: float, smooth: bool = True):
        """
        Set camera zoom level.

        Args:
            zoom: Zoom factor (1.0 = normal, >1.0 = zoom in, <1.0 = zoom out)
            smooth: Whether to smoothly transition to new zoom
        """
        self.target_zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        if not smooth:
            self.zoom = self.target_zoom

    def zoom_in(self, factor: float = 1.2):
        """
        Zoom in by a factor.

        Args:
            factor: Zoom factor to multiply current zoom by
        """
        self.set_zoom(self.zoom * factor)

    def zoom_out(self, factor: float = 1.2):
        """
        Zoom out by a factor.

        Args:
            factor: Zoom factor to divide current zoom by
        """
        self.set_zoom(self.zoom / factor)

    def update(self, delta_time: float):
        """
        Update the camera position and effects.

        Args:
            delta_time: Time elapsed since last frame
        """
        super().update(delta_time)

        # Follow target
        if self.target:
            target_pos = self.target.get_world_position() + self.offset

            # Smooth following
            current_pos = self.transform.position
            direction = target_pos - current_pos

            if self.follow_speed > 0:
                move_distance = self.follow_speed * delta_time
                if direction.magnitude() > move_distance:
                    direction = direction.normalized() * move_distance

            new_pos = current_pos + direction

            # Apply bounds
            new_pos.x = max(self.bounds_min.x, min(self.bounds_max.x, new_pos.x))
            new_pos.y = max(self.bounds_min.y, min(self.bounds_max.y, new_pos.y))

            self.transform.position = new_pos

        # Update shake effect
        if self.shake_timer > 0:
            self.shake_timer -= delta_time
            if self.shake_timer <= 0:
                self.shake_intensity = 0

        # Update zoom smoothing
        if self.smooth_zoom and abs(self.zoom - self.target_zoom) > 0.01:
            zoom_diff = self.target_zoom - self.zoom
            self.zoom += zoom_diff * self.zoom_speed * delta_time

    def get_view_position(self) -> Vector2:
        """
        Get the camera's view position including shake effects.

        Returns:
            Camera position with shake applied
        """
        pos = self.transform.position.copy()

        # Apply shake
        if self.shake_intensity > 0:
            import random
            shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            pos.x += shake_x
            pos.y += shake_y

        return pos

    def world_to_screen(self, world_pos: Vector2, screen_size: Vector2, depth: float = 0.0, height: float = 0.0) -> Vector2:
        """
        Convert world position to screen position relative to this camera with advanced 2.5D support.

        Args:
            world_pos: Position in world space
            screen_size: Size of the screen
            depth: Depth value for 2.5D rendering (negative = background, positive = foreground)
            height: Height value for vertical positioning in 2.5D space

        Returns:
            Position in screen space
        """
        camera_pos = self.get_view_position()
        screen_center = Vector2(screen_size.x / 2, screen_size.y / 2)

        # Calculate relative position
        relative_pos = world_pos - camera_pos

        # Enhanced 2.5D perspective transformation (DOOM/GTA style)
        if depth != 0.0 or height != 0.0:
            # Distance-based scaling for depth with improved perspective
            distance = max(1.0, abs(depth) + 1.0)
            perspective_scale = 1.0 / distance

            # Apply perspective to horizontal position
            relative_pos.x *= perspective_scale

            # Calculate vertical position based on height and perspective
            horizon_offset = screen_size.y * 0.5  # Horizon line at middle of screen
            if height != 0.0:
                # Height affects vertical position with perspective
                height_offset = height / distance * 50  # Scale factor for height visibility
                relative_pos.y = relative_pos.y * perspective_scale - height_offset
            else:
                relative_pos.y *= perspective_scale

            # Add depth-based vertical offset for layering
            if depth < 0:  # Background elements
                relative_pos.y += abs(depth) * 5
            elif depth > 0:  # Foreground elements
                relative_pos.y -= depth * 3

        # Apply zoom and rotation
        if self.rotation != 0:
            # Rotate around camera center
            cos_rot = math.cos(math.radians(self.rotation))
            sin_rot = math.sin(math.radians(self.rotation))

            rotated_x = relative_pos.x * cos_rot - relative_pos.y * sin_rot
            rotated_y = relative_pos.x * sin_rot + relative_pos.y * cos_rot

            relative_pos = Vector2(rotated_x, rotated_y)

        relative_pos = relative_pos * self.zoom

        return relative_pos + screen_center

    def screen_to_world(self, screen_pos: Vector2, screen_size: Vector2) -> Vector2:
        """
        Convert screen position to world position relative to this camera.

        Args:
            screen_pos: Position in screen space
            screen_size: Size of the screen

        Returns:
            Position in world space
        """
        camera_pos = self.get_view_position()
        screen_center = Vector2(screen_size.x / 2, screen_size.y / 2)
        return screen_pos - screen_center + camera_pos

    def is_in_view(self, world_pos: Vector2, size: Vector2, screen_size: Vector2) -> bool:
        """
        Check if a world position and size is visible by this camera.

        Args:
            world_pos: Position to check
            size: Size of the object
            screen_size: Size of the screen

        Returns:
            True if the object is visible, False otherwise
        """
        camera_pos = self.get_view_position()

        # Calculate view bounds
        half_screen = Vector2(screen_size.x / 2, screen_size.y / 2)
        view_min = camera_pos - half_screen
        view_max = camera_pos + half_screen

        # Calculate object bounds
        half_size = Vector2(size.x / 2, size.y / 2)
        obj_min = world_pos - half_size
        obj_max = world_pos + half_size

        # Check overlap
        return not (obj_max.x < view_min.x or obj_min.x > view_max.x or
                   obj_max.y < view_min.y or obj_min.y > view_max.y)