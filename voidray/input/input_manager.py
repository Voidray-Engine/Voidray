"""
VoidRay Input Manager
Centralized input handling for keyboard, mouse, and other devices.
"""

import pygame
from typing import Dict, Set
from ..math.vector2 import Vector2


class Keys:
    """
    Key code constants for common keys.
    """
    # Letters
    A = pygame.K_a
    B = pygame.K_b
    C = pygame.K_c
    D = pygame.K_d
    E = pygame.K_e
    F = pygame.K_f
    G = pygame.K_g
    H = pygame.K_h
    I = pygame.K_i
    J = pygame.K_j
    K = pygame.K_k
    L = pygame.K_l
    M = pygame.K_m
    N = pygame.K_n
    O = pygame.K_o
    P = pygame.K_p
    Q = pygame.K_q
    R = pygame.K_r
    S = pygame.K_s
    T = pygame.K_t
    U = pygame.K_u
    V = pygame.K_v
    W = pygame.K_w
    X = pygame.K_x
    Y = pygame.K_y
    Z = pygame.K_z
    
    # Numbers
    NUM_0 = pygame.K_0
    NUM_1 = pygame.K_1
    NUM_2 = pygame.K_2
    NUM_3 = pygame.K_3
    NUM_4 = pygame.K_4
    NUM_5 = pygame.K_5
    NUM_6 = pygame.K_6
    NUM_7 = pygame.K_7
    NUM_8 = pygame.K_8
    NUM_9 = pygame.K_9
    
    # Special keys
    SPACE = pygame.K_SPACE
    ENTER = pygame.K_RETURN
    ESCAPE = pygame.K_ESCAPE
    BACKSPACE = pygame.K_BACKSPACE
    TAB = pygame.K_TAB
    SHIFT = pygame.K_LSHIFT
    CTRL = pygame.K_LCTRL
    ALT = pygame.K_LALT
    
    # Arrow keys
    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    
    # Function keys
    F1 = pygame.K_F1
    F2 = pygame.K_F2
    F3 = pygame.K_F3
    F4 = pygame.K_F4
    F5 = pygame.K_F5
    F6 = pygame.K_F6
    F7 = pygame.K_F7
    F8 = pygame.K_F8
    F9 = pygame.K_F9
    F10 = pygame.K_F10
    F11 = pygame.K_F11
    F12 = pygame.K_F12


class MouseButtons:
    """
    Mouse button constants.
    """
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEEL_UP = 4
    WHEEL_DOWN = 5


