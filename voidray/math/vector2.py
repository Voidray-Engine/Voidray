"""
VoidRay Vector2 Class
2D vector mathematics for game development.
"""

import math
from typing import Union


class Vector2:
    """
    A 2D vector class with common vector operations.
    """
    
    def __init__(self, x: float = 0, y: float = 0):
        """
        Initialize a 2D vector.
        
        Args:
            x: X component
            y: Y component
        """
        self.x = float(x)
        self.y = float(y)
    
    def __str__(self) -> str:
        return f"Vector2({self.x:.2f}, {self.y:.2f})"
    
    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Vector2):
            return abs(self.x - other.x) < 1e-10 and abs(self.y - other.y) < 1e-10
        return False
    
    def __add__(self, other: 'Vector2') -> 'Vector2':
        """Add two vectors."""
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2') -> 'Vector2':
        """Subtract two vectors."""
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: Union[float, int, 'Vector2']) -> 'Vector2':
        """Multiply vector by scalar or component-wise with another vector."""
        if isinstance(scalar, (int, float)):
            return Vector2(self.x * scalar, self.y * scalar)
        elif isinstance(scalar, Vector2):
            return Vector2(self.x * scalar.x, self.y * scalar.y)
        else:
            raise TypeError("Can only multiply Vector2 by number or Vector2")
    
    def __rmul__(self, scalar: Union[float, int]) -> 'Vector2':
        """Right multiplication by scalar."""
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: Union[float, int, 'Vector2']) -> 'Vector2':
        """Divide vector by scalar or component-wise with another vector."""
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ZeroDivisionError("Cannot divide vector by zero")
            return Vector2(self.x / scalar, self.y / scalar)
        elif isinstance(scalar, Vector2):
            if scalar.x == 0 or scalar.y == 0:
                raise ZeroDivisionError("Cannot divide by vector with zero components")
            return Vector2(self.x / scalar.x, self.y / scalar.y)
        else:
            raise TypeError("Can only divide Vector2 by number or Vector2")
    
    def __neg__(self) -> 'Vector2':
        """Negate the vector."""
        return Vector2(-self.x, -self.y)
    
    def magnitude(self) -> float:
        """
        Get the magnitude (length) of the vector.
        
        Returns:
            Vector magnitude
        """
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def magnitude_squared(self) -> float:
        """
        Get the squared magnitude of the vector (faster than magnitude).
        
        Returns:
            Squared vector magnitude
        """
        return self.x * self.x + self.y * self.y
    
    def normalized(self) -> 'Vector2':
        """
        Get a normalized version of this vector.
        
        Returns:
            Normalized vector with magnitude 1
        """
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)
    
    def normalize(self):
        """
        Normalize this vector in place.
        """
        mag = self.magnitude()
        if mag != 0:
            self.x /= mag
            self.y /= mag
    
    def dot(self, other: 'Vector2') -> float:
        """
        Calculate the dot product with another vector.
        
        Args:
            other: The other vector
            
        Returns:
            Dot product result
        """
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: 'Vector2') -> float:
        """
        Calculate the 2D cross product (returns scalar).
        
        Args:
            other: The other vector
            
        Returns:
            Cross product result
        """
        return self.x * other.y - self.y * other.x
    
    def distance_to(self, other: 'Vector2') -> float:
        """
        Calculate distance to another vector.
        
        Args:
            other: The other vector
            
        Returns:
            Distance between vectors
        """
        return (self - other).magnitude()
    
    def distance_squared_to(self, other: 'Vector2') -> float:
        """
        Calculate squared distance to another vector (faster than distance_to).
        
        Args:
            other: The other vector
            
        Returns:
            Squared distance between vectors
        """
        return (self - other).magnitude_squared()
    
    def angle_to(self, other: 'Vector2') -> float:
        """
        Calculate angle to another vector in radians.
        
        Args:
            other: The other vector
            
        Returns:
            Angle in radians
        """
        return math.atan2(self.cross(other), self.dot(other))
    
    def angle_degrees_to(self, other: 'Vector2') -> float:
        """
        Calculate angle to another vector in degrees.
        
        Args:
            other: The other vector
            
        Returns:
            Angle in degrees
        """
        return math.degrees(self.angle_to(other))
    
    def rotate(self, angle_radians: float) -> 'Vector2':
        """
        Rotate this vector by an angle.
        
        Args:
            angle_radians: Angle to rotate by in radians
            
        Returns:
            New rotated vector
        """
        cos_a = math.cos(angle_radians)
        sin_a = math.sin(angle_radians)
        
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )
    
    def rotate_degrees(self, angle_degrees: float) -> 'Vector2':
        """
        Rotate this vector by an angle in degrees.
        
        Args:
            angle_degrees: Angle to rotate by in degrees
            
        Returns:
            New rotated vector
        """
        return self.rotate(math.radians(angle_degrees))
    
    def lerp(self, other: 'Vector2', t: float) -> 'Vector2':
        """
        Linear interpolation between this vector and another.
        
        Args:
            other: Target vector
            t: Interpolation factor (0.0 to 1.0)
            
        Returns:
            Interpolated vector
        """
        t = max(0.0, min(1.0, t))  # Clamp t to [0, 1]
        return Vector2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )
    
    def reflect(self, normal: 'Vector2') -> 'Vector2':
        """
        Reflect this vector across a normal.
        
        Args:
            normal: Normal vector to reflect across (should be normalized)
            
        Returns:
            Reflected vector
        """
        return self - 2 * self.dot(normal) * normal
    
    def project_onto(self, other: 'Vector2') -> 'Vector2':
        """
        Project this vector onto another vector.
        
        Args:
            other: Vector to project onto
            
        Returns:
            Projected vector
        """
        if other.magnitude_squared() == 0:
            return Vector2(0, 0)
        
        return other * (self.dot(other) / other.magnitude_squared())
    
    def perpendicular(self) -> 'Vector2':
        """
        Get a perpendicular vector (rotated 90 degrees counter-clockwise).
        
        Returns:
            Perpendicular vector
        """
        return Vector2(-self.y, self.x)
    
    def copy(self) -> 'Vector2':
        """
        Create a copy of this vector.
        
        Returns:
            New Vector2 with same values
        """
        return Vector2(self.x, self.y)
    
    def set(self, x: float, y: float):
        """
        Set the components of this vector.
        
        Args:
            x: New X component
            y: New Y component
        """
        self.x = float(x)
        self.y = float(y)
    
    @staticmethod
    def zero() -> 'Vector2':
        """Create a zero vector."""
        return Vector2(0, 0)
    
    @staticmethod
    def one() -> 'Vector2':
        """Create a vector with both components set to 1."""
        return Vector2(1, 1)
    
    @staticmethod
    def up() -> 'Vector2':
        """Create an up vector (0, -1) in screen coordinates."""
        return Vector2(0, -1)
    
    @staticmethod
    def down() -> 'Vector2':
        """Create a down vector (0, 1) in screen coordinates."""
        return Vector2(0, 1)
    
    @staticmethod
    def left() -> 'Vector2':
        """Create a left vector (-1, 0)."""
        return Vector2(-1, 0)
    
    @staticmethod
    def right() -> 'Vector2':
        """Create a right vector (1, 0)."""
        return Vector2(1, 0)
    
    @staticmethod
    def from_angle(angle_radians: float, magnitude: float = 1.0) -> 'Vector2':
        """
        Create a vector from an angle and magnitude.
        
        Args:
            angle_radians: Angle in radians
            magnitude: Vector magnitude
            
        Returns:
            New vector pointing in the specified direction
        """
        return Vector2(
            math.cos(angle_radians) * magnitude,
            math.sin(angle_radians) * magnitude
        )
    
    @staticmethod
    def from_angle_degrees(angle_degrees: float, magnitude: float = 1.0) -> 'Vector2':
        """
        Create a vector from an angle in degrees and magnitude.
        
        Args:
            angle_degrees: Angle in degrees
            magnitude: Vector magnitude
            
        Returns:
            New vector pointing in the specified direction
        """
        return Vector2.from_angle(math.radians(angle_degrees), magnitude)
