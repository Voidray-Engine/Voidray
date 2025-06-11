
"""
VoidRay Physics Module
Handles collision detection, physics simulation, and spatial partitioning.
"""

from .physics_engine import PhysicsEngine
from .physics_system import PhysicsSystem
from .collider import Collider, RectCollider, CircleCollider, BoxCollider
from .rigidbody import Rigidbody

__all__ = [
    'PhysicsEngine', 
    'PhysicsSystem',
    'Collider', 
    'RectCollider', 
    'CircleCollider',
    'BoxCollider',  # Legacy alias
    'Rigidbody'
]
