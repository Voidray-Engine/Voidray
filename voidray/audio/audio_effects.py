
"""
VoidRay Audio Effects System
Advanced audio processing and effects for enhanced game audio.
"""

import pygame
import numpy as np
from typing import Dict, List, Optional, Callable
from ..math.vector2 import Vector2


class AudioEffect:
    """Base class for audio effects."""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.parameters = {}
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Process audio data and return modified audio."""
        if not self.enabled:
            return audio_data
        return self._apply_effect(audio_data)
    
    def _apply_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Override this method to implement specific effects."""
        return audio_data


class ReverbEffect(AudioEffect):
    """Reverb effect for spatial audio."""
    
    def __init__(self, decay: float = 0.5, delay: float = 0.1):
        super().__init__("Reverb")
        self.decay = decay
        self.delay = delay
        self.delay_buffer = None
    
    def _apply_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply reverb effect."""
        if self.delay_buffer is None:
            delay_samples = int(self.delay * 44100)  # Assuming 44.1kHz
            self.delay_buffer = np.zeros(delay_samples)
        
        # Simple reverb implementation
        output = audio_data.copy()
        for i in range(len(audio_data)):
            delayed_sample = self.delay_buffer[i % len(self.delay_buffer)]
            output[i] += delayed_sample * self.decay
            self.delay_buffer[i % len(self.delay_buffer)] = audio_data[i]
        
        return output


class EchoEffect(AudioEffect):
    """Echo effect with configurable delay and feedback."""
    
    def __init__(self, delay: float = 0.3, feedback: float = 0.4):
        super().__init__("Echo")
        self.delay = delay
        self.feedback = feedback
        self.buffer = None
    
    def _apply_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply echo effect."""
        if self.buffer is None:
            buffer_size = int(self.delay * 44100)
            self.buffer = np.zeros(buffer_size)
        
        output = audio_data.copy()
        for i in range(len(audio_data)):
            echo_sample = self.buffer[i % len(self.buffer)]
            output[i] += echo_sample
            self.buffer[i % len(self.buffer)] = audio_data[i] + echo_sample * self.feedback
        
        return output


class AudioEffectChain:
    """Chain multiple audio effects together."""
    
    def __init__(self):
        self.effects: List[AudioEffect] = []
    
    def add_effect(self, effect: AudioEffect):
        """Add an effect to the chain."""
        self.effects.append(effect)
    
    def remove_effect(self, effect_name: str):
        """Remove an effect by name."""
        self.effects = [e for e in self.effects if e.name != effect_name]
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Process audio through all effects in chain."""
        result = audio_data
        for effect in self.effects:
            result = effect.process(result)
        return result


class AudioEffectManager:
    """Manages audio effects for the game engine."""
    
    def __init__(self):
        self.effect_chains: Dict[str, AudioEffectChain] = {}
        self.global_effects = AudioEffectChain()
        self.presets = self._create_presets()
    
    def create_effect_chain(self, name: str) -> AudioEffectChain:
        """Create a new effect chain."""
        chain = AudioEffectChain()
        self.effect_chains[name] = chain
        return chain
    
    def get_effect_chain(self, name: str) -> Optional[AudioEffectChain]:
        """Get an effect chain by name."""
        return self.effect_chains.get(name)
    
    def apply_preset(self, chain_name: str, preset_name: str):
        """Apply a preset configuration to an effect chain."""
        if preset_name in self.presets and chain_name in self.effect_chains:
            chain = self.effect_chains[chain_name]
            preset_config = self.presets[preset_name]
            
            # Clear existing effects
            chain.effects.clear()
            
            # Add preset effects
            for effect_config in preset_config:
                effect = self._create_effect_from_config(effect_config)
                if effect:
                    chain.add_effect(effect)
    
    def _create_presets(self) -> Dict[str, List[Dict]]:
        """Create predefined effect presets."""
        return {
            "cave": [
                {"type": "reverb", "decay": 0.8, "delay": 0.2},
                {"type": "echo", "delay": 0.5, "feedback": 0.3}
            ],
            "underwater": [
                {"type": "reverb", "decay": 0.9, "delay": 0.15}
            ],
            "space": [
                {"type": "echo", "delay": 0.8, "feedback": 0.6},
                {"type": "reverb", "decay": 0.7, "delay": 0.3}
            ]
        }
    
    def _create_effect_from_config(self, config: Dict) -> Optional[AudioEffect]:
        """Create an effect from configuration."""
        effect_type = config.get("type")
        
        if effect_type == "reverb":
            return ReverbEffect(
                decay=config.get("decay", 0.5),
                delay=config.get("delay", 0.1)
            )
        elif effect_type == "echo":
            return EchoEffect(
                delay=config.get("delay", 0.3),
                feedback=config.get("feedback", 0.4)
            )
        
        return None
