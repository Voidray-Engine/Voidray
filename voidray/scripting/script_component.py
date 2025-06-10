
"""
VoidRay Script Component
Allows attaching Python scripts to game objects.
"""

from ..core.component import Component
from .script_manager import script_manager
from typing import Any, Optional


class ScriptComponent(Component):
    """
    Component that allows attaching Python scripts to game objects.
    """
    
    def __init__(self, script_name: str, class_name: str = None, **script_args):
        """
        Initialize script component.
        
        Args:
            script_name: Name of the script file (without .py)
            class_name: Name of the class in the script (optional)
            **script_args: Arguments to pass to the script class constructor
        """
        super().__init__()
        self.script_name = script_name
        self.class_name = class_name
        self.script_args = script_args
        self.script_instance: Optional[Any] = None
        self.initialized = False
    
    def start(self):
        """Initialize the script when component starts."""
        if not self.initialized:
            self.script_instance = script_manager.create_script_instance(
                self.script_name, 
                self.class_name, 
                **self.script_args
            )
            
            if self.script_instance:
                # Link the script instance to the game object
                if hasattr(self.script_instance, 'game_object'):
                    self.script_instance.game_object = self.game_object
                
                # Call start method if it exists
                if hasattr(self.script_instance, 'start'):
                    self.script_instance.start()
                
                self.initialized = True
                print(f"Script component initialized: {self.script_name}")
            else:
                print(f"Failed to initialize script component: {self.script_name}")
    
    def update(self, delta_time: float):
        """Update the script instance."""
        if self.script_instance and hasattr(self.script_instance, 'update'):
            try:
                self.script_instance.update(delta_time)
            except Exception as e:
                print(f"Error in script update ({self.script_name}): {e}")
    
    def call_method(self, method_name: str, *args, **kwargs) -> Any:
        """
        Call a method on the script instance.
        
        Args:
            method_name: Name of the method to call
            *args, **kwargs: Arguments to pass to the method
            
        Returns:
            Return value of the method or None if failed
        """
        if self.script_instance and hasattr(self.script_instance, method_name):
            try:
                method = getattr(self.script_instance, method_name)
                return method(*args, **kwargs)
            except Exception as e:
                print(f"Error calling script method {method_name}: {e}")
        return None
    
    def set_variable(self, var_name: str, value: Any):
        """Set a variable on the script instance."""
        if self.script_instance:
            setattr(self.script_instance, var_name, value)
    
    def get_variable(self, var_name: str) -> Any:
        """Get a variable from the script instance."""
        if self.script_instance and hasattr(self.script_instance, var_name):
            return getattr(self.script_instance, var_name)
        return None
    
    def reload_script(self):
        """Reload the script and recreate the instance."""
        if script_manager.reload_script(self.script_name):
            # Recreate the instance
            old_instance = self.script_instance
            self.script_instance = script_manager.create_script_instance(
                self.script_name, 
                self.class_name, 
                **self.script_args
            )
            
            if self.script_instance:
                # Try to preserve state from old instance
                if old_instance and hasattr(old_instance, '__dict__'):
                    for key, value in old_instance.__dict__.items():
                        if not key.startswith('_') and hasattr(self.script_instance, key):
                            setattr(self.script_instance, key, value)
                
                # Re-link to game object
                if hasattr(self.script_instance, 'game_object'):
                    self.script_instance.game_object = self.game_object
                
                print(f"Script component reloaded: {self.script_name}")
            else:
                print(f"Failed to reload script component: {self.script_name}")
    
    def cleanup(self):
        """Clean up the script component."""
        if self.script_instance and hasattr(self.script_instance, 'cleanup'):
            self.script_instance.cleanup()
        
        self.script_instance = None
        self.initialized = False
