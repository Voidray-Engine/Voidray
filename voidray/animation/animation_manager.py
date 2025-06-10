
"""
VoidRay Animation Manager
Handles sprite animations, tweening, and timeline control.
"""

import pygame
from typing import List, Dict, Callable, Optional, Any
from ..math.vector2 import Vector2


class Animation:
    """Base animation class."""
    
    def __init__(self, name: str, duration: float, loop: bool = True):
        self.name = name
        self.duration = duration
        self.loop = loop
        self.current_time = 0.0
        self.playing = False
        self.speed = 1.0
        self.on_complete: Optional[Callable] = None
        
    def play(self):
        """Start playing the animation."""
        self.playing = True
        
    def pause(self):
        """Pause the animation."""
        self.playing = False
        
    def stop(self):
        """Stop and reset the animation."""
        self.playing = False
        self.current_time = 0.0
        
    def update(self, delta_time: float):
        """Update animation timing."""
        if not self.playing:
            return
            
        self.current_time += delta_time * self.speed
        
        if self.current_time >= self.duration:
            if self.loop:
                self.current_time = 0.0
            else:
                self.current_time = self.duration
                self.playing = False
                if self.on_complete:
                    self.on_complete()
    
    def get_progress(self) -> float:
        """Get animation progress (0.0 to 1.0)."""
        return min(self.current_time / self.duration, 1.0)


class SpriteAnimation(Animation):
    """Sprite sheet based animation."""
    
    def __init__(self, name: str, frames: List[pygame.Surface], frame_duration: float, loop: bool = True):
        total_duration = len(frames) * frame_duration
        super().__init__(name, total_duration, loop)
        
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        
    def update(self, delta_time: float):
        """Update sprite animation."""
        super().update(delta_time)
        
        if self.frames:
            # Calculate current frame
            frame_index = int(self.current_time / self.frame_duration)
            self.current_frame = min(frame_index, len(self.frames) - 1)
    
    def get_current_frame(self) -> pygame.Surface:
        """Get the current animation frame."""
        if self.frames and 0 <= self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return None


class AnimationState:
    """Animation state for state machines."""
    
    def __init__(self, name: str, animation: Animation):
        self.name = name
        self.animation = animation
        self.transitions: Dict[str, Callable[[], bool]] = {}
        
    def add_transition(self, target_state: str, condition: Callable[[], bool]):
        """Add transition condition to another state."""
        self.transitions[target_state] = condition
        
    def check_transitions(self) -> Optional[str]:
        """Check if any transition conditions are met."""
        for target_state, condition in self.transitions.items():
            if condition():
                return target_state
        return None


class AnimationStateMachine:
    """Animation state machine for complex character animations."""
    
    def __init__(self):
        self.states: Dict[str, AnimationState] = {}
        self.current_state: Optional[AnimationState] = None
        self.default_state: Optional[str] = None
        
    def add_state(self, state: AnimationState):
        """Add an animation state."""
        self.states[state.name] = state
        
        if self.default_state is None:
            self.default_state = state.name
            
    def set_state(self, state_name: str):
        """Set the current animation state."""
        if state_name in self.states:
            if self.current_state:
                self.current_state.animation.stop()
                
            self.current_state = self.states[state_name]
            self.current_state.animation.play()
            
    def update(self, delta_time: float):
        """Update the state machine."""
        if not self.current_state:
            if self.default_state:
                self.set_state(self.default_state)
            return
            
        # Update current animation
        self.current_state.animation.update(delta_time)
        
        # Check for state transitions
        next_state = self.current_state.check_transitions()
        if next_state and next_state in self.states:
            self.set_state(next_state)
            
    def get_current_animation(self) -> Optional[Animation]:
        """Get the current animation."""
        return self.current_state.animation if self.current_state else None


class AnimationManager:
    """Manages all animations in the game."""
    
    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.state_machines: List[AnimationStateMachine] = []
        self.sprite_sheets: Dict[str, pygame.Surface] = {}
        
    def load_sprite_sheet(self, name: str, surface: pygame.Surface):
        """Load a sprite sheet for animation creation."""
        self.sprite_sheets[name] = surface
        
    def create_sprite_animation(self, name: str, sprite_sheet_name: str, 
                              frame_width: int, frame_height: int,
                              frame_count: int, frame_duration: float,
                              start_x: int = 0, start_y: int = 0,
                              loop: bool = True) -> SpriteAnimation:
        """Create a sprite animation from a sprite sheet."""
        if sprite_sheet_name not in self.sprite_sheets:
            raise ValueError(f"Sprite sheet '{sprite_sheet_name}' not found")
            
        sprite_sheet = self.sprite_sheets[sprite_sheet_name]
        frames = []
        
        for i in range(frame_count):
            frame_x = start_x + (i * frame_width)
            frame_y = start_y
            
            # Extract frame from sprite sheet
            frame_rect = pygame.Rect(frame_x, frame_y, frame_width, frame_height)
            frame_surface = sprite_sheet.subsurface(frame_rect).copy()
            frames.append(frame_surface)
            
        animation = SpriteAnimation(name, frames, frame_duration, loop)
        self.animations[name] = animation
        return animation
        
    def get_animation(self, name: str) -> Optional[Animation]:
        """Get an animation by name."""
        return self.animations.get(name)
        
    def create_state_machine(self) -> AnimationStateMachine:
        """Create a new animation state machine."""
        state_machine = AnimationStateMachine()
        self.state_machines.append(state_machine)
        return state_machine
        
    def update(self, delta_time: float):
        """Update all animations and state machines."""
        # Update individual animations
        for animation in self.animations.values():
            animation.update(delta_time)
            
        # Update state machines
        for state_machine in self.state_machines:
            state_machine.update(delta_time)
            
    def remove_animation(self, name: str):
        """Remove an animation."""
        if name in self.animations:
            del self.animations[name]
            
    def clear_all(self):
        """Clear all animations and state machines."""
        self.animations.clear()
        self.state_machines.clear()
