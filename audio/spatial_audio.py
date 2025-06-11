
"""
VoidRay Spatial Audio System
3D positioned audio with distance attenuation for immersive 2.5D games.
"""

import pygame
import math
from typing import Dict, List, Optional
from ..math.vector2 import Vector2


class AudioSource:
    """3D positioned audio source."""
    
    def __init__(self, position: Vector2, sound_path: str):
        self.position = position
        self.sound = pygame.mixer.Sound(sound_path)
        self.volume = 1.0
        self.pitch = 1.0
        self.max_distance = 500.0
        self.rolloff_factor = 1.0
        self.is_looping = False
        self.is_playing = False
        self.channel: Optional[pygame.mixer.Channel] = None
        
    def play(self, loops: int = 0):
        """Play the audio source."""
        self.channel = self.sound.play(loops)
        self.is_playing = True
        self.is_looping = loops != 0
        
    def stop(self):
        """Stop the audio source."""
        if self.channel:
            self.channel.stop()
        self.is_playing = False
        
    def set_position(self, position: Vector2):
        """Update audio source position."""
        self.position = position


class SpatialAudioManager:
    """Manages 3D positioned audio for 2.5D games."""
    
    def __init__(self):
        self.audio_sources: List[AudioSource] = []
        self.listener_position = Vector2.zero()
        self.listener_forward = Vector2(0, 1)  # Forward direction
        self.master_volume = 1.0
        self.doppler_factor = 1.0
        self.speed_of_sound = 343.0  # meters per second
        
        # Audio effects
        self.reverb_enabled = False
        self.echo_enabled = False
        self.echo_delay = 0.3
        self.echo_decay = 0.5
        
    def add_audio_source(self, source: AudioSource):
        """Add an audio source to the scene."""
        self.audio_sources.append(source)
        
    def remove_audio_source(self, source: AudioSource):
        """Remove an audio source from the scene."""
        if source in self.audio_sources:
            source.stop()
            self.audio_sources.remove(source)
            
    def set_listener_position(self, position: Vector2, forward: Vector2 = None):
        """Update listener position and orientation."""
        self.listener_position = position
        if forward:
            self.listener_forward = forward.normalized()
            
    def update(self, delta_time: float):
        """Update spatial audio calculations."""
        for source in self.audio_sources:
            if source.is_playing and source.channel:
                self._update_source_audio(source)
                
    def _update_source_audio(self, source: AudioSource):
        """Update audio parameters for a source."""
        distance = (source.position - self.listener_position).magnitude()
        
        # Distance attenuation
        if distance <= 0:
            volume = source.volume
        elif distance >= source.max_distance:
            volume = 0.0
        else:
            # Inverse square law with rolloff
            attenuation = 1.0 / (1.0 + source.rolloff_factor * (distance / source.max_distance))
            volume = source.volume * attenuation
            
        # Apply master volume
        final_volume = volume * self.master_volume
        final_volume = max(0.0, min(1.0, final_volume))
        
        # Set channel volume
        if source.channel:
            source.channel.set_volume(final_volume)
            
        # Calculate stereo panning
        self._update_stereo_panning(source, distance)
        
    def _update_stereo_panning(self, source: AudioSource, distance: float):
        """Update stereo panning based on position."""
        if not source.channel or distance <= 0:
            return
            
        # Calculate relative position
        relative_pos = source.position - self.listener_position
        
        # Project onto listener's right vector (perpendicular to forward)
        right_vector = Vector2(-self.listener_forward.y, self.listener_forward.x)
        pan_factor = relative_pos.dot(right_vector) / distance
        
        # Clamp pan factor to [-1, 1]
        pan_factor = max(-1.0, min(1.0, pan_factor))
        
        # Convert to left/right volumes
        left_volume = (1.0 - pan_factor) * 0.5
        right_volume = (1.0 + pan_factor) * 0.5
        
        # Note: pygame doesn't support per-channel panning directly
        # This would need to be implemented with multiple channels or audio processing
        
    def play_sound_at_position(self, sound_path: str, position: Vector2, 
                              volume: float = 1.0, loops: int = 0) -> AudioSource:
        """Play a sound at a specific world position."""
        source = AudioSource(position, sound_path)
        source.volume = volume
        self.add_audio_source(source)
        source.play(loops)
        return source
        
    def create_ambient_sound(self, sound_path: str, volume: float = 0.5) -> AudioSource:
        """Create an ambient sound that follows the listener."""
        source = AudioSource(self.listener_position, sound_path)
        source.volume = volume
        source.max_distance = float('inf')  # No distance attenuation
        self.add_audio_source(source)
        return source
        
    def set_reverb(self, enabled: bool, room_size: float = 0.5):
        """Enable/disable reverb effect."""
        self.reverb_enabled = enabled
        # Note: Actual reverb implementation would require audio processing
        
    def set_echo(self, enabled: bool, delay: float = 0.3, decay: float = 0.5):
        """Enable/disable echo effect."""
        self.echo_enabled = enabled
        self.echo_delay = delay
        self.echo_decay = decay
        
    def cleanup(self):
        """Clean up all audio sources."""
        for source in self.audio_sources:
            source.stop()
        self.audio_sources.clear()
        
    def get_audio_stats(self) -> Dict[str, any]:
        """Get audio system statistics."""
        active_sources = sum(1 for s in self.audio_sources if s.is_playing)
        return {
            'total_sources': len(self.audio_sources),
            'active_sources': active_sources,
            'listener_position': (self.listener_position.x, self.listener_position.y),
            'master_volume': self.master_volume,
            'reverb_enabled': self.reverb_enabled,
            'echo_enabled': self.echo_enabled
        }
