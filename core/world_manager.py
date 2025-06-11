
"""
VoidRay World Manager
Comprehensive world and level management for large-scale games.
"""

from typing import Dict, List, Optional, Any, Tuple, Callable
import json
import os
import threading
from dataclasses import dataclass
from enum import Enum
from ..math.vector2 import Vector2


class WorldState(Enum):
    """World loading states."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    STREAMING = "streaming"
    UNLOADING = "unloading"


@dataclass
class WorldRegion:
    """Represents a region within a world for streaming."""
    id: str
    bounds: Tuple[float, float, float, float]  # x, y, width, height
    objects: List[Any]
    is_loaded: bool = False
    priority: int = 0
    dependencies: List[str] = None


class LevelData:
    """Container for level data and metadata."""
    
    def __init__(self, level_id: str, file_path: str):
        self.level_id = level_id
        self.file_path = file_path
        self.metadata = {}
        self.objects = []
        self.regions: Dict[str, WorldRegion] = {}
        self.spawn_points = {}
        self.world_bounds = (0, 0, 1000, 1000)
        self.state = WorldState.UNLOADED
        
    def add_region(self, region: WorldRegion):
        """Add a region to this level."""
        self.regions[region.id] = region
    
    def get_regions_in_bounds(self, bounds: Tuple[float, float, float, float]) -> List[WorldRegion]:
        """Get all regions that intersect with the given bounds."""
        x, y, w, h = bounds
        result = []
        
        for region in self.regions.values():
            rx, ry, rw, rh = region.bounds
            if (x < rx + rw and x + w > rx and y < ry + rh and y + h > ry):
                result.append(region)
        
        return result


class WorldManager:
    """
    Manages worlds, levels, and streaming for large-scale games.
    """
    
    def __init__(self, streaming_distance: float = 500.0, unload_distance: float = 1000.0):
        """
        Initialize the world manager.
        
        Args:
            streaming_distance: Distance to start loading regions
            unload_distance: Distance to unload regions
        """
        self.levels: Dict[str, LevelData] = {}
        self.current_level: Optional[LevelData] = None
        self.loaded_regions: Dict[str, WorldRegion] = {}
        
        # Streaming parameters
        self.streaming_distance = streaming_distance
        self.unload_distance = unload_distance
        self.player_position = Vector2(0, 0)
        
        # Threading for background loading
        self.streaming_thread: Optional[threading.Thread] = None
        self.streaming_active = False
        self.streaming_queue = []
        
        # Event callbacks
        self.level_callbacks: Dict[str, List[Callable]] = {
            'level_loaded': [],
            'level_unloaded': [],
            'region_loaded': [],
            'region_unloaded': []
        }
        
        # Performance tracking
        self.streaming_stats = {
            'regions_loaded': 0,
            'regions_unloaded': 0,
            'total_objects': 0,
            'loading_time': 0.0
        }
    
    def register_level(self, level_id: str, file_path: str) -> bool:
        """
        Register a level for management.
        
        Args:
            level_id: Unique identifier for the level
            file_path: Path to the level data file
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"Level file not found: {file_path}")
            return False
        
        level_data = LevelData(level_id, file_path)
        
        try:
            # Load level metadata
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            level_data.metadata = data.get('metadata', {})
            level_data.world_bounds = tuple(data.get('world_bounds', [0, 0, 1000, 1000]))
            
            # Load spawn points
            level_data.spawn_points = data.get('spawn_points', {})
            
            # Load regions
            regions_data = data.get('regions', [])
            for region_data in regions_data:
                region = WorldRegion(
                    id=region_data['id'],
                    bounds=tuple(region_data['bounds']),
                    objects=region_data.get('objects', []),
                    priority=region_data.get('priority', 0),
                    dependencies=region_data.get('dependencies', [])
                )
                level_data.add_region(region)
            
            self.levels[level_id] = level_data
            print(f"Registered level: {level_id} with {len(level_data.regions)} regions")
            return True
            
        except Exception as e:
            print(f"Failed to register level {level_id}: {e}")
            return False
    
    def load_level(self, level_id: str, spawn_point: str = "default") -> bool:
        """
        Load a level and set it as current.
        
        Args:
            level_id: Level to load
            spawn_point: Spawn point to use
            
        Returns:
            True if successful, False otherwise
        """
        if level_id not in self.levels:
            print(f"Level not found: {level_id}")
            return False
        
        # Unload current level
        if self.current_level:
            self.unload_level()
        
        level_data = self.levels[level_id]
        level_data.state = WorldState.LOADING
        
        # Set spawn position
        if spawn_point in level_data.spawn_points:
            spawn_pos = level_data.spawn_points[spawn_point]
            self.player_position = Vector2(spawn_pos[0], spawn_pos[1])
        
        self.current_level = level_data
        level_data.state = WorldState.LOADED
        
        # Start streaming
        self._start_streaming()
        
        # Call callbacks
        self._call_callbacks('level_loaded', level_data)
        
        print(f"Loaded level: {level_id}")
        return True
    
    def unload_level(self):
        """Unload the current level."""
        if not self.current_level:
            return
        
        # Stop streaming
        self._stop_streaming()
        
        # Unload all regions
        for region_id in list(self.loaded_regions.keys()):
            self._unload_region(region_id)
        
        # Call callbacks
        self._call_callbacks('level_unloaded', self.current_level)
        
        self.current_level.state = WorldState.UNLOADED
        self.current_level = None
        
        print("Unloaded current level")
    
    def update_player_position(self, position: Vector2):
        """Update player position for streaming calculations."""
        self.player_position = position
        
        if self.current_level and self.current_level.state == WorldState.LOADED:
            self._update_streaming()
    
    def _update_streaming(self):
        """Update region streaming based on player position."""
        if not self.current_level:
            return
        
        # Calculate streaming bounds
        stream_bounds = (
            self.player_position.x - self.streaming_distance,
            self.player_position.y - self.streaming_distance,
            self.streaming_distance * 2,
            self.streaming_distance * 2
        )
        
        unload_bounds = (
            self.player_position.x - self.unload_distance,
            self.player_position.y - self.unload_distance,
            self.unload_distance * 2,
            self.unload_distance * 2
        )
        
        # Find regions to load
        regions_to_load = self.current_level.get_regions_in_bounds(stream_bounds)
        for region in regions_to_load:
            if region.id not in self.loaded_regions:
                self._queue_region_load(region)
        
        # Find regions to unload
        regions_to_unload = []
        for region_id, region in self.loaded_regions.items():
            rx, ry, rw, rh = region.bounds
            ux, uy, uw, uh = unload_bounds
            
            # Check if region is outside unload bounds
            if not (ux < rx + rw and ux + uw > rx and uy < ry + rh and uy + uh > ry):
                regions_to_unload.append(region_id)
        
        for region_id in regions_to_unload:
            self._queue_region_unload(region_id)
    
    def _queue_region_load(self, region: WorldRegion):
        """Queue a region for background loading."""
        if region.id not in [item[1].id for item in self.streaming_queue if item[0] == 'load']:
            self.streaming_queue.append(('load', region))
    
    def _queue_region_unload(self, region_id: str):
        """Queue a region for unloading."""
        if region_id not in [item[1] for item in self.streaming_queue if item[0] == 'unload']:
            self.streaming_queue.append(('unload', region_id))
    
    def _load_region(self, region: WorldRegion):
        """Load a specific region."""
        if region.id in self.loaded_regions:
            return
        
        try:
            # Load region dependencies first
            if region.dependencies:
                for dep_id in region.dependencies:
                    dep_region = self.current_level.regions.get(dep_id)
                    if dep_region and dep_id not in self.loaded_regions:
                        self._load_region(dep_region)
            
            # Create objects in the region
            # This would integrate with your scene/object system
            region.is_loaded = True
            self.loaded_regions[region.id] = region
            
            # Update stats
            self.streaming_stats['regions_loaded'] += 1
            self.streaming_stats['total_objects'] += len(region.objects)
            
            # Call callbacks
            self._call_callbacks('region_loaded', region)
            
            print(f"Loaded region: {region.id}")
            
        except Exception as e:
            print(f"Failed to load region {region.id}: {e}")
    
    def _unload_region(self, region_id: str):
        """Unload a specific region."""
        if region_id not in self.loaded_regions:
            return
        
        try:
            region = self.loaded_regions[region_id]
            
            # Check for dependents
            dependents = self._find_region_dependents(region_id)
            if dependents:
                print(f"Cannot unload region {region_id}: has dependents {dependents}")
                return
            
            # Unload objects in the region
            # This would integrate with your scene/object system
            region.is_loaded = False
            del self.loaded_regions[region_id]
            
            # Update stats
            self.streaming_stats['regions_unloaded'] += 1
            self.streaming_stats['total_objects'] -= len(region.objects)
            
            # Call callbacks
            self._call_callbacks('region_unloaded', region)
            
            print(f"Unloaded region: {region_id}")
            
        except Exception as e:
            print(f"Failed to unload region {region_id}: {e}")
    
    def _find_region_dependents(self, region_id: str) -> List[str]:
        """Find regions that depend on the given region."""
        dependents = []
        for loaded_region in self.loaded_regions.values():
            if loaded_region.dependencies and region_id in loaded_region.dependencies:
                dependents.append(loaded_region.id)
        return dependents
    
    def _start_streaming(self):
        """Start the background streaming thread."""
        if self.streaming_active:
            return
        
        self.streaming_active = True
        self.streaming_thread = threading.Thread(target=self._streaming_worker, daemon=True)
        self.streaming_thread.start()
    
    def _stop_streaming(self):
        """Stop the background streaming thread."""
        self.streaming_active = False
        if self.streaming_thread:
            self.streaming_thread.join(timeout=1.0)
    
    def _streaming_worker(self):
        """Background worker for region streaming."""
        while self.streaming_active:
            if self.streaming_queue:
                action, data = self.streaming_queue.pop(0)
                
                if action == 'load' and isinstance(data, WorldRegion):
                    self._load_region(data)
                elif action == 'unload' and isinstance(data, str):
                    self._unload_region(data)
            else:
                # Sleep briefly to avoid busy waiting
                threading.Event().wait(0.1)
    
    def add_callback(self, event: str, callback: Callable):
        """Add a callback for world events."""
        if event in self.level_callbacks:
            self.level_callbacks[event].append(callback)
    
    def _call_callbacks(self, event: str, *args):
        """Call callbacks for an event."""
        if event in self.level_callbacks:
            for callback in self.level_callbacks[event]:
                try:
                    callback(*args)
                except Exception as e:
                    print(f"Error in world callback: {e}")
    
    def get_streaming_stats(self) -> Dict[str, Any]:
        """Get streaming performance statistics."""
        return {
            'current_level': self.current_level.level_id if self.current_level else None,
            'loaded_regions': len(self.loaded_regions),
            'total_regions': len(self.current_level.regions) if self.current_level else 0,
            'player_position': (self.player_position.x, self.player_position.y),
            'streaming_distance': self.streaming_distance,
            'statistics': self.streaming_stats.copy()
        }
    
    def create_level_template(self, level_id: str, world_size: Tuple[int, int], 
                            region_size: Tuple[int, int] = (200, 200)) -> Dict[str, Any]:
        """Create a template for a new level."""
        world_width, world_height = world_size
        region_width, region_height = region_size
        
        regions = []
        region_id = 0
        
        for y in range(0, world_height, region_height):
            for x in range(0, world_width, region_width):
                regions.append({
                    'id': f"region_{region_id}",
                    'bounds': [x, y, region_width, region_height],
                    'objects': [],
                    'priority': 0
                })
                region_id += 1
        
        level_template = {
            'metadata': {
                'name': level_id,
                'version': '1.0',
                'created': 'auto-generated'
            },
            'world_bounds': [0, 0, world_width, world_height],
            'spawn_points': {
                'default': [world_width // 2, world_height // 2]
            },
            'regions': regions
        }
        
        return level_template
    
    def save_level_template(self, template: Dict[str, Any], file_path: str):
        """Save a level template to file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(template, f, indent=2)
            print(f"Saved level template to: {file_path}")
        except Exception as e:
            print(f"Failed to save level template: {e}")
