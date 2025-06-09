"""
VoidRay Color Utilities

Provides color representation and manipulation utilities with support
for different color formats and common color operations.
"""

from typing import Tuple, Union


class Color:
    """
    Represents a color with RGBA components and provides utilities
    for color manipulation and format conversion.
    """
    
    def __init__(self, r: Union[int, float] = 255, g: Union[int, float] = 255, 
                 b: Union[int, float] = 255, a: Union[int, float] = 255):
        """
        Initialize a color.
        
        Args:
            r: Red component (0-255 for int, 0.0-1.0 for float)
            g: Green component (0-255 for int, 0.0-1.0 for float)
            b: Blue component (0-255 for int, 0.0-1.0 for float)
            a: Alpha component (0-255 for int, 0.0-1.0 for float)
        """
        # Normalize to 0-255 range
        if isinstance(r, float) and r <= 1.0:
            self.r = int(r * 255)
            self.g = int(g * 255)
            self.b = int(b * 255)
            self.a = int(a * 255)
        else:
            self.r = int(max(0, min(255, r)))
            self.g = int(max(0, min(255, g)))
            self.b = int(max(0, min(255, b)))
            self.a = int(max(0, min(255, a)))
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> 'Color':
        """
        Create a color from RGB values.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            A new Color instance
        """
        return cls(r, g, b, 255)
    
    @classmethod
    def from_rgba(cls, r: int, g: int, b: int, a: int) -> 'Color':
        """
        Create a color from RGBA values.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            a: Alpha component (0-255)
            
        Returns:
            A new Color instance
        """
        return cls(r, g, b, a)
    
    @classmethod
    def from_hex(cls, hex_string: str) -> 'Color':
        """
        Create a color from a hex string.
        
        Args:
            hex_string: Hex color string (e.g., "#FF0000" or "FF0000")
            
        Returns:
            A new Color instance
        """
        hex_string = hex_string.lstrip('#')
        
        if len(hex_string) == 3:
            # Short form (e.g., "F0A")
            hex_string = ''.join([c*2 for c in hex_string])
        
        if len(hex_string) == 6:
            # RGB format
            r = int(hex_string[0:2], 16)
            g = int(hex_string[2:4], 16)
            b = int(hex_string[4:6], 16)
            return cls(r, g, b, 255)
        elif len(hex_string) == 8:
            # RGBA format
            r = int(hex_string[0:2], 16)
            g = int(hex_string[2:4], 16)
            b = int(hex_string[4:6], 16)
            a = int(hex_string[6:8], 16)
            return cls(r, g, b, a)
        else:
            raise ValueError(f"Invalid hex color format: {hex_string}")
    
    @classmethod
    def from_hsv(cls, h: float, s: float, v: float, a: float = 1.0) -> 'Color':
        """
        Create a color from HSV values.
        
        Args:
            h: Hue (0.0-360.0)
            s: Saturation (0.0-1.0)
            v: Value/Brightness (0.0-1.0)
            a: Alpha (0.0-1.0)
            
        Returns:
            A new Color instance
        """
        import math
        
        h = h % 360.0
        c = v * s
        x = c * (1 - abs((h / 60.0) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r = (r + m) * 255
        g = (g + m) * 255
        b = (b + m) * 255
        a = a * 255
        
        return cls(r, g, b, a)
    
    def to_tuple(self) -> Tuple[int, int, int]:
        """
        Convert to RGB tuple.
        
        Returns:
            (r, g, b) tuple
        """
        return (self.r, self.g, self.b)
    
    def to_tuple_rgba(self) -> Tuple[int, int, int, int]:
        """
        Convert to RGBA tuple.
        
        Returns:
            (r, g, b, a) tuple
        """
        return (self.r, self.g, self.b, self.a)
    
    def to_hex(self, include_alpha: bool = False) -> str:
        """
        Convert to hex string.
        
        Args:
            include_alpha: Whether to include alpha in the hex string
            
        Returns:
            Hex color string
        """
        if include_alpha:
            return f"#{self.r:02X}{self.g:02X}{self.b:02X}{self.a:02X}"
        else:
            return f"#{self.r:02X}{self.g:02X}{self.b:02X}"
    
    def to_hsv(self) -> Tuple[float, float, float]:
        """
        Convert to HSV tuple.
        
        Returns:
            (h, s, v) tuple where h is 0-360, s and v are 0.0-1.0
        """
        r = self.r / 255.0
        g = self.g / 255.0
        b = self.b / 255.0
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Value
        v = max_val
        
        # Saturation
        if max_val == 0:
            s = 0
        else:
            s = diff / max_val
        
        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360
        
        return (h, s, v)
    
    def lerp(self, other: 'Color', t: float) -> 'Color':
        """
        Linear interpolation between this color and another.
        
        Args:
            other: Target color
            t: Interpolation factor (0.0 to 1.0)
            
        Returns:
            Interpolated color
        """
        t = max(0.0, min(1.0, t))
        
        r = int(self.r + (other.r - self.r) * t)
        g = int(self.g + (other.g - self.g) * t)
        b = int(self.b + (other.b - self.b) * t)
        a = int(self.a + (other.a - self.a) * t)
        
        return Color(r, g, b, a)
    
    def with_alpha(self, alpha: Union[int, float]) -> 'Color':
        """
        Create a new color with a different alpha value.
        
        Args:
            alpha: New alpha value (0-255 for int, 0.0-1.0 for float)
            
        Returns:
            New color with modified alpha
        """
        if isinstance(alpha, float) and alpha <= 1.0:
            alpha = int(alpha * 255)
        return Color(self.r, self.g, self.b, alpha)
    
    def copy(self) -> 'Color':
        """Create a copy of this color."""
        return Color(self.r, self.g, self.b, self.a)
    
    # Arithmetic operations
    def __add__(self, other: 'Color') -> 'Color':
        """Add two colors (component-wise)."""
        return Color(
            min(255, self.r + other.r),
            min(255, self.g + other.g),
            min(255, self.b + other.b),
            min(255, self.a + other.a)
        )
    
    def __sub__(self, other: 'Color') -> 'Color':
        """Subtract two colors (component-wise)."""
        return Color(
            max(0, self.r - other.r),
            max(0, self.g - other.g),
            max(0, self.b - other.b),
            max(0, self.a - other.a)
        )
    
    def __mul__(self, scalar: Union[int, float]) -> 'Color':
        """Multiply color by a scalar."""
        return Color(
            min(255, int(self.r * scalar)),
            min(255, int(self.g * scalar)),
            min(255, int(self.b * scalar)),
            min(255, int(self.a * scalar))
        )
    
    def __eq__(self, other: 'Color') -> bool:
        """Check if two colors are equal."""
        return (self.r == other.r and self.g == other.g and 
                self.b == other.b and self.a == other.a)
    
    def __str__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"
    
    def __repr__(self) -> str:
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"
    
    # Common color constants
    BLACK = None
    WHITE = None
    RED = None
    GREEN = None
    BLUE = None
    YELLOW = None
    CYAN = None
    MAGENTA = None
    GRAY = None
    TRANSPARENT = None


# Initialize color constants
Color.BLACK = Color(0, 0, 0)
Color.WHITE = Color(255, 255, 255)
Color.RED = Color(255, 0, 0)
Color.GREEN = Color(0, 255, 0)
Color.BLUE = Color(0, 0, 255)
Color.YELLOW = Color(255, 255, 0)
Color.CYAN = Color(0, 255, 255)
Color.MAGENTA = Color(255, 0, 255)
Color.GRAY = Color(128, 128, 128)
Color.TRANSPARENT = Color(0, 0, 0, 0)
"""
VoidRay Color Utilities
Color constants and utilities for the engine.
"""


class Color:
    """Color constants and utilities."""
    
    # Basic colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    
    # Gray shades
    LIGHT_GRAY = (192, 192, 192)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    
    # Extended colors
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    BROWN = (165, 42, 42)
    PINK = (255, 192, 203)
    
    @staticmethod
    def rgba(r: int, g: int, b: int, a: int = 255) -> tuple:
        """Create RGBA color tuple."""
        return (r, g, b, a)
    
    @staticmethod
    def from_hex(hex_color: str) -> tuple:
        """Convert hex color string to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def lerp(color1: tuple, color2: tuple, t: float) -> tuple:
        """Linear interpolation between two colors."""
        t = max(0.0, min(1.0, t))
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))
