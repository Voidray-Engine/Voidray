"""
VoidRay Physics System

The main physics system that manages all physics objects and simulations
including collision detection and response.
"""

from typing import List
from .rigidbody import Rigidbody
from .collision import Collider, CollisionDetector


class PhysicsSystem:
    """
    The main physics system that manages all physics objects and
    handles collision detection and response.
    """
    
    def __init__(self):
        """Initialize the physics system."""
        self.rigidbodies: List[Rigidbody] = []
        self.colliders: List[Collider] = []
        self.collision_detector = CollisionDetector()
        self.gravity = -9.81  # Default gravity (negative Y direction)
    
    def add_rigidbody(self, rigidbody: Rigidbody) -> None:
        """
        Add a rigidbody to the physics system.
        
        Args:
            rigidbody: The rigidbody to add
        """
        if rigidbody not in self.rigidbodies:
            self.rigidbodies.append(rigidbody)
    
    def remove_rigidbody(self, rigidbody: Rigidbody) -> None:
        """
        Remove a rigidbody from the physics system.
        
        Args:
            rigidbody: The rigidbody to remove
        """
        if rigidbody in self.rigidbodies:
            self.rigidbodies.remove(rigidbody)
    
    def add_collider(self, collider: Collider) -> None:
        """
        Add a collider to the physics system.
        
        Args:
            collider: The collider to add
        """
        if collider not in self.colliders:
            self.colliders.append(collider)
    
    def remove_collider(self, collider: Collider) -> None:
        """
        Remove a collider from the physics system.
        
        Args:
            collider: The collider to remove
        """
        if collider in self.colliders:
            self.colliders.remove(collider)
    
    def set_gravity(self, gravity: float) -> None:
        """
        Set the global gravity value.
        
        Args:
            gravity: The gravity acceleration (negative for downward)
        """
        self.gravity = gravity
    
    def update(self, delta_time: float) -> None:
        """
        Update the physics simulation.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Update all rigidbodies
        for rigidbody in self.rigidbodies:
            if rigidbody.enabled:
                self._update_rigidbody(rigidbody, delta_time)
        
        # Handle collisions
        self._handle_collisions()
    
    def _update_rigidbody(self, rigidbody: Rigidbody, delta_time: float) -> None:
        """
        Update a single rigidbody's physics.
        
        Args:
            rigidbody: The rigidbody to update
            delta_time: Time elapsed since last frame
        """
        if not rigidbody.transform:
            return
        
        # Apply gravity if enabled
        if rigidbody.use_gravity:
            rigidbody.velocity.y += self.gravity * delta_time
        
        # Apply drag
        drag_factor = max(0, 1 - rigidbody.drag * delta_time)
        rigidbody.velocity *= drag_factor
        
        # Update position based on velocity
        rigidbody.transform.position += rigidbody.velocity * delta_time
        
        # Update angular velocity and rotation
        angular_drag_factor = max(0, 1 - rigidbody.angular_drag * delta_time)
        rigidbody.angular_velocity *= angular_drag_factor
        rigidbody.transform.rotation += rigidbody.angular_velocity * delta_time
    
    def _handle_collisions(self) -> None:
        """Handle collision detection and response for all colliders."""
        # Check all collider pairs for collisions
        for i in range(len(self.colliders)):
            for j in range(i + 1, len(self.colliders)):
                collider_a = self.colliders[i]
                collider_b = self.colliders[j]
                
                if not collider_a.enabled or not collider_b.enabled:
                    continue
                
                # Check if colliders are on different layers that should collide
                if not self._should_collide(collider_a, collider_b):
                    continue
                
                # Perform collision detection
                collision_info = self.collision_detector.check_collision(collider_a, collider_b)
                
                if collision_info:
                    # Trigger collision events
                    if collider_a.game_object:
                        collider_a.on_collision(collider_b, collision_info)
                    if collider_b.game_object:
                        collider_b.on_collision(collider_a, collision_info)
                    
                    # Handle collision response if both have rigidbodies
                    rigidbody_a = collider_a.game_object.get_component(Rigidbody) if collider_a.game_object else None
                    rigidbody_b = collider_b.game_object.get_component(Rigidbody) if collider_b.game_object else None
                    
                    if rigidbody_a and rigidbody_b:
                        self._resolve_collision(rigidbody_a, rigidbody_b, collision_info)
    
    def _should_collide(self, collider_a: Collider, collider_b: Collider) -> bool:
        """
        Check if two colliders should collide based on their layers.
        
        Args:
            collider_a: First collider
            collider_b: Second collider
            
        Returns:
            True if they should collide, False otherwise
        """
        # For now, all colliders can collide with each other
        # This can be extended with layer masks in the future
        return True
    
    def _resolve_collision(self, rigidbody_a: Rigidbody, rigidbody_b: Rigidbody, 
                          collision_info: dict) -> None:
        """
        Resolve collision between two rigidbodies.
        
        Args:
            rigidbody_a: First rigidbody
            rigidbody_b: Second rigidbody
            collision_info: Information about the collision
        """
        # Simple collision response - separate objects and exchange velocities
        normal = collision_info.get('normal')
        penetration = collision_info.get('penetration', 0)
        
        if not normal:
            return
        
        # Separate objects
        separation = normal * (penetration / 2)
        if rigidbody_a.transform:
            rigidbody_a.transform.position -= separation
        if rigidbody_b.transform:
            rigidbody_b.transform.position += separation
        
        # Calculate relative velocity
        relative_velocity = rigidbody_a.velocity - rigidbody_b.velocity
        
        # Calculate relative velocity along normal
        velocity_along_normal = relative_velocity.dot(normal)
        
        # Do not resolve if velocities are separating
        if velocity_along_normal > 0:
            return
        
        # Calculate restitution (bounciness)
        restitution = min(rigidbody_a.bounciness, rigidbody_b.bounciness)
        
        # Calculate impulse scalar
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        impulse_scalar /= (1 / rigidbody_a.mass) + (1 / rigidbody_b.mass)
        
        # Apply impulse
        impulse = normal * impulse_scalar
        rigidbody_a.velocity += impulse / rigidbody_a.mass
        rigidbody_b.velocity -= impulse / rigidbody_b.mass
"""
VoidRay Physics System
High-level physics system that manages rigidbodies and constraints.
"""

from typing import List, Set
from ..math.vector2 import Vector2
from .rigidbody import Rigidbody
from .physics_engine import PhysicsEngine


class PhysicsSystem:
    """
    High-level physics system that manages rigidbodies and physics simulation.
    """
    
    def __init__(self):
        self.rigidbodies: List[Rigidbody] = []
        self.gravity = Vector2(0, 0)
        self.physics_engine = PhysicsEngine()
        self.sleeping_bodies: Set[Rigidbody] = set()
        self.time_accumulator = 0.0
        self.fixed_timestep = 1.0 / 60.0  # 60 FPS physics
    
    def set_gravity(self, gravity: float):
        """
        Set gravity strength.
        
        Args:
            gravity: Gravity strength (positive for downward)
        """
        self.gravity = Vector2(0, gravity)
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
    
    def update(self, delta_time: float):
        """
        Update the physics simulation.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        # Accumulate time for fixed timestep
        self.time_accumulator += delta_time
        
        # Process fixed timestep updates
        while self.time_accumulator >= self.fixed_timestep:
            self._fixed_update(self.fixed_timestep)
            self.time_accumulator -= self.fixed_timestep
        
        # Update physics engine
        self.physics_engine.update(delta_time)
    
    def _fixed_update(self, fixed_delta: float):
        """
        Fixed timestep physics update.
        
        Args:
            fixed_delta: Fixed timestep duration
        """
        # Update active rigidbodies
        active_bodies = [rb for rb in self.rigidbodies if rb not in self.sleeping_bodies]
        
        for rigidbody in active_bodies:
            if rigidbody.game_object and rigidbody.game_object.active:
                # Apply gravity
                if not rigidbody.is_kinematic and self.gravity.magnitude() > 0:
                    rigidbody.add_force(self.gravity * rigidbody.mass)
                
                # Update rigidbody
                rigidbody.update(fixed_delta)
                
                # Check if body should sleep
                if rigidbody.velocity.magnitude() < 0.1 and rigidbody.angular_velocity < 0.1:
                    rigidbody.sleep_timer += fixed_delta
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
