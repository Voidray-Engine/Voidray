
"""
VoidRay Component Registry
Automatic component discovery and registration system.
"""

from typing import Dict, Type, List, Any
import inspect


class ComponentRegistry:
    """
    Registry for all engine components with automatic discovery.
    """
    
    def __init__(self):
        self._components: Dict[str, Type] = {}
        self._component_categories: Dict[str, List[str]] = {
            "physics": [],
            "graphics": [],
            "audio": [],
            "input": [],
            "gameplay": []
        }
    
    def register_component(self, component_class: Type, category: str = "gameplay"):
        """
        Register a component class.
        
        Args:
            component_class: The component class to register
            category: Category for organization
        """
        name = component_class.__name__
        self._components[name] = component_class
        
        if category in self._component_categories:
            if name not in self._component_categories[category]:
                self._component_categories[category].append(name)
        
        print(f"Registered component: {name} in category '{category}'")
    
    def get_component(self, name: str) -> Type:
        """Get a component class by name."""
        return self._components.get(name)
    
    def list_components(self, category: str = None) -> List[str]:
        """List all components or components in a category."""
        if category:
            return self._component_categories.get(category, [])
        return list(self._components.keys())
    
    def auto_discover(self, modules: List[Any]):
        """
        Automatically discover and register components from modules.
        
        Args:
            modules: List of modules to scan for components
        """
        for module in modules:
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, '_is_component') and obj._is_component:
                    category = getattr(obj, '_component_category', 'gameplay')
                    self.register_component(obj, category)
    
    def create_component(self, name: str, *args, **kwargs):
        """Create an instance of a component by name."""
        component_class = self.get_component(name)
        if component_class:
            return component_class(*args, **kwargs)
        raise ValueError(f"Component '{name}' not found in registry")


# Global component registry
component_registry = ComponentRegistry()


def register_component(category: str = "gameplay"):
    """Decorator for automatic component registration."""
    def decorator(cls):
        cls._is_component = True
        cls._component_category = category
        component_registry.register_component(cls, category)
        return cls
    return decorator
"""
VoidRay Component Registry
Manages component registration and creation for the engine.
"""

from typing import Dict, Type, Optional, Any, List
from .component import Component


class ComponentRegistry:
    """
    Registry for managing component types and creation.
    """
    
    def __init__(self):
        """Initialize the component registry."""
        self._components: Dict[str, Type[Component]] = {}
        self._component_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_component(self, component_class: Type[Component], 
                          name: Optional[str] = None, 
                          metadata: Optional[Dict[str, Any]] = None):
        """
        Register a component class.
        
        Args:
            component_class: Component class to register
            name: Optional custom name (defaults to class name)
            metadata: Optional metadata for the component
        """
        component_name = name or component_class.__name__
        
        self._components[component_name] = component_class
        self._component_metadata[component_name] = metadata or {}
        
        print(f"Registered component: {component_name}")
    
    def create_component(self, name: str, **kwargs) -> Optional[Component]:
        """
        Create a component instance by name.
        
        Args:
            name: Component name
            **kwargs: Arguments to pass to component constructor
            
        Returns:
            Component instance or None if not found
        """
        if name in self._components:
            component_class = self._components[name]
            return component_class(**kwargs)
        
        print(f"Component '{name}' not found in registry")
        return None
    
    def get_component_class(self, name: str) -> Optional[Type[Component]]:
        """
        Get a component class by name.
        
        Args:
            name: Component name
            
        Returns:
            Component class or None if not found
        """
        return self._components.get(name)
    
    def get_registered_components(self) -> List[str]:
        """
        Get list of all registered component names.
        
        Returns:
            List of component names
        """
        return list(self._components.keys())
    
    def get_component_metadata(self, name: str) -> Dict[str, Any]:
        """
        Get metadata for a component.
        
        Args:
            name: Component name
            
        Returns:
            Component metadata dictionary
        """
        return self._component_metadata.get(name, {})
    
    def unregister_component(self, name: str):
        """
        Unregister a component.
        
        Args:
            name: Component name to unregister
        """
        if name in self._components:
            del self._components[name]
            if name in self._component_metadata:
                del self._component_metadata[name]
            print(f"Unregistered component: {name}")


# Global component registry instance
component_registry = ComponentRegistry()


def register_component(component_class: Type[Component], 
                      name: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None):
    """
    Convenience function to register a component.
    
    Args:
        component_class: Component class to register
        name: Optional custom name
        metadata: Optional metadata
    """
    component_registry.register_component(component_class, name, metadata)


def create_component(name: str, **kwargs) -> Optional[Component]:
    """
    Convenience function to create a component.
    
    Args:
        name: Component name
        **kwargs: Constructor arguments
        
    Returns:
        Component instance or None
    """
    return component_registry.create_component(name, **kwargs)
