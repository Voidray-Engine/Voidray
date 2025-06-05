"""
VoidRay Asset Loader
Enhanced asset loading system with better caching and file support.
"""

import pygame
import os
from typing import Dict, Optional, List, Any
from pathlib import Path


class AssetLoader:
    """
    Enhanced Asset Loader that handles images, sounds, and other game assets
    with efficient caching and multiple file format support.
    """

    def __init__(self):
        """Initialize the asset loader."""
        # Asset caches for different types
        self.image_cache: Dict[str, pygame.Surface] = {}
        self.sound_cache: Dict[str, pygame.mixer.Sound] = {}
        self.music_cache: Dict[str, str] = {}  # Store file paths for music

        # Search paths for different asset types
        self.search_paths = {
            "image": ["./", "./assets/", "./images/", "./textures/", "./sprites/", "./examples/assets/"],
            "sound": ["./", "./assets/", "./audio/", "./sounds/", "./sfx/", "./examples/assets/"],
            "music": ["./", "./assets/", "./audio/", "./music/", "./examples/assets/"]
        }

        # Supported file formats
        self.supported_formats = {
            "image": [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".svg", ".tga"],
            "sound": [".wav", ".ogg", ".mp3"],
            "music": [".mp3", ".ogg", ".wav", ".mid", ".midi"]
        }

        # Loading statistics
        self.stats = {
            "images_loaded": 0,
            "sounds_loaded": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "failed_loads": 0
        }

        print("AssetLoader initialized with enhanced caching and format support")

    def add_search_path(self, asset_type: str, path: str):
        """Add a search path for a specific asset type."""
        if asset_type not in self.search_paths:
            self.search_paths[asset_type] = []

        # Normalize path and ensure it exists
        normalized_path = os.path.normpath(path)
        if not normalized_path.endswith("/"):
            normalized_path += "/"

        if normalized_path not in self.search_paths[asset_type]:
            self.search_paths[asset_type].append(normalized_path)

        print(f"Added search path for {asset_type}: {normalized_path}")

    def _find_file(self, filename: str, asset_type: str) -> Optional[str]:
        """Find a file in the search paths."""
        if not filename:
            return None

        # If it's already a full path and exists, use it
        if os.path.isfile(filename):
            return filename

        # Search in configured paths
        for search_path in self.search_paths.get(asset_type, []):
            # Try exact filename first
            full_path = os.path.join(search_path, filename)
            if os.path.isfile(full_path):
                return full_path

            # Try with different extensions if no extension provided
            if "." not in filename:
                for ext in self.supported_formats.get(asset_type, []):
                    full_path_with_ext = full_path + ext
                    if os.path.isfile(full_path_with_ext):
                        return full_path_with_ext

        return None

    def load_image(self, name: str, filename: str = None) -> Optional[pygame.Surface]:
        """
        Load an image asset with enhanced format support.

        Args:
            name: Cache key for the image
            filename: Filename to load (defaults to name if not provided)

        Returns:
            Loaded pygame Surface or None if failed
        """
        if filename is None:
            filename = name

        # Check cache first
        if name in self.image_cache:
            self.stats["cache_hits"] += 1
            return self.image_cache[name]

        self.stats["cache_misses"] += 1

        # Find the file
        file_path = self._find_file(filename, "image")
        if not file_path:
            print(f"Warning: Could not find image file: {filename}")
            self.stats["failed_loads"] += 1
            return None

        try:
            # Load the image
            if file_path.lower().endswith('.svg'):
                # SVG requires special handling - for now, create a placeholder
                print(f"Warning: SVG support limited, using placeholder for: {filename}")
                surface = pygame.Surface((32, 32), pygame.SRCALPHA)
                pygame.draw.circle(surface, (255, 255, 255), (16, 16), 15)
            else:
                surface = pygame.image.load(file_path)
                # Convert to optimize blitting performance
                if surface.get_alpha() is not None:
                    surface = surface.convert_alpha()
                else:
                    surface = surface.convert()

            self.image_cache[name] = surface
            self.stats["images_loaded"] += 1
            print(f"Loaded image: {filename} -> {file_path}")
            return surface

        except pygame.error as e:
            print(f"Failed to load image {filename}: {e}")
            self.stats["failed_loads"] += 1
            return None

    def load_sound(self, name: str, filename: str = None) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound asset.

        Args:
            name: Cache key for the sound
            filename: Filename to load (defaults to name if not provided)

        Returns:
            Loaded pygame Sound or None if failed
        """
        if filename is None:
            filename = name

        # Check cache first
        if name in self.sound_cache:
            self.stats["cache_hits"] += 1
            return self.sound_cache[name]

        self.stats["cache_misses"] += 1

        # Find the file
        file_path = self._find_file(filename, "sound")
        if not file_path:
            print(f"Warning: Could not find sound file: {filename}")
            self.stats["failed_loads"] += 1
            return None

        try:
            sound = pygame.mixer.Sound(file_path)
            self.sound_cache[name] = sound
            self.stats["sounds_loaded"] += 1
            print(f"Loaded sound: {filename} -> {file_path}")
            return sound

        except pygame.error as e:
            print(f"Failed to load sound {filename}: {e}")
            self.stats["failed_loads"] += 1
            return None

    def load_music(self, name: str, filename: str = None) -> bool:
        """
        Load music for background playback.

        Args:
            name: Cache key for the music
            filename: Filename to load (defaults to name if not provided)

        Returns:
            True if loaded successfully, False otherwise
        """
        if filename is None:
            filename = name

        # Find the file
        file_path = self._find_file(filename, "music")
        if not file_path:
            print(f"Warning: Could not find music file: {filename}")
            self.stats["failed_loads"] += 1
            return False

        try:
            # Music is streamed, not cached in memory
            self.music_cache[name] = file_path
            print(f"Registered music: {filename} -> {file_path}")
            return True

        except Exception as e:
            print(f"Failed to register music {filename}: {e}")
            self.stats["failed_loads"] += 1
            return False

    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Get a cached image by name."""
        return self.image_cache.get(name)

    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get a cached sound by name."""
        return self.sound_cache.get(name)

    def get_music_path(self, name: str) -> Optional[str]:
        """Get a music file path by name."""
        return self.music_cache.get(name)

    def preload_assets(self, asset_config: Dict[str, List[str]]):
        """
        Preload a batch of assets.

        Args:
            asset_config: Dictionary with asset types as keys and lists of filenames as values
        """
        print("Preloading assets...")

        for asset_type, filenames in asset_config.items():
            for filename in filenames:
                if asset_type == "image":
                    self.load_image(filename)
                elif asset_type == "sound":
                    self.load_sound(filename)
                elif asset_type == "music":
                    self.load_music(filename)

    def list_available_files(self, asset_type: str) -> List[str]:
        """List all available files of a specific type in search paths."""
        available_files = []
        extensions = self.supported_formats.get(asset_type, [])

        for search_path in self.search_paths.get(asset_type, []):
            if os.path.exists(search_path):
                try:
                    for filename in os.listdir(search_path):
                        file_path = os.path.join(search_path, filename)
                        if os.path.isfile(file_path):
                            file_ext = os.path.splitext(filename)[1].lower()
                            if file_ext in extensions:
                                available_files.append(filename)
                except OSError:
                    continue

        return list(set(available_files))  # Remove duplicates

    def clear_cache(self, asset_type: str = None):
        """Clear asset cache for a specific type or all types."""
        if asset_type == "image" or asset_type is None:
            self.image_cache.clear()
        if asset_type == "sound" or asset_type is None:
            self.sound_cache.clear()
        if asset_type == "music" or asset_type is None:
            self.music_cache.clear()

        print(f"Cleared {asset_type or 'all'} asset cache")

    def clear_all(self):
        """Clear all caches and reset statistics."""
        self.clear_cache()
        self.stats = {
            "images_loaded": 0,
            "sounds_loaded": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "failed_loads": 0
        }

    def get_loading_stats(self) -> Dict[str, int]:
        """Get asset loading statistics."""
        return self.stats.copy()

    def get_cache_info(self) -> Dict[str, int]:
        """Get information about cached assets."""
        return {
            "images_cached": len(self.image_cache),
            "sounds_cached": len(self.sound_cache),
            "music_registered": len(self.music_cache)
        }