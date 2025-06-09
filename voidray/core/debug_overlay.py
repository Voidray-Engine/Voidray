"""
VoidRay Debug Overlay
Provides real-time debugging information and performance metrics.
"""

from ..math.vector2 import Vector2
from ..utils.color import Color


class DebugOverlay:
    """
    Debug overlay that displays engine statistics and performance metrics.
    """

    def __init__(self, engine):
        self.engine = engine
        self.enabled = False
        self.font_size = 14
        self.background_alpha = 128

    def toggle(self):
        """Toggle the debug overlay on/off."""
        self.enabled = not self.enabled

    def render(self, renderer):
        """Render the debug overlay."""
        if not self.enabled:
            return

        # Get engine statistics
        stats = self.engine.get_engine_stats()
        fps = self.engine.get_fps()
        delta_time = self.engine.get_delta_time()
        scene_objects = self.engine.get_scene_object_count()

        # Render semi-transparent background
        overlay_height = 150
        renderer.draw_rect(
            Vector2(10, 10), 
            Vector2(250, overlay_height), 
            (0, 0, 0, self.background_alpha), 
            filled=True, 
            layer='ui'
        )

        # Render debug text
        y_offset = 20
        line_height = 18

        debug_lines = [
            f"FPS: {fps:.1f}",
            f"Delta Time: {delta_time*1000:.1f}ms",
            f"Frames Rendered: {stats['frames_rendered']}",
            f"Scene Objects: {scene_objects}",
            f"Physics Objects: {stats['physics_objects']}",
            f"Rendering Mode: {stats.get('rendering_mode', 'Unknown')}",
            f"Engine State: {self.engine.state_manager.current_state.name.lower() if self.engine.state_manager.current_state else 'unknown'}"
        ]

        for i, line in enumerate(debug_lines):
            renderer.draw_text(
                line,
                Vector2(20, y_offset + i * line_height),
                Color.WHITE,
                self.font_size,
                layer='ui'
            )