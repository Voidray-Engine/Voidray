"""
VoidRay Particle System
Advanced particle effects for 2D/2.5D games.
"""

import pygame
import random
import math
from typing import List, Callable, Optional, Dict, Any
from ..math.vector2 import Vector2
from ..utils.color import Color


class Particle:
    """Individual particle with physics and rendering properties."""

    def __init__(self, position: Vector2):
        self.position = position
        self.velocity = Vector2.zero()
        self.acceleration = Vector2.zero()

        # Visual properties
        self.color = Color.WHITE
        self.size = 4.0
        self.life = 1.0
        self.max_life = 1.0
        self.alpha = 255

        # Physics properties
        self.gravity_scale = 1.0
        self.drag = 0.0
        self.rotation = 0.0
        self.angular_velocity = 0.0

        # Custom properties
        self.custom_data = {}

    def update(self, delta_time: float, gravity: Vector2 = Vector2.zero()):
        """Update particle physics and properties."""
        # Apply gravity
        if gravity.magnitude() > 0:
            self.acceleration += gravity * self.gravity_scale

        # Apply drag
        if self.drag > 0:
            drag_force = self.velocity * -self.drag
            self.velocity += drag_force * delta_time

        # Update physics
        self.velocity += self.acceleration * delta_time
        self.position += self.velocity * delta_time
        self.rotation += self.angular_velocity * delta_time

        # Update life
        self.life -= delta_time

        # Update alpha based on life
        life_ratio = self.life / self.max_life
        self.alpha = int(255 * max(0, life_ratio))

        # Reset acceleration (forces are applied each frame)
        self.acceleration = Vector2.zero()

    def is_alive(self) -> bool:
        """Check if particle is still alive."""
        return self.life > 0

    def render(self, renderer):
        """Render the particle."""
        if not self.is_alive():
            return

        # Create surface with alpha
        particle_color = (*self.color[:3], self.alpha)

        # Render as circle (can be extended for sprites)
        pygame.draw.circle(
            renderer.screen,
            particle_color[:3],
            (int(self.position.x), int(self.position.y)),
            int(self.size)
        )


class ParticleSystem:
    """Manages a collection of particles with emission and behavior."""

    def __init__(self, position: Vector2, max_particles: int = 1000):
        self.position = position
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        self.active = True

        # Emission properties
        self.emission_rate = 50.0  # particles per second
        self.emission_timer = 0.0
        self.auto_emit = True
        self.burst_count = 0

        # Particle spawn properties
        self.spawn_area = Vector2(10, 10)  # spawn area size
        self.initial_velocity = Vector2(0, -100)
        self.velocity_variation = Vector2(50, 20)
        self.life_range = (1.0, 3.0)
        self.size_range = (2.0, 8.0)
        self.color_start = Color.WHITE
        self.color_end = Color.RED

        # Physics
        self.gravity = Vector2(0, 98)
        self.drag = 0.1

        # Custom update functions
        self.update_functions: List[Callable[[Particle, float], None]] = []

    def emit_particle(self) -> Particle:
        """Emit a single particle."""
        # Random spawn position within area
        spawn_offset = Vector2(
            random.uniform(-self.spawn_area.x/2, self.spawn_area.x/2),
            random.uniform(-self.spawn_area.y/2, self.spawn_area.y/2)
        )
        spawn_pos = self.position + spawn_offset

        # Create particle
        particle = Particle(spawn_pos)

        # Set initial velocity with variation
        vel_x = self.initial_velocity.x + random.uniform(-self.velocity_variation.x, self.velocity_variation.x)
        vel_y = self.initial_velocity.y + random.uniform(-self.velocity_variation.y, self.velocity_variation.y)
        particle.velocity = Vector2(vel_x, vel_y)

        # Set life
        particle.life = random.uniform(*self.life_range)
        particle.max_life = particle.life

        # Set size
        particle.size = random.uniform(*self.size_range)

        # Set color
        particle.color = self.color_start

        # Set physics properties
        particle.drag = self.drag

        return particle

    def emit_burst(self, count: int):
        """Emit a burst of particles."""
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                particle = self.emit_particle()
                self.particles.append(particle)

    def add_update_function(self, func: Callable[[Particle, float], None]):
        """Add custom particle update function."""
        self.update_functions.append(func)

    def update(self, delta_time: float):
        """Update all particles and emission."""
        if not self.active:
            return

        # Handle emission
        if self.auto_emit and self.emission_rate > 0:
            self.emission_timer += delta_time
            particles_to_emit = int(self.emission_timer * self.emission_rate)

            if particles_to_emit > 0:
                self.emission_timer -= particles_to_emit / self.emission_rate

                for _ in range(particles_to_emit):
                    if len(self.particles) < self.max_particles:
                        particle = self.emit_particle()
                        self.particles.append(particle)

        # Handle burst emission
        if self.burst_count > 0:
            self.emit_burst(min(self.burst_count, self.max_particles - len(self.particles)))
            self.burst_count = 0

        # Update particles
        for particle in self.particles[:]:
            particle.update(delta_time, self.gravity)

            # Apply custom update functions
            for update_func in self.update_functions:
                update_func(particle, delta_time)

            # Remove dead particles
            if not particle.is_alive():
                self.particles.remove(particle)

    def render(self, renderer):
        """Render all particles."""
        for particle in self.particles:
            particle.render(renderer)

    def clear(self):
        """Remove all particles."""
        self.particles.clear()

    def get_particle_count(self) -> int:
        """Get current particle count."""
        return len(self.particles)


