
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import sys
import os
import re
from io import StringIO
import contextlib

class SyntaxHighlighter:
    """Advanced syntax highlighter for Python and VoidRay API."""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.setup_tags()
        
    def setup_tags(self):
        """Setup color tags for different syntax elements."""
        # Python keywords
        self.text_widget.tag_config("python_keyword", foreground="#569cd6")  # Blue
        self.text_widget.tag_config("python_builtin", foreground="#4fc1ff")  # Light blue
        self.text_widget.tag_config("python_string", foreground="#ce9178")   # Orange
        self.text_widget.tag_config("python_comment", foreground="#6a9955")  # Green
        self.text_widget.tag_config("python_number", foreground="#b5cea8")   # Light green
        
        # VoidRay API specific
        self.text_widget.tag_config("voidray_api", foreground="#c586c0")     # Purple
        self.text_widget.tag_config("voidray_class", foreground="#4ec9b0")   # Cyan
        self.text_widget.tag_config("voidray_method", foreground="#dcdcaa")  # Yellow
        
        # General
        self.text_widget.tag_config("function_def", foreground="#dcdcaa")    # Yellow
        self.text_widget.tag_config("class_def", foreground="#4ec9b0")       # Cyan
        
    def highlight_syntax(self):
        """Apply syntax highlighting to the entire text."""
        content = self.text_widget.get("1.0", tk.END)
        
        # Clear existing tags
        for tag in ["python_keyword", "python_builtin", "python_string", "python_comment", 
                   "python_number", "voidray_api", "voidray_class", "voidray_method", 
                   "function_def", "class_def"]:
            self.text_widget.tag_remove(tag, "1.0", tk.END)
        
        # Python keywords
        python_keywords = r'\b(def|class|if|elif|else|for|while|try|except|finally|import|from|as|return|yield|lambda|with|assert|break|continue|pass|global|nonlocal|True|False|None|and|or|not|in|is)\b'
        self._highlight_pattern(python_keywords, "python_keyword")
        
        # Python builtins
        python_builtins = r'\b(print|len|range|enumerate|zip|open|input|int|float|str|list|dict|tuple|set|bool|type|isinstance|hasattr|getattr|setattr|super|__init__|__str__|__repr__)\b'
        self._highlight_pattern(python_builtins, "python_builtin")
        
        # VoidRay API classes
        voidray_classes = r'\b(Engine|Scene|GameObject|Sprite|Vector2|Color|InputManager|Keys|BoxCollider|CircleCollider|Rigidbody|Transform|Camera|PhysicsEngine|AudioManager|AssetLoader)\b'
        self._highlight_pattern(voidray_classes, "voidray_class")
        
        # VoidRay API functions and methods
        voidray_methods = r'\b(configure|start|stop|on_init|on_update|on_render|register_scene|set_scene|get_engine|create_colored_rect|create_colored_circle|add_component|get_component|set_velocity|add_impulse|is_key_pressed|is_key_just_pressed|draw_text|draw_rect|clear|present)\b'
        self._highlight_pattern(voidray_methods, "voidray_method")
        
        # VoidRay namespace
        voidray_api = r'\bvoidray\b'
        self._highlight_pattern(voidray_api, "voidray_api")
        
        # Strings
        string_patterns = [r'"[^"]*"', r"'[^']*'", r'""".*?"""', r"'''.*?'''"]
        for pattern in string_patterns:
            self._highlight_pattern(pattern, "python_string")
        
        # Comments
        self._highlight_pattern(r'#.*$', "python_comment")
        
        # Numbers
        self._highlight_pattern(r'\b\d+\.?\d*\b', "python_number")
        
        # Function definitions
        self._highlight_pattern(r'def\s+(\w+)', "function_def", group=1)
        
        # Class definitions
        self._highlight_pattern(r'class\s+(\w+)', "class_def", group=1)
    
    def _highlight_pattern(self, pattern, tag, group=0):
        """Helper method to highlight a regex pattern."""
        start = "1.0"
        while True:
            match = self.text_widget.search(pattern, start, tk.END, regexp=True)
            if not match:
                break
            
            if group > 0:
                # Highlight specific group
                match_obj = re.search(pattern, self.text_widget.get(match, f"{match} lineend"))
                if match_obj and len(match_obj.groups()) >= group:
                    group_start = match_obj.start(group)
                    group_end = match_obj.end(group)
                    start_idx = f"{match.split('.')[0]}.{int(match.split('.')[1]) + group_start}"
                    end_idx = f"{match.split('.')[0]}.{int(match.split('.')[1]) + group_end}"
                    self.text_widget.tag_add(tag, start_idx, end_idx)
            else:
                # Highlight entire match
                end_match = f"{match}+{len(self.text_widget.get(match, f'{match} wordend'))}c"
                self.text_widget.tag_add(tag, match, end_match)
            
            start = f"{match}+1c"

