
"""
VoidRay Resource Pool
Manages object pooling for better memory performance.
"""

from typing import Dict, List, Callable, TypeVar, Generic
import weakref

T = TypeVar('T')

class ObjectPool(Generic[T]):
    """
    Generic object pool for reusing objects instead of creating/destroying them.
    """
    
    def __init__(self, factory: Callable[[], T], reset_func: Callable[[T], None] = None, max_size: int = 100):
        """
        Initialize object pool.
        
        Args:
            factory: Function that creates new objects
            reset_func: Function to reset objects when returning to pool
            max_size: Maximum number of pooled objects
        """
        self.factory = factory
        self.reset_func = reset_func
        self.max_size = max_size
        self.pool: List[T] = []
        self.active_objects: weakref.WeakSet = weakref.WeakSet()
    
    def get(self) -> T:
        """Get an object from the pool or create a new one."""
        if self.pool:
            obj = self.pool.pop()
        else:
            obj = self.factory()
        
        self.active_objects.add(obj)
        return obj
    
    def return_object(self, obj: T):
        """Return an object to the pool."""
        if len(self.pool) < self.max_size:
            if self.reset_func:
                self.reset_func(obj)
            self.pool.append(obj)
        
        if obj in self.active_objects:
            self.active_objects.remove(obj)
    
    def clear(self):
        """Clear the pool."""
        self.pool.clear()
        
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics."""
        return {
            'pooled': len(self.pool),
            'active': len(self.active_objects),
            'max_size': self.max_size
        }


class ResourceManager:
    """
    Manages resource pools and automatic cleanup.
    """
    
    def __init__(self):
        self.pools: Dict[str, ObjectPool] = {}
        self.cleanup_callbacks: List[Callable] = []
    
    def create_pool(self, name: str, factory: Callable, reset_func: Callable = None, max_size: int = 100):
        """Create a new object pool."""
        self.pools[name] = ObjectPool(factory, reset_func, max_size)
    
    def get_from_pool(self, pool_name: str):
        """Get object from named pool."""
        if pool_name in self.pools:
            return self.pools[pool_name].get()
        return None
    
    def return_to_pool(self, pool_name: str, obj):
        """Return object to named pool."""
        if pool_name in self.pools:
            self.pools[pool_name].return_object(obj)
    
    def add_cleanup_callback(self, callback: Callable):
        """Add cleanup callback for shutdown."""
        self.cleanup_callbacks.append(callback)
    
    def cleanup_all(self):
        """Clean up all resources."""
        for pool in self.pools.values():
            pool.clear()
        
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in cleanup callback: {e}")
        
        self.cleanup_callbacks.clear()
    
    def get_memory_stats(self) -> Dict:
        """Get memory usage statistics."""
        stats = {}
        for name, pool in self.pools.items():
            stats[name] = pool.get_stats()
        return stats
