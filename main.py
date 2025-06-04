"""
VoidRay Game Engine - Main Entry Point
======================================

This is the main entry point for the VoidRay game engine demonstration.
It provides a simple menu to run different example games and showcases
the capabilities of the engine.
"""

import sys
import os

# Add the voidray package to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voidray import Engine, Scene, Vector2, Keys
from voidray.graphics.renderer import Color
import subprocess


class MenuScene(Scene):
    """
    A simple menu scene that allows users to select different example games.
    """
    
    def __init__(self):
        super().__init__("MainMenu")
        self.selected_option = 0
        self.options = [
            ("Basic Game", "examples/basic_game.py", "Simple movement and collision example"),
            ("Platformer Demo", "examples/platformer_demo.py", "Physics-based platformer with jumping"),
            ("Space Shooter", "examples/space_shooter.py", "Advanced shooter with enemies and power-ups"),
            ("Quit", None, "Exit the VoidRay engine demo")
        ]
    
    def on_enter(self):
        super().on_enter()
        print("VoidRay Game Engine Demo")
        print("========================")
        print("Use UP/DOWN arrows to navigate, ENTER to select")
        print()
        self.display_menu()
    
    def display_menu(self):
        """Display the current menu options in console."""
        print("\nAvailable Examples:")
        for i, (name, script, description) in enumerate(self.options):
            marker = ">" if i == self.selected_option else " "
            print(f"{marker} {i+1}. {name}")
            print(f"    {description}")
        print()
    
    def update(self, delta_time):
        super().update(delta_time)
        
        input_manager = self.engine.input_manager
        
        # Navigate menu
        if input_manager.is_key_just_pressed(Keys.UP):
            self.selected_option = (self.selected_option - 1) % len(self.options)
            self.display_menu()
        
        if input_manager.is_key_just_pressed(Keys.DOWN):
            self.selected_option = (self.selected_option + 1) % len(self.options)
            self.display_menu()
        
        # Select option
        if input_manager.is_key_just_pressed(Keys.ENTER):
            self.select_option()
        
        # Direct number keys
        for i in range(len(self.options)):
            key = getattr(Keys, f'NUM_{i+1}', None)
            if key and input_manager.is_key_just_pressed(key):
                self.selected_option = i
                self.select_option()
                break
        
        # Quick quit
        if input_manager.is_key_just_pressed(Keys.ESCAPE):
            self.engine.stop()
    
    def select_option(self):
        """Execute the selected menu option."""
        name, script, description = self.options[self.selected_option]
        
        if script is None:  # Quit option
            print("Thank you for trying VoidRay!")
            self.engine.stop()
        else:
            print(f"\nLaunching {name}...")
            print(f"Description: {description}")
            print("Close the game window to return to this menu.\n")
            
            try:
                # Launch the selected example in a new process
                result = subprocess.run([sys.executable, script], 
                                      cwd=os.path.dirname(os.path.abspath(__file__)))
                
                if result.returncode != 0:
                    print(f"Example exited with code {result.returncode}")
                else:
                    print(f"{name} finished successfully.")
                
            except FileNotFoundError:
                print(f"Error: Could not find {script}")
                print("Make sure you're running this from the VoidRay root directory.")
            except Exception as e:
                print(f"Error launching {name}: {e}")
            
            print("\nReturning to menu...")
            self.display_menu()
    
    def render(self, renderer):
        super().render(renderer)
        
        # Draw title
        title_text = "VoidRay Game Engine"
        title_size = renderer.get_text_size(title_text, 32)
        title_pos = Vector2((self.engine.width - title_size[0]) / 2, 50)
        renderer.draw_text(title_text, title_pos, Color.WHITE, 32)
        
        # Draw subtitle
        subtitle_text = "Select an example to run:"
        subtitle_size = renderer.get_text_size(subtitle_text, 20)
        subtitle_pos = Vector2((self.engine.width - subtitle_size[0]) / 2, 100)
        renderer.draw_text(subtitle_text, subtitle_pos, Color.LIGHT_GRAY, 20)
        
        # Draw menu options
        start_y = 180
        for i, (name, script, description) in enumerate(self.options):
            y_pos = start_y + i * 80
            
            # Highlight selected option
            if i == self.selected_option:
                # Draw selection background
                renderer.draw_rect(Vector2(50, y_pos - 5), Vector2(self.engine.width - 100, 70), 
                                 Color.DARK_GRAY, True)
            
            # Draw option number and name
            option_text = f"{i+1}. {name}"
            renderer.draw_text(option_text, Vector2(70, y_pos), 
                             Color.CYAN if i == self.selected_option else Color.WHITE, 24)
            
            # Draw description
            renderer.draw_text(description, Vector2(90, y_pos + 30), 
                             Color.LIGHT_GRAY, 16)
        
        # Draw controls
        controls_y = self.engine.height - 80
        renderer.draw_text("Controls:", Vector2(20, controls_y), Color.WHITE, 18)
        renderer.draw_text("UP/DOWN: Navigate  |  ENTER: Select  |  1-4: Direct select  |  ESC: Quit", 
                          Vector2(20, controls_y + 25), Color.LIGHT_GRAY, 14)
        
        # Draw engine info
        info_text = f"VoidRay v1.0.0 - Built with Python and Pygame"
        info_size = renderer.get_text_size(info_text, 12)
        info_pos = Vector2(self.engine.width - info_size[0] - 20, self.engine.height - 30)
        renderer.draw_text(info_text, info_pos, Color.GRAY, 12)


