"""
VoidRay Collider System
Defines various types of collision shapes and detection methods.
"""

import math
from typing import Optional, Callable, TYPE_CHECKING
from ..math.vector2 import Vector2

if TYPE_CHECKING:
    from ..core.game_object import GameObject


class Collider:
    """
    Base class for all collision shapes.
    """
    
    def __init__(self, game_object: Optional['GameObject'] = None):
        """
        Initialize a collider.
        
        Args:
            game_object: The GameObject this collider is attached to
        """
        self.game_object = game_object
        self.is_trigger = False  # If True, doesn't resolve collisions
        self.is_static = True    # Static by default - objects control their own movement
        self.velocity = Vector2(0, 0)  # Current velocity
        self.on_collision: Optional[Callable[['Collider'], None]] = None
        
    def get_world_position(self) -> Vector2:
        """
        Get the world position of this collider.
        
        Returns:
            World position as Vector2
        """
        if self.game_object:
            return self.game_object.get_world_position()
        return Vector2(0, 0)
    
    def check_collision(self, other: 'Collider') -> bool:
        """
        Check if this collider is colliding with another.
        
        Args:
            other: The other collider to check against
            
        Returns:
            True if colliding, False otherwise
        """
        # Override in subclasses
        return False
    
    def contains_point(self, point: Vector2) -> bool:
        """
        Check if a point is inside this collider.
        
        Args:
            point: Point to check
            
        Returns:
            True if point is inside, False otherwise
        """
        # Override in subclasses
        return False
    
    def get_bounds_radius(self) -> float:
        """
        Get the approximate radius of this collider for broad-phase collision detection.
        
        Returns:
            Bounding radius in pixels
        """
        # Override in subclasses
        return 0.0


class RectCollider(Collider):
    """
    A rectangular collision shape.
    """
    
    def __init__(self, game_object: Optional['GameObject'] = None, 
                 width: float = 32, height: float = 32, offset: Vector2 = None):
        """
        Initialize a rectangular collider.
        
        Args:
            game_object: The GameObject this collider is attached to
            width: Width of the rectangle
            height: Height of the rectangle
            offset: Offset from the GameObject's position
        """
        super().__init__(game_object)
        self.width = width
        self.height = height
        self.offset = offset or Vector2(0, 0)
    
    def get_rect(self) -> tuple:
        """
        Get the rectangle bounds (x, y, width, height).
        
        Returns:
            Tuple of (x, y, width, height)
        """
        center = self.get_world_position() + self.offset
        x = center.x - self.width / 2
        y = center.y - self.height / 2
        return (x, y, self.width, self.height)
    
    def check_collision(self, other: Collider) -> bool:
        """
        Check collision with another collider.
        
        Args:
            other: The other collider
            
        Returns:
            True if colliding, False otherwise
        """
        if isinstance(other, RectCollider):
            return self._check_rect_rect(other)
        elif isinstance(other, CircleCollider):
            return self._check_rect_circle(other)
        return False
    
    def _check_rect_rect(self, other: 'RectCollider') -> bool:
        """
        Check collision between two rectangles.
        
        Args:
            other: The other rectangle collider
            
        Returns:
            True if colliding, False otherwise
        """
        x1, y1, w1, h1 = self.get_rect()
        x2, y2, w2, h2 = other.get_rect()
        
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)
    
    def _check_rect_circle(self, other: 'CircleCollider') -> bool:
        """
        Check collision between this rectangle and a circle.
        
        Args:
            other: The circle collider
            
        Returns:
            True if colliding, False otherwise
        """
        rect_x, rect_y, rect_w, rect_h = self.get_rect()
        circle_center = other.get_world_position() + other.offset
        circle_radius = other.radius
        
        # Find the closest point on the rectangle to the circle center
        closest_x = max(rect_x, min(circle_center.x, rect_x + rect_w))
        closest_y = max(rect_y, min(circle_center.y, rect_y + rect_h))
        
        # Calculate distance from circle center to closest point
        distance = math.sqrt((circle_center.x - closest_x) ** 2 + (circle_center.y - closest_y) ** 2)
        
        return distance <= circle_radius
    
    def contains_point(self, point: Vector2) -> bool:
        """
        Check if a point is inside this rectangle.
        
        Args:
            point: Point to check
            
        Returns:
            True if point is inside, False otherwise
        """
        x, y, w, h = self.get_rect()
        return x <= point.x <= x + w and y <= point.y <= y + h
    
    def get_bounds_radius(self) -> float:
        """
        Get the bounding radius of this rectangle.
        
        Returns:
            Radius that encompasses the entire rectangle
        """
        return math.sqrt(self.width * self.width + self.height * self.height) / 2


class CircleCollider(Collider):
    """
    A circular collision shape.
    """
    
    def __init__(self, game_object: Optional['GameObject'] = None, 
                 radius: float = 16, offset: Vector2 = None):
        """
        Initialize a circular collider.
        
        Args:
            game_object: The GameObject this collider is attached to
            radius: Radius of the circle
            offset: Offset from the GameObject's position
        """
        super().__init__(game_object)
        self.radius = radius
        self.offset = offset or Vector2(0, 0)
    
    def get_center(self) -> Vector2:
        """
        Get the center position of this circle.
        
        Returns:
            Center position as Vector2
        """
        return self.get_world_position() + self.offset
    
    def check_collision(self, other: Collider) -> bool:
        """
        Check collision with another collider.
        
        Args:
            other: The other collider
            
        Returns:
            True if colliding, False otherwise
        """
        if isinstance(other, CircleCollider):
            return self._check_circle_circle(other)
        elif isinstance(other, RectCollider):
            return other._check_rect_circle(self)  # Use the rect's implementation
        return False
    
    def _check_circle_circle(self, other: 'CircleCollider') -> bool:
        """
        Check collision between two circles.
        
        Args:
            other: The other circle collider
            
        Returns:
            True if colliding, False otherwise
        """
        center1 = self.get_center()
        center2 = other.get_center()
        distance = (center1 - center2).magnitude()
        
        return distance <= (self.radius + other.radius)
    
    def contains_point(self, point: Vector2) -> bool:
        """
        Check if a point is inside this circle.
        
        Args:
            point: Point to check
            
        Returns:
            True if point is inside, False otherwise
        """
        center = self.get_center()
        distance = (point - center).magnitude()
        return distance <= self.radius
    
    def get_bounds_radius(self) -> float:
        """
        Get the bounding radius of this circle.
        
        Returns:
            The radius of the circle
        """
        return self.radius
