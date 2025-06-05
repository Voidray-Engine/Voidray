"""
VoidRay Asset Loader
Centralized system for loading and caching game assets.
"""

import pygame
import json
import os
from typing import Dict, Any, Optional


class AssetLoader:
    """
    Manages loading and caching of game assets.
    """
    
    def __init__(self):
        """
        Initialize the asset loader.
        """
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.data: Dict[str, Any] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        
        # Asset search paths
        self.image_paths = ["assets/images/", "images/", "./"]
        self.sound_paths = ["assets/sounds/", "sounds/", "./"]
        self.data_paths = ["assets/data/", "data/", "./"]
        self.font_paths = ["assets/fonts/", "fonts/", "./"]
        
        print("Asset loader initialized")
    
    def add_search_path(self, asset_type: str, path: str):
        """
        Add a search path for a specific asset type.
        
        Args:
            asset_type: Type of asset ('image', 'sound', 'data', 'font')
            path: Path to add to search list
        """
        if asset_type == "image":
            self.image_paths.insert(0, path)
        elif asset_type == "sound":
            self.sound_paths.insert(0, path)
        elif asset_type == "data":
            self.data_paths.insert(0, path)
        elif asset_type == "font":
            self.font_paths.insert(0, path)
    
    def _find_file(self, filename: str, search_paths: list) -> Optional[str]:
        """
        Find a file in the search paths.
        
        Args:
            filename: Name of the file to find
            search_paths: List of paths to search
            
        Returns:
            Full path to the file or None if not found
        """
        for path in search_paths:
            full_path = os.path.join(path, filename)
            if os.path.exists(full_path):
                return full_path
        return None
    
    def load_image(self, name: str, filename: str, convert_alpha: bool = True) -> pygame.Surface:
        """
        Load an image asset.
        
        Args:
            name: Identifier for the image
            filename: Filename of the image
            convert_alpha: Whether to convert with alpha channel
            
        Returns:
            The loaded pygame Surface
        """
        if name in self.images:
            return self.images[name]
        
        file_path = self._find_file(filename, self.image_paths)
        if not file_path:
            print(f"Image file not found: {filename}")
            # Create a placeholder surface
            surface = pygame.Surface((32, 32))
            surface.fill((255, 0, 255))  # Magenta placeholder
            self.images[name] = surface
            return surface
        
        try:
            if convert_alpha:
                surface = pygame.image.load(file_path).convert_alpha()
            else:
                surface = pygame.image.load(file_path).convert()
            
            self.images[name] = surface
            print(f"Loaded image: {name} from {file_path}")
            return surface
            
        except pygame.error as e:
            print(f"Error loading image {file_path}: {e}")
            # Create a placeholder surface
            surface = pygame.Surface((32, 32))
            surface.fill((255, 0, 255))  # Magenta placeholder
            self.images[name] = surface
            return surface
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """
        Get a loaded image by name.
        
        Args:
            name: Name of the image
            
        Returns:
            The pygame Surface or None if not found
        """
        return self.images.get(name)
    
    def load_sound(self, name: str, filename: str) -> pygame.mixer.Sound:
        """
        Load a sound asset.
        
        Args:
            name: Identifier for the sound
            filename: Filename of the sound
            
        Returns:
            The loaded pygame Sound
        """
        if name in self.sounds:
            return self.sounds[name]
        
        # Check if mixer is available
        try:
            pygame.mixer.get_init()
        except pygame.error:
            print(f"Audio not available, skipping sound: {filename}")
            return None
        
        file_path = self._find_file(filename, self.sound_paths)
        if not file_path:
            print(f"Sound file not found: {filename}")
            return None
        
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
            print(f"Loaded sound: {name} from {file_path}")
            return sound
            
        except pygame.error as e:
            print(f"Error loading sound {file_path}: {e}")
            return None
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """
        Get a loaded sound by name.
        
        Args:
            name: Name of the sound
            
        Returns:
            The pygame Sound or None if not found
        """
        return self.sounds.get(name)
    
    def load_data(self, name: str, filename: str) -> Any:
        """
        Load a JSON data file.
        
        Args:
            name: Identifier for the data
            filename: Filename of the JSON file
            
        Returns:
            The loaded data structure
        """
        if name in self.data:
            return self.data[name]
        
        file_path = self._find_file(filename, self.data_paths)
        if not file_path:
            print(f"Data file not found: {filename}")
            self.data[name] = {}
            return {}
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.data[name] = data
            print(f"Loaded data: {name} from {file_path}")
            return data
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data {file_path}: {e}")
            self.data[name] = {}
            return {}
    
    def get_data(self, name: str) -> Any:
        """
        Get loaded data by name.
        
        Args:
            name: Name of the data
            
        Returns:
            The data or None if not found
        """
        return self.data.get(name)
    
    def load_font(self, name: str, filename: str = None, size: int = 24) -> pygame.font.Font:
        """
        Load a font asset.
        
        Args:
            name: Identifier for the font
            filename: Filename of the font (None for system default)
            size: Font size
            
        Returns:
            The loaded pygame Font
        """
        font_key = f"{name}_{size}"
        if font_key in self.fonts:
            return self.fonts[font_key]
        
        if filename:
            file_path = self._find_file(filename, self.font_paths)
            if file_path:
                try:
                    font = pygame.font.Font(file_path, size)
                    self.fonts[font_key] = font
                    print(f"Loaded font: {name} from {file_path}")
                    return font
                except pygame.error as e:
                    print(f"Error loading font {file_path}: {e}")
        
        # Fall back to system default font
        font = pygame.font.Font(None, size)
        self.fonts[font_key] = font
        return font
    
    def get_font(self, name: str, size: int = 24) -> Optional[pygame.font.Font]:
        """
        Get a loaded font by name and size.
        
        Args:
            name: Name of the font
            size: Font size
            
        Returns:
            The pygame Font or None if not found
        """
        font_key = f"{name}_{size}"
        return self.fonts.get(font_key)
    
    def preload_assets(self, asset_list: Dict[str, Any]):
        """
        Preload a list of assets from a configuration.
        
        Args:
            asset_list: Dictionary defining assets to load
        """
        print("Preloading assets...")
        
        # Load images
        if "images" in asset_list:
            for name, filename in asset_list["images"].items():
                self.load_image(name, filename)
        
        # Load sounds
        if "sounds" in asset_list:
            for name, filename in asset_list["sounds"].items():
                self.load_sound(name, filename)
        
        # Load data
        if "data" in asset_list:
            for name, filename in asset_list["data"].items():
                self.load_data(name, filename)
        
        # Load fonts
        if "fonts" in asset_list:
            for name, config in asset_list["fonts"].items():
                if isinstance(config, dict):
                    filename = config.get("filename")
                    size = config.get("size", 24)
                    self.load_font(name, filename, size)
                else:
                    self.load_font(name, config)
        
        print("Asset preloading complete")
    
    def unload_asset(self, asset_type: str, name: str):
        """
        Unload a specific asset from memory.
        
        Args:
            asset_type: Type of asset ('image', 'sound', 'data', 'font')
            name: Name of the asset to unload
        """
        if asset_type == "image" and name in self.images:
            del self.images[name]
        elif asset_type == "sound" and name in self.sounds:
            del self.sounds[name]
        elif asset_type == "data" and name in self.data:
            del self.data[name]
        elif asset_type == "font":
            # Remove all font sizes for this name
            keys_to_remove = [key for key in self.fonts.keys() if key.startswith(f"{name}_")]
            for key in keys_to_remove:
                del self.fonts[key]
    
    def clear_all(self):
        """
        Clear all loaded assets from memory.
        """
        self.images.clear()
        self.sounds.clear()
        self.data.clear()
        self.fonts.clear()
        print("All assets cleared from memory")
