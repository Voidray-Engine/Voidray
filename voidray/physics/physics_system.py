"""
VoidRay Physics System
High-level physics system that manages rigidbodies and coordinates with the physics engine.
"""

from typing import List, Set
from ..math.vector2 import Vector2
from .rigidbody import Rigidbody
from .physics_engine import PhysicsEngine


class PhysicsSystem:
    """
    High-level physics system that manages rigidbodies and physics simulation.
    This coordinates with the PhysicsEngine for collision detection.
    """

    def __init__(self):
        self.rigidbodies: List[Rigidbody] = []
        self.physics_engine = PhysicsEngine()
        self.sleeping_bodies: Set[Rigidbody] = set()
        self.time_accumulator = 0.0
        self.fixed_timestep = 1.0 / 60.0  # 60 FPS physics
        self.max_fixed_updates_per_frame = 4  # Prevent spiral of death

    def set_gravity(self, gravity: float):
        """
        Set gravity strength.

        Args:
            gravity: Gravity strength (positive for downward)
        """
        self.physics_engine.set_gravity(gravity)

    def add_rigidbody(self, rigidbody: Rigidbody):
        """
        Add a rigidbody to the physics simulation.

        Args:
            rigidbody: The rigidbody to add
        """
        if rigidbody not in self.rigidbodies:
            self.rigidbodies.append(rigidbody)

    def remove_rigidbody(self, rigidbody: Rigidbody):
        """
        Remove a rigidbody from the physics simulation.

        Args:
            rigidbody: The rigidbody to remove
        """
        if rigidbody in self.rigidbodies:
            self.rigidbodies.remove(rigidbody)
        if rigidbody in self.sleeping_bodies:
            self.sleeping_bodies.remove(rigidbody)

    def add_collider(self, collider):
        """
        Add a collider to the physics simulation.

        Args:
            collider: The collider to add
        """
        self.physics_engine.add_collider(collider)

    def remove_collider(self, collider):
        """
        Remove a collider from the physics simulation.

        Args:
            collider: The collider to remove
        """
        self.physics_engine.remove_collider(collider)

    def update(self, delta_time: float):
        """
        Update the physics simulation.

        Args:
            delta_time: Time elapsed since last frame
        """
        # Clamp delta_time to prevent instability
        delta_time = min(delta_time, 0.1)

        # Accumulate time for fixed timestep
        self.time_accumulator += delta_time

        # Process fixed timestep updates
        updates_performed = 0
        while (self.time_accumulator >= self.fixed_timestep and 
               updates_performed < self.max_fixed_updates_per_frame):
            self._fixed_update(self.fixed_timestep)
            self.time_accumulator -= self.fixed_timestep
            updates_performed += 1

        # Update physics engine (handles collisions)
        self.physics_engine.update(delta_time)

        # Clean up sleeping bodies periodically
        if updates_performed > 0:
            self._update_sleeping_bodies()

    def _fixed_update(self, fixed_delta: float):
        """
        Fixed timestep physics update for rigidbodies.

        Args:
            fixed_delta: Fixed timestep duration
        """
        # Update active rigidbodies
        active_bodies = [rb for rb in self.rigidbodies if rb not in self.sleeping_bodies]

        for rigidbody in active_bodies:
            if rigidbody.game_object and rigidbody.game_object.active and not rigidbody.is_kinematic:
                # Rigidbody handles its own update now
                rigidbody.update(fixed_delta)

    def _update_sleeping_bodies(self):
        """Update sleeping state of rigidbodies."""
        for rigidbody in list(self.rigidbodies):
            if rigidbody in self.sleeping_bodies:
                continue

            if (rigidbody.velocity.magnitude() < 0.1 and 
                abs(rigidbody.angular_velocity) < 0.1):
                rigidbody.sleep_timer += self.fixed_timestep
                if rigidbody.sleep_timer > 1.0:  # Sleep after 1 second of low movement
                    self.sleeping_bodies.add(rigidbody)
            else:
                rigidbody.sleep_timer = 0.0

    def wake_rigidbody(self, rigidbody: Rigidbody):
        """
        Wake up a sleeping rigidbody.

        Args:
            rigidbody: The rigidbody to wake
        """
        if rigidbody in self.sleeping_bodies:
            self.sleeping_bodies.remove(rigidbody)
            rigidbody.sleep_timer = 0.0

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
            if rigidbody.game_object and rigidbody.game_object.active:
                distance = (rigidbody.game_object.transform.position - center).magnitude()
                if distance <= radius:
                    result.append(rigidbody)
        return result

    def apply_explosion(self, center: Vector2, force: float, radius: float):
        """
        Apply explosion force to all rigidbodies in range.

        Args:
            center: Explosion center
            force: Explosion force
            radius: Explosion radius
        """
        for rigidbody in self.get_rigidbodies_in_area(center, radius):
            if not rigidbody.is_kinematic:
                direction = rigidbody.game_object.transform.position - center
                distance = direction.magnitude()

                if distance > 0:
                    # Falloff with distance
                    falloff = max(0, 1.0 - distance / radius)
                    explosion_force = direction.normalized() * force * falloff
                    rigidbody.add_impulse(explosion_force)
                    self.wake_rigidbody(rigidbody)

    def set_time_scale(self, scale: float):
        """
        Set physics time scale.

        Args:
            scale: Time scale multiplier
        """
        self.physics_engine.set_time_scale(scale)

    def set_max_velocity(self, max_vel: float):
        """
        Set maximum velocity for all rigidbodies.

        Args:
            max_vel: Maximum velocity
        """
        self.physics_engine.set_max_velocity(max_vel)

    def get_performance_stats(self) -> dict:
        """
        Get physics performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        return {
            'active_rigidbodies': len([rb for rb in self.rigidbodies if rb not in self.sleeping_bodies]),
            'sleeping_rigidbodies': len(self.sleeping_bodies),
            'total_colliders': len(self.physics_engine.colliders),
            'collision_checks_last_frame': self.physics_engine.get_collision_count()
        }