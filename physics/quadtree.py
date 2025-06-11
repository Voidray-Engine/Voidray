
"""
Advanced Quadtree Spatial Partitioning System
High-performance spatial indexing for collision detection and object queries.
"""

from typing import List, Optional, Set, Tuple, Callable
from ..math.vector2 import Vector2
import time


class QuadTreeNode:
    """A node in the quadtree spatial structure."""
    
    def __init__(self, bounds: Tuple[float, float, float, float], max_objects: int = 10, max_depth: int = 8):
        self.bounds = bounds  # (x, y, width, height)
        self.max_objects = max_objects
        self.max_depth = max_depth
        self.objects = []
        self.children = [None, None, None, None]  # NW, NE, SW, SE
        self.is_divided = False
        
    def insert(self, obj, position: Vector2, size: Vector2 = None) -> bool:
        """Insert an object into the quadtree."""
        if not self._contains_point(position):
            return False
        
        # If we have capacity and no children, add object here
        if len(self.objects) < self.max_objects and not self.is_divided:
            self.objects.append((obj, position, size))
            return True
        
        # If we haven't subdivided yet, do it now
        if not self.is_divided:
            self._subdivide()
        
        # Try to insert into children
        for child in self.children:
            if child.insert(obj, position, size):
                return True
        
        # If it doesn't fit in any child, keep it at this level
        self.objects.append((obj, position, size))
        return True
    
    def query_range(self, bounds: Tuple[float, float, float, float]) -> List:
        """Query objects within a rectangular range."""
        found = []
        
        # Check if this node intersects with query range
        if not self._intersects(bounds):
            return found
        
        # Check objects at this level
        for obj, pos, size in self.objects:
            if self._point_in_bounds(pos, bounds):
                found.append(obj)
        
        # Query children if they exist
        if self.is_divided:
            for child in self.children:
                found.extend(child.query_range(bounds))
        
        return found
    
    def query_radius(self, center: Vector2, radius: float) -> List:
        """Query objects within a circular radius."""
        # Convert circle to bounding box for initial culling
        bounds = (
            center.x - radius,
            center.y - radius,
            radius * 2,
            radius * 2
        )
        
        candidates = self.query_range(bounds)
        
        # Filter by actual distance
        result = []
        for obj in candidates:
            # Get object position (this would need to be stored with the object)
            obj_pos = getattr(obj, 'position', center)
            if hasattr(obj, 'transform'):
                obj_pos = obj.transform.position
            
            distance = (obj_pos - center).magnitude()
            if distance <= radius:
                result.append(obj)
        
        return result
    
    def remove(self, obj, position: Vector2) -> bool:
        """Remove an object from the quadtree."""
        if not self._contains_point(position):
            return False
        
        # Try to remove from this level
        for i, (stored_obj, pos, size) in enumerate(self.objects):
            if stored_obj is obj:
                del self.objects[i]
                return True
        
        # Try to remove from children
        if self.is_divided:
            for child in self.children:
                if child.remove(obj, position):
                    return True
        
        return False
    
    def clear(self):
        """Clear all objects from the quadtree."""
        self.objects.clear()
        if self.is_divided:
            for child in self.children:
                child.clear()
        self.children = [None, None, None, None]
        self.is_divided = False
    
    def _subdivide(self):
        """Subdivide this node into four children."""
        x, y, w, h = self.bounds
        half_w = w / 2
        half_h = h / 2
        
        # Create four children: NW, NE, SW, SE
        self.children[0] = QuadTreeNode((x, y, half_w, half_h), self.max_objects, self.max_depth - 1)
        self.children[1] = QuadTreeNode((x + half_w, y, half_w, half_h), self.max_objects, self.max_depth - 1)
        self.children[2] = QuadTreeNode((x, y + half_h, half_w, half_h), self.max_objects, self.max_depth - 1)
        self.children[3] = QuadTreeNode((x + half_w, y + half_h, half_w, half_h), self.max_objects, self.max_depth - 1)
        
        self.is_divided = True
    
    def _contains_point(self, point: Vector2) -> bool:
        """Check if a point is within this node's bounds."""
        x, y, w, h = self.bounds
        return (x <= point.x < x + w and y <= point.y < y + h)
    
    def _intersects(self, other_bounds: Tuple[float, float, float, float]) -> bool:
        """Check if this node intersects with another bounds."""
        x1, y1, w1, h1 = self.bounds
        x2, y2, w2, h2 = other_bounds
        
        return not (x1 >= x2 + w2 or x2 >= x1 + w1 or y1 >= y2 + h2 or y2 >= y1 + h1)
    
    def _point_in_bounds(self, point: Vector2, bounds: Tuple[float, float, float, float]) -> bool:
        """Check if a point is within given bounds."""
        x, y, w, h = bounds
        return (x <= point.x <= x + w and y <= point.y <= y + h)
    
    def get_stats(self) -> dict:
        """Get statistics about the quadtree."""
        stats = {
            'objects_at_level': len(self.objects),
            'is_divided': self.is_divided,
            'depth': 0,
            'total_objects': len(self.objects),
            'total_nodes': 1
        }
        
        if self.is_divided:
            for child in self.children:
                child_stats = child.get_stats()
                stats['total_objects'] += child_stats['total_objects']
                stats['total_nodes'] += child_stats['total_nodes']
                stats['depth'] = max(stats['depth'], child_stats['depth'] + 1)
        
        return stats


