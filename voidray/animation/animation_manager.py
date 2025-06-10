
"""
VoidRay Animation Manager
Complete animation system supporting sprite animations, tweening, and timelines.
"""

import pygame
from typing import Dict, List, Optional, Callable, Any
from ..math.vector2 import Vector2
from .tween import TweenManager


class SpriteAnimation:
    """Sprite-based animation with frame sequences."""
    
    def __init__(self, name: str, frames: List[pygame.Surface], frame_duration: float = 0.1):
        self.name = name
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.time_accumulator = 0.0
        self.is_playing = False
        self.is_looping = True
        self.playback_speed = 1.0
        
        # Animation events
        self.on_frame_changed: Optional[Callable[[int], None]] = None
        self.on_animation_finished: Optional[Callable[[], None]] = None
    
    def play(self, loop: bool = True):
        """Start playing the animation."""
        self.is_playing = True
        self.is_looping = loop
        self.current_frame = 0
        self.time_accumulator = 0.0
    
    def stop(self):
        """Stop the animation."""
        self.is_playing = False
        self.current_frame = 0
        self.time_accumulator = 0.0
    
    def pause(self):
        """Pause the animation."""
        self.is_playing = False
    
    def resume(self):
        """Resume the animation."""
        self.is_playing = True
    
    def update(self, delta_time: float):
        """Update animation frame."""
        if not self.is_playing or not self.frames:
            return
        
        self.time_accumulator += delta_time * self.playback_speed
        
        if self.time_accumulator >= self.frame_duration:
            old_frame = self.current_frame
            self.current_frame += 1
            self.time_accumulator = 0.0
            
            if self.current_frame >= len(self.frames):
                if self.is_looping:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.is_playing = False
                    if self.on_animation_finished:
                        self.on_animation_finished()
            
            if old_frame != self.current_frame and self.on_frame_changed:
                self.on_frame_changed(self.current_frame)
    
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Get the current frame surface."""
        if not self.frames or self.current_frame >= len(self.frames):
            return None
        return self.frames[self.current_frame]
    
    def set_frame(self, frame_index: int):
        """Set specific frame."""
        if 0 <= frame_index < len(self.frames):
            self.current_frame = frame_index


class AnimationState:
    """Animation state for state machines."""
    
    def __init__(self, name: str, animation: SpriteAnimation):
        self.name = name
        self.animation = animation
        self.transitions: Dict[str, 'AnimationTransition'] = {}
    
    def add_transition(self, condition: str, target_state: str, transition_time: float = 0.0):
        """Add transition to another state."""
        self.transitions[condition] = AnimationTransition(target_state, transition_time)


class AnimationTransition:
    """Transition between animation states."""
    
    def __init__(self, target_state: str, transition_time: float = 0.0):
        self.target_state = target_state
        self.transition_time = transition_time


class AnimationStateMachine:
    """State machine for complex animation control."""
    
    def __init__(self):
        self.states: Dict[str, AnimationState] = {}
        self.current_state: Optional[AnimationState] = None
        self.parameters: Dict[str, Any] = {}
    
    def add_state(self, state: AnimationState):
        """Add animation state."""
        self.states[state.name] = state
        if self.current_state is None:
            self.current_state = state
    
    def set_parameter(self, name: str, value: Any):
        """Set animation parameter for transitions."""
        self.parameters[name] = value
    
    def trigger(self, condition: str):
        """Trigger a transition condition."""
        if self.current_state and condition in self.current_state.transitions:
            transition = self.current_state.transitions[condition]
            target_state = self.states.get(transition.target_state)
            if target_state:
                self.current_state = target_state
                target_state.animation.play()
    
    def update(self, delta_time: float):
        """Update current animation state."""
        if self.current_state:
            self.current_state.animation.update(delta_time)
    
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Get current animation frame."""
        if self.current_state:
            return self.current_state.animation.get_current_frame()
        return None


