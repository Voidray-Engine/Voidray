
"""
VoidRay Node System
Advanced hierarchical node system inspired by Godot for flexible scene composition.
"""

from typing import List, Optional, Dict, Any, Type, TypeVar
from abc import ABC, abstractmethod
import uuid

T = TypeVar('T', bound='Node')


class NodeSignal:
    """Signal system for node communication."""
    
    def __init__(self, name: str):
        self.name = name
        self.connections: List = []
    
    def connect(self, callable_obj, *args):
        """Connect a function to this signal."""
        self.connections.append((callable_obj, args))
    
    def disconnect(self, callable_obj):
        """Disconnect a function from this signal."""
        self.connections = [(conn, args) for conn, args in self.connections if conn != callable_obj]
    
    def emit(self, *args):
        """Emit the signal to all connected functions."""
        for callable_obj, connect_args in self.connections:
            try:
                callable_obj(*(args + connect_args))
            except Exception as e:
                print(f"Error in signal {self.name}: {e}")


class Node:
    """
    Base node class - foundation of the scene tree.
    Every game object inherits from Node.
    """
    
    def __init__(self, name: str = "Node"):
        self.name = name
        self.unique_id = str(uuid.uuid4())
        
        # Hierarchy
        self.parent: Optional['Node'] = None
        self.children: List['Node'] = []
        
        # Node state
        self.active = True
        self.visible = True
        self.process_mode = "inherit"  # inherit, always, when_paused, disabled
        
        # Signals
        self.signals: Dict[str, NodeSignal] = {}
        self._setup_default_signals()
        
        # Groups
        self.groups: set = set()
        
        # Properties
        self.properties: Dict[str, Any] = {}
        
        # Transform (for nodes that need positioning)
        from ..math.transform import Transform
        self.transform = Transform()
    
    def _setup_default_signals(self):
        """Setup default signals for all nodes."""
        self.signals['ready'] = NodeSignal('ready')
        self.signals['tree_entered'] = NodeSignal('tree_entered')
        self.signals['tree_exiting'] = NodeSignal('tree_exiting')
    
    def add_child(self, child: 'Node', force_readable_name: bool = False):
        """Add a child node."""
        if child.parent:
            child.parent.remove_child(child)
        
        child.parent = self
        self.children.append(child)
        
        # Ensure unique names among siblings
        if force_readable_name:
            child.name = self._get_unique_child_name(child.name)
        
        child._enter_tree()
    
    def remove_child(self, child: 'Node'):
        """Remove a child node."""
        if child in self.children:
            child._exit_tree()
            child.parent = None
            self.children.remove(child)
    
    def get_child(self, index: int) -> Optional['Node']:
        """Get child by index."""
        if 0 <= index < len(self.children):
            return self.children[index]
        return None
    
    def get_child_count(self) -> int:
        """Get number of children."""
        return len(self.children)
    
    def find_child(self, name: str, recursive: bool = True) -> Optional['Node']:
        """Find child by name."""
        for child in self.children:
            if child.name == name:
                return child
            if recursive:
                result = child.find_child(name, True)
                if result:
                    return result
        return None
    
    def get_node(self, path: str) -> Optional['Node']:
        """Get node by path (e.g., 'Player/Weapon/Bullet')."""
        parts = path.split('/')
        current = self
        
        for part in parts:
            if part == '..':
                current = current.parent
                if not current:
                    return None
            else:
                current = current.find_child(part, False)
                if not current:
                    return None
        
        return current
    
    def get_parent(self) -> Optional['Node']:
        """Get parent node."""
        return self.parent
    
    def get_tree(self) -> Optional['SceneTree']:
        """Get the scene tree this node belongs to."""
        current = self
        while current.parent:
            current = current.parent
        
        if hasattr(current, '_scene_tree'):
            return current._scene_tree
        return None
    
    def is_in_tree(self) -> bool:
        """Check if node is in the scene tree."""
        return self.get_tree() is not None
    
    def add_to_group(self, group: str):
        """Add node to a group."""
        self.groups.add(group)
        tree = self.get_tree()
        if tree:
            tree.add_to_group(group, self)
    
    def remove_from_group(self, group: str):
        """Remove node from a group."""
        self.groups.discard(group)
        tree = self.get_tree()
        if tree:
            tree.remove_from_group(group, self)
    
    def is_in_group(self, group: str) -> bool:
        """Check if node is in a group."""
        return group in self.groups
    
    def queue_free(self):
        """Mark node for deletion at the end of frame."""
        tree = self.get_tree()
        if tree:
            tree.queue_delete(self)
    
    def duplicate(self) -> 'Node':
        """Create a duplicate of this node."""
        # Basic duplication - can be overridden by subclasses
        new_node = type(self)(self.name + "_duplicate")
        new_node.active = self.active
        new_node.visible = self.visible
        new_node.process_mode = self.process_mode
        new_node.properties = self.properties.copy()
        
        # Duplicate children
        for child in self.children:
            new_node.add_child(child.duplicate())
        
        return new_node
    
    def _get_unique_child_name(self, base_name: str) -> str:
        """Generate unique name among siblings."""
        existing_names = {child.name for child in self.children}
        if base_name not in existing_names:
            return base_name
        
        counter = 2
        while f"{base_name}{counter}" in existing_names:
            counter += 1
        
        return f"{base_name}{counter}"
    
    def _enter_tree(self):
        """Called when node enters the scene tree."""
        self.signals['tree_entered'].emit()
        self._ready()
        
        # Process children
        for child in self.children:
            child._enter_tree()
    
    def _exit_tree(self):
        """Called when node exits the scene tree."""
        self.signals['tree_exiting'].emit()
        
        # Process children
        for child in self.children:
            child._exit_tree()
    
    def _ready(self):
        """Called when node is ready (after entering tree)."""
        self.signals['ready'].emit()
        self.ready()
    
    # Virtual methods to be overridden
    def ready(self):
        """Called when the node is ready. Override in subclasses."""
        pass
    
    def process(self, delta: float):
        """Called every frame. Override in subclasses."""
        pass
    
    def physics_process(self, delta: float):
        """Called every physics frame. Override in subclasses."""
        pass
    
    def update(self, delta: float):
        """Update this node and all children."""
        if not self.active:
            return
        
        # Process this node
        if self.process_mode in ['inherit', 'always']:
            self.process(delta)
        
        # Process children
        for child in self.children[:]:  # Copy list to handle modifications
            child.update(delta)
    
    def render(self, renderer):
        """Render this node and all children."""
        if not self.active or not self.visible:
            return
        
        # Render this node
        self._render(renderer)
        
        # Render children
        for child in self.children:
            child.render(renderer)
    
    def _render(self, renderer):
        """Internal render method. Override in subclasses."""
        pass