class InputManager:
    """
    Manages all input from keyboard, mouse, and other devices.
    """
    
    def __init__(self):
        """
        Initialize the input manager.
        """
        # Keyboard state
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()
        
        # Mouse state
        self.mouse_position = Vector2(0, 0)
        self.mouse_buttons_pressed: Set[int] = set()
        self.mouse_buttons_just_pressed: Set[int] = set()
        self.mouse_buttons_just_released: Set[int] = set()
        self.mouse_wheel_delta = 0
        
        # Gamepad state
        pygame.joystick.init()
        self.gamepads = {}
        self.gamepad_buttons_pressed = {}
        self.gamepad_buttons_just_pressed = {}
        self.gamepad_buttons_just_released = {}
        self.gamepad_axes = {}
        
        # Initialize connected gamepads
        for i in range(pygame.joystick.get_count()):
            gamepad = pygame.joystick.Joystick(i)
            gamepad.init()
            self.gamepads[i] = gamepad
            self.gamepad_buttons_pressed[i] = set()
            self.gamepad_buttons_just_pressed[i] = set()
            self.gamepad_buttons_just_released[i] = set()
            self.gamepad_axes[i] = {}
        
        # Previous frame state for comparison
        self._prev_keys_pressed: Set[int] = set()
        self._prev_mouse_buttons_pressed: Set[int] = set()
        self._prev_gamepad_buttons_pressed = {}
    
    def handle_event(self, event: pygame.event.Event):
        """
        Handle a pygame event.
        
        Args:
            event: The pygame event to handle
        """
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons_pressed.add(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons_pressed.discard(event.button)
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_position = Vector2(event.pos[0], event.pos[1])
        elif event.type == pygame.MOUSEWHEEL:
            self.mouse_wheel_delta = event.y
    
    def update(self):
        """
        Update input state. Call this once per frame after handling events.
        """
        # Update mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_position = Vector2(mouse_pos[0], mouse_pos[1])
        
        # Calculate just pressed/released keys
        self.keys_just_pressed = self.keys_pressed - self._prev_keys_pressed
        self.keys_just_released = self._prev_keys_pressed - self.keys_pressed
        
        # Calculate just pressed/released mouse buttons
        self.mouse_buttons_just_pressed = self.mouse_buttons_pressed - self._prev_mouse_buttons_pressed
        self.mouse_buttons_just_released = self._prev_mouse_buttons_pressed - self.mouse_buttons_pressed
        
        # Store current state for next frame
        self._prev_keys_pressed = self.keys_pressed.copy()
        self._prev_mouse_buttons_pressed = self.mouse_buttons_pressed.copy()
        
        # Reset wheel delta
        self.mouse_wheel_delta = 0
    
    # Keyboard methods
    def is_key_pressed(self, key: int) -> bool:
        """
        Check if a key is currently being held down.
        
        Args:
            key: Key code to check
            
        Returns:
            True if the key is pressed, False otherwise
        """
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key: int) -> bool:
        """
        Check if a key was just pressed this frame.
        
        Args:
            key: Key code to check
            
        Returns:
            True if the key was just pressed, False otherwise
        """
        return key in self.keys_just_pressed
    
    def is_key_just_released(self, key: int) -> bool:
        """
        Check if a key was just released this frame.
        
        Args:
            key: Key code to check
            
        Returns:
            True if the key was just released, False otherwise
        """
        return key in self.keys_just_released
    
    def get_axis(self, negative_key: int, positive_key: int) -> float:
        """
        Get an axis value based on two keys (-1 to 1).
        
        Args:
            negative_key: Key for negative direction
            positive_key: Key for positive direction
            
        Returns:
            Axis value from -1 to 1
        """
        value = 0.0
        if self.is_key_pressed(negative_key):
            value -= 1.0
        if self.is_key_pressed(positive_key):
            value += 1.0
        return value
    
    def get_movement_vector(self) -> Vector2:
        """
        Get a normalized movement vector based on WASD/arrow keys.
        
        Returns:
            Movement vector as Vector2
        """
        x = self.get_axis(Keys.A, Keys.D) + self.get_axis(Keys.LEFT, Keys.RIGHT)
        y = self.get_axis(Keys.W, Keys.S) + self.get_axis(Keys.UP, Keys.DOWN)
        
        movement = Vector2(x, -y)  # Invert Y for screen coordinates
        if movement.magnitude() > 1.0:
            movement = movement.normalized()
        
        return movement
    
    # Mouse methods
    def is_mouse_button_pressed(self, button: int) -> bool:
        """
        Check if a mouse button is currently being held down.
        
        Args:
            button: Mouse button to check
            
        Returns:
            True if the button is pressed, False otherwise
        """
        return button in self.mouse_buttons_pressed
    
    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """
        Check if a mouse button was just pressed this frame.
        
        Args:
            button: Mouse button to check
            
        Returns:
            True if the button was just pressed, False otherwise
        """
        return button in self.mouse_buttons_just_pressed
    
    def is_mouse_button_just_released(self, button: int) -> bool:
        """
        Check if a mouse button was just released this frame.
        
        Args:
            button: Mouse button to check
            
        Returns:
            True if the button was just released, False otherwise
        """
        return button in self.mouse_buttons_just_released
    
    def get_mouse_position(self) -> Vector2:
        """
        Get the current mouse position.
        
        Returns:
            Mouse position as Vector2
        """
        return self.mouse_position.copy()
    
    def get_mouse_world_position(self, camera) -> Vector2:
        """
        Get the mouse position in world coordinates relative to a camera.
        
        Args:
            camera: Camera to use for conversion
            
        Returns:
            Mouse world position as Vector2
        """
        screen_size = Vector2(pygame.display.get_surface().get_width(),
                            pygame.display.get_surface().get_height())
        return camera.screen_to_world(self.mouse_position, screen_size)
    
    def get_mouse_wheel_delta(self) -> int:
        """
        Get the mouse wheel scroll delta for this frame.
        
        Returns:
            Wheel delta (positive for up, negative for down)
        """
        return self.mouse_wheel_delta
    
    # Gamepad methods
    def is_gamepad_button_pressed(self, gamepad_id: int, button: int) -> bool:
        """Check if a gamepad button is pressed."""
        return gamepad_id in self.gamepad_buttons_pressed and button in self.gamepad_buttons_pressed[gamepad_id]
    
    def is_gamepad_button_just_pressed(self, gamepad_id: int, button: int) -> bool:
        """Check if a gamepad button was just pressed."""
        return gamepad_id in self.gamepad_buttons_just_pressed and button in self.gamepad_buttons_just_pressed[gamepad_id]
    
    def get_gamepad_axis(self, gamepad_id: int, axis: int) -> float:
        """Get gamepad axis value (-1 to 1)."""
        if gamepad_id in self.gamepad_axes and axis in self.gamepad_axes[gamepad_id]:
            return self.gamepad_axes[gamepad_id][axis]
        return 0.0
    
    def get_gamepad_movement_vector(self, gamepad_id: int = 0) -> Vector2:
        """Get movement vector from gamepad left stick."""
        x = self.get_gamepad_axis(gamepad_id, 0)  # Left stick X
        y = self.get_gamepad_axis(gamepad_id, 1)  # Left stick Y
        return Vector2(x, y)
    
    def get_connected_gamepads(self) -> list:
        """Get list of connected gamepad IDs."""
        return list(self.gamepads.keys())