class ParticleSystemManager:
    """Manages multiple particle systems."""

    def __init__(self):
        self.systems: Dict[str, ParticleSystem] = {}
        self.presets: Dict[str, Dict[str, Any]] = {}
        self._create_default_presets()

    def _create_default_presets(self):
        """Create default particle system presets."""
        # Fire effect
        self.presets["fire"] = {
            "emission_rate": 100,
            "initial_velocity": Vector2(0, -150),
            "velocity_variation": Vector2(30, 20),
            "life_range": (0.5, 1.5),
            "size_range": (3, 8),
            "color_start": Color.YELLOW,
            "color_end": Color.RED,
            "gravity": Vector2(0, -50),
            "drag": 0.5
        }

        # Explosion effect
        self.presets["explosion"] = {
            "emission_rate": 0,  # burst only
            "initial_velocity": Vector2(0, 0),
            "velocity_variation": Vector2(200, 200),
            "life_range": (1.0, 2.0),
            "size_range": (2, 6),
            "color_start": Color.WHITE,
            "color_end": Color.GRAY,
            "gravity": Vector2(0, 100),
            "drag": 0.2
        }

        # Magic sparkles
        self.presets["sparkles"] = {
            "emission_rate": 50,
            "initial_velocity": Vector2(0, -50),
            "velocity_variation": Vector2(100, 100),
            "life_range": (2.0, 4.0),
            "size_range": (1, 4),
            "color_start": Color.CYAN,
            "color_end": Color.BLUE,
            "gravity": Vector2(0, 0),
            "drag": 0.8
        }

    def create_system(self, position: Vector2, preset: str = None) -> ParticleSystem:
        """Create a new particle system."""
        system = ParticleSystem(position)

        if preset and preset in self.presets:
            preset_data = self.presets[preset]
            for key, value in preset_data.items():
                if hasattr(system, key):
                    setattr(system, key, value)

        self.systems[str(id(system))] = system
        return system

    def remove_system(self, system: ParticleSystem):
        """Remove a particle system."""
        system_id = str(id(system))
        if system_id in self.systems:
            del self.systems[system_id]

    def update(self, delta_time: float):
        """Update all particle systems."""
        for system_id in list(self.systems.keys()):
            system = self.systems[system_id]
            system.update(delta_time)

            # Remove inactive systems with no particles
            if not system.active and system.get_particle_count() == 0:
                del self.systems[system_id]

    def render(self, renderer):
        """Render all active particle systems."""
        for system in self.systems.values():
            if system.active:
                system.render(renderer)

    def clear_all_systems(self):
        """Clear all particle systems for cleanup."""
        for system in self.systems.values():
            system.active = False
            system.clear()
        self.systems.clear()

    def get_total_particle_count(self) -> int:
        """Get total particle count across all systems."""
        return sum(system.get_particle_count() for system in self.systems.values())