class Node2D(Node):
    """2D node with transform capabilities."""
    
    def __init__(self, name: str = "Node2D"):
        super().__init__(name)
        self.z_index = 0
        self.z_as_relative = True
    
    def get_global_position(self):
        """Get global position in world space."""
        if self.parent and isinstance(self.parent, Node2D):
            return self.parent.get_global_position() + self.transform.position
        return self.transform.position
    
    def get_global_scale(self):
        """Get global scale."""
        if self.parent and isinstance(self.parent, Node2D):
            parent_scale = self.parent.get_global_scale()
            return Vector2(
                self.transform.scale.x * parent_scale.x,
                self.transform.scale.y * parent_scale.y
            )
        return self.transform.scale
    
    def get_global_rotation(self):
        """Get global rotation."""
        if self.parent and isinstance(self.parent, Node2D):
            return self.parent.get_global_rotation() + self.transform.rotation
        return self.transform.rotation


class SceneTree:
    """Manages the scene tree and node operations."""
    
    def __init__(self):
        self.root: Optional[Node] = None
        self.groups: Dict[str, set] = {}
        self.deletion_queue: List[Node] = []
        
    def set_root(self, root: Node):
        """Set the root node of the tree."""
        self.root = root
        root._scene_tree = self
        root._enter_tree()
    
    def add_to_group(self, group: str, node: Node):
        """Add node to a group."""
        if group not in self.groups:
            self.groups[group] = set()
        self.groups[group].add(node)
    
    def remove_from_group(self, group: str, node: Node):
        """Remove node from a group."""
        if group in self.groups:
            self.groups[group].discard(node)
    
    def get_nodes_in_group(self, group: str) -> List[Node]:
        """Get all nodes in a group."""
        return list(self.groups.get(group, set()))
    
    def queue_delete(self, node: Node):
        """Queue node for deletion."""
        if node not in self.deletion_queue:
            self.deletion_queue.append(node)
    
    def process_deletions(self):
        """Process queued deletions."""
        for node in self.deletion_queue:
            if node.parent:
                node.parent.remove_child(node)
        
        self.deletion_queue.clear()
    
    def update(self, delta: float):
        """Update the entire tree."""
        if self.root:
            self.root.update(delta)
        self.process_deletions()
    
    def render(self, renderer):
        """Render the entire tree."""
        if self.root:
            self.root.render(renderer)
