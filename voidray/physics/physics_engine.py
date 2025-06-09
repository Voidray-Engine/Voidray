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
        self.spatial_grid_size = 200.0
        self.max_velocity = 2000.0
        self.time_scale = 1.0
    
    def set_gravity(self, gravity: float):
        """
        Set gravity strength (positive for downward).
        
        Args:
            gravity: Gravity strength in pixels per second squared
        """
        self.gravity = Vector2(0, gravity)
        print(f"Physics gravity set to {gravity}")
    
    def set_time_scale(self, scale: float):
        """
        Set physics time scale for slow motion or speed up effects.
        
        Args:
            scale: Time scale multiplier (1.0 = normal, 0.5 = half speed, 2.0 = double speed)
        """
        self.time_scale = max(0.0, scale)
    
    def set_max_velocity(self, max_vel: float):
        """
        Set maximum velocity to prevent objects from moving too fast.
        
        Args:
            max_vel: Maximum velocity in pixels per second
        """
        self.max_velocity = max_vel
        
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
    
    def update(self, delta_time: float):
        """
        Update physics simulation with optimizations.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Performance optimization: Skip physics updates if no active colliders
        active_colliders = [c for c in self.colliders if c.game_object and c.game_object.active]
        
        if not active_colliders:
            return
        
        # Update all active colliders
        for collider in active_colliders:
            self._update_collider(collider, delta_time)
        
        # Optimized collision detection
        self._check_collisions_optimized(active_colliders)
    
    def _update_collider(self, collider: Collider, delta_time: float):
        """
        Update a single collider's physics.
        
        Args:
            collider: The collider to update
            delta_time: Time elapsed since last frame
        """
        # Apply physics if object has a rigidbody component
        if collider.game_object:
            # Try to get rigidbody component
            try:
                from .rigidbody import Rigidbody
                rigidbody = collider.game_object.get_component(Rigidbody)
                if rigidbody:
                    # Apply gravity only if enabled
                    if self.gravity.magnitude() > 0:
                        rigidbody.velocity += self.gravity * delta_time
                    
                    # Clamp velocity to max
                    if rigidbody.velocity.magnitude() > self.max_velocity:
                        rigidbody.velocity = rigidbody.velocity.normalized() * self.max_velocity
                    
                    # Apply velocity to position
                    current_pos = collider.game_object.transform.position
                    new_pos = current_pos + rigidbody.velocity * delta_time * self.time_scale
                    collider.game_object.transform.position = new_pos
            except ImportError:
                pass  # Rigidbody component not available
    
    def _check_collisions(self):
        """
        Check for collisions between all colliders.
        """
        for i in range(len(self.colliders)):
            for j in range(i + 1, len(self.colliders)):
                collider1 = self.colliders[i]
                collider2 = self.colliders[j]
                
                # Skip if both are static
                if collider1.is_static and collider2.is_static:
                    continue
                
                # Skip if either object is inactive
                if (not collider1.game_object or not collider1.game_object.active or
                    not collider2.game_object or not collider2.game_object.active):
                    continue
                
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
                    try:
                        from .rigidbody import Rigidbody
                        rigidbody = collider2.game_object.get_component(Rigidbody)
                        if rigidbody:
                            normal = separation.normalized()
                            rigidbody.velocity = rigidbody.velocity - normal * rigidbody.velocity.dot(normal)
                    except ImportError:
                        pass
        elif collider2.is_static:
            # Only move collider1
            separation = self._get_separation_vector(collider1, collider2)
            if collider1.game_object:
                collider1.game_object.transform.position += separation
                # Stop velocity in collision direction
                if separation.magnitude() > 0:
                    try:
                        from .rigidbody import Rigidbody
                        rigidbody = collider1.game_object.get_component(Rigidbody)
                        if rigidbody:
                            normal = separation.normalized()
                            rigidbody.velocity = rigidbody.velocity - normal * rigidbody.velocity.dot(normal)
                    except ImportError:
                        pass
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
    
    def _check_collisions_optimized(self, active_colliders: List[Collider]):
        """
        Optimized collision detection using spatial partitioning concepts.
        
        Args:
            active_colliders: List of active colliders to check
        """
        # Simple spatial optimization: group colliders by rough grid
        grid_size = 200
        collision_grid = {}
        
        # Group colliders by grid cell
        for collider in active_colliders:
            if collider.game_object:
                pos = collider.get_world_position()
                grid_x = int(pos.x // grid_size)
                grid_y = int(pos.y // grid_size)
                grid_key = (grid_x, grid_y)
                
                if grid_key not in collision_grid:
                    collision_grid[grid_key] = []
                collision_grid[grid_key].append(collider)
        
        # Check collisions within each grid cell and adjacent cells
        checked_pairs = set()
        
        for grid_key, colliders in collision_grid.items():
            # Check collisions within this cell
            for i in range(len(colliders)):
                for j in range(i + 1, len(colliders)):
                    collider1, collider2 = colliders[i], colliders[j]
                    pair = tuple(sorted([id(collider1), id(collider2)]))
                    
                    if pair not in checked_pairs:
                        checked_pairs.add(pair)
                        self._process_collision_pair(collider1, collider2)
            
            # Check adjacent cells to avoid missing edge cases
            grid_x, grid_y = grid_key
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    
                    adjacent_key = (grid_x + dx, grid_y + dy)
                    if adjacent_key in collision_grid:
                        for collider1 in colliders:
                            for collider2 in collision_grid[adjacent_key]:
                                pair = tuple(sorted([id(collider1), id(collider2)]))
                                
                                if pair not in checked_pairs:
                                    checked_pairs.add(pair)
                                    self._process_collision_pair(collider1, collider2)
    
    def _process_collision_pair(self, collider1: Collider, collider2: Collider):
        """
        Process a collision pair with all checks.
        
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
    
    def optimize_performance(self):
        """
        Optimize physics performance by removing inactive colliders.
        """
        # Remove colliders from inactive game objects
        active_colliders = []
        for collider in self.colliders:
            if collider.game_object and collider.game_object.active:
                active_colliders.append(collider)
        
        removed_count = len(self.colliders) - len(active_colliders)
        self.colliders = active_colliders
        
        if removed_count > 0:
            print(f"Physics optimization: Removed {removed_count} inactive colliders")
    
    def set_spatial_grid_size(self, size: float):
        """
        Set the spatial grid size for collision optimization.
        
        Args:
            size: Grid cell size in world units
        """
        self.spatial_grid_size = size
