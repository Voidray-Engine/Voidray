"""
VoidRay Collision System

Handles collision detection between different types of colliders
and provides collision information for physics response.
"""

import pygame
from typing import Optional, Dict, Any
from ..core.component import Component
from ..math.vector2 import Vector2


class Collider(Component):
    """
    Base class for all collision shapes. Provides collision detection
    capabilities for game objects.
    """
    
    def __init__(self):
        """Initialize the collider."""
        super().__init__()
        self.is_trigger = False  # If true, collisions don't cause physical response
        self.layer = 0  # Collision layer
    
    def on_attach(self) -> None:
        """Called when attached to a game object."""
        # Register with physics system if available
        if hasattr(self.game_object, 'scene') and self.game_object.scene:
            engine = self.game_object.scene.engine
            if engine and hasattr(engine, 'physics_system'):
                engine.physics_system.add_collider(self)
    
    def on_detach(self) -> None:
        """Called when detached from a game object."""
        # Unregister from physics system if available
        if hasattr(self.game_object, 'scene') and self.game_object.scene:
            engine = self.game_object.scene.engine
            if engine and hasattr(engine, 'physics_system'):
                engine.physics_system.remove_collider(self)
    
    def on_collision(self, other: 'Collider', collision_info: Dict[str, Any]) -> None:
        """
        Called when this collider collides with another.
        
        Args:
            other: The other collider involved in the collision
            collision_info: Information about the collision
        """
        # Handle player-ball collisions
        if self.game_object and other.game_object:
            # Check if this is a player hitting a ball
            if (hasattr(self.game_object, 'name') and 'Player' in self.game_object.name and
                hasattr(other.game_object, 'name') and 'Ball' in other.game_object.name):
                
                # Get the ball's rigidbody
                ball_rb = other.game_object.get_component(Rigidbody)
                if ball_rb:
                    # Calculate push direction from player to ball
                    push_direction = (other.game_object.transform.position - 
                                    self.game_object.transform.position).normalized()
                    
                    # Apply impulse to push the ball away
                    push_force = push_direction * 300  # Adjust force as needed
                    ball_rb.add_impulse(push_force)
            
            # Check if this is a ball hitting a player (reverse case)
            elif (hasattr(self.game_object, 'name') and 'Ball' in self.game_object.name and
                  hasattr(other.game_object, 'name') and 'Player' in other.game_object.name):
                
                # Get this ball's rigidbody
                ball_rb = self.game_object.get_component(Rigidbody)
                if ball_rb:
                    # Calculate push direction from player to ball
                    push_direction = (self.game_object.transform.position - 
                                    other.game_object.transform.position).normalized()
                    
                    # Apply impulse to push the ball away
                    push_force = push_direction * 300  # Adjust force as needed
                    ball_rb.add_impulse(push_force)
    
    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle of this collider.
        Should be overridden by subclasses.
        
        Returns:
            The bounding rectangle
        """
        if self.transform:
            pos = self.transform.position
            return pygame.Rect(int(pos.x), int(pos.y), 1, 1)
        return pygame.Rect(0, 0, 1, 1)


class BoxCollider(Collider):
    """A rectangular collision shape."""
    
    def __init__(self, width: float = 1, height: float = 1, offset: Vector2 = Vector2.zero()):
        """
        Initialize the box collider.
        
        Args:
            width: Width of the collision box
            height: Height of the collision box
            offset: Offset from the transform position
        """
        super().__init__()
        self.width = width
        self.height = height
        self.offset = offset
    
    def get_bounds(self) -> pygame.Rect:
        """Get the bounding rectangle of this box collider."""
        if not self.transform:
            return pygame.Rect(0, 0, int(self.width), int(self.height))
        
        pos = self.transform.position + self.offset
        scale = self.transform.scale
        
        scaled_width = self.width * scale.x
        scaled_height = self.height * scale.y
        
        return pygame.Rect(
            int(pos.x - scaled_width / 2),
            int(pos.y - scaled_height / 2),
            int(scaled_width),
            int(scaled_height)
        )


class CircleCollider(Collider):
    """A circular collision shape."""
    
    def __init__(self, radius: float = 1, offset: Vector2 = Vector2.zero()):
        """
        Initialize the circle collider.
        
        Args:
            radius: Radius of the collision circle
            offset: Offset from the transform position
        """
        super().__init__()
        self.radius = radius
        self.offset = offset
    
    def get_bounds(self) -> pygame.Rect:
        """Get the bounding rectangle of this circle collider."""
        if not self.transform:
            diameter = int(self.radius * 2)
            return pygame.Rect(0, 0, diameter, diameter)
        
        pos = self.transform.position + self.offset
        scale = max(self.transform.scale.x, self.transform.scale.y)  # Use uniform scale
        
        scaled_radius = self.radius * scale
        diameter = int(scaled_radius * 2)
        
        return pygame.Rect(
            int(pos.x - scaled_radius),
            int(pos.y - scaled_radius),
            diameter,
            diameter
        )
    
    def get_center(self) -> Vector2:
        """Get the center position of the circle."""
        if not self.transform:
            return self.offset
        return self.transform.position + self.offset


class CollisionDetector:
    """
    Handles collision detection between different types of colliders.
    """
    
    def check_collision(self, collider_a: Collider, collider_b: Collider) -> Optional[Dict[str, Any]]:
        """
        Check for collision between two colliders.
        
        Args:
            collider_a: First collider
            collider_b: Second collider
            
        Returns:
            Collision information dictionary if collision occurred, None otherwise
        """
        # Determine collision check based on collider types
        if isinstance(collider_a, BoxCollider) and isinstance(collider_b, BoxCollider):
            return self._check_box_box_collision(collider_a, collider_b)
        elif isinstance(collider_a, CircleCollider) and isinstance(collider_b, CircleCollider):
            return self._check_circle_circle_collision(collider_a, collider_b)
        elif isinstance(collider_a, BoxCollider) and isinstance(collider_b, CircleCollider):
            return self._check_box_circle_collision(collider_a, collider_b)
        elif isinstance(collider_a, CircleCollider) and isinstance(collider_b, BoxCollider):
            result = self._check_box_circle_collision(collider_b, collider_a)
            if result:
                # Flip the normal since we swapped the order
                result['normal'] = -result['normal']
            return result
        
        # Fallback to bounding box collision
        return self._check_bounds_collision(collider_a, collider_b)
    
    def _check_box_box_collision(self, box_a: BoxCollider, box_b: BoxCollider) -> Optional[Dict[str, Any]]:
        """Check collision between two box colliders."""
        rect_a = box_a.get_bounds()
        rect_b = box_b.get_bounds()
        
        if rect_a.colliderect(rect_b):
            # Calculate collision normal and penetration
            center_a = Vector2(rect_a.centerx, rect_a.centery)
            center_b = Vector2(rect_b.centerx, rect_b.centery)
            
            # Calculate overlap on each axis
            overlap_x = min(rect_a.right - rect_b.left, rect_b.right - rect_a.left)
            overlap_y = min(rect_a.bottom - rect_b.top, rect_b.bottom - rect_a.top)
            
            # Use the axis with less overlap as the collision normal
            if overlap_x < overlap_y:
                normal = Vector2(1 if center_a.x < center_b.x else -1, 0)
                penetration = overlap_x
            else:
                normal = Vector2(0, 1 if center_a.y < center_b.y else -1)
                penetration = overlap_y
            
            collision_info = {
                'normal': normal,
                'penetration': penetration,
                'point': center_a + (center_b - center_a) * 0.5
            }
            
            # Trigger collision callbacks
            box_a.on_collision(box_b, collision_info)
            box_b.on_collision(box_a, collision_info)
            
            return collision_info
        
        return None
    
    def _check_circle_circle_collision(self, circle_a: CircleCollider, circle_b: CircleCollider) -> Optional[Dict[str, Any]]:
        """Check collision between two circle colliders."""
        center_a = circle_a.get_center()
        center_b = circle_b.get_center()
        
        # Get scaled radii
        scale_a = max(circle_a.transform.scale.x, circle_a.transform.scale.y) if circle_a.transform else 1
        scale_b = max(circle_b.transform.scale.x, circle_b.transform.scale.y) if circle_b.transform else 1
        
        radius_a = circle_a.radius * scale_a
        radius_b = circle_b.radius * scale_b
        
        distance = center_a.distance_to(center_b)
        combined_radius = radius_a + radius_b
        
        if distance < combined_radius:
            # Calculate collision normal and penetration
            if distance > 0:
                normal = (center_b - center_a).normalized()
            else:
                normal = Vector2(1, 0)  # Default normal if centers are identical
            
            penetration = combined_radius - distance
            collision_point = center_a + normal * radius_a
            
            collision_info = {
                'normal': normal,
                'penetration': penetration,
                'point': collision_point
            }
            
            # Trigger collision callbacks
            circle_a.on_collision(circle_b, collision_info)
            circle_b.on_collision(circle_a, collision_info)
            
            return collision_info
        
        return None
    
    def _check_box_circle_collision(self, box: BoxCollider, circle: CircleCollider) -> Optional[Dict[str, Any]]:
        """Check collision between a box and a circle collider."""
        box_rect = box.get_bounds()
        circle_center = circle.get_center()
        
        # Get scaled circle radius
        scale = max(circle.transform.scale.x, circle.transform.scale.y) if circle.transform else 1
        circle_radius = circle.radius * scale
        
        # Find the closest point on the box to the circle center
        closest_x = max(box_rect.left, min(circle_center.x, box_rect.right))
        closest_y = max(box_rect.top, min(circle_center.y, box_rect.bottom))
        closest_point = Vector2(closest_x, closest_y)
        
        # Check if the distance is less than the circle radius
        distance = circle_center.distance_to(closest_point)
        
        if distance < circle_radius:
            # Calculate collision normal and penetration
            if distance > 0:
                normal = (circle_center - closest_point).normalized()
            else:
                # Circle center is inside the box
                box_center = Vector2(box_rect.centerx, box_rect.centery)
                normal = (circle_center - box_center).normalized()
            
            penetration = circle_radius - distance
            
            collision_info = {
                'normal': normal,
                'penetration': penetration,
                'point': closest_point
            }
            
            # Trigger collision callbacks
            box.on_collision(circle, collision_info)
            circle.on_collision(box, collision_info)
            
            return collision_info
        
        return None
    
    def _check_bounds_collision(self, collider_a: Collider, collider_b: Collider) -> Optional[Dict[str, Any]]:
        """Fallback collision check using bounding rectangles."""
        rect_a = collider_a.get_bounds()
        rect_b = collider_b.get_bounds()
        
        if rect_a.colliderect(rect_b):
            # Simple collision with basic normal calculation
            center_a = Vector2(rect_a.centerx, rect_a.centery)
            center_b = Vector2(rect_b.centerx, rect_b.centery)
            
            direction = center_b - center_a
            if direction.magnitude() > 0:
                normal = direction.normalized()
            else:
                normal = Vector2(1, 0)
            
            return {
                'normal': normal,
                'penetration': 1,  # Minimal penetration
                'point': center_a + (center_b - center_a) * 0.5
            }
        
        return None
