
"""
VoidRay Advanced Physics Engine
Enhanced physics simulation with optimized collision detection, advanced features, and improved performance.
"""

from typing import List, Callable, Optional, Set, Dict, Any, Tuple
from ..math.vector2 import Vector2
from .collider import Collider
import time


class PhysicsEngine:
    """
    Advanced physics engine with optimized collision detection and enhanced features.
    """
    
    def __init__(self):
        """Initialize the advanced physics engine."""
        self.gravity = Vector2(0, 0)
        self.colliders: List[Collider] = []
        self.collision_callbacks: List[Callable[[Collider, Collider, Dict[str, Any]], None]] = []
        
        # Advanced spatial partitioning
        self.spatial_grid_size = 64.0
        self.spatial_grid: Dict[Tuple[int, int], List[Collider]] = {}
        
        # Performance optimizations
        self.max_velocity = 2000.0
        self.time_scale = 1.0
        self.collision_iterations = 2
        self.position_correction_percent = 0.8
        self.penetration_slop = 0.01
        
        # Advanced features
        self.enable_continuous_collision = True
        self.enable_sleeping = True
        self.sleep_velocity_threshold = 0.5
        self.sleep_time_threshold = 1.0
        
        # Performance tracking
        self._collision_checks_this_frame = 0
        self._active_colliders_cache: List[Collider] = []
        self._sleeping_colliders: Set[Collider] = set()
        self._cache_dirty = True
        self._frame_time = 0.0
        
        # Collision resolution improvements
        self.restitution_threshold = 1.0
        self.friction_combine_mode = "average"  # "average", "multiply", "min", "max"
        
        print("Advanced Physics Engine initialized")

    def set_gravity(self, gravity: float):
        """Set gravity strength (positive for downward)."""
        self.gravity = Vector2(0, gravity)

    def set_advanced_settings(self, **kwargs):
        """Configure advanced physics settings."""
        if 'continuous_collision' in kwargs:
            self.enable_continuous_collision = kwargs['continuous_collision']
        if 'sleeping' in kwargs:
            self.enable_sleeping = kwargs['sleeping']
        if 'sleep_threshold' in kwargs:
            self.sleep_velocity_threshold = kwargs['sleep_threshold']
        if 'iterations' in kwargs:
            self.collision_iterations = max(1, kwargs['iterations'])
        if 'grid_size' in kwargs:
            self.spatial_grid_size = max(32.0, kwargs['grid_size'])

    def add_collider(self, collider: Collider):
        """Add a collider with enhanced tracking."""
        if collider not in self.colliders:
            self.colliders.append(collider)
            self._cache_dirty = True
            # Initialize sleep state
            if hasattr(collider, 'sleep_timer'):
                collider.sleep_timer = 0.0
                collider.is_sleeping = False

    def remove_collider(self, collider: Collider):
        """Remove a collider with cleanup."""
        if collider in self.colliders:
            self.colliders.remove(collider)
            self._sleeping_colliders.discard(collider)
            self._cache_dirty = True
            # Clear from spatial grid
            self._remove_from_spatial_grid(collider)

    def update(self, delta_time: float):
        """Enhanced physics update with advanced features."""
        start_time = time.perf_counter()
        
        # Reset performance counters
        self._collision_checks_this_frame = 0
        
        # Update caches if needed
        if self._cache_dirty:
            self._update_active_colliders_cache()
            self._rebuild_spatial_grid()
        
        if not self._active_colliders_cache:
            return
        
        # Wake up sleeping colliders if forces are applied
        self._check_wake_conditions()
        
        # Update physics for active colliders
        for collider in self._active_colliders_cache:
            if collider not in self._sleeping_colliders:
                self._update_collider_physics(collider, delta_time)
        
        # Multiple iteration collision resolution
        for iteration in range(self.collision_iterations):
            self._perform_collision_detection()
            if iteration < self.collision_iterations - 1:
                self._update_spatial_grid()
        
        # Check for sleeping colliders
        if self.enable_sleeping:
            self._check_sleeping_conditions(delta_time)
        
        # Performance tracking
        self._frame_time = time.perf_counter() - start_time

    def _update_active_colliders_cache(self):
        """Update the cache of active colliders with better filtering."""
        self._active_colliders_cache = [
            c for c in self.colliders 
            if (c.game_object and c.game_object.active and 
                not getattr(c, 'is_destroyed', False))
        ]
        self._cache_dirty = False

    def _rebuild_spatial_grid(self):
        """Rebuild the spatial partitioning grid."""
        self.spatial_grid.clear()
        for collider in self._active_colliders_cache:
            self._add_to_spatial_grid(collider)

    def _update_spatial_grid(self):
        """Update spatial grid for moved objects."""
        for collider in self._active_colliders_cache:
            if collider not in self._sleeping_colliders:
                self._remove_from_spatial_grid(collider)
                self._add_to_spatial_grid(collider)

    def _add_to_spatial_grid(self, collider: Collider):
        """Add collider to spatial grid."""
        if not collider.game_object:
            return
            
        pos = collider.get_world_position()
        bounds_radius = collider.get_bounds_radius()
        
        # Calculate grid cells
        min_x = int((pos.x - bounds_radius) // self.spatial_grid_size)
        max_x = int((pos.x + bounds_radius) // self.spatial_grid_size)
        min_y = int((pos.y - bounds_radius) // self.spatial_grid_size)
        max_y = int((pos.y + bounds_radius) // self.spatial_grid_size)
        
        for grid_x in range(min_x, max_x + 1):
            for grid_y in range(min_y, max_y + 1):
                grid_key = (grid_x, grid_y)
                if grid_key not in self.spatial_grid:
                    self.spatial_grid[grid_key] = []
                if collider not in self.spatial_grid[grid_key]:
                    self.spatial_grid[grid_key].append(collider)

    def _remove_from_spatial_grid(self, collider: Collider):
        """Remove collider from spatial grid."""
        keys_to_clean = []
        for grid_key, colliders in self.spatial_grid.items():
            if collider in colliders:
                colliders.remove(collider)
                if not colliders:
                    keys_to_clean.append(grid_key)
        
        for key in keys_to_clean:
            del self.spatial_grid[key]

    def _update_collider_physics(self, collider: Collider, delta_time: float):
        """Enhanced collider physics update."""
        if not collider.game_object:
            return
        
        try:
            from .rigidbody import Rigidbody
            rigidbody = collider.game_object.get_component(Rigidbody)
            if rigidbody and not rigidbody.is_kinematic:
                # Apply gravity
                if rigidbody.use_gravity and self.gravity.magnitude() > 0:
                    rigidbody.add_force(self.gravity * rigidbody.mass)
                
                # Store previous position for continuous collision detection
                if self.enable_continuous_collision:
                    rigidbody.previous_position = rigidbody.game_object.transform.position
                
                # Update rigidbody physics
                rigidbody.update(delta_time * self.time_scale)
                
                # Velocity limiting
                if rigidbody.velocity.magnitude() > self.max_velocity:
                    rigidbody.velocity = rigidbody.velocity.normalized() * self.max_velocity
                
                # Advanced damping
                self._apply_advanced_damping(rigidbody, delta_time)
                
        except ImportError:
            pass

    def _apply_advanced_damping(self, rigidbody, delta_time: float):
        """Apply advanced damping effects."""
        # Air resistance (quadratic drag)
        if rigidbody.velocity.magnitude() > 0:
            drag_force = rigidbody.velocity.normalized() * -rigidbody.drag * rigidbody.velocity.magnitude_squared()
            rigidbody.add_force(drag_force * delta_time)
        
        # Angular damping
        if hasattr(rigidbody, 'angular_velocity') and hasattr(rigidbody, 'angular_drag'):
            rigidbody.angular_velocity *= (1.0 - rigidbody.angular_drag * delta_time)

    def _perform_collision_detection(self):
        """Enhanced collision detection with spatial partitioning."""
        checked_pairs: Set[Tuple[int, int]] = set()
        
        for grid_colliders in self.spatial_grid.values():
            if len(grid_colliders) < 2:
                continue
                
            for i in range(len(grid_colliders)):
                for j in range(i + 1, len(grid_colliders)):
                    collider1, collider2 = grid_colliders[i], grid_colliders[j]
                    
                    # Create unique pair ID
                    pair_id = (min(id(collider1), id(collider2)), max(id(collider1), id(collider2)))
                    
                    if pair_id not in checked_pairs:
                        checked_pairs.add(pair_id)
                        
                        # Skip sleeping pairs
                        if (collider1 in self._sleeping_colliders and 
                            collider2 in self._sleeping_colliders):
                            continue
                        
                        self._process_collision_pair(collider1, collider2)

    def _process_collision_pair(self, collider1: Collider, collider2: Collider):
        """Enhanced collision pair processing."""
        # Broad phase checks
        if not self._should_process_collision(collider1, collider2):
            return
        
        self._collision_checks_this_frame += 1
        
        # Enhanced collision detection
        collision_info = self._get_enhanced_collision_info(collider1, collider2)
        
        if collision_info:
            # Wake up sleeping colliders
            if collider1 in self._sleeping_colliders:
                self._wake_collider(collider1)
            if collider2 in self._sleeping_colliders:
                self._wake_collider(collider2)
            
            # Trigger callbacks
            self._trigger_collision_callbacks(collider1, collider2, collision_info)
            
            # Resolve collision
            if not collider1.is_trigger and not collider2.is_trigger:
                self._resolve_enhanced_collision(collider1, collider2, collision_info)

    def _should_process_collision(self, collider1: Collider, collider2: Collider) -> bool:
        """Enhanced collision filtering."""
        # Basic checks
        if collider1.is_static and collider2.is_static:
            return False
        
        if (not collider1.game_object or not collider1.game_object.active or
            not collider2.game_object or not collider2.game_object.active):
            return False
        
        # Layer-based collision matrix (can be extended)
        return self._check_collision_layers(collider1, collider2)

    def _check_collision_layers(self, collider1: Collider, collider2: Collider) -> bool:
        """Check if colliders should collide based on layers."""
        # Default implementation - can be extended with collision matrix
        layer1 = getattr(collider1, 'collision_layer', 0)
        layer2 = getattr(collider2, 'collision_layer', 0)
        
        # For now, allow all layer collisions
        return True

    def _get_enhanced_collision_info(self, collider1: Collider, collider2: Collider) -> Optional[Dict[str, Any]]:
        """Get enhanced collision information."""
        collision_info = collider1.get_collision_info(collider2)
        
        if collision_info and self.enable_continuous_collision:
            # Add continuous collision detection data
            collision_info.update(self._get_continuous_collision_info(collider1, collider2))
        
        return collision_info

    def _get_continuous_collision_info(self, collider1: Collider, collider2: Collider) -> Dict[str, Any]:
        """Calculate continuous collision detection information."""
        continuous_info = {}
        
        try:
            from .rigidbody import Rigidbody
            rb1 = collider1.game_object.get_component(Rigidbody) if collider1.game_object else None
            rb2 = collider2.game_object.get_component(Rigidbody) if collider2.game_object else None
            
            if rb1 and hasattr(rb1, 'previous_position'):
                continuous_info['rb1_movement'] = rb1.game_object.transform.position - rb1.previous_position
            if rb2 and hasattr(rb2, 'previous_position'):
                continuous_info['rb2_movement'] = rb2.game_object.transform.position - rb2.previous_position
                
        except ImportError:
            pass
        
        return continuous_info

    def _resolve_enhanced_collision(self, collider1: Collider, collider2: Collider, collision_info: Dict[str, Any]):
        """Enhanced collision resolution with improved physics."""
        normal = collision_info.get('normal', Vector2(1, 0))
        penetration = collision_info.get('penetration', 0)
        
        if penetration <= self.penetration_slop:
            return
        
        # Get rigidbodies
        try:
            from .rigidbody import Rigidbody
            rb1 = collider1.game_object.get_component(Rigidbody) if collider1.game_object else None
            rb2 = collider2.game_object.get_component(Rigidbody) if collider2.game_object else None
        except ImportError:
            rb1 = rb2 = None
        
        # Enhanced positional correction
        self._resolve_position_correction(collider1, collider2, normal, penetration, rb1, rb2)
        
        # Enhanced velocity resolution
        if rb1 and rb2:
            self._resolve_enhanced_velocities(rb1, rb2, normal, collision_info)

    def _resolve_position_correction(self, collider1: Collider, collider2: Collider, 
                                   normal: Vector2, penetration: float, rb1, rb2):
        """Enhanced position correction with mass consideration."""
        correction_magnitude = max(penetration - self.penetration_slop, 0) * self.position_correction_percent
        
        if collider1.is_static and not collider2.is_static:
            correction = normal * correction_magnitude
            if collider2.game_object:
                collider2.game_object.transform.position += correction
        elif collider2.is_static and not collider1.is_static:
            correction = -normal * correction_magnitude
            if collider1.game_object:
                collider1.game_object.transform.position += correction
        elif not collider1.is_static and not collider2.is_static:
            # Mass-based correction
            if rb1 and rb2:
                total_inv_mass = (1.0 / rb1.mass) + (1.0 / rb2.mass)
                if total_inv_mass > 0:
                    correction1 = -normal * correction_magnitude * (1.0 / rb1.mass) / total_inv_mass
                    correction2 = normal * correction_magnitude * (1.0 / rb2.mass) / total_inv_mass
                else:
                    correction1 = correction2 = Vector2.zero()
            else:
                correction1 = -normal * correction_magnitude * 0.5
                correction2 = normal * correction_magnitude * 0.5
            
            if collider1.game_object:
                collider1.game_object.transform.position += correction1
            if collider2.game_object:
                collider2.game_object.transform.position += correction2

    def _resolve_enhanced_velocities(self, rb1, rb2, normal: Vector2, collision_info: Dict[str, Any]):
        """Enhanced velocity resolution with improved physics."""
        # Calculate relative velocity
        relative_velocity = rb1.velocity - rb2.velocity
        velocity_along_normal = relative_velocity.dot(normal)
        
        # Skip if separating
        if velocity_along_normal > 0:
            return
        
        # Enhanced restitution calculation
        restitution = self._calculate_restitution(rb1, rb2, velocity_along_normal)
        
        # Calculate impulse with enhanced mass handling
        inv_mass1 = 1.0 / rb1.mass if rb1.mass > 0 else 0
        inv_mass2 = 1.0 / rb2.mass if rb2.mass > 0 else 0
        
        impulse_scalar = -(1 + restitution) * velocity_along_normal / (inv_mass1 + inv_mass2)
        
        # Apply impulse
        impulse = normal * impulse_scalar
        if not rb1.is_kinematic:
            rb1.velocity += impulse * inv_mass1
        if not rb2.is_kinematic:
            rb2.velocity -= impulse * inv_mass2
        
        # Enhanced friction
        self._apply_enhanced_friction(rb1, rb2, normal, impulse_scalar, relative_velocity)

    def _calculate_restitution(self, rb1, rb2, velocity_along_normal: float) -> float:
        """Calculate restitution with threshold."""
        base_restitution = min(rb1.bounciness, rb2.bounciness)
        
        # Apply restitution threshold
        if abs(velocity_along_normal) < self.restitution_threshold:
            return 0.0
        
        return base_restitution

    def _apply_enhanced_friction(self, rb1, rb2, normal: Vector2, normal_impulse: float, relative_velocity: Vector2):
        """Enhanced friction with multiple combination modes."""
        # Calculate tangent
        tangent = relative_velocity - normal * relative_velocity.dot(normal)
        if tangent.magnitude() < 0.001:
            return
        
        tangent = tangent.normalized()
        
        # Combine friction coefficients
        friction = self._combine_friction(rb1.friction, rb2.friction)
        
        # Calculate friction impulse
        inv_mass1 = 1.0 / rb1.mass if rb1.mass > 0 else 0
        inv_mass2 = 1.0 / rb2.mass if rb2.mass > 0 else 0
        
        friction_impulse = -relative_velocity.dot(tangent) / (inv_mass1 + inv_mass2)
        
        # Coulomb friction
        max_friction = abs(normal_impulse * friction)
        if abs(friction_impulse) > max_friction:
            friction_impulse = max_friction * (-1 if friction_impulse > 0 else 1)
        
        # Apply friction
        friction_vector = tangent * friction_impulse
        if not rb1.is_kinematic:
            rb1.velocity += friction_vector * inv_mass1
        if not rb2.is_kinematic:
            rb2.velocity -= friction_vector * inv_mass2

    def _combine_friction(self, friction1: float, friction2: float) -> float:
        """Combine friction coefficients using specified mode."""
        if self.friction_combine_mode == "average":
            return (friction1 + friction2) / 2
        elif self.friction_combine_mode == "multiply":
            return friction1 * friction2
        elif self.friction_combine_mode == "min":
            return min(friction1, friction2)
        elif self.friction_combine_mode == "max":
            return max(friction1, friction2)
        else:
            return (friction1 + friction2) / 2

    def _check_wake_conditions(self):
        """Check if sleeping colliders should wake up."""
        for collider in list(self._sleeping_colliders):
            if self._should_wake_collider(collider):
                self._wake_collider(collider)

    def _should_wake_collider(self, collider: Collider) -> bool:
        """Check if a collider should wake up."""
        try:
            from .rigidbody import Rigidbody
            rigidbody = collider.game_object.get_component(Rigidbody) if collider.game_object else None
            if rigidbody:
                # Wake if forces are applied
                if hasattr(rigidbody, 'accumulated_force') and rigidbody.accumulated_force.magnitude() > 0.1:
                    return True
                
                # Wake if velocity is above threshold
                if rigidbody.velocity.magnitude() > self.sleep_velocity_threshold:
                    return True
        except ImportError:
            pass
        
        return False

    def _wake_collider(self, collider: Collider):
        """Wake up a sleeping collider."""
        self._sleeping_colliders.discard(collider)
        if hasattr(collider, 'sleep_timer'):
            collider.sleep_timer = 0.0
            collider.is_sleeping = False

    def _check_sleeping_conditions(self, delta_time: float):
        """Check which colliders should go to sleep."""
        for collider in self._active_colliders_cache:
            if collider in self._sleeping_colliders:
                continue
            
            try:
                from .rigidbody import Rigidbody
                rigidbody = collider.game_object.get_component(Rigidbody) if collider.game_object else None
                if rigidbody and not rigidbody.is_kinematic:
                    if rigidbody.velocity.magnitude() < self.sleep_velocity_threshold:
                        if not hasattr(collider, 'sleep_timer'):
                            collider.sleep_timer = 0.0
                        collider.sleep_timer += delta_time
                        
                        if collider.sleep_timer >= self.sleep_time_threshold:
                            self._put_collider_to_sleep(collider)
                    else:
                        if hasattr(collider, 'sleep_timer'):
                            collider.sleep_timer = 0.0
            except ImportError:
                pass

    def _put_collider_to_sleep(self, collider: Collider):
        """Put a collider to sleep."""
        self._sleeping_colliders.add(collider)
        if hasattr(collider, 'is_sleeping'):
            collider.is_sleeping = True
        
        # Zero out small velocities
        try:
            from .rigidbody import Rigidbody
            rigidbody = collider.game_object.get_component(Rigidbody) if collider.game_object else None
            if rigidbody:
                rigidbody.velocity = Vector2.zero()
                if hasattr(rigidbody, 'angular_velocity'):
                    rigidbody.angular_velocity = 0.0
        except ImportError:
            pass

    def _trigger_collision_callbacks(self, collider1: Collider, collider2: Collider, collision_info: Dict[str, Any]):
        """Trigger collision callbacks with error handling."""
        # Global callbacks
        for callback in self.collision_callbacks:
            try:
                callback(collider1, collider2, collision_info)
            except Exception as e:
                print(f"Error in collision callback: {e}")
        
        # Individual collider callbacks
        try:
            collider1.trigger_collision_event(collider2, collision_info)
            collider2.trigger_collision_event(collider1, collision_info)
        except Exception as e:
            print(f"Error in collider callback: {e}")

    # Enhanced query methods
    def raycast_enhanced(self, start: Vector2, direction: Vector2, max_distance: float = float('inf'), 
                        layer_mask: int = -1) -> Optional[Dict[str, Any]]:
        """Enhanced raycast with detailed hit information."""
        closest_hit = None
        closest_distance = max_distance
        
        for collider in self._active_colliders_cache:
            if layer_mask != -1:
                collider_layer = getattr(collider, 'collision_layer', 0)
                if not (layer_mask & (1 << collider_layer)):
                    continue
            
            # Enhanced ray-collider intersection
            hit_info = self._raycast_collider(start, direction, collider, closest_distance)
            if hit_info and hit_info['distance'] < closest_distance:
                closest_distance = hit_info['distance']
                closest_hit = hit_info
        
        return closest_hit

    def _raycast_collider(self, start: Vector2, direction: Vector2, collider: Collider, max_distance: float) -> Optional[Dict[str, Any]]:
        """Perform raycast against a single collider with proper shape detection."""
        # Enhanced raycast for different collider types
        from .collision import BoxCollider, CircleCollider
        
        if isinstance(collider, CircleCollider):
            return self._raycast_circle(start, direction, collider, max_distance)
        elif isinstance(collider, BoxCollider):
            return self._raycast_box(start, direction, collider, max_distance)
        else:
            # Fallback to simple sphere test
            to_collider = collider.get_world_position() - start
            projection = to_collider.dot(direction)
            
            if 0 <= projection <= max_distance:
                closest_point = start + direction * projection
                distance_to_center = (closest_point - collider.get_world_position()).magnitude()
                
                if distance_to_center <= collider.get_bounds_radius():
                    return {
                        'collider': collider,
                        'distance': projection,
                        'point': closest_point,
                        'normal': (closest_point - collider.get_world_position()).normalized()
                    }
            
            return None
    
    def _raycast_circle(self, start: Vector2, direction: Vector2, collider, max_distance: float) -> Optional[Dict[str, Any]]:
        """Raycast against a circle collider."""
        center = collider.get_world_position()
        radius = collider.radius
        
        # Ray-circle intersection
        to_center = center - start
        projection = to_center.dot(direction)
        
        if projection < 0:
            return None
        
        closest_point = start + direction * projection
        distance_to_center = (closest_point - center).magnitude()
        
        if distance_to_center <= radius:
            # Calculate actual intersection point
            offset = (radius * radius - distance_to_center * distance_to_center) ** 0.5
            hit_distance = projection - offset
            
            if 0 <= hit_distance <= max_distance:
                hit_point = start + direction * hit_distance
                normal = (hit_point - center).normalized()
                
                return {
                    'collider': collider,
                    'distance': hit_distance,
                    'point': hit_point,
                    'normal': normal
                }
        
        return None
    
    def _raycast_box(self, start: Vector2, direction: Vector2, collider, max_distance: float) -> Optional[Dict[str, Any]]:
        """Raycast against a box collider."""
        center = collider.get_world_position()
        half_size = Vector2(collider.width / 2, collider.height / 2)
        
        # AABB ray intersection
        min_point = center - half_size
        max_point = center + half_size
        
        t_min = 0
        t_max = max_distance
        
        # Check X slab
        if abs(direction.x) < 1e-8:
            if start.x < min_point.x or start.x > max_point.x:
                return None
        else:
            t1 = (min_point.x - start.x) / direction.x
            t2 = (max_point.x - start.x) / direction.x
            
            if t1 > t2:
                t1, t2 = t2, t1
            
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
            
            if t_min > t_max:
                return None
        
        # Check Y slab
        if abs(direction.y) < 1e-8:
            if start.y < min_point.y or start.y > max_point.y:
                return None
        else:
            t1 = (min_point.y - start.y) / direction.y
            t2 = (max_point.y - start.y) / direction.y
            
            if t1 > t2:
                t1, t2 = t2, t1
            
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
            
            if t_min > t_max:
                return None
        
        if t_min >= 0:
            hit_point = start + direction * t_min
            # Calculate normal based on which face was hit
            diff = hit_point - center
            
            if abs(diff.x) > abs(diff.y):
                normal = Vector2(1 if diff.x > 0 else -1, 0)
            else:
                normal = Vector2(0, 1 if diff.y > 0 else -1)
            
            return {
                'collider': collider,
                'distance': t_min,
                'point': hit_point,
                'normal': normal
            }
        
        return None

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get detailed performance statistics."""
        return {
            'collision_checks': self._collision_checks_this_frame,
            'active_colliders': len(self._active_colliders_cache),
            'sleeping_colliders': len(self._sleeping_colliders),
            'spatial_grid_cells': len(self.spatial_grid),
            'frame_time_ms': self._frame_time * 1000,
            'total_colliders': len(self.colliders),
            'gravity': (self.gravity.x, self.gravity.y),
            'time_scale': self.time_scale
        }

    def optimize_performance(self):
        """Comprehensive performance optimization."""
        # Clean up destroyed objects
        before_count = len(self.colliders)
        self.colliders = [c for c in self.colliders if c.game_object is not None]
        removed_count = before_count - len(self.colliders)
        
        # Rebuild caches
        self._cache_dirty = True
        self._update_active_colliders_cache()
        self._rebuild_spatial_grid()
        
        # Clean up sleeping colliders set
        self._sleeping_colliders = {c for c in self._sleeping_colliders if c in self.colliders}
        
        if removed_count > 0:
            print(f"Physics optimization: Removed {removed_count} orphaned colliders")

    def debug_draw_spatial_grid(self, renderer):
        """Draw spatial grid for debugging."""
        from ..graphics.renderer import Color
        
        for (grid_x, grid_y), colliders in self.spatial_grid.items():
            if colliders:
                x = grid_x * self.spatial_grid_size
                y = grid_y * self.spatial_grid_size
                
                renderer.draw_rect(
                    Vector2(x, y),
                    Vector2(self.spatial_grid_size, self.spatial_grid_size),
                    Color.GREEN if len(colliders) == 1 else Color.YELLOW,
                    filled=False
                )
