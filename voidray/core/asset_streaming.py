
"""
Advanced Asset Streaming System
Intelligent loading and unloading of assets based on proximity and usage patterns.
"""

import threading
import time
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
import os
import pickle
from ..math.vector2 import Vector2


class AssetStream:
    """Represents a streamable asset with metadata."""
    
    def __init__(self, asset_id: str, file_path: str, priority: int = 0):
        self.asset_id = asset_id
        self.file_path = file_path
        self.priority = priority
        self.loaded = False
        self.last_used = time.time()
        self.reference_count = 0
        self.memory_size = 0
        self.data = None
        
    def mark_used(self):
        """Mark asset as recently used."""
        self.last_used = time.time()
        self.reference_count += 1


class AssetStreamingSystem:
    """
    Advanced asset streaming system for large-scale games.
    Automatically loads and unloads assets based on player position and usage patterns.
    """
    
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory_usage = 0
        
        # Asset management
        self.assets: Dict[str, AssetStream] = {}
        self.loaded_assets: Dict[str, Any] = {}
        self.loading_queue: List[str] = []
        self.unload_queue: List[str] = []
        
        # Streaming regions
        self.streaming_regions: Dict[str, Dict] = {}
        self.player_position = Vector2(0, 0)
        self.streaming_radius = 1000.0
        
        # Background loading
        self.background_loading = True
        self.loader_thread = None
        self.loading_active = False
        
        # Performance metrics
        self.load_times: Dict[str, float] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Predictive loading
        self.movement_prediction = True
        self.predicted_areas: List[Vector2] = []
        
        print("Advanced Asset Streaming System initialized")
    
    def register_asset(self, asset_id: str, file_path: str, position: Vector2 = None, 
                      priority: int = 0, auto_load: bool = False):
        """Register an asset for streaming."""
        stream = AssetStream(asset_id, file_path, priority)
        self.assets[asset_id] = stream
        
        if position:
            self.streaming_regions[asset_id] = {
                'position': position,
                'radius': 500.0,
                'priority': priority
            }
        
        if auto_load:
            self.request_load(asset_id)
    
    def register_asset_pack(self, pack_name: str, asset_configs: List[Dict]):
        """Register multiple assets as a pack."""
        for config in asset_configs:
            asset_id = f"{pack_name}_{config['name']}"
            self.register_asset(
                asset_id,
                config['path'],
                config.get('position'),
                config.get('priority', 0)
            )
    
    def update_player_position(self, position: Vector2):
        """Update player position for proximity-based streaming."""
        self.player_position = position
        
        # Predict future positions
        if self.movement_prediction:
            self._update_movement_prediction()
        
        # Check for assets to load/unload
        self._update_streaming_regions()
    
    def request_load(self, asset_id: str, immediate: bool = False) -> bool:
        """Request an asset to be loaded."""
        if asset_id not in self.assets:
            return False
        
        asset = self.assets[asset_id]
        if asset.loaded:
            asset.mark_used()
            self.cache_hits += 1
            return True
        
        self.cache_misses += 1
        
        if immediate:
            return self._load_asset_immediate(asset_id)
        else:
            if asset_id not in self.loading_queue:
                self.loading_queue.append(asset_id)
                self._sort_loading_queue()
            return False
    
    def get_asset(self, asset_id: str) -> Optional[Any]:
        """Get a loaded asset."""
        if asset_id in self.loaded_assets:
            self.assets[asset_id].mark_used()
            return self.loaded_assets[asset_id]
        
        # Try to load immediately if not loaded
        if self.request_load(asset_id, immediate=True):
            return self.loaded_assets.get(asset_id)
        
        return None
    
    def unload_asset(self, asset_id: str):
        """Unload an asset from memory."""
        if asset_id in self.loaded_assets:
            asset = self.assets[asset_id]
            self.current_memory_usage -= asset.memory_size
            
            del self.loaded_assets[asset_id]
            asset.loaded = False
            asset.data = None
            
            print(f"Unloaded asset: {asset_id}")
    
    def start_background_loading(self):
        """Start background asset loading thread."""
        if self.background_loading and not self.loading_active:
            self.loading_active = True
            self.loader_thread = threading.Thread(target=self._background_loader, daemon=True)
            self.loader_thread.start()
    
    def stop_background_loading(self):
        """Stop background loading."""
        self.loading_active = False
        if self.loader_thread:
            self.loader_thread.join(timeout=1.0)
    
    def _background_loader(self):
        """Background thread for loading assets."""
        while self.loading_active:
            if self.loading_queue:
                asset_id = self.loading_queue.pop(0)
                self._load_asset_immediate(asset_id)
            
            # Process unload queue
            if self.unload_queue:
                asset_id = self.unload_queue.pop(0)
                self.unload_asset(asset_id)
            
            # Memory management
            self._manage_memory()
            
            time.sleep(0.01)  # Small delay to prevent CPU spinning
    
    def _load_asset_immediate(self, asset_id: str) -> bool:
        """Load an asset immediately."""
        if asset_id not in self.assets:
            return False
        
        asset = self.assets[asset_id]
        if asset.loaded:
            return True
        
        start_time = time.time()
        
        try:
            # Load based on file extension
            if asset.file_path.endswith(('.png', '.jpg', '.jpeg')):
                import pygame
                data = pygame.image.load(asset.file_path).convert_alpha()
            elif asset.file_path.endswith('.wav'):
                import pygame
                data = pygame.mixer.Sound(asset.file_path)
            elif asset.file_path.endswith('.json'):
                import json
                with open(asset.file_path, 'r') as f:
                    data = json.load(f)
            else:
                # Generic file loading
                with open(asset.file_path, 'rb') as f:
                    data = f.read()
            
            # Calculate memory usage
            if hasattr(data, 'get_size'):
                width, height = data.get_size()
                asset.memory_size = width * height * 4  # Assume RGBA
            else:
                asset.memory_size = len(str(data)) if data else 1024
            
            # Store asset
            asset.data = data
            asset.loaded = True
            self.loaded_assets[asset_id] = data
            self.current_memory_usage += asset.memory_size
            
            load_time = time.time() - start_time
            self.load_times[asset_id] = load_time
            
            print(f"Loaded asset: {asset_id} ({load_time:.3f}s)")
            return True
            
        except Exception as e:
            print(f"Failed to load asset {asset_id}: {e}")
            return False
    
    def _update_streaming_regions(self):
        """Update which assets should be loaded based on streaming regions."""
        for asset_id, region in self.streaming_regions.items():
            distance = (region['position'] - self.player_position).magnitude()
            
            if distance <= region['radius']:
                # Within range - should be loaded
                self.request_load(asset_id)
            elif distance > region['radius'] * 2:
                # Far away - candidate for unloading
                if asset_id in self.loaded_assets:
                    if asset_id not in self.unload_queue:
                        self.unload_queue.append(asset_id)
    
    def _update_movement_prediction(self):
        """Predict future player positions for preloading."""
        # Simple prediction based on current movement
        # In a real implementation, this would use velocity and acceleration
        prediction_distance = 200.0
        
        # Predict positions in multiple directions
        directions = [
            Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1),
            Vector2(1, 1).normalized(), Vector2(-1, 1).normalized(),
            Vector2(1, -1).normalized(), Vector2(-1, -1).normalized()
        ]
        
        self.predicted_areas = [
            self.player_position + direction * prediction_distance 
            for direction in directions
        ]
    
    def _sort_loading_queue(self):
        """Sort loading queue by priority and distance."""
        def sort_key(asset_id):
            asset = self.assets[asset_id]
            priority = asset.priority
            
            # Distance-based priority
            if asset_id in self.streaming_regions:
                distance = (self.streaming_regions[asset_id]['position'] - self.player_position).magnitude()
                distance_priority = max(0, 1000 - distance)
            else:
                distance_priority = 0
            
            return -(priority + distance_priority)
        
        self.loading_queue.sort(key=sort_key)
    
    def _manage_memory(self):
        """Manage memory usage by unloading old assets."""
        if self.current_memory_usage > self.max_memory_bytes:
            # Find assets to unload (oldest, lowest priority)
            candidates = []
            
            for asset_id, asset in self.assets.items():
                if asset.loaded and asset.reference_count == 0:
                    age = time.time() - asset.last_used
                    candidates.append((asset_id, age, asset.priority))
            
            # Sort by age and priority
            candidates.sort(key=lambda x: (x[2], -x[1]))  # Low priority, old age first
            
            # Unload until under memory limit
            for asset_id, _, _ in candidates:
                if self.current_memory_usage <= self.max_memory_bytes * 0.8:
                    break
                self.unload_asset(asset_id)
    
    def get_streaming_stats(self) -> Dict[str, Any]:
        """Get streaming system statistics."""
        return {
            'total_assets': len(self.assets),
            'loaded_assets': len(self.loaded_assets),
            'memory_usage_mb': self.current_memory_usage / (1024 * 1024),
            'memory_limit_mb': self.max_memory_bytes / (1024 * 1024),
            'cache_hit_rate': self.cache_hits / max(1, self.cache_hits + self.cache_misses),
            'loading_queue_size': len(self.loading_queue),
            'unload_queue_size': len(self.unload_queue),
            'streaming_regions': len(self.streaming_regions)
        }
    
    def optimize_memory(self):
        """Force memory optimization."""
        print("Optimizing asset memory...")
        initial_usage = self.current_memory_usage
        
        # Unload all unreferenced assets older than 30 seconds
        cutoff_time = time.time() - 30.0
        to_unload = []
        
        for asset_id, asset in self.assets.items():
            if (asset.loaded and asset.reference_count == 0 and 
                asset.last_used < cutoff_time):
                to_unload.append(asset_id)
        
        for asset_id in to_unload:
            self.unload_asset(asset_id)
        
        freed_mb = (initial_usage - self.current_memory_usage) / (1024 * 1024)
        print(f"Asset optimization freed {freed_mb:.2f} MB")
    
    def preload_region(self, center: Vector2, radius: float):
        """Preload all assets in a region."""
        for asset_id, region in self.streaming_regions.items():
            distance = (region['position'] - center).magnitude()
            if distance <= radius:
                self.request_load(asset_id)
    
    def cleanup(self):
        """Clean up the streaming system."""
        self.stop_background_loading()
        
        # Unload all assets
        for asset_id in list(self.loaded_assets.keys()):
            self.unload_asset(asset_id)
        
        print("Asset streaming system cleaned up")
