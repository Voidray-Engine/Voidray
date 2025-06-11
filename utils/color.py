"""
VoidRay Color Utilities
Color constants and utilities for the VoidRay engine.
"""

class Color:
    """
    Color utility class with common color constants.
    """
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (192, 192, 192)
    DARK_GRAY = (64, 64, 64)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    BROWN = (165, 42, 42)
    PINK = (255, 192, 203)

    @staticmethod
    def rgb(r: int, g: int, b: int) -> tuple:
        """Create RGB color tuple with validation."""
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    @staticmethod
    def rgba(r: int, g: int, b: int, a: int) -> tuple:
        """Create RGBA color tuple with validation."""
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), max(0, min(255, a)))