"""
VoidRay Collider System
Defines various types of collision shapes and detection methods.
"""

import math
from typing import Optional, Callable, TYPE_CHECKING, Dict, Any
from ..math.vector2 import Vector2
from ..core.component import Component

if TYPE_CHECKING:
    from ..core.game_object import GameObject


class Collider(Component):
    """
    Base class for all collision shapes.
    """

    def __init__(self):
        """
        Initialize a collider.
        """
        super().__init__()
        self.is_trigger = False  # If True, doesn't resolve collisions
        self.is_static = False   # If True, won't move during collision resolution
        self.layer = 0          # Collision layer for filtering
        self.on_collision: Optional[Callable[['Collider', Dict[str, Any]], None]] = None
        self.on_trigger_enter: Optional[Callable[['Collider'], None]] = None
        self.on_trigger_exit: Optional[Callable[['Collider'], None]] = None

        # Internal state
        self._in_collision_with = set()

    def on_attach(self) -> None:
        """Called when attached to a game object."""
        # Register with physics engine if available
        if hasattr(self.game_object, 'scene') and self.game_object.scene:
            engine = self.game_object.scene.engine
            if engine and hasattr(engine, 'physics_engine'):
                engine.physics_engine.add_collider(self)

    def on_detach(self) -> None:
        """Called when detached from a game object."""
        # Unregister from physics engine if available
        if hasattr(self.game_object, 'scene') and self.game_object.scene:
            engine = self.game_object.scene.engine
            if engine and hasattr(engine, 'physics_engine'):
                engine.physics_engine.remove_collider(self)

    def get_world_position(self) -> Vector2:
        """
        Get the world position of this collider.

        Returns:
            World position as Vector2
        """
        if self.game_object:
            return self.game_object.transform.position
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

    def get_collision_info(self, other: 'Collider') -> Optional[Dict[str, Any]]:
        """
        Get detailed collision information.

        Args:
            other: The other collider

        Returns:
            Collision info dict or None if no collision
        """
        # Override in subclasses for detailed collision info
        if self.check_collision(other):
            return {
                'normal': Vector2(1, 0),
                'penetration': 1.0,
                'point': self.get_world_position()
            }
        return None

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
        return 1.0

    def trigger_collision_event(self, other: 'Collider', collision_info: Dict[str, Any]) -> None:
        """
        Trigger collision events.

        Args:
            other: The other collider
            collision_info: Collision information
        """
        if self.is_trigger:
            # Handle trigger events
            if other not in self._in_collision_with:
                self._in_collision_with.add(other)
                if self.on_trigger_enter:
                    self.on_trigger_enter(other)
            elif other in self._in_collision_with:
                # Still in collision, no event needed
                pass
        else:
            # Handle collision events
            if self.on_collision:
                self.on_collision(other, collision_info)

    def trigger_collision_exit(self, other: 'Collider') -> None:
        """
        Trigger collision exit events.

        Args:
            other: The other collider that we're no longer colliding with
        """
        if other in self._in_collision_with:
            self._in_collision_with.remove(other)
            if self.is_trigger and self.on_trigger_exit:
                self.on_trigger_exit(other)