class ProgrammingAssistant:
    """Programming assistant with code completion and suggestions."""
    
    def __init__(self, editor):
        self.editor = editor
        self.suggestions_window = None
        
    def get_voidray_suggestions(self, current_word):
        """Get VoidRay API suggestions."""
        voidray_api = {
            'voidray': ['configure', 'start', 'stop', 'on_init', 'on_update', 'on_render', 
                       'register_scene', 'set_scene', 'get_engine'],
            'Engine': ['__init__', 'configure', 'start', 'stop', 'set_scene', 'get_fps'],
            'Scene': ['__init__', 'on_enter', 'on_exit', 'update', 'render', 'add_object'],
            'Sprite': ['__init__', 'create_colored_rect', 'create_colored_circle', 'update', 
                      'add_component', 'get_component'],
            'Vector2': ['__init__', 'x', 'y', 'zero', 'normalized', 'magnitude'],
            'Color': ['RED', 'GREEN', 'BLUE', 'YELLOW', 'WHITE', 'BLACK', 'CYAN', 'MAGENTA'],
            'Keys': ['LEFT', 'RIGHT', 'UP', 'DOWN', 'SPACE', 'ESCAPE', 'ENTER'],
            'InputManager': ['is_key_pressed', 'is_key_just_pressed', 'is_key_just_released'],
            'Rigidbody': ['set_velocity', 'add_impulse', 'set_mass', 'set_bounciness']
        }
        
        suggestions = []
        for category, items in voidray_api.items():
            if current_word.lower() in category.lower():
                suggestions.extend([f"{category}.{item}" for item in items])
            for item in items:
                if current_word.lower() in item.lower():
                    suggestions.append(f"{category}.{item}")
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    def show_suggestions(self, event=None):
        """Show code completion suggestions."""
        cursor_pos = self.editor.code_editor.index(tk.INSERT)
        line_text = self.editor.code_editor.get(f"{cursor_pos.split('.')[0]}.0", cursor_pos)
        
        # Get current word
        words = re.findall(r'\w+', line_text)
        current_word = words[-1] if words else ""
        
        if len(current_word) < 2:
            return
        
        suggestions = self.get_voidray_suggestions(current_word)
        
        if suggestions:
            self._display_suggestions(suggestions, cursor_pos)
    
    def _display_suggestions(self, suggestions, cursor_pos):
        """Display suggestions in a popup window."""
        if self.suggestions_window:
            self.suggestions_window.destroy()
        
        self.suggestions_window = tk.Toplevel(self.editor.root)
        self.suggestions_window.wm_overrideredirect(True)
        
        # Position near cursor
        x, y = self.editor.code_editor.winfo_rootx(), self.editor.code_editor.winfo_rooty()
        self.suggestions_window.geometry(f"+{x+50}+{y+50}")
        
        listbox = tk.Listbox(self.suggestions_window, height=min(10, len(suggestions)))
        listbox.pack()
        
        for suggestion in suggestions:
            listbox.insert(tk.END, suggestion)
        
        # Auto-hide after 5 seconds
        self.editor.root.after(5000, lambda: self.suggestions_window.destroy() if self.suggestions_window else None)

class VoidRayGUIEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VoidRay Game Engine - Advanced Code Editor")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')  # Dark theme
        
        # Variables
        self.current_file = None
        self.preview_process = None
        
        # Initialize components
        self.syntax_highlighter = None
        self.programming_assistant = None
        
        self.setup_ui()
        self.setup_dark_theme()
        
    def setup_dark_theme(self):
        """Setup dark theme for the editor."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure dark theme colors
        style.configure('TLabel', background='#1e1e1e', foreground='#ffffff')
        style.configure('TFrame', background='#1e1e1e')
        style.configure('TLabelFrame', background='#1e1e1e', foreground='#ffffff')
        style.configure('TButton', background='#3c3c3c', foreground='#ffffff')
        style.map('TButton', background=[('active', '#505050')])
        
    def setup_ui(self):        
        # Main container with paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for file explorer and help
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=1)
        
        # Right panel for editor and console
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=4)
        
        # Setup panels
        self.create_left_panel(left_panel)
        self.create_code_editor(right_panel)
        self.create_console(right_panel)
        
        # Load default template
        self.load_default_template()
        
        # Initialize syntax highlighter and assistant BEFORE menu creation
        self.syntax_highlighter = SyntaxHighlighter(self.code_editor)
        self.programming_assistant = ProgrammingAssistant(self)
        
        # Now create menu bar that references the assistant
        self.create_menu_bar()
        
        # Bind events for real-time highlighting
        self.code_editor.bind('<KeyRelease>', self.on_text_change)
        self.code_editor.bind('<Control-space>', self.programming_assistant.show_suggestions)
        
    def create_left_panel(self, parent):
        """Create left panel with help and API reference."""
        # API Reference
        api_frame = ttk.LabelFrame(parent, text="VoidRay API Reference", padding=5)
        api_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        api_tree = ttk.Treeview(api_frame, height=15)
        api_tree.pack(fill=tk.BOTH, expand=True)
        
        # Populate API tree
        self.populate_api_tree(api_tree)
        
        # Help panel
        help_frame = ttk.LabelFrame(parent, text="Quick Help", padding=5)
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        help_text = scrolledtext.ScrolledText(help_frame, height=10, width=30, 
                                            font=('Consolas', 9), bg='#2d2d30', fg='#ffffff',
                                            wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        help_content = """VoidRay Quick Reference:

🎮 BASIC SETUP:
import voidray
voidray.configure(800, 600, "Game")
voidray.start()

🎨 SPRITES:
sprite = Sprite("name")
sprite.create_colored_rect(40, 40, Color.BLUE)

⚡ PHYSICS:
rigidbody = Rigidbody()
collider = BoxCollider(40, 40)
sprite.add_component(rigidbody)

🎯 INPUT:
input_manager.is_key_pressed(Keys.LEFT)
input_manager.is_key_just_pressed(Keys.SPACE)

📦 SCENES:
scene = Scene("Game")
voidray.register_scene("game", scene)
voidray.set_scene("game")

💡 TIPS:
- Press Ctrl+Space for auto-completion
- F3 toggles debug overlay in game
- ESC typically exits game loops
- Use delta_time for smooth movement

🔧 COMMON PATTERNS:
# Movement
velocity = Vector2(speed, 0)
transform.position += velocity * delta_time

# Collision response
def on_collision(other, info):
    # Handle collision here
    pass

