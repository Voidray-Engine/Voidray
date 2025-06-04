"""
VoidRay Audio Manager
Centralized audio system for playing sounds and music.
"""

import pygame
from typing import Dict, Optional


class AudioManager:
    """
    Manages all audio playback including sound effects and background music.
    """
    
    def __init__(self):
        """
        Initialize the audio manager.
        """
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.current_music: Optional[str] = None
        self.audio_available = False
        
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.audio_available = True
            print("Audio system initialized")
        except pygame.error as e:
            print(f"Audio system not available: {e}")
            print("Continuing without audio support")
    
    def load_sound(self, name: str, file_path: str):
        """
        Load a sound effect from file.
        
        Args:
            name: Identifier for the sound
            file_path: Path to the audio file
        """
        if not self.audio_available:
            return
            
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(self.sfx_volume)
            self.sounds[name] = sound
            print(f"Loaded sound: {name} from {file_path}")
        except pygame.error as e:
            print(f"Error loading sound {file_path}: {e}")
    
    def play_sound(self, name: str, volume: float = 1.0, loops: int = 0):
        """
        Play a loaded sound effect.
        
        Args:
            name: Name of the sound to play
            volume: Volume multiplier (0.0 to 1.0)
            loops: Number of times to loop (-1 for infinite)
        """
        if not self.audio_available:
            return
            
        if name in self.sounds:
            sound = self.sounds[name]
            sound.set_volume(self.sfx_volume * volume)
            sound.play(loops)
        else:
            print(f"Sound '{name}' not found")
    
    def stop_sound(self, name: str):
        """
        Stop a playing sound effect.
        
        Args:
            name: Name of the sound to stop
        """
        if not self.audio_available:
            return
            
        if name in self.sounds:
            self.sounds[name].stop()
    
    def load_music(self, file_path: str):
        """
        Load background music from file.
        
        Args:
            file_path: Path to the music file
        """
        if not self.audio_available:
            return
            
        try:
            pygame.mixer.music.load(file_path)
            print(f"Loaded music: {file_path}")
        except pygame.error as e:
            print(f"Error loading music {file_path}: {e}")
    
    def play_music(self, file_path: Optional[str] = None, loops: int = -1, fade_in: float = 0):
        """
        Play background music.
        
        Args:
            file_path: Path to music file (None to play already loaded music)
            loops: Number of times to loop (-1 for infinite)
            fade_in: Fade in time in seconds
        """
        if not self.audio_available:
            return
            
        try:
            if file_path:
                self.load_music(file_path)
                self.current_music = file_path
            
            pygame.mixer.music.set_volume(self.music_volume)
            
            if fade_in > 0:
                pygame.mixer.music.play(loops, fade_ms=int(fade_in * 1000))
            else:
                pygame.mixer.music.play(loops)
                
        except pygame.error as e:
            print(f"Error playing music: {e}")
    
    def stop_music(self, fade_out: float = 0):
        """
        Stop background music.
        
        Args:
            fade_out: Fade out time in seconds
        """
        if not self.audio_available:
            return
            
        if fade_out > 0:
            pygame.mixer.music.fadeout(int(fade_out * 1000))
        else:
            pygame.mixer.music.stop()
    
    def pause_music(self):
        """
        Pause background music.
        """
        if not self.audio_available:
            return
            
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """
        Resume paused background music.
        """
        if not self.audio_available:
            return
            
        pygame.mixer.music.unpause()
    
    def is_music_playing(self) -> bool:
        """
        Check if music is currently playing.
        
        Returns:
            True if music is playing, False otherwise
        """
        if not self.audio_available:
            return False
            
        return pygame.mixer.music.get_busy()
    
    def set_music_volume(self, volume: float):
        """
        Set the background music volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        
        if self.audio_available:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float):
        """
        Set the sound effects volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        if self.audio_available:
            # Update volume for all loaded sounds
            for sound in self.sounds.values():
                sound.set_volume(self.sfx_volume)
    
    def get_music_volume(self) -> float:
        """
        Get the current music volume.
        
        Returns:
            Current music volume (0.0 to 1.0)
        """
        return self.music_volume
    
    def get_sfx_volume(self) -> float:
        """
        Get the current sound effects volume.
        
        Returns:
            Current SFX volume (0.0 to 1.0)
        """
        return self.sfx_volume
    
    def cleanup(self):
        """
        Clean up audio resources.
        """
        if self.audio_available:
            pygame.mixer.music.stop()
            for sound in self.sounds.values():
                sound.stop()
            pygame.mixer.quit()
            print("Audio system cleaned up")
        else:
            print("Audio system was not initialized")
