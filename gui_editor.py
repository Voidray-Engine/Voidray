
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
        
        # VoidRay API classes - Updated for new engine
        voidray_classes = r'\b(Engine|Scene|GameObject|Sprite|Vector2|Color|InputManager|Keys|BoxCollider|CircleCollider|Rigidbody|Transform|Camera|PhysicsEngine|AudioManager|AssetLoader|ResourceManager|WorldManager|SceneManager|Profiler|DebugOverlay|LevelEditor|Advanced2DRenderer)\b'
        self._highlight_pattern(voidray_classes, "voidray_class")
        
        # VoidRay API functions and methods - Updated for new engine
        voidray_methods = r'\b(configure|start|stop|on_init|on_update|on_render|register_scene|set_scene|get_engine|create_colored_rect|create_colored_circle|add_component|get_component|set_velocity|add_impulse|is_key_pressed|is_key_just_pressed|draw_text|draw_rect|clear|present|set_rendering_mode|enable_performance_mode|load_level|preload_game_assets|get_engine_stats|optimize_for_mobile)\b'
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
        """Get VoidRay API suggestions - Updated for new engine."""
        voidray_api = {
            'voidray': ['configure', 'start', 'stop', 'on_init', 'on_update', 'on_render', 
                       'register_scene', 'set_scene', 'get_engine'],
            'Engine': ['__init__', 'configure', 'start', 'stop', 'set_scene', 'get_fps', 
                      'set_rendering_mode', 'enable_performance_mode', 'load_level', 'get_engine_stats',
                      'optimize_for_mobile', 'preload_game_assets'],
            'Scene': ['__init__', 'on_enter', 'on_exit', 'update', 'render', 'add_object',
                     'get_walls', 'get_light_sources', 'load_level'],
            'Sprite': ['__init__', 'create_colored_rect', 'create_colored_circle', 'update', 
                      'add_component', 'get_component'],
            'Vector2': ['__init__', 'x', 'y', 'zero', 'normalized', 'magnitude'],
            'Color': ['RED', 'GREEN', 'BLUE', 'YELLOW', 'WHITE', 'BLACK', 'CYAN', 'MAGENTA'],
            'Keys': ['LEFT', 'RIGHT', 'UP', 'DOWN', 'SPACE', 'ESCAPE', 'ENTER'],
            'InputManager': ['is_key_pressed', 'is_key_just_pressed', 'is_key_just_released'],
            'Rigidbody': ['set_velocity', 'add_impulse', 'set_mass', 'set_bounciness'],
            'Advanced2DRenderer': ['set_rendering_mode', 'add_wall', 'add_light_source', 
                                  'create_procedural_texture', 'get_text_size'],
            'ResourceManager': ['preload_asset_pack', 'get_memory_usage', 'enable_streaming'],
            'WorldManager': ['register_level', 'load_region', 'update_streaming'],
            'LevelEditor': ['run', 'save_level', 'load_level', 'add_wall', 'add_light'],
            'DebugOverlay': ['toggle', 'render'],
            'Profiler': ['start_profile', 'end_profile', 'get_stats']
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
        self.root.title("VoidRay Game Engine - Advanced Code Editor v2.5")
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
        # API Reference - Updated for new engine
        api_frame = ttk.LabelFrame(parent, text="VoidRay API Reference v2.5", padding=5)
        api_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        api_tree = ttk.Treeview(api_frame, height=15)
        api_tree.pack(fill=tk.BOTH, expand=True)
        
        # Populate API tree
        self.populate_api_tree(api_tree)
        
        # Help panel - Updated for new features
        help_frame = ttk.LabelFrame(parent, text="Quick Help - v2.5 Features", padding=5)
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        help_text = scrolledtext.ScrolledText(help_frame, height=10, width=30, 
                                            font=('Consolas', 9), bg='#2d2d30', fg='#ffffff',
                                            wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        help_content = """VoidRay v2.5 Quick Reference:

🎮 BASIC SETUP:
import voidray
voidray.configure(800, 600, "Game")
voidray.start()

🆕 NEW ENGINE FEATURES:
# 2.5D Rendering
engine.set_rendering_mode("2.5D")

# Performance Mode
engine.enable_performance_mode(True)

# Mobile Optimization  
engine.optimize_for_mobile()

# Level Loading
engine.load_level("level1.json")

🏗️ ADVANCED SYSTEMS:
# Resource Management
resource_manager = ResourceManager()
resource_manager.preload_asset_pack("textures", config)

# World Streaming
world_manager = WorldManager()
world_manager.register_level("level1", "data/level1.json")

# Profiling
profiler.start_profile("render_loop")
# ... game code ...
profiler.end_profile("render_loop")

🔧 DEVELOPMENT TOOLS:
# Level Editor
from voidray.tools import LevelEditor
editor = LevelEditor()
editor.run()

# Debug Overlay (F3 in game)
debug_overlay.toggle()

⚡ PERFORMANCE:
- Use engine.get_engine_stats() for metrics
- Enable performance mode for demanding games
- Use world streaming for large levels
- Profile with built-in profiler

🎨 2.5D FEATURES:
- Wall rendering with textures
- Dynamic lighting system
- Sector-based level design
- Fog effects and render distance

💡 TIPS:
- Check logs/ folder for performance reports
- Use Advanced2DRenderer for 2.5D games
- Preload assets for better performance
- Test on mobile with optimize_for_mobile()
"""
        
        help_text.insert("1.0", help_content)
        help_text.config(state=tk.DISABLED)
        
    def populate_api_tree(self, tree):
        """Populate the API reference tree - Updated for new engine."""
        # Core Engine - Updated
        engine_node = tree.insert("", "end", text="🎮 Engine v2.5", open=True)
        tree.insert(engine_node, "end", text="configure(width, height, title, fps)")
        tree.insert(engine_node, "end", text="start() / stop()")
        tree.insert(engine_node, "end", text="set_rendering_mode('2D'|'2.5D')")
        tree.insert(engine_node, "end", text="enable_performance_mode(enabled)")
        tree.insert(engine_node, "end", text="optimize_for_mobile()")
        tree.insert(engine_node, "end", text="get_engine_stats()")
        
        # Scene Management
        scene_node = tree.insert("", "end", text="🎬 Scene Management", open=True)
        tree.insert(scene_node, "end", text="register_scene(name, scene)")
        tree.insert(scene_node, "end", text="set_scene(name)")
        tree.insert(scene_node, "end", text="load_level(level_name)")
        
        # 2.5D Rendering - NEW
        render_node = tree.insert("", "end", text="🎨 2.5D Rendering", open=True)
        tree.insert(render_node, "end", text="Advanced2DRenderer")
        tree.insert(render_node, "end", text="add_wall(start, end, texture)")
        tree.insert(render_node, "end", text="add_light_source(pos, intensity)")
        tree.insert(render_node, "end", text="create_procedural_texture(name)")
        
        # Resource Management - NEW
        resource_node = tree.insert("", "end", text="🗃️ Resource Management", open=True)
        tree.insert(resource_node, "end", text="ResourceManager(max_memory_mb)")
        tree.insert(resource_node, "end", text="preload_asset_pack(name, config)")
        tree.insert(resource_node, "end", text="get_memory_usage()")
        
        # World Management - NEW
        world_node = tree.insert("", "end", text="🌍 World Management", open=True)
        tree.insert(world_node, "end", text="WorldManager(streaming_distance)")
        tree.insert(world_node, "end", text="register_level(id, file_path)")
        tree.insert(world_node, "end", text="update_streaming(player_pos)")
        
        # Development Tools - NEW
        tools_node = tree.insert("", "end", text="🔧 Dev Tools", open=True)
        tree.insert(tools_node, "end", text="LevelEditor() - Visual editor")
        tree.insert(tools_node, "end", text="DebugOverlay.toggle() - F3 key")
        tree.insert(tools_node, "end", text="Profiler.start_profile(name)")
        
        # Physics
        physics_node = tree.insert("", "end", text="⚡ Physics", open=True)
        tree.insert(physics_node, "end", text="Rigidbody() / BoxCollider()")
        tree.insert(physics_node, "end", text="set_velocity(vector)")
        tree.insert(physics_node, "end", text="add_impulse(force)")
        
        # Input
        input_node = tree.insert("", "end", text="🎯 Input", open=True)
        tree.insert(input_node, "end", text="is_key_pressed(key)")
        tree.insert(input_node, "end", text="Keys.LEFT, RIGHT, UP, DOWN")
        tree.insert(input_node, "end", text="Keys.SPACE, ESCAPE, ENTER")
        
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
        
        # Tools Menu - NEW
        tools_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Level Editor", command=self.open_level_editor)
        tools_menu.add_command(label="Performance Report", command=self.show_performance_report)
        tools_menu.add_separator()
        tools_menu.add_command(label="Generate 2.5D Template", command=self.generate_2_5d_template)
        
        # Examples Menu - Updated
        examples_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Examples", menu=examples_menu)
        examples_menu.add_command(label="Basic 2D Game", command=lambda: self.load_example_template("basic_2d"))
        examples_menu.add_command(label="2.5D Demo", command=lambda: self.load_example_template("2_5d_demo"))
        examples_menu.add_command(label="Physics Demo", command=lambda: self.load_example_template("physics"))
        examples_menu.add_command(label="Performance Test", command=lambda: self.load_example_template("performance"))
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="VoidRay Documentation", command=self.show_documentation)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_code_editor(self, parent):
        # Code Editor Frame
        editor_frame = ttk.LabelFrame(parent, text="Code Editor - VoidRay v2.5", padding=5)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        toolbar = ttk.Frame(editor_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="▶ Run", command=self.run_game).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="⏹ Stop", command=self.stop_game).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🔨 Build", command=self.build_to_py).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="✓ Check", command=self.check_syntax).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🛠️ Tools", command=self.open_level_editor).pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(toolbar, text="Ready - VoidRay v2.5")
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
        console_frame = ttk.LabelFrame(parent, text="Console Output & Performance", padding=5)
        console_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Console text area with dark theme
        self.console = scrolledtext.ScrolledText(console_frame, height=8, 
                                               font=('Consolas', 9), 
                                               bg='#0c0c0c', fg='#ffffff',
                                               selectbackground='#264f78')
        self.console.pack(fill=tk.BOTH, expand=True)
        
        self.log_message("🚀 VoidRay Advanced Editor v2.5 initialized")
        self.log_message("🆕 New features: 2.5D rendering, performance mode, level editor")
        self.log_message("💡 Tips: Ctrl+Space for auto-completion, F3 for game debug mode")
        self.log_message("📚 Check the API Reference panel for new v2.5 features")
        
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
    
    def open_level_editor(self):
        """Open the VoidRay level editor."""
        try:
            subprocess.Popen([sys.executable, "-c", 
                            "from voidray.tools import LevelEditor; LevelEditor().run()"])
            self.log_message("🛠️ Level Editor launched in separate window")
        except Exception as e:
            self.log_message(f"❌ Failed to launch Level Editor: {str(e)}")
    
    def show_performance_report(self):
        """Show the latest performance report."""
        report_path = "logs/final_performance_report.json"
        if os.path.exists(report_path):
            try:
                import json
                with open(report_path, 'r') as f:
                    report = json.load(f)
                
                # Create performance report window
                perf_window = tk.Toplevel(self.root)
                perf_window.title("Performance Report")
                perf_window.geometry("600x400")
                perf_window.configure(bg='#1e1e1e')
                
                perf_text = scrolledtext.ScrolledText(perf_window, wrap=tk.WORD,
                                                    bg='#1e1e1e', fg='#ffffff')
                perf_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Format report data
                frame_stats = report.get('frame_stats', {})
                memory_stats = report.get('memory_stats', {})
                
                report_content = f"""VoidRay Engine Performance Report
=====================================

FRAME PERFORMANCE:
- Average FPS: {frame_stats.get('avg_fps', 0):.1f}
- Min FPS: {frame_stats.get('min_fps', 0):.1f}
- Max FPS: {frame_stats.get('max_fps', 0):.1f}
- Frame Time: {frame_stats.get('avg_frame_time', 0):.3f}s

MEMORY USAGE:
- Current Memory: {memory_stats.get('current_memory_mb', 0):.2f} MB
- Average Memory: {memory_stats.get('avg_memory_mb', 0):.2f} MB
- Peak Memory: {memory_stats.get('max_memory_mb', 0):.2f} MB

OPTIMIZATION SUGGESTIONS:
{self._get_optimization_suggestions(frame_stats)}
"""
                
                perf_text.insert("1.0", report_content)
                perf_text.config(state=tk.DISABLED)
                
            except Exception as e:
                self.log_message(f"❌ Failed to load performance report: {str(e)}")
        else:
            self.log_message("📊 No performance report found. Run a game first.")
    
    def _get_optimization_suggestions(self, frame_stats):
        """Generate optimization suggestions based on performance data."""
        suggestions = []
        avg_fps = frame_stats.get('avg_fps', 60)
        
        if avg_fps < 30:
            suggestions.append("- Enable performance mode: engine.enable_performance_mode(True)")
            suggestions.append("- Consider mobile optimizations: engine.optimize_for_mobile()")
        elif avg_fps < 45:
            suggestions.append("- Reduce render distance in 2.5D mode")
            suggestions.append("- Use object culling for off-screen sprites")
        else:
            suggestions.append("- Performance is good! Consider adding more features.")
        
        return "\n".join(suggestions) if suggestions else "Performance is optimal!"
    
    def generate_2_5d_template(self):
        """Generate a 2.5D game template."""
        template = '''"""
VoidRay 2.5D Game Template
Advanced game with 2.5D rendering, performance monitoring, and modern features.
"""

import voidray
from voidray import Scene, GameObject, Sprite, Vector2, Keys
from voidray.graphics.renderer import Color
from voidray.core.resource_manager import ResourceManager
from voidray.core.world_manager import WorldManager


class Player(Sprite):
    """Enhanced player with 2.5D movement."""
    
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


class Game2_5D_Scene(Scene):
    """Main 2.5D game scene with advanced features."""
    
    def __init__(self):
        super().__init__("Game2_5D")
        
    def on_enter(self):
        super().on_enter()
        
        # Set up 2.5D rendering
        engine = voidray.get_engine()
        engine.set_rendering_mode("2.5D")
        
        # Enable performance optimizations
        engine.enable_performance_mode(True)
        
        # Create player at center of screen
        self.player = Player()
        self.player.transform.position = Vector2(400, 300)
        self.add_object(self.player)
        
        # Set up sample 2.5D level geometry
        self._setup_2_5d_level()
        
        print("🎮 2.5D Game scene started - Use arrow keys to move!")
        print("📊 Press F3 to toggle debug overlay")
        
    def _setup_2_5d_level(self):
        """Set up a sample 2.5D level."""
        engine = voidray.get_engine()
        renderer = engine.renderer
        
        # Add some walls for 2.5D effect
        renderer.add_wall(Vector2(100, 100), Vector2(700, 100), "brick", 64)
        renderer.add_wall(Vector2(700, 100), Vector2(700, 500), "stone", 64)
        renderer.add_wall(Vector2(700, 500), Vector2(100, 500), "brick", 64)
        renderer.add_wall(Vector2(100, 500), Vector2(100, 100), "stone", 64)
        
        # Add lighting
        renderer.add_light_source(Vector2(400, 300), 1.0, (255, 255, 200), 200.0)
        renderer.add_light_source(Vector2(200, 200), 0.8, (255, 200, 200), 150.0)
        
        print("🏗️ 2.5D level geometry created")
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check for exit key
        input_manager = voidray.get_engine().input_manager
        if input_manager.is_key_just_pressed(Keys.ESCAPE):
            voidray.stop()
        
        # Toggle debug overlay with F3
        if input_manager.is_key_just_pressed(Keys.F3):
            engine = voidray.get_engine()
            if hasattr(engine, 'debug_overlay'):
                engine.debug_overlay.toggle()


def init_game():
    """Initialize the game - called once when engine starts."""
    # Set up resource management
    engine = voidray.get_engine()
    
    # Preload assets for better performance
    asset_config = {
        "textures": ["brick.png", "stone.png", "metal.png"],
        "sounds": ["footstep.wav", "ambient.mp3"]
    }
    
    try:
        engine.preload_game_assets({"main_pack": asset_config})
    except Exception as e:
        print(f"⚠️ Asset preloading skipped: {e}")
    
    # Create and register the 2.5D scene
    scene = Game2_5D_Scene()
    voidray.register_scene("game2_5d", scene)
    voidray.set_scene("game2_5d")
    
    # Create sample textures if needed
    engine.create_sample_textures()


def main():
    """Main entry point."""
    print("🚀 Starting VoidRay 2.5D Game...")
    print("🆕 Using VoidRay Engine v2.5 features")
    
    # Configure the engine with performance settings
    voidray.configure(
        width=800, 
        height=600, 
        title="VoidRay 2.5D Demo", 
        fps=60
    )
    
    # Register initialization callback
    voidray.on_init(init_game)
    
    # Start the engine
    voidray.start()
    
    # Show performance stats after game ends
    engine = voidray.get_engine()
    if hasattr(engine, 'get_engine_stats'):
        stats = engine.get_engine_stats()
        print("📊 Final Performance Stats:")
        print(f"   Average FPS: {stats.get('avg_fps', 'N/A')}")
        print(f"   Total Objects: {stats.get('object_count', 'N/A')}")


if __name__ == "__main__":
    main()
'''
        
        self.code_editor.delete('1.0', tk.END)
        self.code_editor.insert('1.0', template)
        self.apply_syntax_highlighting()
        self.update_line_numbers()
        self.status_label.config(text="2.5D Template Generated")
        self.log_message("🎨 2.5D game template generated with new engine features")
    
    def load_example_template(self, template_type):
        """Load different example templates based on type."""
        if template_type == "2_5d_demo":
            self.generate_2_5d_template()
        elif template_type == "performance":
            self._load_performance_template()
        elif template_type == "physics":
            self._load_physics_template()
        else:
            self.load_default_template()
    
    def _load_performance_template(self):
        """Load a performance testing template."""
        template = '''"""
VoidRay Performance Test Template
Tests engine performance with many objects and 2.5D rendering.
"""

import voidray
from voidray import Scene, GameObject, Sprite, Vector2, Keys
from voidray.graphics.renderer import Color
import random


class PerformanceTestScene(Scene):
    """Scene for testing engine performance."""
    
    def __init__(self):
        super().__init__("PerformanceTest")
        self.objects = []
        
    def on_enter(self):
        super().on_enter()
        
        # Configure for performance testing
        engine = voidray.get_engine()
        engine.set_rendering_mode("2.5D")
        engine.enable_performance_mode(True)
        
        # Create many test objects
        self.create_test_objects(500)  # Adjust number for testing
        
        print("⚡ Performance test started")
        print("📊 Press F3 to view real-time performance stats")
        
    def create_test_objects(self, count):
        """Create many objects for performance testing."""
        colors = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.CYAN]
        
        for i in range(count):
            sprite = Sprite(f"TestObject_{i}")
            sprite.create_colored_rect(
                random.randint(5, 20),
                random.randint(5, 20),
                random.choice(colors)
            )
            
            # Random position
            sprite.transform.position = Vector2(
                random.randint(50, 750),
                random.randint(50, 550)
            )
            
            self.add_object(sprite)
            self.objects.append(sprite)
    
    def update(self, delta_time):
        super().update(delta_time)
        
        # Animate objects for performance testing
        for obj in self.objects:
            obj.transform.position.x += random.uniform(-50, 50) * delta_time
            obj.transform.position.y += random.uniform(-50, 50) * delta_time
            
            # Keep objects on screen
            if obj.transform.position.x < 0:
                obj.transform.position.x = 800
            elif obj.transform.position.x > 800:
                obj.transform.position.x = 0
                
            if obj.transform.position.y < 0:
                obj.transform.position.y = 600
            elif obj.transform.position.y > 600:
                obj.transform.position.y = 0
        
        # Exit on ESC
        input_manager = voidray.get_engine().input_manager
        if input_manager.is_key_just_pressed(Keys.ESCAPE):
            voidray.stop()


def init_game():
    """Initialize performance test."""
    scene = PerformanceTestScene()
    voidray.register_scene("perf_test", scene)
    voidray.set_scene("perf_test")


def main():
    """Main entry point."""
    print("⚡ VoidRay Performance Test")
    
    voidray.configure(800, 600, "VoidRay Performance Test", 60)
    voidray.on_init(init_game)
    voidray.start()


if __name__ == "__main__":
    main()
'''
        
        self.code_editor.delete('1.0', tk.END)
        self.code_editor.insert('1.0', template)
        self.apply_syntax_highlighting()
        self.update_line_numbers()
        self.status_label.config(text="Performance Template Loaded")
        self.log_message("⚡ Performance test template loaded")
    
    def _load_physics_template(self):
        """Load enhanced physics template."""
        template = '''"""
VoidRay Enhanced Physics Demo
Demonstrates advanced physics features in the updated engine.
"""

import voidray
from voidray import Scene, GameObject, Sprite, Vector2, Keys
from voidray.graphics.renderer import Color
from voidray.physics import Rigidbody, BoxCollider


class PhysicsObject(Sprite):
    """Physics-enabled sprite."""
    
    def __init__(self, name, size, color, mass=1.0):
        super().__init__(name)
        self.create_colored_rect(size, size, color)
        
        # Add physics components
        self.rigidbody = Rigidbody()
        self.rigidbody.set_mass(mass)
        self.add_component(self.rigidbody)
        
        self.collider = BoxCollider(size, size)
        self.add_component(self.collider)


class PhysicsScene(Scene):
    """Enhanced physics demonstration scene."""
    
    def __init__(self):
        super().__init__("Physics")
        
    def on_enter(self):
        super().on_enter()
        
        # Set up physics optimizations
        engine = voidray.get_engine()
        engine.enable_performance_mode(True)
        
        # Create physics objects
        self.create_physics_objects()
        
        print("⚡ Enhanced physics demo started")
        print("🎯 Click to add objects, arrow keys to apply forces")
        
    def create_physics_objects(self):
        """Create various physics objects."""
        # Create some falling objects
        for i in range(5):
            obj = PhysicsObject(f"FallingBox_{i}", 30, Color.BLUE, mass=1.0)
            obj.transform.position = Vector2(200 + i * 50, 100)
            self.add_object(obj)
        
        # Create ground objects
        for i in range(10):
            ground = PhysicsObject(f"Ground_{i}", 40, Color.GREEN, mass=10.0)
            ground.transform.position = Vector2(i * 80, 500)
            ground.rigidbody.set_velocity(Vector2.zero())
            self.add_object(ground)
    
    def update(self, delta_time):
        super().update(delta_time)
        
        input_manager = voidray.get_engine().input_manager
        
        # Apply forces with arrow keys
        if input_manager.is_key_pressed(Keys.LEFT):
            self._apply_force_to_objects(Vector2(-500, 0))
        if input_manager.is_key_pressed(Keys.RIGHT):
            self._apply_force_to_objects(Vector2(500, 0))
        if input_manager.is_key_pressed(Keys.UP):
            self._apply_force_to_objects(Vector2(0, -500))
        
        if input_manager.is_key_just_pressed(Keys.ESCAPE):
            voidray.stop()
    
    def _apply_force_to_objects(self, force):
        """Apply force to all physics objects."""
        for obj in self.objects:
            if hasattr(obj, 'rigidbody'):
                obj.rigidbody.add_impulse(force)


def init_game():
    """Initialize physics demo."""
    scene = PhysicsScene()
    voidray.register_scene("physics", scene)
    voidray.set_scene("physics")


def main():
    """Main entry point."""
    print("⚡ VoidRay Enhanced Physics Demo")
    
    voidray.configure(800, 600, "VoidRay Physics Demo", 60)
    voidray.on_init(init_game)
    voidray.start()


if __name__ == "__main__":
    main()
'''
        
        self.code_editor.delete('1.0', tk.END)
        self.code_editor.insert('1.0', template)
        self.apply_syntax_highlighting()
        self.update_line_numbers()
        self.status_label.config(text="Physics Template Loaded")
        self.log_message("⚡ Enhanced physics template loaded")
    
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
        """Show updated VoidRay documentation."""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("VoidRay v2.5 Documentation")
        doc_window.geometry("700x600")
        doc_window.configure(bg='#1e1e1e')
        
        doc_text = scrolledtext.ScrolledText(doc_window, wrap=tk.WORD, 
                                           bg='#1e1e1e', fg='#ffffff')
        doc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        documentation = """
VoidRay Game Engine v2.5 Documentation
======================================

🆕 NEW IN VERSION 2.5:

2.5D RENDERING:
- Set rendering mode: engine.set_rendering_mode("2.5D")
- Add walls: renderer.add_wall(start, end, texture, height)
- Add lights: renderer.add_light_source(position, intensity, color, radius)
- Create textures: renderer.create_procedural_texture(name, width, height, pattern)

PERFORMANCE FEATURES:
- Performance mode: engine.enable_performance_mode(True)
- Mobile optimization: engine.optimize_for_mobile()
- Performance stats: engine.get_engine_stats()
- Profiling: profiler.start_profile(name) / end_profile(name)

RESOURCE MANAGEMENT:
- ResourceManager for memory management
- Asset preloading: engine.preload_game_assets(asset_packs)
- Streaming for large games
- Automatic memory optimization

WORLD MANAGEMENT:
- WorldManager for large-scale games
- Level streaming and region loading
- Dynamic world loading based on player position

DEVELOPMENT TOOLS:
- LevelEditor for visual level creation
- DebugOverlay (F3 key) for real-time stats
- Performance reports in logs/ folder
- Enhanced profiling system

ENHANCED PHYSICS:
- Improved spatial partitioning
- Better collision detection
- Performance optimizations
- Physics object sleeping

GETTING STARTED WITH 2.5D:
1. Set rendering mode to "2.5D"
2. Create walls and sectors for your level
3. Add light sources for atmosphere
4. Use the level editor for visual editing

PERFORMANCE OPTIMIZATION:
1. Enable performance mode for demanding games
2. Use mobile optimizations for lower-end devices
3. Monitor performance with built-in profiler
4. Check logs for detailed performance reports

BEST PRACTICES:
- Use resource streaming for large games
- Profile performance-critical sections
- Preload assets for smoother gameplay
- Use the debug overlay during development
- Test on different performance levels

LEVEL EDITING:
- Use the visual level editor for 2.5D levels
- Save/load levels in JSON format
- Place walls, lights, and sprites visually
- Test levels directly in the editor

See the examples for complete implementations of these features.
        """
        
        doc_text.insert("1.0", documentation)
        doc_text.config(state=tk.DISABLED)
    
    def show_shortcuts(self):
        """Show updated keyboard shortcuts."""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts v2.5")
        shortcuts_window.geometry("450x350")
        shortcuts_window.configure(bg='#1e1e1e')
        
        shortcuts_text = scrolledtext.ScrolledText(shortcuts_window, wrap=tk.WORD,
                                                 bg='#1e1e1e', fg='#ffffff')
        shortcuts_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        shortcuts = """
VoidRay Editor v2.5 Keyboard Shortcuts
======================================

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

RUNNING & BUILDING:
F5          Run game
Shift+F5    Stop game
Ctrl+B      Build to .py file
F7          Check syntax

🆕 NEW TOOLS:
F6          Open Level Editor
Ctrl+P      Show Performance Report
Ctrl+T      Generate 2.5D Template
Ctrl+Shift+T Performance Test Template

IN-GAME (VoidRay):
F3          Toggle debug overlay (NEW!)
ESC         Usually exits game
Arrow Keys  Common movement controls
Space       Common action key

🆕 LEVEL EDITOR:
1-4         Switch tools (Wall, Light, Sprite, Select)
G           Toggle grid
Ctrl+S      Save level
Ctrl+O      Open level
Ctrl+N      New level
WASD/Arrows Camera movement

EDITOR FEATURES:
- Real-time syntax highlighting for v2.5 API
- Auto-completion for new engine features
- Integrated performance monitoring
- Direct access to development tools
- 2.5D template generation
        """
        
        shortcuts_text.insert("1.0", shortcuts)
        shortcuts_text.config(state=tk.DISABLED)
        
    def new_project(self):
        if messagebox.askyesno("New Project", "Create a new project? Unsaved changes will be lost."):
            self.current_file = None
            self.load_default_template()
            self.status_label.config(text="New Project - VoidRay v2.5")
            self.log_message("📝 New project created with v2.5 template")
            
    def load_default_template(self):
        template = '''"""
VoidRay Game Template v2.5
Create your amazing game with the latest engine features!
"""

import voidray
from voidray import Scene, GameObject, Sprite, Vector2, Keys
from voidray.graphics.renderer import Color


class Player(Sprite):
    """Enhanced player with improved movement."""
    
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
    """Main game scene with v2.5 features."""
    
    def __init__(self):
        super().__init__("Game")
        
    def on_enter(self):
        super().on_enter()
        
        # Enable new engine features
        engine = voidray.get_engine()
        
        # Uncomment for 2.5D mode:
        # engine.set_rendering_mode("2.5D")
        
        # Enable performance optimizations
        engine.enable_performance_mode(True)
        
        # Create player at center of screen
        self.player = Player()
        self.player.transform.position = Vector2(400, 300)
        self.add_object(self.player)
        
        print("🎮 Game scene started - Use arrow keys to move!")
        print("📊 Press F3 to toggle debug overlay")
        print("🆕 Using VoidRay Engine v2.5 features")
        
    def update(self, delta_time):
        super().update(delta_time)
        
        # Check for exit key
        input_manager = voidray.get_engine().input_manager
        if input_manager.is_key_just_pressed(Keys.ESCAPE):
            voidray.stop()
        
        # Toggle debug overlay
        if input_manager.is_key_just_pressed(Keys.F3):
            engine = voidray.get_engine()
            if hasattr(engine, 'debug_overlay'):
                engine.debug_overlay.toggle()


def init_game():
    """Initialize the game - called once when engine starts."""
    scene = GameScene()
    voidray.register_scene("game", scene)
    voidray.set_scene("game")


def main():
    """Main entry point."""
    print("🚀 Starting VoidRay Game v2.5...")
    
    # Configure the engine
    voidray.configure(
        width=800, 
        height=600, 
        title="My VoidRay Game v2.5", 
        fps=60
    )
    
    # Register initialization callback
    voidray.on_init(init_game)
    
    # Start the engine
    voidray.start()
    
    # Show performance stats after game ends
    engine = voidray.get_engine()
    if hasattr(engine, 'get_engine_stats'):
        stats = engine.get_engine_stats()
        print("📊 Final Performance Stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")


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
            
    def show_auto_complete(self):
        """Show auto-completion suggestions safely."""
        if self.programming_assistant:
            self.programming_assistant.show_suggestions()
        else:
            self.log_message("⚠️ Programming assistant not yet initialized")
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About VoidRay Advanced Editor v2.5", 
                          "VoidRay Game Engine - Advanced Code Editor v2.5\n\n"
                          "🆕 NEW FEATURES:\n"
                          "🎨 2.5D rendering support\n"
                          "⚡ Performance mode and mobile optimization\n"
                          "🛠️ Integrated level editor\n"
                          "📊 Performance monitoring and profiling\n"
                          "🗃️ Advanced resource management\n"
                          "🌍 World streaming for large games\n\n"
                          "EXISTING FEATURES:\n"
                          "🤖 Programming assistant with auto-completion\n"
                          "📚 Built-in API reference and documentation\n"
                          "🌙 Dark theme optimized for coding\n"
                          "⚡ Real-time syntax checking\n"
                          "🔍 Advanced find and replace\n\n"
                          "Create amazing 2D and 2.5D games with VoidRay!")
        
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
    print("🚀 Starting VoidRay Advanced Code Editor v2.5...")
    print("🆕 Now with 2.5D support, performance tools, and level editor!")
    app = VoidRayGUIEditor()
    app.run()


if __name__ == "__main__":
    main()