🎵 AUDIO:
audio_manager.play_music("music.mp3")
audio_manager.play_sound("effect.wav")
"""
        
        help_text.insert("1.0", help_content)
        help_text.config(state=tk.DISABLED)
        
    def populate_api_tree(self, tree):
        """Populate the API reference tree."""
        # Core Engine
        engine_node = tree.insert("", "end", text="🎮 Engine", open=True)
        tree.insert(engine_node, "end", text="configure(width, height, title, fps)")
        tree.insert(engine_node, "end", text="start()")
        tree.insert(engine_node, "end", text="stop()")
        tree.insert(engine_node, "end", text="get_engine()")
        
        # Scene Management
        scene_node = tree.insert("", "end", text="🎬 Scene", open=True)
        tree.insert(scene_node, "end", text="register_scene(name, scene)")
        tree.insert(scene_node, "end", text="set_scene(name)")
        tree.insert(scene_node, "end", text="on_enter()")
        tree.insert(scene_node, "end", text="on_exit()")
        
        # Sprites & Graphics
        sprite_node = tree.insert("", "end", text="🎨 Sprite", open=True)
        tree.insert(sprite_node, "end", text="create_colored_rect(w, h, color)")
        tree.insert(sprite_node, "end", text="create_colored_circle(radius, color)")
        tree.insert(sprite_node, "end", text="add_component(component)")
        tree.insert(sprite_node, "end", text="get_component(type)")
        
        # Physics
        physics_node = tree.insert("", "end", text="⚡ Physics", open=True)
        tree.insert(physics_node, "end", text="Rigidbody()")
        tree.insert(physics_node, "end", text="BoxCollider(width, height)")
        tree.insert(physics_node, "end", text="CircleCollider(radius)")
        tree.insert(physics_node, "end", text="set_velocity(vector)")
        tree.insert(physics_node, "end", text="add_impulse(force)")
        
        # Input
        input_node = tree.insert("", "end", text="🎯 Input", open=True)
        tree.insert(input_node, "end", text="is_key_pressed(key)")
        tree.insert(input_node, "end", text="is_key_just_pressed(key)")
        tree.insert(input_node, "end", text="Keys.LEFT, RIGHT, UP, DOWN")
        tree.insert(input_node, "end", text="Keys.SPACE, ESCAPE, ENTER")
        
        # Colors
        color_node = tree.insert("", "end", text="🌈 Colors", open=True)
        tree.insert(color_node, "end", text="Color.RED, GREEN, BLUE")
        tree.insert(color_node, "end", text="Color.YELLOW, WHITE, BLACK")
        tree.insert(color_node, "end", text="Color.CYAN, MAGENTA")
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root, bg='#3c3c3c', fg='white')
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find", command=self.show_find_dialog)
        edit_menu.add_command(label="Replace", command=self.show_replace_dialog)
        edit_menu.add_separator()
        edit_menu.add_command(label="Auto-Complete", command=self.show_auto_complete)
        
        # Build Menu
        build_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Build", menu=build_menu)
        build_menu.add_command(label="Build to .py", command=self.build_to_py)
        build_menu.add_command(label="Run Game", command=self.run_game)
        build_menu.add_command(label="Stop Game", command=self.stop_game)
        build_menu.add_separator()
        build_menu.add_command(label="Check Syntax", command=self.check_syntax)
        
        # Examples Menu
        examples_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Examples", menu=examples_menu)
        examples_menu.add_command(label="Basic Game", command=lambda: self.load_example("basic_game.py"))
        examples_menu.add_command(label="Physics Demo", command=lambda: self.load_example("main.py"))
        examples_menu.add_command(label="Pong Game", command=lambda: self.load_example("pong_game.py"))
        examples_menu.add_command(label="Asteroids", command=lambda: self.load_example("asteroids_demo.py"))
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="VoidRay Documentation", command=self.show_documentation)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_code_editor(self, parent):
        # Code Editor Frame
        editor_frame = ttk.LabelFrame(parent, text="Code Editor", padding=5)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        toolbar = ttk.Frame(editor_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="▶ Run", command=self.run_game).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="⏹ Stop", command=self.stop_game).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🔨 Build", command=self.build_to_py).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="✓ Check", command=self.check_syntax).pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(toolbar, text="Ready")
        self.status_label.pack(side=tk.RIGHT)
        
        # Code text area with line numbers
        text_frame = ttk.Frame(editor_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(text_frame, width=4, padx=3, takefocus=0,
                                  border=0, state='disabled', wrap='none',
                                  bg='#2d2d30', fg='#858585')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Code editor with dark theme
        self.code_editor = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, 
                                                   font=('Consolas', 11),
                                                   bg='#1e1e1e', fg='#d4d4d4',
                                                   insertbackground='#ffffff',
                                                   selectbackground='#264f78')
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events for line numbers and syntax highlighting
        self.code_editor.bind('<KeyRelease>', self.update_line_numbers)
        self.code_editor.bind('<Button-1>', self.update_line_numbers)
        self.code_editor.bind('<MouseWheel>', self.update_line_numbers)
        
    def create_console(self, parent):
        # Console Frame
        console_frame = ttk.LabelFrame(parent, text="Console Output", padding=5)
        console_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Console text area with dark theme
        self.console = scrolledtext.ScrolledText(console_frame, height=8, 
                                               font=('Consolas', 9), 
                                               bg='#0c0c0c', fg='#ffffff',
                                               selectbackground='#264f78')
        self.console.pack(fill=tk.BOTH, expand=True)
        
        self.log_message("🚀 VoidRay Advanced Editor initialized")
        self.log_message("💡 Tips: Ctrl+Space for auto-completion, F3 for game debug mode")
        self.log_message("📚 Check the API Reference panel for quick help")
        
    def on_text_change(self, event=None):
        """Handle text changes for syntax highlighting."""
        self.update_line_numbers()
        
        # Delay syntax highlighting to avoid performance issues
        if hasattr(self, '_highlight_timer'):
            self.root.after_cancel(self._highlight_timer)
        
        self._highlight_timer = self.root.after(300, self.apply_syntax_highlighting)
        
        # Update status
        self.status_label.config(text="Modified")
    
    def apply_syntax_highlighting(self):
        """Apply syntax highlighting with delay."""
        if self.syntax_highlighter:
            self.syntax_highlighter.highlight_syntax()
        
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
        
    def check_syntax(self):
        """Check Python syntax of current code."""
        try:
            code = self.code_editor.get('1.0', tk.END)
            compile(code, '<string>', 'exec')
            self.log_message("✅ Syntax check passed - No errors found")
            self.status_label.config(text="Syntax OK")
        except SyntaxError as e:
            self.log_message(f"❌ Syntax Error on line {e.lineno}: {e.msg}")
            self.status_label.config(text="Syntax Error")
        except Exception as e:
            self.log_message(f"⚠️ Warning: {str(e)}")
    
    def show_find_dialog(self):
        """Show find dialog."""
        find_window = tk.Toplevel(self.root)
        find_window.title("Find")
        find_window.geometry("300x100")
        find_window.configure(bg='#1e1e1e')
        
        ttk.Label(find_window, text="Find:").pack(pady=5)
        find_entry = ttk.Entry(find_window, width=40)
        find_entry.pack(pady=5)
        find_entry.focus()
        
        def do_find():
            text = find_entry.get()
            if text:
                start_pos = self.code_editor.search(text, tk.INSERT)
                if start_pos:
                    end_pos = f"{start_pos}+{len(text)}c"
                    self.code_editor.tag_remove(tk.SEL, "1.0", tk.END)
                    self.code_editor.tag_add(tk.SEL, start_pos, end_pos)
                    self.code_editor.mark_set(tk.INSERT, end_pos)
                    self.code_editor.see(start_pos)
        
        ttk.Button(find_window, text="Find", command=do_find).pack(pady=5)
        find_entry.bind('<Return>', lambda e: do_find())
    
    def show_replace_dialog(self):
        """Show find and replace dialog."""
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Find & Replace")
        replace_window.geometry("350x150")
        replace_window.configure(bg='#1e1e1e')
        
        ttk.Label(replace_window, text="Find:").pack(pady=2)
        find_entry = ttk.Entry(replace_window, width=40)
        find_entry.pack(pady=2)
        
        ttk.Label(replace_window, text="Replace with:").pack(pady=2)
        replace_entry = ttk.Entry(replace_window, width=40)
        replace_entry.pack(pady=2)
        
        button_frame = ttk.Frame(replace_window)
        button_frame.pack(pady=10)
        
        def do_replace():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            if find_text:
                content = self.code_editor.get("1.0", tk.END)
                new_content = content.replace(find_text, replace_text)
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert("1.0", new_content)
                self.apply_syntax_highlighting()
        
        ttk.Button(button_frame, text="Replace All", command=do_replace).pack(side=tk.LEFT, padx=5)
        find_entry.focus()
    
    def show_documentation(self):
        """Show VoidRay documentation."""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("VoidRay Documentation")
        doc_window.geometry("600x500")
        doc_window.configure(bg='#1e1e1e')
        
        doc_text = scrolledtext.ScrolledText(doc_window, wrap=tk.WORD, 
                                           bg='#1e1e1e', fg='#ffffff')
        doc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        documentation = """
