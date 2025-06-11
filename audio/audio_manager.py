"""
VoidRay Advanced Audio Manager
Comprehensive audio system for demanding games with streaming, 3D audio, and effects.
"""

import pygame
import threading
import os
from typing import Dict, Optional, List, Tuple
from ..math.vector2 import Vector2


class AudioChannel:
    """Represents an audio channel with effects and controls."""

    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.channel = pygame.mixer.Channel(channel_id)
        self.volume = 1.0
        self.pan = 0.0  # -1.0 (left) to 1.0 (right)
        self.effects = {}

    def play(self, sound, loops=0, fade_ms=0):
        """Play sound on this channel."""
        if fade_ms > 0:
            return self.channel.play(sound, loops, fade_ms=fade_ms)
        return self.channel.play(sound, loops)

    def set_volume(self, volume: float):
        """Set channel volume."""
        self.volume = max(0.0, min(1.0, volume))
        self.channel.set_volume(self.volume)

    def stop(self):
        """Stop playback on this channel."""
        self.channel.stop()

    def is_busy(self) -> bool:
        """Check if channel is playing audio."""
        return self.channel.get_busy()


class AudioManager:
    """
    Advanced audio manager supporting streaming, 3D audio, and multiple channels.
    """

    def __init__(self, channels: int = 16, frequency: int = 44100, buffer_size: int = 1024):
        """
        Initialize the enhanced audio manager.

        Args:
            channels: Number of audio channels
            frequency: Audio frequency
            buffer_size: Audio buffer size
        """
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.master_volume = 1.0
        self.current_music: Optional[str] = None
        self.audio_available = False
        self.channels: List[AudioChannel] = []
        self.listener_position = Vector2(0, 0)
        self.listener_orientation = 0.0
        self.sound_cache_limit = 100

        # Audio threading for non-blocking operations
        self.audio_thread_pool = []
        self.streaming_enabled = True

        # Audio effects
        self.reverb_enabled = False
        self.doppler_enabled = True
        self.distance_model = "inverse"  # "linear", "inverse", "exponential"

        # Initialize pygame mixer with comprehensive error handling
        try:
            pygame.mixer.pre_init(
                frequency=frequency, 
                size=-16, 
                channels=2, 
                buffer=buffer_size
            )
            pygame.mixer.init()
            pygame.mixer.set_num_channels(channels)

            # Initialize audio channels
            for i in range(channels):
                self.channels.append(AudioChannel(i))

            self.audio_available = True
            print(f"Enhanced audio system initialized - {channels} channels at {frequency}Hz")

        except (pygame.error, OSError) as e:
            print(f"Audio system not available: {e}")
            print("Continuing without audio support")
            self.audio_available = False
            # Initialize dummy mixer to prevent crashes
            self.channels = []

    @property
    def available(self) -> bool:
        """Compatibility property for engine validator."""
        return self.audio_available

    def set_master_volume(self, volume: float):
        """Set master volume affecting all audio."""
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_all_volumes()

    def _update_all_volumes(self):
        """Update all volume levels based on master volume."""
        if not self.audio_available:
            return

        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        for sound in self.sounds.values():
            # Note: pygame doesn't support per-sound volume, handled in playback
            pass

    def load_sound(self, name: str, file_path: str, streaming: bool = False):
        """
        Load a sound effect with optional streaming.

        Args:
            name: Identifier for the sound
            file_path: Path to the audio file
            streaming: Whether to use streaming for large files
        """
        if not self.audio_available:
            return

        # Check cache limit
        if len(self.sounds) >= self.sound_cache_limit:
            self._cleanup_old_sounds()

        try:
            if streaming and self.streaming_enabled:
                # For large files, we'll load them when needed
                self.sounds[name] = {"path": file_path, "streaming": True}
            else:
                sound = pygame.mixer.Sound(file_path)
                sound.set_volume(self.sfx_volume * self.master_volume)
                self.sounds[name] = sound

            print(f"Loaded sound: {name} from {file_path}")

        except pygame.error as e:
            print(f"Error loading sound {file_path}: {e}")

    def load_sound_batch(self, sound_list: Dict[str, str]):
        """
        Load multiple sounds in batch for better performance.

        Args:
            sound_list: Dictionary of {name: file_path}
        """
        print(f"Loading {len(sound_list)} sounds in batch...")

        for name, file_path in sound_list.items():
            self.load_sound(name, file_path)

        print("Batch loading complete")

    def play_sound(self, name: str, volume: float = 1.0, loops: int = 0, 
                   channel: Optional[int] = None, position: Optional[Vector2] = None):
        """
        Play a sound with advanced options.

        Args:
            name: Name of the sound to play
            volume: Volume multiplier
            loops: Number of times to loop
            channel: Specific channel to use (None for auto)
            position: 3D position for spatial audio
        """
        if not self.audio_available or name not in self.sounds:
            return None

        sound_data = self.sounds[name]

        # Handle streaming sounds
        if isinstance(sound_data, dict) and sound_data.get("streaming"):
            sound = pygame.mixer.Sound(sound_data["path"])
        else:
            sound = sound_data

        # Calculate 3D audio if position provided
        if position:
            volume, pan = self._calculate_3d_audio(position, volume)

        # Find available channel
        target_channel = None
        if channel is not None and 0 <= channel < len(self.channels):
            target_channel = self.channels[channel]
        else:
            # Find free channel
            for ch in self.channels:
                if not ch.is_busy():
                    target_channel = ch
                    break

        if target_channel:
            sound.set_volume(volume * self.sfx_volume * self.master_volume)
            return target_channel.play(sound, loops)

        return None

    def play_sound_3d(self, name: str, position: Vector2, volume: float = 1.0, 
                      max_distance: float = 1000.0, loops: int = 0):
        """
        Play sound with 3D positioning.

        Args:
            name: Sound name
            position: World position of sound
            volume: Base volume
            max_distance: Maximum hearing distance
            loops: Loop count
        """
        if not self.audio_available:
            return None

        # Calculate distance attenuation
        distance = (position - self.listener_position).magnitude()

        if distance > max_distance:
            return None  # Too far to hear

        # Apply distance model
        if self.distance_model == "linear":
            distance_factor = max(0, 1.0 - (distance / max_distance))
        elif self.distance_model == "inverse":
            distance_factor = 1.0 / (1.0 + distance / 100.0)
        else:  # exponential
            distance_factor = pow(0.5, distance / 100.0)

        adjusted_volume = volume * distance_factor

        return self.play_sound(name, adjusted_volume, loops, position=position)

    def _calculate_3d_audio(self, position: Vector2, base_volume: float) -> Tuple[float, float]:
        """Calculate volume and pan for 3D audio."""
        relative_pos = position - self.listener_position
        distance = relative_pos.magnitude()

        # Calculate pan based on horizontal position
        if distance > 0:
            pan = relative_pos.x / max(distance, 1.0)
            pan = max(-1.0, min(1.0, pan))
        else:
            pan = 0.0

        return base_volume, pan

    def set_listener(self, position: Vector2, orientation: float = 0.0):
        """
        Set 3D audio listener position and orientation.

        Args:
            position: Listener position in world space
            orientation: Listener orientation in degrees
        """
        self.listener_position = position
        self.listener_orientation = orientation

    def load_music(self, file_path: str, streaming: bool = True):
        """
        Load background music with streaming support.

        Args:
            file_path: Path to the music file
            streaming: Whether to stream the music
        """
        if not self.audio_available:
            return

        try:
            if streaming:
                # pygame.mixer.music automatically streams
                pygame.mixer.music.load(file_path)
            else:
                pygame.mixer.music.load(file_path)

            print(f"Loaded music: {file_path}")

        except pygame.error as e:
            print(f"Error loading music {file_path}: {e}")

    def play_music(self, file_path: Optional[str] = None, loops: int = -1, 
                   fade_in: float = 0, start_pos: float = 0):
        """
        Play background music with advanced options.

        Args:
            file_path: Path to music file
            loops: Number of times to loop (-1 for infinite)
            fade_in: Fade in time in seconds
            start_pos: Starting position in seconds
        """
        if not self.audio_available:
            return

        try:
            if file_path:
                self.load_music(file_path)
                self.current_music = file_path

            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

            if fade_in > 0:
                pygame.mixer.music.play(loops, start=start_pos, fade_ms=int(fade_in * 1000))
            else:
                pygame.mixer.music.play(loops, start=start_pos)

        except pygame.error as e:
            print(f"Error playing music: {e}")

    def create_sound_group(self, name: str, sound_list: List[str], 
                          max_concurrent: int = 3):
        """
        Create a sound group for managing multiple instances.

        Args:
            name: Group name
            sound_list: List of sound names in the group
            max_concurrent: Maximum concurrent instances
        """
        # This would be used for things like footsteps, gunshots, etc.
        # Implementation would track active instances per group
        pass

    def apply_audio_effect(self, effect_name: str, **params):
        """
        Apply audio effects (reverb, echo, etc.).

        Args:
            effect_name: Name of the effect
            **params: Effect parameters
        """
        if effect_name == "reverb":
            self.reverb_enabled = params.get("enabled", True)
        # Additional effects would be implemented here

    def pause_all_sounds(self):
        """Pause all currently playing sounds."""
        if not self.audio_available:
            return

        for channel in self.channels:
            channel.channel.pause()

    def unpause_all_sounds(self):
        """Unpause all paused sounds."""
        if not self.audio_available:
            return

        for channel in self.channels:
            channel.channel.unpause()

    def stop_all_sounds(self):
        """Stop all currently playing sounds."""
        if not self.audio_available:
            return

        pygame.mixer.stop()

    def get_audio_info(self) -> Dict:
        """Get detailed audio system information."""
        if not self.audio_available:
            return {"available": False}

        return {
            "available": True,
            "frequency": pygame.mixer.get_init()[0] if pygame.mixer.get_init() else 0,
            "channels": len(self.channels),
            "loaded_sounds": len(self.sounds),
            "master_volume": self.master_volume,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "active_channels": sum(1 for ch in self.channels if ch.is_busy())
        }

    def _cleanup_old_sounds(self):
        """Clean up least recently used sounds."""
        # Simple implementation - remove first 10 sounds
        # In a full implementation, you'd track usage and remove LRU
        items_to_remove = list(self.sounds.keys())[:10]
        for key in items_to_remove:
            del self.sounds[key]

        print(f"Cleaned up {len(items_to_remove)} sounds from cache")

    def preload_audio_pack(self, pack_name: str, audio_files: Dict[str, str]):
        """
        Preload an entire audio pack for a level or scene.

        Args:
            pack_name: Name of the audio pack
            audio_files: Dictionary of audio files to load
        """
        print(f"Preloading audio pack: {pack_name}")

        for name, file_path in audio_files.items():
            self.load_sound(f"{pack_name}_{name}", file_path)

        print(f"Audio pack '{pack_name}' loaded with {len(audio_files)} sounds")

    def set_music_volume(self, volume: float):
        """Set music volume."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.audio_available:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    def set_sfx_volume(self, volume: float):
        """Set sound effects volume."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._update_all_volumes()

    def cleanup(self):
        """Clean up audio resources."""
        if self.audio_available:
            self.stop_all_sounds()
            pygame.mixer.music.stop()

            # Stop any audio threads
            for thread in self.audio_thread_pool:
                if thread.is_alive():
                    thread.join(timeout=1.0)

            pygame.mixer.quit()
            print("Enhanced audio system cleaned up")