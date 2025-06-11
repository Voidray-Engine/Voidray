
"""
VoidRay Script Manager
Handles loading, execution, and hot-reloading of Python scripts.
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import traceback
import threading
import time
import math


class ScriptManager:
    """
    Manages Python scripts for dynamic game behavior and modding support.
    """
    
    def __init__(self, scripts_path: str = "scripts"):
        """
        Initialize the script manager.
        
        Args:
            scripts_path: Directory containing game scripts
        """
        self.scripts_path = scripts_path
        self.loaded_scripts: Dict[str, Any] = {}
        self.script_instances: Dict[str, Any] = {}
        self.script_watchers: Dict[str, float] = {}  # filename -> last_modified
        self.hot_reload_enabled = True
        self.sandbox_enabled = True
        
        # Ensure scripts directory exists
        os.makedirs(scripts_path, exist_ok=True)
        
        # Add scripts path to Python path
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        
        print(f"Script manager initialized with path: {scripts_path}")
    
    def load_script(self, script_name: str, hot_reload: bool = True) -> Optional[Any]:
        """
        Load a Python script by name.
        
        Args:
            script_name: Name of the script file (without .py extension)
            hot_reload: Whether to enable hot reloading for this script
            
        Returns:
            The loaded script module or None if failed
        """
        script_file = f"{script_name}.py"
        script_path = os.path.join(self.scripts_path, script_file)
        
        if not os.path.exists(script_path):
            print(f"Script not found: {script_path}")
            return None
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                
                # Execute in sandboxed environment if enabled
                if self.sandbox_enabled:
                    self._setup_sandbox(module)
                
                spec.loader.exec_module(module)
                
                # Store the loaded script
                self.loaded_scripts[script_name] = module
                
                # Set up hot reloading
                if hot_reload and self.hot_reload_enabled:
                    self.script_watchers[script_path] = os.path.getmtime(script_path)
                
                print(f"Loaded script: {script_name}")
                return module
            
        except Exception as e:
            print(f"Error loading script {script_name}: {e}")
            traceback.print_exc()
        
        return None
    
    def _setup_sandbox(self, module: Any):
        """Set up a sandboxed environment for script execution."""
        # Add safe builtins and game API
        safe_builtins = {
            'print': print,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
        }
        
        # Add VoidRay engine access
        try:
            import voidray
            safe_builtins['voidray'] = voidray
        except ImportError:
            pass
        
        # Restrict dangerous functions
        module.__builtins__ = safe_builtins
    
    def create_script_instance(self, script_name: str, class_name: str = None, *args, **kwargs) -> Optional[Any]:
        """
        Create an instance of a class from a loaded script.
        
        Args:
            script_name: Name of the script
            class_name: Name of the class to instantiate (defaults to script_name)
            *args, **kwargs: Arguments to pass to the class constructor
            
        Returns:
            Instance of the class or None if failed
        """
        if script_name not in self.loaded_scripts:
            self.load_script(script_name)
        
        if script_name not in self.loaded_scripts:
            return None
        
        module = self.loaded_scripts[script_name]
        
        # Default class name to script name (capitalized)
        if class_name is None:
            class_name = script_name.capitalize()
        
        try:
            if hasattr(module, class_name):
                script_class = getattr(module, class_name)
                instance = script_class(*args, **kwargs)
                
                # Store instance for management
                instance_key = f"{script_name}_{class_name}"
                self.script_instances[instance_key] = instance
                
                print(f"Created script instance: {instance_key}")
                return instance
            else:
                print(f"Class {class_name} not found in script {script_name}")
        
        except Exception as e:
            print(f"Error creating script instance: {e}")
            traceback.print_exc()
        
        return None
    
    def call_script_function(self, script_name: str, function_name: str, *args, **kwargs) -> Any:
        """
        Call a function from a loaded script.
        
        Args:
            script_name: Name of the script
            function_name: Name of the function to call
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Return value of the function or None if failed
        """
        if script_name not in self.loaded_scripts:
            self.load_script(script_name)
        
        if script_name not in self.loaded_scripts:
            return None
        
        module = self.loaded_scripts[script_name]
        
        try:
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                return func(*args, **kwargs)
            else:
                print(f"Function {function_name} not found in script {script_name}")
        
        except Exception as e:
            print(f"Error calling script function: {e}")
            traceback.print_exc()
        
        return None
    
    def reload_script(self, script_name: str) -> bool:
        """
        Reload a script and update all instances.
        
        Args:
            script_name: Name of the script to reload
            
        Returns:
            True if reload was successful
        """
        if script_name in self.loaded_scripts:
            try:
                # Reload the module
                module = self.loaded_scripts[script_name]
                importlib.reload(module)
                
                print(f"Reloaded script: {script_name}")
                return True
                
            except Exception as e:
                print(f"Error reloading script {script_name}: {e}")
                traceback.print_exc()
        
        return False
    
    def check_for_changes(self):
        """Check for script file changes and hot reload if necessary."""
        if not self.hot_reload_enabled:
            return
        
        for script_path, last_modified in list(self.script_watchers.items()):
            try:
                current_modified = os.path.getmtime(script_path)
                if current_modified > last_modified:
                    # File has been modified
                    script_name = Path(script_path).stem
                    print(f"Script changed, reloading: {script_name}")
                    
                    if self.reload_script(script_name):
                        self.script_watchers[script_path] = current_modified
                    
            except OSError:
                # File might have been deleted
                continue
    
    def update(self, delta_time: float):
        """Update script manager (call from main game loop)."""
        # Check for hot reload changes
        self.check_for_changes()
        
        # Update script instances that have an update method
        for instance_key, instance in list(self.script_instances.items()):
            if hasattr(instance, 'update'):
                try:
                    instance.update(delta_time)
                except Exception as e:
                    print(f"Error updating script instance {instance_key}: {e}")
    
    def create_sample_script(self, script_name: str) -> str:
        """Create a sample script file for reference."""
        sample_content = f'''"""
