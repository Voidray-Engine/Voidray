
"""
VoidRay Resource Manager
Enterprise-grade resource management with streaming, pooling, and memory optimization.
"""

from typing import Dict, Any, Optional, List, Callable, Union
import os
import threading
import time
import weakref
import hashlib
import json
from queue import Queue, Empty
from abc import ABC, abstractmethod


class ResourceMetadata:
    """Metadata for tracking resource usage and performance."""
    
    def __init__(self, resource_id: str, file_path: str, resource_type: str):
        self.resource_id = resource_id
        self.file_path = file_path
        self.resource_type = resource_type
        self.load_time = 0.0
        self.last_accessed = time.time()
        self.access_count = 0
        self.memory_size = 0
        self.ref_count = 0
        self.is_streaming = False
        self.priority = 0  # Higher priority = keep in memory longer


class ResourceLoader(ABC):
    """Abstract base class for resource loaders."""
    
    @abstractmethod
    def can_load(self, file_path: str) -> bool:
        """Check if this loader can handle the file type."""
        pass
    
    @abstractmethod
    def load(self, file_path: str) -> Any:
        """Load the resource from file."""
        pass
    
    @abstractmethod
    def unload(self, resource: Any):
        """Clean up the resource."""
        pass


class ImageLoader(ResourceLoader):
    """Loader for image resources."""
    
    def can_load(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tga']
    
    def load(self, file_path: str) -> Any:
        import pygame
        return pygame.image.load(file_path).convert_alpha()
    
    def unload(self, resource: Any):
        # Pygame surfaces are automatically garbage collected
        pass


class AudioLoader(ResourceLoader):
    """Loader for audio resources."""
    
    def can_load(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.wav', '.mp3', '.ogg', '.flac']
    
    def load(self, file_path: str) -> Any:
        import pygame
        return pygame.mixer.Sound(file_path)
    
    def unload(self, resource: Any):
        # Pygame sounds are automatically garbage collected
        pass


class TextLoader(ResourceLoader):
    """Loader for text resources."""
    
    def can_load(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.txt', '.json', '.xml', '.csv', '.yaml', '.ini']
    
    def load(self, file_path: str) -> Any:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                import json
                return json.load(f)
            else:
                return f.read()
    
    def unload(self, resource: Any):
        # Strings are automatically garbage collected
        pass


class ResourceManager:
    """
    Enterprise-grade resource management system with streaming, pooling, and optimization.
    """
    
    def __init__(self, max_memory_mb: int = 512, enable_streaming: bool = True):
        """
        Initialize the resource manager.
        
        Args:
            max_memory_mb: Maximum memory usage in MB
            enable_streaming: Enable streaming for large resources
        """
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.enable_streaming = enable_streaming
        
        # Resource storage
        self.resources: Dict[str, Any] = {}
        self.metadata: Dict[str, ResourceMetadata] = {}
        self.weak_refs: Dict[str, weakref.ref] = {}
        
        # Resource loaders
        self.loaders: List[ResourceLoader] = [
            ImageLoader(),
            AudioLoader(),
            TextLoader()
        ]
        
        # Streaming system
        self.streaming_queue: Queue = Queue()
        self.streaming_thread: Optional[threading.Thread] = None
        self.streaming_active = False
        
        # Memory management
        self.current_memory_usage = 0
        self.memory_threshold = 0.8  # Start cleanup at 80% memory usage
        
        # Resource pools for frequently used resources
        self.resource_pools: Dict[str, List[Any]] = {}
        self.pool_sizes: Dict[str, int] = {}
        
        # Performance tracking
        self.load_statistics: Dict[str, Dict[str, float]] = {}
        self.cache_hit_rate = 0.0
        self.total_requests = 0
        self.cache_hits = 0
        
        # Dependency tracking
        self.dependencies: Dict[str, List[str]] = {}
        self.dependents: Dict[str, List[str]] = {}
        
        if enable_streaming:
            self._start_streaming_thread()
    
    def register_loader(self, loader: ResourceLoader):
        """Register a custom resource loader."""
        self.loaders.append(loader)
    
    def create_resource_pool(self, pool_name: str, max_size: int = 10):
        """Create a resource pool for frequently used resources."""
        self.resource_pools[pool_name] = []
        self.pool_sizes[pool_name] = max_size
    
    def load_resource(self, resource_id: str, file_path: str, 
                     priority: int = 0, dependencies: List[str] = None) -> Any:
        """
        Load a resource with advanced features.
        
        Args:
            resource_id: Unique identifier for the resource
            file_path: Path to the resource file
            priority: Resource priority (higher = keep longer)
            dependencies: List of dependent resource IDs
            
        Returns:
            Loaded resource or None if failed
        """
        self.total_requests += 1
        
        # Check if already loaded
        if resource_id in self.resources:
            self.cache_hits += 1
            metadata = self.metadata[resource_id]
            metadata.last_accessed = time.time()
            metadata.access_count += 1
            self._update_cache_hit_rate()
            return self.resources[resource_id]
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Resource file not found: {file_path}")
            return None
        
        # Find appropriate loader
        loader = self._find_loader(file_path)
        if not loader:
            print(f"No loader found for file: {file_path}")
            return None
        
        # Load dependencies first
        if dependencies:
            for dep_id in dependencies:
                if dep_id not in self.resources:
                    print(f"Warning: Dependency {dep_id} not loaded for {resource_id}")
        
        # Check memory before loading
        if self._should_free_memory():
            self._free_memory()
        
        # Load the resource
        start_time = time.time()
        try:
            resource = loader.load(file_path)
            load_time = time.time() - start_time
            
            # Create metadata
            metadata = ResourceMetadata(resource_id, file_path, type(loader).__name__)
            metadata.load_time = load_time
            metadata.priority = priority
            metadata.memory_size = self._estimate_memory_size(resource)
            
            # Store resource and metadata
            self.resources[resource_id] = resource
            self.metadata[resource_id] = metadata
            self.current_memory_usage += metadata.memory_size
            
            # Track dependencies
            if dependencies:
                self.dependencies[resource_id] = dependencies
                for dep_id in dependencies:
                    if dep_id not in self.dependents:
                        self.dependents[dep_id] = []
                    self.dependents[dep_id].append(resource_id)
            
            # Update statistics
            resource_type = type(loader).__name__
            if resource_type not in self.load_statistics:
                self.load_statistics[resource_type] = {'total_time': 0, 'count': 0}
            
            self.load_statistics[resource_type]['total_time'] += load_time
            self.load_statistics[resource_type]['count'] += 1
            
            self._update_cache_hit_rate()
            
            print(f"Loaded resource '{resource_id}' in {load_time:.3f}s ({metadata.memory_size} bytes)")
            return resource
            
        except Exception as e:
            print(f"Failed to load resource '{resource_id}': {e}")
            return None
    
    def load_resource_async(self, resource_id: str, file_path: str, 
                           callback: Callable = None, priority: int = 0):
        """Load a resource asynchronously."""
        if self.enable_streaming:
            self.streaming_queue.put((resource_id, file_path, callback, priority))
        else:
            # Fallback to synchronous loading
            resource = self.load_resource(resource_id, file_path, priority)
            if callback:
                callback(resource_id, resource)
    
    def get_resource(self, resource_id: str) -> Optional[Any]:
        """Get a cached resource."""
        if resource_id in self.resources:
            metadata = self.metadata[resource_id]
            metadata.last_accessed = time.time()
            metadata.access_count += 1
            return self.resources[resource_id]
        return None
    
    def unload_resource(self, resource_id: str, force: bool = False):
        """
        Unload a resource from memory.
        
        Args:
            resource_id: Resource to unload
            force: Force unload even if there are dependencies
        """
        if resource_id not in self.resources:
            return
        
        # Check for dependents
        if not force and resource_id in self.dependents:
            dependents = self.dependents[resource_id]
            active_dependents = [dep for dep in dependents if dep in self.resources]
            if active_dependents:
                print(f"Cannot unload {resource_id}: has active dependents {active_dependents}")
                return
        
        # Get loader for cleanup
        metadata = self.metadata[resource_id]
        loader = self._find_loader(metadata.file_path)
        
        # Clean up resource
        if loader:
            try:
                loader.unload(self.resources[resource_id])
            except Exception as e:
                print(f"Error unloading resource {resource_id}: {e}")
        
        # Remove from memory
        self.current_memory_usage -= metadata.memory_size
        del self.resources[resource_id]
        del self.metadata[resource_id]
        
        # Clean up dependencies
        if resource_id in self.dependencies:
            del self.dependencies[resource_id]
        
        if resource_id in self.dependents:
            del self.dependents[resource_id]
        
        print(f"Unloaded resource: {resource_id}")
    
    def preload_resources(self, resource_list: List[Dict[str, Any]]):
        """Preload a list of resources."""
        print(f"Preloading {len(resource_list)} resources...")
        
        for resource_info in resource_list:
            resource_id = resource_info['id']
            file_path = resource_info['path']
            priority = resource_info.get('priority', 0)
            dependencies = resource_info.get('dependencies', [])
            
            self.load_resource(resource_id, file_path, priority, dependencies)
        
        print("Resource preloading complete")
    
    def get_from_pool(self, pool_name: str):
        """Get a resource from a pool."""
        if pool_name in self.resource_pools and self.resource_pools[pool_name]:
            return self.resource_pools[pool_name].pop()
        return None
    
    def return_to_pool(self, pool_name: str, resource: Any):
        """Return a resource to a pool."""
        if pool_name in self.resource_pools:
            pool = self.resource_pools[pool_name]
            max_size = self.pool_sizes.get(pool_name, 10)
            
            if len(pool) < max_size:
                pool.append(resource)
    
    def _find_loader(self, file_path: str) -> Optional[ResourceLoader]:
        """Find an appropriate loader for a file."""
        for loader in self.loaders:
            if loader.can_load(file_path):
                return loader
        return None
    
    def _estimate_memory_size(self, resource: Any) -> int:
        """Estimate memory usage of a resource."""
        import sys
        
        try:
            # Basic size estimation
            size = sys.getsizeof(resource)
            
            # Special handling for pygame surfaces
            if hasattr(resource, 'get_size') and hasattr(resource, 'get_bitsize'):
                width, height = resource.get_size()
                bits_per_pixel = resource.get_bitsize()
                size = width * height * (bits_per_pixel // 8)
            
            return size
        except:
            return 1024  # Default estimate
    
    def _should_free_memory(self) -> bool:
        """Check if memory should be freed."""
        usage_ratio = self.current_memory_usage / self.max_memory_bytes
        return usage_ratio > self.memory_threshold
    
    def _free_memory(self):
        """Free memory by unloading least recently used resources."""
        if not self.metadata:
            return
        
        # Sort resources by access time and priority
        sorted_resources = sorted(
            self.metadata.items(),
            key=lambda x: (x[1].priority, x[1].last_accessed)
        )
        
        target_memory = self.max_memory_bytes * 0.6  # Free down to 60%
        
        for resource_id, metadata in sorted_resources:
            if self.current_memory_usage <= target_memory:
                break
            
            # Don't unload high priority resources
            if metadata.priority > 5:
                continue
            
            self.unload_resource(resource_id)
        
        print(f"Memory cleanup complete. Usage: {self.current_memory_usage / 1024 / 1024:.1f}MB")
    
    def _start_streaming_thread(self):
        """Start the background streaming thread."""
        self.streaming_active = True
        self.streaming_thread = threading.Thread(target=self._streaming_worker, daemon=True)
        self.streaming_thread.start()
    
    def _streaming_worker(self):
        """Background worker for streaming resources."""
        while self.streaming_active:
            try:
                resource_id, file_path, callback, priority = self.streaming_queue.get(timeout=1.0)
                
                resource = self.load_resource(resource_id, file_path, priority)
                
                if callback:
                    callback(resource_id, resource)
                    
            except Empty:
                continue
            except Exception as e:
                print(f"Error in streaming worker: {e}")
    
    def _update_cache_hit_rate(self):
        """Update cache hit rate statistics."""
        if self.total_requests > 0:
            self.cache_hit_rate = self.cache_hits / self.total_requests
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get detailed memory usage statistics."""
        resource_breakdown = {}
        for resource_id, metadata in self.metadata.items():
            resource_type = metadata.resource_type
            if resource_type not in resource_breakdown:
                resource_breakdown[resource_type] = {'count': 0, 'memory': 0}
            
            resource_breakdown[resource_type]['count'] += 1
            resource_breakdown[resource_type]['memory'] += metadata.memory_size
        
        return {
            'total_memory_mb': self.current_memory_usage / 1024 / 1024,
            'max_memory_mb': self.max_memory_bytes / 1024 / 1024,
            'memory_usage_percent': (self.current_memory_usage / self.max_memory_bytes) * 100,
            'resource_count': len(self.resources),
            'cache_hit_rate': self.cache_hit_rate,
            'resource_breakdown': resource_breakdown,
            'load_statistics': self.load_statistics
        }
    
    def cleanup(self):
        """Clean up the resource manager."""
        self.streaming_active = False
        if self.streaming_thread:
            self.streaming_thread.join(timeout=1.0)
        
        # Unload all resources
        resource_ids = list(self.resources.keys())
        for resource_id in resource_ids:
            self.unload_resource(resource_id, force=True)
        
        print("Resource manager cleanup complete")
