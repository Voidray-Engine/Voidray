"""
VoidRay Physics Engine
Core physics simulation and collision detection system.
"""

from typing import List, Callable, Optional
from ..math.vector2 import Vector2
from .collider import Collider


class PhysicsEngine:
    """
    The main physics engine that handles collision detection and resolution.
    """
    
    def __init__(self):
        """
        Initialize the physics engine.
        """
        self.gravity = Vector2(0, 0)  # No gravity by default - can be enabled per game
        self.colliders: List[Collider] = []
        self.collision_callbacks: List[Callable[[Collider, Collider], None]] = []
        
        # Spatial partitioning for better performance
        self.grid_size = 64  # Size of each grid cell
        self.spatial_grid = {}  # Dictionary to store colliders by grid position
        self.frame_count = 0
        self.optimization_enabled = True
        
    def add_collider(self, collider: Collider):
        """
        Add a collider to the physics simulation.
        
        Args:
            collider: The collider to add
        """
        if collider not in self.colliders:
            self.colliders.append(collider)
    
    def remove_collider(self, collider: Collider):
        """
        Remove a collider from the physics simulation.
        
        Args:
            collider: The collider to remove
        """
        if collider in self.colliders:
            self.colliders.remove(collider)
    
    def add_collision_callback(self, callback: Callable[[Collider, Collider], None]):
        """
        Add a callback function that will be called when collisions occur.
        
        Args:
            callback: Function to call with (collider1, collider2) parameters
        """
        self.collision_callbacks.append(callback)
    
    def _get_grid_key(self, position: Vector2) -> tuple:
        """
        Get grid key for spatial partitioning.
        
        Args:
            position: World position
            
        Returns:
            Grid key as tuple
        """
        return (int(position.x // self.grid_size), int(position.y // self.grid_size))
    
    def _update_spatial_grid(self):
        """
        Update spatial partitioning grid.
        """
        if not self.optimization_enabled:
            return
            
        self.spatial_grid.clear()
        
        for collider in self.colliders:
            if collider.game_object and collider.game_object.active:
                pos = collider.get_world_position()
                radius = collider.get_bounds_radius()
                
                # Add to multiple grid cells if collider spans them
                min_x = int((pos.x - radius) // self.grid_size)
                max_x = int((pos.x + radius) // self.grid_size)
                min_y = int((pos.y - radius) // self.grid_size)
                max_y = int((pos.y + radius) // self.grid_size)
                
                for gx in range(min_x, max_x + 1):
                    for gy in range(min_y, max_y + 1):
                        key = (gx, gy)
                        if key not in self.spatial_grid:
                            self.spatial_grid[key] = []
                        self.spatial_grid[key].append(collider)
    
    def update(self, delta_time: float):
        """
        Update physics simulation.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Update all colliders
        for collider in self.colliders:
            if collider.game_object and collider.game_object.active:
                self._update_collider(collider, delta_time)
        
        # Check for collisions
        self._check_collisions()
    
    def _update_collider(self, collider: Collider, delta_time: float):
        """
        Update a single collider's physics.
        
        Args:
            collider: The collider to update
            delta_time: Time elapsed since last frame
        """
        # Skip physics updates - objects control their own movement
        # Only apply physics for special cases where explicitly requested
        if False:
            # Apply gravity only if enabled
            if self.gravity.magnitude() > 0:
                collider.velocity += self.gravity * delta_time
            
            # Apply velocity to position
            if collider.game_object:
                current_pos = collider.game_object.transform.position
                new_pos = current_pos + collider.velocity * delta_time
                collider.game_object.transform.position = new_pos
    
    def _check_collisions(self):
        """
        Check for collisions between all colliders.
        """
        # Update spatial grid every few frames for performance
        if self.frame_count % 3 == 0:
            self._update_spatial_grid()
        self.frame_count += 1
        
        checked_pairs = set()
        
        if self.optimization_enabled and self.spatial_grid:
            # Use spatial partitioning
            for colliders_in_cell in self.spatial_grid.values():
                for i in range(len(colliders_in_cell)):
                    for j in range(i + 1, len(colliders_in_cell)):
                        collider1 = colliders_in_cell[i]
                        collider2 = colliders_in_cell[j]
                        
                        # Avoid checking the same pair twice
                        pair = (min(id(collider1), id(collider2)), max(id(collider1), id(collider2)))
                        if pair in checked_pairs:
                            continue
                        checked_pairs.add(pair)
                        
                        self._process_collision_pair(collider1, collider2)
        else:
            # Fallback to brute force
            for i in range(len(self.colliders)):
                for j in range(i + 1, len(self.colliders)):
                    collider1 = self.colliders[i]
                    collider2 = self.colliders[j]
                    self._process_collision_pair(collider1, collider2)
    
    def _process_collision_pair(self, collider1: Collider, collider2: Collider):
        """
        Process a potential collision between two colliders.
        
        Args:
            collider1: First collider
            collider2: Second collider
        """
                
                # Skip if both are static
        if collider1.is_static and collider2.is_static:
            return
        
        # Skip if either object is inactive
        if (not collider1.game_object or not collider1.game_object.active or
            not collider2.game_object or not collider2.game_object.active):
            return
        
        # Check collision
        if self._check_collision(collider1, collider2):
            # Call collision callbacks
            for callback in self.collision_callbacks:
                callback(collider1, collider2)
            
            # Call individual collider callbacks
            if collider1.on_collision:
                collider1.on_collision(collider2)
            if collider2.on_collision:
                collider2.on_collision(collider1)
            
            # Resolve collision if needed
            if not collider1.is_trigger and not collider2.is_trigger:
                self._resolve_collision(collider1, collider2)
    
    def _check_collision(self, collider1: Collider, collider2: Collider) -> bool:
        """
        Check if two colliders are colliding.
        
        Args:
            collider1: First collider
            collider2: Second collider
            
        Returns:
            True if colliding, False otherwise
        """
        return collider1.check_collision(collider2)
    
    def _resolve_collision(self, collider1: Collider, collider2: Collider):
        """
        Resolve collision between two colliders.
        
        Args:
            collider1: First collider
            collider2: Second collider
        """
        # Simple collision resolution - separate objects
        if collider1.is_static:
            # Only move collider2
            separation = self._get_separation_vector(collider2, collider1)
            if collider2.game_object:
                collider2.game_object.transform.position += separation
                # Stop velocity in collision direction
                if separation.magnitude() > 0:
                    normal = separation.normalized()
                    collider2.velocity = collider2.velocity - normal * collider2.velocity.dot(normal)
        elif collider2.is_static:
            # Only move collider1
            separation = self._get_separation_vector(collider1, collider2)
            if collider1.game_object:
                collider1.game_object.transform.position += separation
                # Stop velocity in collision direction
                if separation.magnitude() > 0:
                    normal = separation.normalized()
                    collider1.velocity = collider1.velocity - normal * collider1.velocity.dot(normal)
        else:
            # Move both objects
            separation = self._get_separation_vector(collider1, collider2)
            half_separation = separation * 0.5
            
            if collider1.game_object:
                collider1.game_object.transform.position += half_separation
            if collider2.game_object:
                collider2.game_object.transform.position -= half_separation
    
    def _get_separation_vector(self, collider1: Collider, collider2: Collider) -> Vector2:
        """
        Get the minimum separation vector to resolve collision.
        
        Args:
            collider1: First collider
            collider2: Second collider
            
        Returns:
            Separation vector
        """
        # This is a simplified implementation
        # In a full engine, you'd want more sophisticated collision resolution
        
        pos1 = collider1.get_world_position()
        pos2 = collider2.get_world_position()
        
        direction = pos1 - pos2
        if direction.magnitude() == 0:
            direction = Vector2(1, 0)  # Default separation direction
        
        # Estimate minimum separation distance
        min_distance = collider1.get_bounds_radius() + collider2.get_bounds_radius()
        current_distance = direction.magnitude()
        
        if current_distance < min_distance:
            separation_distance = min_distance - current_distance + 1  # +1 for small buffer
            return direction.normalized() * separation_distance
        
        return Vector2(0, 0)
    
    def query_point(self, point: Vector2) -> List[Collider]:
        """
        Find all colliders that contain a specific point.
        
        Args:
            point: Point to query
            
        Returns:
            List of colliders containing the point
        """
        result = []
        for collider in self.colliders:
            if (collider.game_object and collider.game_object.active and 
                collider.contains_point(point)):
                result.append(collider)
        return result
    
    def query_area(self, center: Vector2, radius: float) -> List[Collider]:
        """
        Find all colliders within a circular area.
        
        Args:
            center: Center of the query area
            radius: Radius of the query area
            
        Returns:
            List of colliders in the area
        """
        result = []
        for collider in self.colliders:
            if (collider.game_object and collider.game_object.active):
                distance = (collider.get_world_position() - center).magnitude()
                if distance <= radius + collider.get_bounds_radius():
                    result.append(collider)
        return result
    
    def raycast(self, start: Vector2, direction: Vector2, max_distance: float = float('inf')) -> Optional[Collider]:
        """
        Cast a ray and find the first collider it hits.
        
        Args:
            start: Ray start position
            direction: Ray direction (should be normalized)
            max_distance: Maximum ray distance
            
        Returns:
            First collider hit, or None if no hit
        """
        closest_collider = None
        closest_distance = max_distance
        
        for collider in self.colliders:
            if collider.game_object and collider.game_object.active:
                # Simple ray-circle intersection test
                to_collider = collider.get_world_position() - start
                projection = to_collider.dot(direction)
                
                if 0 <= projection <= closest_distance:
                    closest_point = start + direction * projection
                    distance_to_center = (closest_point - collider.get_world_position()).magnitude()
                    
                    if distance_to_center <= collider.get_bounds_radius():
                        if projection < closest_distance:
                            closest_distance = projection
                            closest_collider = collider
        
        return closest_collider
