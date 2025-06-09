
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
