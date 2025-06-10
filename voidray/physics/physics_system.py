"""
VoidRay Physics System
High-level physics system that manages rigidbodies and coordinates with the physics engine.
"""

from typing import List, Set, Optional, Callable, Dict
from ..math.vector2 import Vector2
from .rigidbody import Rigidbody
from .physics_engine import PhysicsEngine


class PhysicsSystem:
    """
    High-level physics system that manages rigidbodies and integrates with the physics engine.
    """

    def __init__(self):
        """Initialize the physics system."""
        self.rigidbodies: List[Rigidbody] = []
        self.physics_engine: Optional[PhysicsEngine] = None
        self.gravity = Vector2(0, 981)  # Default gravity in pixels per second squared
        self.time_scale = 1.0
        self.sleeping_threshold = 0.1  # Velocity threshold for putting objects to sleep
        self.sleep_time_threshold = 1.0  # Time threshold for sleeping
        
        # Collision callbacks
        self.collision_callbacks: Dict[str, List[Callable]] = {
            'collision_enter': [],
            'collision_stay': [],
            'collision_exit': []
        }

    def set_physics_engine(self, physics_engine: PhysicsEngine):
        """Set the physics engine to coordinate with."""
        self.physics_engine = physics_engine

    def add_rigidbody(self, rigidbody: Rigidbody):
        """
        Add a rigidbody to the physics system.

        Args:
            rigidbody: The rigidbody to add
        """
        if rigidbody not in self.rigidbodies:
            self.rigidbodies.append(rigidbody)

    def remove_rigidbody(self, rigidbody: Rigidbody):
        """
        Remove a rigidbody from the physics system.

        Args:
            rigidbody: The rigidbody to remove
        """
        if rigidbody in self.rigidbodies:
            self.rigidbodies.remove(rigidbody)

    def set_gravity(self, gravity: Vector2):
        """
        Set the global gravity.

        Args:
            gravity: Gravity vector in pixels per second squared
        """
        self.gravity = gravity
        if self.physics_engine:
            self.physics_engine.set_gravity(gravity.y)

    def update(self, delta_time: float):
        """
        Update all rigidbodies in the system.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        scaled_delta = delta_time * self.time_scale

        # Update all active rigidbodies
        active_rigidbodies = [rb for rb in self.rigidbodies if rb.enabled and not rb.is_sleeping]

        for rigidbody in active_rigidbodies:
            if not rigidbody.is_kinematic:
                # Apply gravity if enabled
                if rigidbody.use_gravity:
                    rigidbody.add_force(self.gravity * rigidbody.mass)

                # Update rigidbody
                rigidbody.update(scaled_delta)

                # Check for sleeping
                self._check_sleeping(rigidbody, scaled_delta)

        # Wake up sleeping rigidbodies if they have forces applied
        sleeping_rigidbodies = [rb for rb in self.rigidbodies if rb.is_sleeping]
        for rigidbody in sleeping_rigidbodies:
            if rigidbody.accumulated_force.magnitude() > 0.1:
                self._wake_up(rigidbody)

    def _check_sleeping(self, rigidbody: Rigidbody, delta_time: float):
        """Check if a rigidbody should go to sleep."""
        if rigidbody.velocity.magnitude() < self.sleeping_threshold:
            rigidbody.sleep_timer += delta_time
            if rigidbody.sleep_timer >= self.sleep_time_threshold:
                self._put_to_sleep(rigidbody)
        else:
            rigidbody.sleep_timer = 0.0

    def _put_to_sleep(self, rigidbody: Rigidbody):
        """Put a rigidbody to sleep."""
        rigidbody.is_sleeping = True
        rigidbody.velocity = Vector2(0, 0)
        rigidbody.angular_velocity = 0.0
        print(f"Rigidbody {rigidbody} went to sleep")

    def _wake_up(self, rigidbody: Rigidbody):
        """Wake up a sleeping rigidbody."""
        rigidbody.is_sleeping = False
        rigidbody.sleep_timer = 0.0
        print(f"Rigidbody {rigidbody} woke up")

    def apply_impulse_to_area(self, center: Vector2, radius: float, impulse: Vector2):
        """
        Apply an impulse to all rigidbodies in a circular area.

        Args:
            center: Center of the area
            radius: Radius of the area
            impulse: Impulse to apply
        """
        for rigidbody in self.rigidbodies:
            if rigidbody.game_object and rigidbody.game_object.transform:
                position = rigidbody.game_object.transform.position
                distance = (position - center).magnitude()

                if distance <= radius:
                    # Apply impulse with falloff based on distance
                    falloff = 1.0 - (distance / radius)
                    scaled_impulse = impulse * falloff
                    rigidbody.add_impulse(scaled_impulse)

                    # Wake up if sleeping
                    if rigidbody.is_sleeping:
                        self._wake_up(rigidbody)

    def get_rigidbodies_in_area(self, center: Vector2, radius: float) -> List[Rigidbody]:
        """
        Get all rigidbodies within a circular area.

        Args:
            center: Center of the area
            radius: Radius of the area

        Returns:
            List of rigidbodies in the area
        """
        result = []
        for rigidbody in self.rigidbodies:
            if rigidbody.game_object and rigidbody.game_object.transform:
                position = rigidbody.game_object.transform.position
                distance = (position - center).magnitude()

                if distance <= radius:
                    result.append(rigidbody)

        return result

    def get_statistics(self) -> dict:
        """Get physics system statistics."""
        active_count = len([rb for rb in self.rigidbodies if not rb.is_sleeping])
        sleeping_count = len([rb for rb in self.rigidbodies if rb.is_sleeping])

        return {
            'total_rigidbodies': len(self.rigidbodies),
            'active_rigidbodies': active_count,
            'sleeping_rigidbodies': sleeping_count,
            'gravity': (self.gravity.x, self.gravity.y),
            'time_scale': self.time_scale
        }

    def add_collision_callback(self, event_type: str, callback: Callable):
        """
        Add a collision callback.
        
        Args:
            event_type: 'collision_enter', 'collision_stay', or 'collision_exit'
            callback: Function to call on collision
        """
        if event_type in self.collision_callbacks:
            self.collision_callbacks[event_type].append(callback)

    def remove_collision_callback(self, event_type: str, callback: Callable):
        """Remove a collision callback."""
        if event_type in self.collision_callbacks and callback in self.collision_callbacks[event_type]:
            self.collision_callbacks[event_type].remove(callback)

    def _trigger_collision_events(self, collision_data: Dict):
        """Trigger collision events."""
        for callback in self.collision_callbacks.get('collision_enter', []):
            try:
                callback(collision_data)
            except Exception as e:
                print(f"Error in collision callback: {e}")

    def optimize_performance(self):
        """Optimize physics performance by removing inactive rigidbodies."""
        before_count = len(self.rigidbodies)

        # Remove rigidbodies that no longer have game objects
        self.rigidbodies = [rb for rb in self.rigidbodies if rb.game_object is not None]

        removed_count = before_count - len(self.rigidbodies)
        if removed_count > 0:
            print(f"Physics optimization: Removed {removed_count} orphaned rigidbodies")