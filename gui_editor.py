
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import sys
import os
from io import StringIO
import contextlib

class VoidRayGUIEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VoidRay Game Engine - GUI Editor")
        self.root.geometry("1200x800")
        
        # Variables
        self.current_file = None
        self.preview_process = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Menu Bar
        self.create_menu_bar()
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Code Editor (main area)
        self.create_code_editor(main_frame)
        
        # Console at bottom
        self.create_console(main_frame)
        
        # Load default template
        self.load_default_template()
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Build Menu
        build_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Build", menu=build_menu)
        build_menu.add_command(label="Build to .py", command=self.build_to_py)
        build_menu.add_command(label="Run Game", command=self.run_game)
        build_menu.add_command(label="Stop Game", command=self.stop_game)
        
        # Examples Menu
        examples_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Examples", menu=examples_menu)
        examples_menu.add_command(label="Basic Game", command=lambda: self.load_example("basic_game.py"))
        examples_menu.add_command(label="Physics Demo", command=lambda: self.load_example("main.py"))
        examples_menu.add_command(label="Pong Game", command=lambda: self.load_example("pong_game.py"))
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_code_editor(self, parent):
        # Code Editor Frame
        editor_frame = ttk.LabelFrame(parent, text="Code Editor", padding=5)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        toolbar = ttk.Frame(editor_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Run", command=self.run_game).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Stop", command=self.stop_game).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Build", command=self.build_to_py).pack(side=tk.LEFT, padx=(0, 5))
        
        # Code text area with line numbers
        text_frame = ttk.Frame(editor_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(text_frame, width=4, padx=3, takefocus=0,
                                  border=0, state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Code editor
        self.code_editor = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, 
                                                   font=('Consolas', 11))
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events for line numbers
        self.code_editor.bind('<KeyRelease>', self.update_line_numbers)
        self.code_editor.bind('<Button-1>', self.update_line_numbers)
        self.code_editor.bind('<MouseWheel>', self.update_line_numbers)
        
    
        
    def create_console(self, parent):
        # Console Frame
        console_frame = ttk.LabelFrame(parent, text="Console", padding=5)
        console_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Console text area
        self.console = scrolledtext.ScrolledText(console_frame, height=8, 
                                               font=('Consolas', 9), bg='black', fg='white')
        self.console.pack(fill=tk.BOTH, expand=True)
        
        self.log_message("VoidRay GUI Editor initialized")
        self.log_message("Ready to create games!")
        
    def update_line_numbers(self, event=None):
        # Update line numbers
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        
        lines = self.code_editor.get('1.0', tk.END).count('\n')
        line_numbers_string = '\n'.join(str(i) for i in range(1, lines))
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        
    def log_message(self, message):
        self.console.insert(tk.END, f"{message}\n")
        self.console.see(tk.END)
        
    def new_project(self):
        if messagebox.askyesno("New Project", "Create a new project? Unsaved changes will be lost."):
            self.current_file = None
            self.load_default_template()
            self.log_message("New project created")
            
    def load_default_template(self):
        template = '''"""
VoidRay Game Template
Create your game here!
"""

import voidray
from voidray import Scene, GameObject, Sprite, Vector2, Keys
from voidray.graphics.renderer import Color


class Player(Sprite):
    """A simple player that can move around."""
    
    def __init__(self):
        super().__init__("Player")
        self.create_colored_rect(40, 40, Color.BLUE)
        self.speed = 300
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Get input
        input_manager = voidray.get_engine().input_manager
        
        # Move the player
        velocity = Vector2.zero()
        if input_manager.is_key_pressed(Keys.LEFT):
            velocity.x = -self.speed
        if input_manager.is_key_pressed(Keys.RIGHT):
            velocity.x = self.speed
        if input_manager.is_key_pressed(Keys.UP):
            velocity.y = -self.speed
        if input_manager.is_key_pressed(Keys.DOWN):
            velocity.y = self.speed
            
        self.transform.position += velocity * delta_time


class GameScene(Scene):
    """Main game scene."""
    
    def __init__(self):
        super().__init__("Game")
        
    def on_enter(self):
        super().on_enter()
        
        # Create player
        self.player = Player()
        self.player.transform.position = Vector2(400, 300)
        self.add_object(self.player)
        
        print("Game scene started - Use arrow keys to move!")
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check for exit
        input_manager = voidray.get_engine().input_manager
        if input_manager.is_key_just_pressed(Keys.ESCAPE):
            voidray.stop()


def init_game():
    """Initialize the game."""
    scene = GameScene()
    voidray.register_scene("game", scene)
    voidray.set_scene("game")


def main():
    """Main entry point."""
    voidray.configure(width=800, height=600, title="My VoidRay Game", fps=60)
    voidray.on_init(init_game)
    voidray.start()


if __name__ == "__main__":
    main()
'''
        self.code_editor.delete('1.0', tk.END)
        self.code_editor.insert('1.0', template)
        self.update_line_numbers()
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                self.code_editor.delete('1.0', tk.END)
                self.code_editor.insert('1.0', content)
                self.current_file = file_path
                self.update_line_numbers()
                self.log_message(f"Opened: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
                
    def save_file(self):
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as_file()
            
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            
    def save_to_file(self, file_path):
        try:
            content = self.code_editor.get('1.0', tk.END)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            self.log_message(f"Saved: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
            
    def build_to_py(self):
        """Build/save the current code as a .py file."""
        if not self.current_file or not self.current_file.endswith('.py'):
            # If no current file or not a .py file, prompt for save location
            file_path = filedialog.asksaveasfilename(
                title="Build to Python File",
                defaultextension=".py",
                filetypes=[("Python files", "*.py")]
            )
            
            if not file_path:
                return
                
            self.current_file = file_path
            
        # Save the current content
        self.save_to_file(self.current_file)
        self.log_message(f"Built to: {self.current_file}")
        messagebox.showinfo("Build Complete", f"Successfully built to:\n{self.current_file}")
        
    def run_game(self):
        """Run the current game code."""
        if self.preview_process:
            self.stop_game()
            
        # Save current code to a temporary file
        temp_file = "temp_game.py"
        try:
            content = self.code_editor.get('1.0', tk.END)
            with open(temp_file, 'w', encoding='utf-8') as file:
                file.write(content)
                
            # Run the game in a separate process
            def run_process():
                try:
                    self.preview_process = subprocess.Popen(
                        [sys.executable, temp_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    # Read output in real-time
                    while self.preview_process.poll() is None:
                        output = self.preview_process.stdout.readline()
                        if output:
                            self.root.after(0, lambda: self.log_message(f"Game: {output.strip()}"))
                            
                    # Get any remaining output
                    stdout, stderr = self.preview_process.communicate()
                    if stdout:
                        self.root.after(0, lambda: self.log_message(f"Game: {stdout}"))
                    if stderr:
                        self.root.after(0, lambda: self.log_message(f"Game Error: {stderr}"))
                        
                    self.root.after(0, lambda: self.log_message("Game process ended"))
                    self.root.after(0, lambda: setattr(self, 'preview_process', None))
                    
                except Exception as e:
                    self.root.after(0, lambda: self.log_message(f"Error running game: {str(e)}"))
                    
            threading.Thread(target=run_process, daemon=True).start()
            self.log_message("Starting game...")
            
        except Exception as e:
            self.log_message(f"Failed to run game: {str(e)}")
            
    def stop_game(self):
        """Stop the running game."""
        if self.preview_process:
            self.preview_process.terminate()
            self.preview_process = None
            self.log_message("Game stopped")
            
    
        
    def load_example(self, example_name):
        """Load an example file."""
        example_path = os.path.join("examples", example_name)
        if os.path.exists(example_path):
            try:
                with open(example_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                self.code_editor.delete('1.0', tk.END)
                self.code_editor.insert('1.0', content)
                self.current_file = None  # Don't set as current file
                self.update_line_numbers()
                self.log_message(f"Loaded example: {example_name}")
                
            except Exception as e:
                self.log_message(f"Failed to load example {example_name}: {str(e)}")
        else:
            self.log_message(f"Example not found: {example_path}")
            
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", 
                          "VoidRay Game Engine - GUI Editor\n\n"
                          "A visual editor for creating games with the VoidRay engine.\n\n"
                          "Features:\n"
                          "• Code editor with syntax highlighting\n"
                          "• Live game preview\n"
                          "• Console output\n"
                          "• Build to .py functionality\n"
                          "• Example templates")
        
    def run(self):
        """Start the GUI application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle application closing."""
        if self.preview_process:
            self.stop_game()
        self.root.destroy()


def main():
    """Main entry point for the GUI editor."""
    app = VoidRayGUIEditor()
    app.run()


if __name__ == "__main__":
    main()
