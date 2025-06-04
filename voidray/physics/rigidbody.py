"""
VoidRay Rigidbody

Provides physics simulation for game objects including velocity,
acceleration, and physics properties like mass and drag.
"""

from ..core.component import Component
from ..math.vector2 import Vector2


class Rigidbody(Component):
    """
    A physics component that gives game objects physical properties
    and behavior in the physics simulation.
    """
    
    def __init__(self):
        """Initialize the rigidbody with default physics properties."""
        super().__init__()
        
        # Linear motion properties
        self.velocity = Vector2.zero()
        self.mass = 1.0
        self.drag = 0.0  # Linear damping
        self.use_gravity = True
        self.bounciness = 0.0  # Restitution coefficient (0 = no bounce, 1 = perfect bounce)
        
        # Angular motion properties
        self.angular_velocity = 0.0  # Rotation speed in degrees per second
        self.angular_drag = 0.0  # Angular damping
        
        # Constraints
        self.freeze_rotation = False
        self.freeze_position_x = False
        self.freeze_position_y = False
    
    def on_attach(self) -> None:
        """Called when attached to a game object."""
        # Register with physics system if available
        if hasattr(self.game_object, '_scene') and self.game_object._scene:
            engine = self.game_object._scene.engine
            if engine and hasattr(engine, 'physics_system'):
                engine.physics_system.add_rigidbody(self)
    
    def on_detach(self) -> None:
        """Called when detached from a game object."""
        # Unregister from physics system if available
        if hasattr(self.game_object, '_scene') and self.game_object._scene:
            engine = self.game_object._scene.engine
            if engine and hasattr(engine, 'physics_system'):
                engine.physics_system.remove_rigidbody(self)
    
    def add_force(self, force: Vector2) -> None:
        """
        Add a force to the rigidbody (F = ma, so acceleration = F/m).
        
        Args:
            force: The force vector to apply
        """
        acceleration = force / self.mass
        self.velocity += acceleration
    
    def add_impulse(self, impulse: Vector2) -> None:
        """
        Add an impulse to the rigidbody (immediate velocity change).
        
        Args:
            impulse: The impulse vector to apply
        """
        velocity_change = impulse / self.mass
        self.velocity += velocity_change
    
    def add_torque(self, torque: float) -> None:
        """
        Add rotational torque to the rigidbody.
        
        Args:
            torque: The torque to apply (in degrees per second squared)
        """
        # Simplified torque application (assuming unit moment of inertia)
        angular_acceleration = torque / self.mass
        self.angular_velocity += angular_acceleration
    
    def set_velocity(self, velocity: Vector2) -> None:
        """
        Set the rigidbody's velocity directly.
        
        Args:
            velocity: The new velocity vector
        """
        self.velocity = velocity.copy()
    
    def set_angular_velocity(self, angular_velocity: float) -> None:
        """
        Set the rigidbody's angular velocity directly.
        
        Args:
            angular_velocity: The new angular velocity in degrees per second
        """
        self.angular_velocity = angular_velocity
    
    def stop(self) -> None:
        """Stop all motion by setting velocities to zero."""
        self.velocity = Vector2.zero()
        self.angular_velocity = 0.0
    
    def set_mass(self, mass: float) -> None:
        """
        Set the mass of the rigidbody.
        
        Args:
            mass: The new mass (must be positive)
        """
        self.mass = max(0.01, mass)  # Prevent zero or negative mass
    
    def set_drag(self, drag: float) -> None:
        """
        Set the linear drag coefficient.
        
        Args:
            drag: The drag coefficient (0 = no drag, higher = more drag)
        """
        self.drag = max(0, drag)
    
    def set_angular_drag(self, angular_drag: float) -> None:
        """
        Set the angular drag coefficient.
        
        Args:
            angular_drag: The angular drag coefficient
        """
        self.angular_drag = max(0, angular_drag)
    
    def set_bounciness(self, bounciness: float) -> None:
        """
        Set the bounciness (restitution) of the rigidbody.
        
        Args:
            bounciness: The bounciness factor (0 = no bounce, 1 = perfect bounce)
        """
        self.bounciness = max(0, min(1, bounciness))
    
    def set_gravity_enabled(self, enabled: bool) -> None:
        """
        Enable or disable gravity for this rigidbody.
        
        Args:
            enabled: Whether gravity should affect this rigidbody
        """
        self.use_gravity = enabled
    
    def freeze_position(self, x: bool = False, y: bool = False) -> None:
        """
        Freeze position on specific axes.
        
        Args:
            x: Whether to freeze X position
            y: Whether to freeze Y position
        """
        self.freeze_position_x = x
        self.freeze_position_y = y
    
    def set_freeze_rotation(self, freeze: bool) -> None:
        """
        Freeze or unfreeze rotation.
        
        Args:
            freeze: Whether to freeze rotation
        """
        self.freeze_rotation = freeze
    
    def get_kinetic_energy(self) -> float:
        """
        Calculate the kinetic energy of the rigidbody.
        
        Returns:
            The kinetic energy (0.5 * m * v^2)
        """
        speed_squared = self.velocity.magnitude_squared()
        return 0.5 * self.mass * speed_squared
    
    def get_momentum(self) -> Vector2:
        """
        Calculate the momentum of the rigidbody.
        
        Returns:
            The momentum vector (m * v)
        """
        return self.velocity * self.mass
    
    def __str__(self) -> str:
        return f"Rigidbody(mass={self.mass}, velocity={self.velocity})"
    
    def __repr__(self) -> str:
        return (f"Rigidbody(mass={self.mass}, velocity={self.velocity}, "
                f"angular_velocity={self.angular_velocity}, use_gravity={self.use_gravity})")
