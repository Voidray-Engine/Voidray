"""
VoidRay Transform Class
Represents position, rotation, and scale transformations.
"""

from .vector2 import Vector2


class Transform:
    """
    Represents a 2D transformation with position, rotation, and scale.
    """
    
    def __init__(self, position: Vector2 = None, rotation: float = 0, scale: Vector2 = None):
        """
        Initialize a transform.
        
        Args:
            position: Position as Vector2 (defaults to zero)
            rotation: Rotation in degrees (defaults to 0)
            scale: Scale as Vector2 (defaults to (1, 1))
        """
        self.position = position or Vector2.zero()
        self.rotation = rotation  # In degrees
        self.scale = scale or Vector2.one()
    
    def translate(self, offset: Vector2):
        """
        Move the transform by an offset.
        
        Args:
            offset: Translation offset as Vector2
        """
        self.position += offset
    
    def rotate(self, angle_degrees: float):
        """
        Rotate the transform by an angle.
        
        Args:
            angle_degrees: Rotation angle in degrees
        """
        self.rotation += angle_degrees
        # Keep rotation in 0-360 range
        self.rotation = self.rotation % 360
    
    def scale_by(self, factor: Vector2):
        """
        Scale the transform by a factor.
        
        Args:
            factor: Scale factor as Vector2
        """
        self.scale = Vector2(self.scale.x * factor.x, self.scale.y * factor.y)
    
    def set_position(self, position: Vector2):
        """
        Set the position of the transform.
        
        Args:
            position: New position as Vector2
        """
        self.position = position.copy()
    
    def set_rotation(self, rotation: float):
        """
        Set the rotation of the transform.
        
        Args:
            rotation: New rotation in degrees
        """
        self.rotation = rotation % 360
    
    def set_scale(self, scale: Vector2):
        """
        Set the scale of the transform.
        
        Args:
            scale: New scale as Vector2
        """
        self.scale = scale.copy()
    
    def get_forward_vector(self) -> Vector2:
        """
        Get the forward direction vector based on current rotation.
        
        Returns:
            Forward vector as Vector2
        """
        return Vector2.from_angle_degrees(self.rotation)
    
    def get_right_vector(self) -> Vector2:
        """
        Get the right direction vector based on current rotation.
        
        Returns:
            Right vector as Vector2
        """
        return Vector2.from_angle_degrees(self.rotation + 90)
    
    def transform_point(self, local_point: Vector2) -> Vector2:
        """
        Transform a local point to world space.
        
        Args:
            local_point: Point in local space
            
        Returns:
            Point in world space
        """
        # Apply scale
        scaled_point = Vector2(local_point.x * self.scale.x, local_point.y * self.scale.y)
        
        # Apply rotation
        rotated_point = scaled_point.rotate_degrees(self.rotation)
        
        # Apply translation
        world_point = rotated_point + self.position
        
        return world_point
    
    def inverse_transform_point(self, world_point: Vector2) -> Vector2:
        """
        Transform a world point to local space.
        
        Args:
            world_point: Point in world space
            
        Returns:
            Point in local space
        """
        # Remove translation
        translated_point = world_point - self.position
        
        # Remove rotation
        unrotated_point = translated_point.rotate_degrees(-self.rotation)
        
        # Remove scale
        if self.scale.x != 0 and self.scale.y != 0:
            local_point = Vector2(unrotated_point.x / self.scale.x, unrotated_point.y / self.scale.y)
        else:
            local_point = Vector2.zero()
        
        return local_point
    
    def look_at(self, target: Vector2):
        """
        Rotate the transform to look at a target position.
        
        Args:
            target: Target position to look at
        """
        direction = target - self.position
        if direction.magnitude() > 0:
            import math
            self.rotation = math.degrees(math.atan2(direction.y, direction.x))
    
    def copy(self) -> 'Transform':
        """
        Create a copy of this transform.
        
        Returns:
            New Transform with same values
        """
        return Transform(self.position.copy(), self.rotation, self.scale.copy())
    
    def __str__(self) -> str:
        return f"Transform(pos={self.position}, rot={self.rotation:.1f}°, scale={self.scale})"
    
    def __repr__(self) -> str:
        return self.__str__()