VoidRay Game Engine Documentation
================================

GETTING STARTED:
1. Import VoidRay: import voidray
2. Configure engine: voidray.configure(width, height, title, fps)
3. Create scenes and game objects
4. Start the engine: voidray.start()

CORE CONCEPTS:

Engine:
- Central game management system
- Handles rendering, input, physics, audio
- Use voidray.get_engine() to access

Scenes:
- Containers for game objects
- Manage game states (menu, gameplay, etc.)
- Override on_enter(), on_exit(), update(), render()

Game Objects & Sprites:
- Base entities in your game
- Sprites handle visual representation
- Use components for behavior

Components:
- Modular behavior system
- Rigidbody: Physics simulation
- Colliders: Collision detection
- Custom components: Your own logic

Physics:
- Built-in physics engine
- Gravity, velocity, collision response
- Use Rigidbody and Collider components

Input:
- Keyboard and mouse support
- Frame-perfect input detection
- Check Keys class for key constants

Audio:
- Music and sound effect playback
- Volume control and looping
- Multiple format support

BEST PRACTICES:
- Use delta_time for frame-rate independent movement
- Organize code into scenes and components
- Clean up resources in on_exit() methods
- Use meaningful names for game objects
- Test on different frame rates

COMMON PATTERNS:
See the examples folder for complete implementations.
        """
        
        doc_text.insert("1.0", documentation)
        doc_text.config(state=tk.DISABLED)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts."""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("400x300")
        shortcuts_window.configure(bg='#1e1e1e')
        
        shortcuts_text = scrolledtext.ScrolledText(shortcuts_window, wrap=tk.WORD,
                                                 bg='#1e1e1e', fg='#ffffff')
        shortcuts_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        shortcuts = """
VoidRay Editor Keyboard Shortcuts
================================

GENERAL:
Ctrl+N      New project
Ctrl+O      Open file
Ctrl+S      Save file
Ctrl+Shift+S Save as...

EDITING:
Ctrl+F      Find text
Ctrl+H      Find and replace
Ctrl+Space  Auto-completion suggestions
Tab         Indent selection
Shift+Tab   Unindent selection

RUNNING:
F5          Run game
Shift+F5    Stop game
Ctrl+B      Build to .py file
F7          Check syntax

IN-GAME (VoidRay):
F3          Toggle debug overlay
ESC         Usually exits game
Arrow Keys  Common movement controls
Space       Common action key

EDITOR FEATURES:
- Real-time syntax highlighting
- Auto-completion for VoidRay API
- Line numbers
- Dark theme optimized for coding
- API reference panel
        """
        
        shortcuts_text.insert("1.0", shortcuts)
        shortcuts_text.config(state=tk.DISABLED)
        
    def new_project(self):
        if messagebox.askyesno("New Project", "Create a new project? Unsaved changes will be lost."):
            self.current_file = None
            self.load_default_template()
            self.status_label.config(text="New Project")
            self.log_message("📝 New project created")
            
    def load_default_template(self):
        template = '''"""
VoidRay Game Template
Create your amazing game here!
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
        
        # Get input manager
        input_manager = voidray.get_engine().input_manager
        
        # Calculate movement
        velocity = Vector2.zero()
        if input_manager.is_key_pressed(Keys.LEFT):
            velocity.x = -self.speed
        if input_manager.is_key_pressed(Keys.RIGHT):
            velocity.x = self.speed
        if input_manager.is_key_pressed(Keys.UP):
            velocity.y = -self.speed
        if input_manager.is_key_pressed(Keys.DOWN):
            velocity.y = self.speed
            
        # Apply movement with delta_time for smooth motion
        self.transform.position += velocity * delta_time


class GameScene(Scene):
    """Main game scene."""
    
    def __init__(self):
        super().__init__("Game")
        
    def on_enter(self):
        super().on_enter()
        
        # Create player at center of screen
        self.player = Player()
        self.player.transform.position = Vector2(400, 300)
        self.add_object(self.player)
        
        print("🎮 Game scene started - Use arrow keys to move!")
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check for exit key
        input_manager = voidray.get_engine().input_manager
        if input_manager.is_key_just_pressed(Keys.ESCAPE):
            voidray.stop()


def init_game():
    """Initialize the game - called once when engine starts."""
    scene = GameScene()
    voidray.register_scene("game", scene)
    voidray.set_scene("game")


def main():
    """Main entry point."""
    print("🚀 Starting VoidRay Game...")
    
    # Configure the engine
    voidray.configure(
        width=800, 
        height=600, 
        title="My VoidRay Game", 
        fps=60
    )
    
    # Register initialization callback
    voidray.on_init(init_game)
    
    # Start the engine
    voidray.start()


if __name__ == "__main__":
    main()
'''
        self.code_editor.delete('1.0', tk.END)
        self.code_editor.insert('1.0', template)
        self.apply_syntax_highlighting()
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
                self.apply_syntax_highlighting()
                self.update_line_numbers()
                self.status_label.config(text=f"Opened: {os.path.basename(file_path)}")
                self.log_message(f"📂 Opened: {file_path}")
                
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
            self.status_label.config(text=f"Saved: {os.path.basename(file_path)}")
            self.log_message(f"💾 Saved: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
            
    def build_to_py(self):
        """Build/save the current code as a .py file."""
        if not self.current_file or not self.current_file.endswith('.py'):
            file_path = filedialog.asksaveasfilename(
                title="Build to Python File",
                defaultextension=".py",
                filetypes=[("Python files", "*.py")]
            )
            
            if not file_path:
                return
                
            self.current_file = file_path
            
        self.save_to_file(self.current_file)
        self.log_message(f"🔨 Built to: {self.current_file}")
        messagebox.showinfo("Build Complete", f"Successfully built to:\n{self.current_file}")
        
    def run_game(self):
        """Run the current game code."""
        if self.preview_process:
            self.stop_game()
            
        # Check syntax first
        self.check_syntax()
            
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
                            self.root.after(0, lambda msg=output: self.log_message(f"🎮 {msg.strip()}"))
                            
                    # Get any remaining output
                    stdout, stderr = self.preview_process.communicate()
                    if stdout:
                        self.root.after(0, lambda: self.log_message(f"🎮 {stdout}"))
                    if stderr:
                        self.root.after(0, lambda: self.log_message(f"❌ Game Error: {stderr}"))
                        
                    self.root.after(0, lambda: self.log_message("🏁 Game process ended"))
                    self.root.after(0, lambda: setattr(self, 'preview_process', None))
                    self.root.after(0, lambda: self.status_label.config(text="Game Stopped"))
                    
                except Exception as e:
                    self.root.after(0, lambda: self.log_message(f"❌ Error running game: {str(e)}"))
                    
            threading.Thread(target=run_process, daemon=True).start()
            self.status_label.config(text="Game Running")
            self.log_message("🚀 Starting game...")
            
        except Exception as e:
            self.log_message(f"❌ Failed to run game: {str(e)}")
            
    def stop_game(self):
        """Stop the running game."""
        if self.preview_process:
            self.preview_process.terminate()
            self.preview_process = None
            self.status_label.config(text="Game Stopped")
            self.log_message("⏹ Game stopped")
            
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
                self.apply_syntax_highlighting()
                self.update_line_numbers()
                self.status_label.config(text=f"Example: {example_name}")
                self.log_message(f"📋 Loaded example: {example_name}")
                
            except Exception as e:
                self.log_message(f"❌ Failed to load example {example_name}: {str(e)}")
        else:
            self.log_message(f"❌ Example not found: {example_path}")
            
    def show_auto_complete(self):
        """Show auto-completion suggestions safely."""
        if self.programming_assistant:
            self.programming_assistant.show_suggestions()
        else:
            self.log_message("⚠️ Programming assistant not yet initialized")
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About VoidRay Advanced Editor", 
                          "VoidRay Game Engine - Advanced Code Editor v2.0\n\n"
                          "🎮 Professional game development environment\n"
                          "🎨 Syntax highlighting with API-specific colors\n"
                          "🤖 Programming assistant with auto-completion\n"
                          "📚 Built-in API reference and documentation\n"
                          "🌙 Dark theme optimized for coding\n"
                          "⚡ Real-time syntax checking\n"
                          "🔍 Advanced find and replace\n\n"
                          "Create amazing games with VoidRay!")
        
    def run(self):
        """Start the GUI application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set initial focus and apply syntax highlighting
        self.code_editor.focus()
        self.root.after(100, self.apply_syntax_highlighting)
        
        self.root.mainloop()
        
    def on_closing(self):
        """Handle application closing."""
        if self.preview_process:
            self.stop_game()
        self.root.destroy()


def main():
    """Main entry point for the advanced GUI editor."""
    print("🚀 Starting VoidRay Advanced Code Editor...")
    app = VoidRayGUIEditor()
    app.run()


if __name__ == "__main__":
    main()
