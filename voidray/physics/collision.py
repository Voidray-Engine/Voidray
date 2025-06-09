"""
VoidRay Collision System

This module has been consolidated into the main collider.py and physics_engine.py files
to avoid duplication and improve maintainability.

This file is kept for backward compatibility but redirects to the main implementations.
"""

# Import the main implementations
from .collider import Collider, RectCollider, CircleCollider

# Legacy aliases
BoxCollider = RectCollider

class CollisionDetector:
    """
    Legacy collision detector class.
    Use the collision detection methods in PhysicsEngine instead.
    """

    def __init__(self):
        print("Warning: CollisionDetector is deprecated. Use PhysicsEngine collision detection instead.")

    def check_collision(self, collider_a, collider_b):
        """Check collision between two colliders using their built-in methods."""
        return collider_a.check_collision(collider_b)

# Export for backward compatibility
__all__ = ['Collider', 'BoxCollider', 'CircleCollider', 'CollisionDetector']