def print_welcome():
    """Print welcome message and basic information."""
    print("=" * 60)
    print("VoidRay 2D Game Engine - Demo Launcher")
    print("=" * 60)
    print()
    print("Welcome to VoidRay! This demo launcher will help you explore")
    print("the capabilities of the VoidRay game engine through interactive")
    print("examples.")
    print()
    print("What is VoidRay?")
    print("- A lightweight 2D game engine built with Python and Pygame")
    print("- Perfect for learning game development or rapid prototyping")
    print("- Features physics, audio, input handling, and more")
    print("- No external editor required - everything is code-driven")
    print()
    print("Getting Started:")
    print("1. Use this demo to explore the example games")
    print("2. Read the documentation in the documentation/ folder")
    print("3. Study the example source code in the examples/ folder")
    print("4. Create your own games using VoidRay!")
    print()
    print("System Requirements:")
    print("- Python 3.8+ with Pygame installed")
    print("- Any modern computer with basic graphics support")
    print()


def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import pygame
        return True
    except ImportError:
        print("Error: Pygame is not installed!")
        print("Please install it with: pip install pygame")
        return False


def check_examples():
    """Check if example files exist."""
    examples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")
    
    if not os.path.exists(examples_dir):
        print("Warning: examples/ directory not found!")
        return False
    
    required_examples = ["basic_game.py", "platformer_demo.py", "space_shooter.py"]
    missing_examples = []
    
    for example in required_examples:
        example_path = os.path.join(examples_dir, example)
        if not os.path.exists(example_path):
            missing_examples.append(example)
    
    if missing_examples:
        print(f"Warning: Missing example files: {', '.join(missing_examples)}")
        return False
    
    return True


def main():
    """Main entry point for the VoidRay demo."""
    print_welcome()
    
    # Check dependencies
    if not check_dependencies():
        print("Please install the required dependencies and try again.")
        sys.exit(1)
    
    # Check examples
    if not check_examples():
        print("Some example files are missing. The demo may not work correctly.")
        response = input("Continue anyway? (y/n): ").lower().strip()
        if response != 'y' and response != 'yes':
            sys.exit(1)
    
    print("Dependencies OK. Starting VoidRay demo launcher...")
    print()
    
    try:
        # Create and run the demo engine
        engine = Engine(800, 600, "VoidRay Game Engine - Demo Launcher", 60)
        menu_scene = MenuScene()
        engine.set_scene(menu_scene)
        engine.run()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"Error running demo: {e}")
        print("Please check your installation and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
