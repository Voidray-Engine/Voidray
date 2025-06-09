
"""
VoidRay Engine Error Dialog
Displays fatal error messages in a popup window when the engine crashes.
"""

import pygame
import sys
import traceback
from typing import Optional
from ..math.vector2 import Vector2


class ErrorDialog:
    """
    A simple error dialog window for displaying fatal errors.
    """

    def __init__(self, width: int = 500, height: int = 300):
        """
        Initialize the error dialog.

        Args:
            width: Dialog width in pixels
            height: Dialog height in pixels
        """
        self.width = width
        self.height = height
        self.screen = None
        self.clock = None
        self.font = None
        self.title_font = None
        self.running = False

    def show_error(self, error_title: str, error_message: str, details: Optional[str] = None):
        """
        Show the error dialog with the given message.

        Args:
            error_title: Title of the error (e.g., "Fatal Error")
            error_message: Main error message
            details: Optional detailed error information
        """
        try:
            # Initialize pygame if not already done
            if not pygame.get_init():
                pygame.init()

            # Create error dialog window
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("VoidRay Engine - Error")
            self.clock = pygame.time.Clock()

            # Initialize fonts
            pygame.font.init()
            self.title_font = pygame.font.Font(None, 32)
            self.font = pygame.font.Font(None, 20)

            self.running = True
            self._run_dialog_loop(error_title, error_message, details)

        except Exception as e:
            # If the dialog itself fails, print to console
            print(f"ERROR DIALOG FAILED: {e}")
            print(f"Original Error: {error_title} - {error_message}")
            if details:
                print(f"Details: {details}")

    def _run_dialog_loop(self, error_title: str, error_message: str, details: Optional[str]):
        """Run the dialog event loop."""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if clicked on OK button
                    mouse_pos = pygame.mouse.get_pos()
                    ok_button_rect = pygame.Rect(self.width//2 - 40, self.height - 60, 80, 30)
                    if ok_button_rect.collidepoint(mouse_pos):
                        self.running = False

            # Clear screen
            self.screen.fill((40, 40, 40))

            # Draw dialog
            self._draw_dialog(error_title, error_message, details)

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

        # Clean up
        pygame.quit()

    def _draw_dialog(self, error_title: str, error_message: str, details: Optional[str]):
        """Draw the error dialog content."""
        margin = 20
        y_pos = margin

        # Draw title
        title_surface = self.title_font.render(error_title, True, (255, 100, 100))
        title_rect = title_surface.get_rect()
        title_rect.centerx = self.width // 2
        title_rect.y = y_pos
        self.screen.blit(title_surface, title_rect)
        y_pos += title_rect.height + 20

        # Draw main error message
        message_lines = self._wrap_text(error_message, self.width - 2 * margin)
        for line in message_lines:
            line_surface = self.font.render(line, True, (255, 255, 255))
            line_rect = line_surface.get_rect()
            line_rect.x = margin
            line_rect.y = y_pos
            self.screen.blit(line_surface, line_rect)
            y_pos += line_rect.height + 5

        # Draw details if provided
        if details:
            y_pos += 10
            details_title = self.font.render("Details:", True, (200, 200, 200))
            self.screen.blit(details_title, (margin, y_pos))
            y_pos += details_title.get_height() + 5

            details_lines = self._wrap_text(details, self.width - 2 * margin)[:8]  # Limit lines
            for line in details_lines:
                line_surface = self.font.render(line, True, (180, 180, 180))
                line_rect = line_surface.get_rect()
                line_rect.x = margin
                line_rect.y = y_pos
                self.screen.blit(line_surface, line_rect)
                y_pos += line_rect.height + 2

        # Draw OK button
        ok_button_rect = pygame.Rect(self.width//2 - 40, self.height - 60, 80, 30)
        pygame.draw.rect(self.screen, (100, 100, 100), ok_button_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), ok_button_rect, 2)

        ok_text = self.font.render("OK", True, (255, 255, 255))
        ok_text_rect = ok_text.get_rect()
        ok_text_rect.center = ok_button_rect.center
        self.screen.blit(ok_text, ok_text_rect)

        # Draw instructions
        instructions = self.font.render("Press ESC, ENTER, or click OK to close", True, (150, 150, 150))
        instructions_rect = instructions.get_rect()
        instructions_rect.centerx = self.width // 2
        instructions_rect.y = self.height - 20
        self.screen.blit(instructions, instructions_rect)

    def _wrap_text(self, text: str, max_width: int) -> list:
        """Wrap text to fit within the specified width."""
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_surface = self.font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines


# Global error dialog instance
_error_dialog = ErrorDialog()


def show_fatal_error(error_title: str = "Fatal Error", error_message: str = "An unexpected error occurred", 
                    exception: Optional[Exception] = None):
    """
    Show a fatal error dialog.

    Args:
        error_title: Title of the error dialog
        error_message: Main error message to display
        exception: Optional exception object for detailed information
    """
    details = None
    if exception:
        details = f"{type(exception).__name__}: {str(exception)}"
        # Add traceback if available
        tb_lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
        if tb_lines:
            details += "\n" + "".join(tb_lines[-3:])  # Show last 3 lines of traceback

    _error_dialog.show_error(error_title, error_message, details)
