
"""
VoidRay Physics Engine
Core physics simulation and collision detection system.
"""

from typing import List, Callable, Optional, Set, Dict, Any
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
        self.gravity = Vector2(0, 0)  # No gravity by default
        self.colliders: List[Collider] = []
        self.collision_callbacks: List[Callable[[Collider, Collider, Dict[str, Any]], None]] = []
        self.spatial_grid_size = 128.0
        self.max_velocity = 2000.0
        self.time_scale = 1.0
        self.collision_iterations = 1  # Number of collision resolution iterations
        
        # Performance tracking
        self._collision_checks_this_frame = 0
        self._active_colliders_cache: List[Collider] = []
        self._cache_dirty = True
    
    def set_gravity(self, gravity: float):
        """
        Set gravity strength (positive for downward).
        
        Args:
            gravity: Gravity strength in pixels per second squared
        """
        self.gravity = Vector2(0, gravity)
    
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
            self._cache_dirty = True
    
    def remove_collider(self, collider: Collider):
        """
        Remove a collider from the physics simulation.
        
        Args:
            collider: The collider to remove
        """
        if collider in self.colliders:
            self.colliders.remove(collider)
            self._cache_dirty = True
    
    def add_collision_callback(self, callback: Callable[[Collider, Collider, Dict[str, Any]], None]):
        """
        Add a callback function that will be called when collisions occur.
        
        Args:
            callback: Function to call with (collider1, collider2, collision_info) parameters
        """
        self.collision_callbacks.append(callback)
    
    def update(self, delta_time: float):
        """
        Update physics simulation with optimizations.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Reset performance counters
        self._collision_checks_this_frame = 0
        
        # Update active colliders cache if needed
        if self._cache_dirty:
            self._update_active_colliders_cache()
        
        if not self._active_colliders_cache:
            return
        
        # Update all active colliders with rigidbodies
        for collider in self._active_colliders_cache:
            self._update_collider(collider, delta_time)
        
        # Perform collision detection and resolution
        for iteration in range(self.collision_iterations):
            self._check_collisions_optimized(self._active_colliders_cache)
    
    def _update_active_colliders_cache(self):
        """Update the cache of active colliders."""
        self._active_colliders_cache = [
            c for c in self.colliders 
            if c.game_object and c.game_object.active
        ]
        self._cache_dirty = False
    
    def _update_collider(self, collider: Collider, delta_time: float):
        """
        Update a single collider's physics.
        
        Args:
            collider: The collider to update
            delta_time: Time elapsed since last frame
        """
        if not collider.game_object:
            return
        
        # Try to get rigidbody component
        try:
            from .rigidbody import Rigidbody
            rigidbody = collider.game_object.get_component(Rigidbody)
            if rigidbody and not rigidbody.is_kinematic:
                # Apply gravity
                if rigidbody.use_gravity and self.gravity.magnitude() > 0:
                    rigidbody.add_force(self.gravity * rigidbody.mass)
                
                # Update rigidbody physics
                rigidbody.update(delta_time * self.time_scale)
                
                # Clamp velocity to max
                if rigidbody.velocity.magnitude() > self.max_velocity:
                    rigidbody.velocity = rigidbody.velocity.normalized() * self.max_velocity
        except ImportError:
            pass
    
    def _check_collisions_optimized(self, active_colliders: List[Collider]):
        """
        Optimized collision detection using spatial partitioning.
        
        Args:
            active_colliders: List of active colliders to check
        """
        # Spatial partitioning
        collision_grid: Dict[tuple, List[Collider]] = {}
        
        # Group colliders by grid cell
        for collider in active_colliders:
            if collider.game_object:
                pos = collider.get_world_position()
                bounds_radius = collider.get_bounds_radius()
                
                # Calculate grid cells this collider might occupy
                min_x = int((pos.x - bounds_radius) // self.spatial_grid_size)
                max_x = int((pos.x + bounds_radius) // self.spatial_grid_size)
                min_y = int((pos.y - bounds_radius) // self.spatial_grid_size)
                max_y = int((pos.y + bounds_radius) // self.spatial_grid_size)
                
                for grid_x in range(min_x, max_x + 1):
                    for grid_y in range(min_y, max_y + 1):
                        grid_key = (grid_x, grid_y)
                        if grid_key not in collision_grid:
                            collision_grid[grid_key] = []
                        collision_grid[grid_key].append(collider)
        
        # Check collisions within each grid cell
        checked_pairs: Set[tuple] = set()
        
        for colliders_in_cell in collision_grid.values():
            for i in range(len(colliders_in_cell)):
                for j in range(i + 1, len(colliders_in_cell)):
                    collider1, collider2 = colliders_in_cell[i], colliders_in_cell[j]
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
        
        # Skip if they're on incompatible layers
        if not self._should_collide(collider1, collider2):
            return
        
        # Increment collision check counter
        self._collision_checks_this_frame += 1
        
        # Get detailed collision information
        collision_info = collider1.get_collision_info(collider2)
        
        if collision_info:
            # Call global collision callbacks
            for callback in self.collision_callbacks:
                try:
                    callback(collider1, collider2, collision_info)
                except Exception as e:
                    print(f"Error in collision callback: {e}")
            
            # Call individual collider callbacks
            collider1.trigger_collision_event(collider2, collision_info)
            collider2.trigger_collision_event(collider1, collision_info)
            
            # Resolve collision if neither is a trigger
            if not collider1.is_trigger and not collider2.is_trigger:
                self._resolve_collision(collider1, collider2, collision_info)
    
    def _should_collide(self, collider1: Collider, collider2: Collider) -> bool:
        """
        Check if two colliders should collide based on their layers.
        
        Args:
            collider1: First collider
            collider2: Second collider
            
        Returns:
            True if they should collide, False otherwise
        """
        # Simple layer collision - can be extended with collision matrices
        return True
    
    def _resolve_collision(self, collider1: Collider, collider2: Collider, collision_info: Dict[str, Any]):
        """
        Resolve collision between two colliders.
        
        Args:
            collider1: First collider
            collider2: Second collider
            collision_info: Collision information
        """
        normal = collision_info.get('normal', Vector2(1, 0))
        penetration = collision_info.get('penetration', 0)
        
        if penetration <= 0:
            return
        
        # Get rigidbodies
        try:
            from .rigidbody import Rigidbody
            rb1 = collider1.game_object.get_component(Rigidbody) if collider1.game_object else None
            rb2 = collider2.game_object.get_component(Rigidbody) if collider2.game_object else None
        except ImportError:
            rb1 = rb2 = None
        
        # Positional correction
        correction_percent = 0.8  # Percentage of penetration to correct
        slop = 0.01  # Allowed penetration to prevent jitter
        
        correction_magnitude = max(penetration - slop, 0) * correction_percent
        
        if collider1.is_static and not collider2.is_static:
            # Only move collider2
            if collider2.game_object:
                correction = normal * correction_magnitude
                collider2.game_object.transform.position += correction
        elif collider2.is_static and not collider1.is_static:
            # Only move collider1
            if collider1.game_object:
                correction = -normal * correction_magnitude
                collider1.game_object.transform.position += correction
        elif not collider1.is_static and not collider2.is_static:
            # Move both objects
            total_mass = 1.0
            if rb1 and rb2:
                total_mass = rb1.mass + rb2.mass
                mass1_ratio = rb2.mass / total_mass
                mass2_ratio = rb1.mass / total_mass
            else:
                mass1_ratio = mass2_ratio = 0.5
            
            correction1 = -normal * correction_magnitude * mass1_ratio
            correction2 = normal * correction_magnitude * mass2_ratio
            
            if collider1.game_object:
                collider1.game_object.transform.position += correction1
            if collider2.game_object:
                collider2.game_object.transform.position += correction2
        
        # Velocity resolution
        if rb1 and rb2 and not rb1.is_kinematic and not rb2.is_kinematic:
            self._resolve_collision_velocities(rb1, rb2, normal)
    
    def _resolve_collision_velocities(self, rb1, rb2, normal: Vector2):
        """
        Resolve collision velocities using conservation of momentum.
        
        Args:
            rb1: First rigidbody
            rb2: Second rigidbody
            normal: Collision normal (pointing from rb1 to rb2)
        """
        # Calculate relative velocity
        relative_velocity = rb1.velocity - rb2.velocity
        
        # Calculate relative velocity along normal
        velocity_along_normal = relative_velocity.dot(normal)
        
        # Do not resolve if velocities are separating
        if velocity_along_normal > 0:
            return
        
        # Calculate restitution (bounciness)
        restitution = min(rb1.bounciness, rb2.bounciness)
        
        # Calculate impulse scalar
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        impulse_scalar /= (1 / rb1.mass) + (1 / rb2.mass)
        
        # Apply impulse
        impulse = normal * impulse_scalar
        rb1.velocity += impulse / rb1.mass
        rb2.velocity -= impulse / rb2.mass
        
        # Apply friction
        self._apply_friction(rb1, rb2, normal, impulse_scalar)
    
    def _apply_friction(self, rb1, rb2, normal: Vector2, normal_impulse: float):
        """
        Apply friction to the collision.
        
        Args:
            rb1: First rigidbody
            rb2: Second rigidbody
            normal: Collision normal
            normal_impulse: Normal impulse magnitude
        """
        # Calculate relative velocity
        relative_velocity = rb1.velocity - rb2.velocity
        
        # Calculate tangent vector
        tangent = relative_velocity - normal * relative_velocity.dot(normal)
        if tangent.magnitude() > 0.001:
            tangent = tangent.normalized()
        else:
            return
        
        # Calculate friction impulse
        friction_coefficient = (rb1.friction + rb2.friction) / 2
        friction_impulse = -relative_velocity.dot(tangent) / ((1 / rb1.mass) + (1 / rb2.mass))
        
        # Clamp friction impulse
        if abs(friction_impulse) > abs(normal_impulse * friction_coefficient):
            friction_impulse = normal_impulse * friction_coefficient * (-1 if friction_impulse > 0 else 1)
        
        # Apply friction impulse
        friction_vector = tangent * friction_impulse
        rb1.velocity += friction_vector / rb1.mass
        rb2.velocity -= friction_vector / rb2.mass
    
    def query_point(self, point: Vector2) -> List[Collider]:
        """
        Find all colliders that contain a specific point.
        
        Args:
            point: Point to query
            
        Returns:
            List of colliders containing the point
        """
        result = []
        for collider in self._active_colliders_cache:
            if collider.contains_point(point):
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
        for collider in self._active_colliders_cache:
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
        
        for collider in self._active_colliders_cache:
            # Simple ray-bounds intersection test
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
    
    def get_collision_count(self) -> int:
        """Get the number of collision checks performed this frame."""
        return self._collision_checks_this_frame
    
    def optimize_performance(self):
        """Optimize physics performance by cleaning up inactive colliders."""
        self._cache_dirty = True
        self._update_active_colliders_cache()
    
    def set_collision_iterations(self, iterations: int):
        """
        Set the number of collision resolution iterations per frame.
        
        Args:
            iterations: Number of iterations (higher = more accurate but slower)
        """
        self.collision_iterations = max(1, iterations)
    
    def set_spatial_grid_size(self, size: float):
        """
        Set the spatial grid size for collision optimization.
        
        Args:
            size: Grid cell size in pixels
        """
        self.spatial_grid_size = max(32.0, size)