class AdvancedQuadTree:
    """
    Advanced quadtree implementation with performance optimizations.
    """
    
    def __init__(self, bounds: Tuple[float, float, float, float], max_objects: int = 10, max_depth: int = 8):
        self.root = QuadTreeNode(bounds, max_objects, max_depth)
        self.object_positions = {}  # Track object positions for updates
        self.total_objects = 0
        
        # Performance tracking
        self.query_count = 0
        self.query_time = 0.0
        self.last_rebuild_time = 0.0
        
        # Auto-optimization
        self.auto_optimize = True
        self.optimization_interval = 5.0  # seconds
        self.last_optimization = time.time()
        
    def insert(self, obj, position: Vector2, size: Vector2 = None) -> bool:
        """Insert an object with tracking."""
        success = self.root.insert(obj, position, size)
        if success:
            self.object_positions[obj] = position
            self.total_objects += 1
        return success
    
    def update_object(self, obj, new_position: Vector2, size: Vector2 = None) -> bool:
        """Update an object's position in the quadtree."""
        if obj in self.object_positions:
            old_position = self.object_positions[obj]
            
            # Remove from old position
            self.root.remove(obj, old_position)
            
            # Insert at new position
            success = self.root.insert(obj, new_position, size)
            if success:
                self.object_positions[obj] = new_position
            return success
        else:
            # New object
            return self.insert(obj, new_position, size)
    
    def remove(self, obj) -> bool:
        """Remove an object from tracking."""
        if obj in self.object_positions:
            position = self.object_positions[obj]
            success = self.root.remove(obj, position)
            if success:
                del self.object_positions[obj]
                self.total_objects -= 1
            return success
        return False
    
    def query_range(self, bounds: Tuple[float, float, float, float]) -> List:
        """Query with performance tracking."""
        start_time = time.perf_counter()
        
        result = self.root.query_range(bounds)
        
        self.query_time += time.perf_counter() - start_time
        self.query_count += 1
        
        return result
    
    def query_radius(self, center: Vector2, radius: float) -> List:
        """Query circular area with performance tracking."""
        start_time = time.perf_counter()
        
        result = self.root.query_radius(center, radius)
        
        self.query_time += time.perf_counter() - start_time
        self.query_count += 1
        
        return result
    
    def query_nearest(self, position: Vector2, max_count: int = 1, max_radius: float = float('inf')) -> List:
        """Find nearest objects to a position."""
        # Start with a small radius and expand if needed
        search_radius = 100.0
        found_objects = []
        
        while len(found_objects) < max_count and search_radius <= max_radius:
            candidates = self.query_radius(position, search_radius)
            
            # Calculate distances and sort
            with_distances = []
            for obj in candidates:
                obj_pos = getattr(obj, 'position', position)
                if hasattr(obj, 'transform'):
                    obj_pos = obj.transform.position
                
                distance = (obj_pos - position).magnitude()
                if distance <= max_radius:
                    with_distances.append((obj, distance))
            
            # Sort by distance and take the closest
            with_distances.sort(key=lambda x: x[1])
            found_objects = [obj for obj, dist in with_distances[:max_count]]
            
            if len(found_objects) < max_count:
                search_radius *= 2  # Expand search
            else:
                break
        
        return found_objects
    
    def rebuild(self):
        """Rebuild the quadtree for optimization."""
        start_time = time.perf_counter()
        
        # Store all objects
        all_objects = list(self.object_positions.items())
        
        # Clear the tree
        self.root.clear()
        self.object_positions.clear()
        self.total_objects = 0
        
        # Re-insert all objects
        for obj, position in all_objects:
            self.insert(obj, position)
        
        self.last_rebuild_time = time.perf_counter() - start_time
        print(f"Quadtree rebuilt in {self.last_rebuild_time:.3f}s")
    
    def update(self, delta_time: float):
        """Update the quadtree (auto-optimization)."""
        if self.auto_optimize:
            current_time = time.time()
            if current_time - self.last_optimization > self.optimization_interval:
                self._auto_optimize()
                self.last_optimization = current_time
    
    def _auto_optimize(self):
        """Automatic optimization based on performance metrics."""
        stats = self.get_performance_stats()
        
        # Rebuild if average query time is too high
        avg_query_time = stats.get('avg_query_time_ms', 0)
        if avg_query_time > 5.0:  # 5ms threshold
            print(f"Auto-optimizing quadtree (avg query time: {avg_query_time:.2f}ms)")
            self.rebuild()
            
            # Reset performance counters
            self.query_count = 0
            self.query_time = 0.0
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics."""
        tree_stats = self.root.get_stats()
        
        avg_query_time = (self.query_time / max(1, self.query_count)) * 1000  # ms
        
        return {
            'total_objects': self.total_objects,
            'tree_depth': tree_stats['depth'],
            'tree_nodes': tree_stats['total_nodes'],
            'query_count': self.query_count,
            'avg_query_time_ms': avg_query_time,
            'last_rebuild_time_ms': self.last_rebuild_time * 1000,
            'objects_per_node': self.total_objects / max(1, tree_stats['total_nodes'])
        }
    
    def clear(self):
        """Clear the entire quadtree."""
        self.root.clear()
        self.object_positions.clear()
        self.total_objects = 0
    
    def debug_draw(self, renderer):
        """Draw quadtree structure for debugging."""
        self._debug_draw_node(renderer, self.root)
    
    def _debug_draw_node(self, renderer, node):
        """Recursively draw quadtree nodes."""
        x, y, w, h = node.bounds
        
        # Draw node boundary
        color = (0, 255, 0) if len(node.objects) > 0 else (100, 100, 100)
        renderer.draw_rect(Vector2(x, y), Vector2(w, h), color, filled=False)
        
        # Draw children
        if node.is_divided:
            for child in node.children:
                self._debug_draw_node(renderer, child)