class RectCollider(Collider):
    """
    A rectangular collision shape.
    """

    def __init__(self, width: float = 32, height: float = 32, offset: Vector2 = None):
        """
        Initialize a rectangular collider.

        Args:
            width: Width of the rectangle
            height: Height of the rectangle
            offset: Offset from the GameObject's position
        """
        super().__init__()
        self.width = width
        self.height = height
        self.offset = offset or Vector2(0, 0)

    def get_rect_bounds(self) -> tuple:
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

    def get_collision_info(self, other: 'Collider') -> Optional[Dict[str, Any]]:
        """
        Get detailed collision information.

        Args:
            other: The other collider

        Returns:
            Collision info dict or None if no collision
        """
        if isinstance(other, RectCollider):
            return self._get_rect_rect_info(other)
        elif isinstance(other, CircleCollider):
            return self._get_rect_circle_info(other)
        return None

    def _check_rect_rect(self, other: 'RectCollider') -> bool:
        """Check collision between two rectangles."""
        x1, y1, w1, h1 = self.get_rect_bounds()
        x2, y2, w2, h2 = other.get_rect_bounds()

        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

    def _get_rect_rect_info(self, other: 'RectCollider') -> Optional[Dict[str, Any]]:
        """Get detailed collision info for rect-rect collision."""
        if not self._check_rect_rect(other):
            return None

        x1, y1, w1, h1 = self.get_rect_bounds()
        x2, y2, w2, h2 = other.get_rect_bounds()

        # Calculate overlap
        overlap_x = min(x1 + w1, x2 + w2) - max(x1, x2)
        overlap_y = min(y1 + h1, y2 + h2) - max(y1, y2)

        # Use minimum overlap axis for separation
        if overlap_x < overlap_y:
            # Separate on X axis
            normal = Vector2(-1 if x1 < x2 else 1, 0)
            penetration = overlap_x
        else:
            # Separate on Y axis
            normal = Vector2(0, -1 if y1 < y2 else 1)
            penetration = overlap_y

        contact_point = Vector2(
            max(x1, x2) + min(w1, w2) / 2,
            max(y1, y2) + min(h1, h2) / 2
        )

        return {
            'normal': normal,
            'penetration': penetration,
            'point': contact_point
        }

    def _check_rect_circle(self, other: 'CircleCollider') -> bool:
        """Check collision between this rectangle and a circle."""
        rect_x, rect_y, rect_w, rect_h = self.get_rect_bounds()
        circle_center = other.get_center()
        circle_radius = other.radius

        # Find the closest point on the rectangle to the circle center
        closest_x = max(rect_x, min(circle_center.x, rect_x + rect_w))
        closest_y = max(rect_y, min(circle_center.y, rect_y + rect_h))

        # Calculate distance from circle center to closest point
        distance = math.sqrt((circle_center.x - closest_x) ** 2 + (circle_center.y - closest_y) ** 2)

        return distance <= circle_radius

    def _get_rect_circle_info(self, other: 'CircleCollider') -> Optional[Dict[str, Any]]:
        """Get detailed collision info for rect-circle collision."""
        if not self._check_rect_circle(other):
            return None

        rect_x, rect_y, rect_w, rect_h = self.get_rect_bounds()
        circle_center = other.get_center()
        circle_radius = other.radius

        # Find closest point on rectangle
        closest_x = max(rect_x, min(circle_center.x, rect_x + rect_w))
        closest_y = max(rect_y, min(circle_center.y, rect_y + rect_h))
        closest_point = Vector2(closest_x, closest_y)

        # Calculate normal and penetration
        to_circle = circle_center - closest_point
        distance = to_circle.magnitude()

        if distance > 0:
            normal = to_circle.normalized()
        else:
            # Circle center is inside rectangle
            rect_center = Vector2(rect_x + rect_w/2, rect_y + rect_h/2)
            normal = (circle_center - rect_center).normalized()

        penetration = circle_radius - distance

        return {
            'normal': normal,
            'penetration': penetration,
            'point': closest_point
        }

    def contains_point(self, point: Vector2) -> bool:
        """Check if a point is inside this rectangle."""
        x, y, w, h = self.get_rect_bounds()
        return x <= point.x <= x + w and y <= point.y <= y + h

    def get_bounds_radius(self) -> float:
        """Get the bounding radius of this rectangle."""
        return math.sqrt(self.width * self.width + self.height * self.height) / 2


class CircleCollider(Collider):
    """
    A circular collision shape.
    """

    def __init__(self, radius: float = 16, offset: Vector2 = None):
        """
        Initialize a circular collider.

        Args:
            radius: Radius of the circle
            offset: Offset from the GameObject's position
        """
        super().__init__()
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
            return other._check_rect_circle(self)
        return False

    def get_collision_info(self, other: 'Collider') -> Optional[Dict[str, Any]]:
        """
        Get detailed collision information.

        Args:
            other: The other collider

        Returns:
            Collision info dict or None if no collision
        """
        if isinstance(other, CircleCollider):
            return self._get_circle_circle_info(other)
        elif isinstance(other, RectCollider):
            # Use rect's implementation but flip the normal
            info = other._get_rect_circle_info(self)
            if info:
                info['normal'] = -info['normal']
            return info
        return None

    def _check_circle_circle(self, other: 'CircleCollider') -> bool:
        """Check collision between two circles."""
        center1 = self.get_center()
        center2 = other.get_center()
        distance = (center1 - center2).magnitude()

        return distance <= (self.radius + other.radius)

    def _get_circle_circle_info(self, other: 'CircleCollider') -> Optional[Dict[str, Any]]:
        """Get detailed collision info for circle-circle collision."""
        if not self._check_circle_circle(other):
            return None

        center1 = self.get_center()
        center2 = other.get_center()
        distance = (center1 - center2).magnitude()
        combined_radius = self.radius + other.radius

        if distance > 0:
            normal = (center2 - center1).normalized()
        else:
            normal = Vector2(1, 0)  # Default normal if circles are exactly overlapping

        penetration = combined_radius - distance
        contact_point = center1 + normal * self.radius

        return {
            'normal': normal,
            'penetration': penetration,
            'point': contact_point
        }

    def contains_point(self, point: Vector2) -> bool:
        """Check if a point is inside this circle."""
        center = self.get_center()
        distance = (point - center).magnitude()
        return distance <= self.radius

    def get_bounds_radius(self) -> float:
        """Get the bounding radius of this circle."""
        return self.radius


# Legacy aliases for backward compatibility
BoxCollider = RectCollider