class AnimationManager:
    """Complete animation management system."""
    
    def __init__(self):
        self.animations: Dict[str, SpriteAnimation] = {}
        self.state_machines: Dict[str, AnimationStateMachine] = {}
        self.tween_manager = TweenManager()
        self.sprite_sheets: Dict[str, pygame.Surface] = {}
        
        # Global animation settings
        self.global_speed_multiplier = 1.0
        self.paused = False
    
    def load_sprite_sheet(self, name: str, image_path: str) -> bool:
        """Load a sprite sheet for creating animations."""
        try:
            sprite_sheet = pygame.image.load(image_path).convert_alpha()
            self.sprite_sheets[name] = sprite_sheet
            return True
        except pygame.error as e:
            print(f"Failed to load sprite sheet {name}: {e}")
            return False
    
    def create_sprite_animation(self, name: str, sprite_sheet_name: str, 
                              frame_width: int, frame_height: int, 
                              frame_count: int, frame_duration: float = 0.1,
                              start_x: int = 0, start_y: int = 0) -> SpriteAnimation:
        """Create sprite animation from sprite sheet."""
        if sprite_sheet_name not in self.sprite_sheets:
            raise ValueError(f"Sprite sheet '{sprite_sheet_name}' not found")
        
        sprite_sheet = self.sprite_sheets[sprite_sheet_name]
        frames = []
        
        for i in range(frame_count):
            # Calculate frame position
            frames_per_row = sprite_sheet.get_width() // frame_width
            row = i // frames_per_row
            col = i % frames_per_row
            
            x = start_x + col * frame_width
            y = start_y + row * frame_height
            
            # Extract frame
            frame_rect = pygame.Rect(x, y, frame_width, frame_height)
            frame = sprite_sheet.subsurface(frame_rect).copy()
            frames.append(frame)
        
        animation = SpriteAnimation(name, frames, frame_duration)
        self.animations[name] = animation
        return animation
    
    def create_state_machine(self, name: str) -> AnimationStateMachine:
        """Create animation state machine."""
        state_machine = AnimationStateMachine()
        self.state_machines[name] = state_machine
        return state_machine
    
    def get_animation(self, name: str) -> Optional[SpriteAnimation]:
        """Get animation by name."""
        return self.animations.get(name)
    
    def get_state_machine(self, name: str) -> Optional[AnimationStateMachine]:
        """Get state machine by name."""
        return self.state_machines.get(name)
    
    def update(self, delta_time: float):
        """Update all animations and tweens."""
        if self.paused:
            return
        
        effective_delta = delta_time * self.global_speed_multiplier
        
        # Update sprite animations
        for animation in self.animations.values():
            animation.update(effective_delta)
        
        # Update state machines
        for state_machine in self.state_machines.values():
            state_machine.update(effective_delta)
        
        # Update tweens
        self.tween_manager.update(effective_delta)
    
    def pause_all(self):
        """Pause all animations."""
        self.paused = True
    
    def resume_all(self):
        """Resume all animations."""
        self.paused = False
    
    def set_global_speed(self, speed: float):
        """Set global animation speed multiplier."""
        self.global_speed_multiplier = max(0.0, speed)
    
    # Tween system integration
    def tween_to(self, target_object: Any, target_values: Dict[str, float], 
                 duration: float, ease_type: str = "linear") -> int:
        """Create a tween animation."""
        return self.tween_manager.tween_to(target_object, target_values, duration, ease_type)
    
    def tween_from(self, target_object: Any, start_values: Dict[str, float], 
                   duration: float, ease_type: str = "linear") -> int:
        """Create a from tween animation."""
        return self.tween_manager.tween_from(target_object, start_values, duration, ease_type)
    
    def stop_tween(self, tween_id: int):
        """Stop a specific tween."""
        self.tween_manager.stop_tween(tween_id)
    
    def clear_all_tweens(self):
        """Clear all active tweens."""
        self.tween_manager.clear_all()
