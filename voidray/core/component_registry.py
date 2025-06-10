"""
VoidRay Component Registry
Registry for all engine components with automatic discovery.
"""

from typing import Dict, List, Type, Any
import inspect
from .component import Component


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
        if not issubclass(component_class, Component):
            raise ValueError(f"Component {component_class.__name__} must inherit from Component")

        name = component_class.__name__
        self._components[name] = component_class

        if category in self._component_categories:
            if name not in self._component_categories[category]:
                self._component_categories[category].append(name)
        else:
            self._component_categories[category] = [name]

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
        Automatically discover components in the given modules.

        Args:
            modules: List of modules to search for components
        """
        for module in modules:
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Component) and 
                    obj != Component):

                    # Determine category based on module name
                    module_name = module.__name__.lower()
                    if 'physics' in module_name:
                        category = 'physics'
                    elif 'graphics' in module_name or 'rendering' in module_name:
                        category = 'graphics'
                    elif 'audio' in module_name:
                        category = 'audio'
                    elif 'input' in module_name:
                        category = 'input'
                    else:
                        category = 'gameplay'

                    self.register_component(obj, category)

    def create_component(self, name: str) -> Component:
        """
        Create an instance of a component by name.

        Args:
            name: Name of the component to create

        Returns:
            Component instance or None if not found
        """
        component_class = self.get_component(name)
        if component_class:
            return component_class()
        return None

    def get_categories(self) -> List[str]:
        """Get all component categories."""
        return list(self._component_categories.keys())


# Global component registry instance
component_registry = ComponentRegistry()