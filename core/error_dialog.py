"""
VoidRay Error Dialog System
Professional error reporting and user-friendly error dialogs.
"""

import traceback
import sys
from typing import Optional


def show_fatal_error(title: str, message: str, exception: Optional[Exception] = None):
    """
    Show a fatal error dialog to the user.

    Args:
        title: Error dialog title
        message: User-friendly error message
        exception: Optional exception that caused the error
    """
    print(f"\n{'='*60}")
    print(f"FATAL ERROR: {title}")
    print(f"{'='*60}")
    print(f"Message: {message}")

    if exception:
        print(f"Exception: {type(exception).__name__}: {str(exception)}")
        print("\nDetailed Traceback:")
        traceback.print_exc()

    print(f"{'='*60}")
    print("The engine will now exit. Please check the error details above.")
    print("If this is a bug, please report it to the VoidRay development team.")
    print(f"{'='*60}\n")

    # Try to use tkinter for a graphical dialog
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()  # Hide the root window

        detailed_message = message
        if exception:
            detailed_message += f"\n\nTechnical Details:\n{type(exception).__name__}: {str(exception)}"

        messagebox.showerror(title, detailed_message)
        root.destroy()

    except ImportError:
        # Tkinter not available, console output is sufficient
        pass
    except Exception as dialog_error:
        print(f"Could not show graphical error dialog: {dialog_error}")


def show_warning_dialog(title: str, message: str):
    """
    Show a warning dialog to the user.

    Args:
        title: Warning dialog title
        message: Warning message
    """
    print(f"\nWARNING: {title}")
    print(f"Message: {message}\n")

    # Try to use tkinter for a graphical dialog
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()

        messagebox.showwarning(title, message)
        root.destroy()

    except ImportError:
        pass
    except Exception:
        pass


def log_error(error_type: str, message: str, exception: Optional[Exception] = None):
    """
    Log an error without showing a dialog.

    Args:
        error_type: Type of error
        message: Error message
        exception: Optional exception
    """
    from .logger import engine_logger

    log_message = f"{error_type}: {message}"
    if exception:
        log_message += f" - {type(exception).__name__}: {str(exception)}"

    engine_logger.error(log_message)

    if exception:
        # Log the full traceback
        import io
        trace_stream = io.StringIO()
        traceback.print_exc(file=trace_stream)
        engine_logger.debug(f"Traceback:\n{trace_stream.getvalue()}")