Sample VoidRay Script: {script_name}
This demonstrates how to create game scripts.
"""

import voidray
from voidray import GameObject, Vector2


class {script_name.capitalize()}(GameObject):
    """Sample script class that can be attached to game objects."""
    
    def __init__(self, name="{script_name}"):
        super().__init__(name)
        self.speed = 100
        self.timer = 0
        print(f"{{self.__class__.__name__}} initialized")
    
    def update(self, delta_time):
        """Called every frame by the script manager."""
        super().update(delta_time)
        
        self.timer += delta_time
        
        # Example: Move in a circle
        radius = 50
        self.transform.position.x = 400 + radius * math.cos(self.timer)
        self.transform.position.y = 300 + radius * math.sin(self.timer)
    
    def on_collision(self, other):
        """Called when this object collides with another."""
        print(f"{{self.name}} collided with {{other.name}}")
    
    def custom_behavior(self, message):
        """Custom function that can be called from the game."""
        print(f"{{self.name}} received message: {{message}}")
        return f"Response from {{self.name}}"


def sample_function():
    """Sample standalone function."""
    print("Sample function called from script!")
    return "Hello from {script_name} script!"


# Script initialization (runs when script is loaded)
if __name__ != "__main__":
    print(f"{script_name} script loaded successfully")
'''
        
        script_path = os.path.join(self.scripts_path, f"{script_name}.py")
        
        try:
            with open(script_path, 'w') as f:
                f.write(sample_content)
            print(f"Created sample script: {script_path}")
            return script_path
        except Exception as e:
            print(f"Error creating sample script: {e}")
            return ""
    
    def list_scripts(self) -> list:
        """List all available scripts in the scripts directory."""
        scripts = []
        try:
            for file in os.listdir(self.scripts_path):
                if file.endswith('.py') and not file.startswith('__'):
                    scripts.append(file[:-3])  # Remove .py extension
        except OSError:
            pass
        return scripts
    
    def unload_script(self, script_name: str):
        """Unload a script and clean up its instances."""
        # Remove instances
        instances_to_remove = [key for key in self.script_instances.keys() 
                             if key.startswith(f"{script_name}_")]
        for key in instances_to_remove:
            del self.script_instances[key]
        
        # Remove from loaded scripts
        if script_name in self.loaded_scripts:
            del self.loaded_scripts[script_name]
        
        # Remove from watchers
        script_path = os.path.join(self.scripts_path, f"{script_name}.py")
        if script_path in self.script_watchers:
            del self.script_watchers[script_path]
        
        print(f"Unloaded script: {script_name}")
    
    def cleanup(self):
        """Clean up all scripts and instances."""
        self.script_instances.clear()
        self.loaded_scripts.clear()
        self.script_watchers.clear()
        print("Script manager cleaned up")


# Global script manager instance
script_manager = ScriptManager()
