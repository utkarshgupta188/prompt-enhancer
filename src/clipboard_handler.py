"""
Clipboard handling module.
Captures selected text from any application using clipboard simulation.
"""

import time
import pyperclip
from pynput.keyboard import Controller, Key


keyboard_controller = Controller()


def capture_selected_text() -> str:
    """
    Captures the currently selected text from any application.

    Simulates Ctrl+C to copy selected text to clipboard,
    reads the clipboard, and returns the text.
    """
    # Save current clipboard content
    try:
        original_clipboard = pyperclip.paste()
    except Exception:
        original_clipboard = ""

    # Clear clipboard
    try:
        pyperclip.copy("")
    except Exception:
        pass

    # Small delay to ensure focus is on the right window
    time.sleep(0.05)

    # Force release Shift and Ctrl just in case the user is still holding them
    from pynput.keyboard import Key
    keyboard_controller.release(Key.shift)
    keyboard_controller.release(Key.shift_l)
    keyboard_controller.release(Key.shift_r)
    keyboard_controller.release('e')
    keyboard_controller.release('E')

    time.sleep(0.05)
    
    # Simulate Ctrl+C
    keyboard_controller.press(Key.ctrl)
    keyboard_controller.press('c')
    keyboard_controller.release('c')
    keyboard_controller.release(Key.ctrl)

    # Wait for clipboard to be populated
    time.sleep(0.15)

    # Read the clipboard
    try:
        selected_text = pyperclip.paste()
    except Exception:
        selected_text = ""

    # If clipboard is still empty, the user didn't have text selected
    if not selected_text:
        # Restore original clipboard
        try:
            pyperclip.copy(original_clipboard)
        except Exception:
            pass
        return ""

    return selected_text


def paste_text(text: str) -> None:
    """
    Pastes the given text into the currently focused application.

    Copies text to clipboard and simulates Ctrl+V.
    """
    try:
        pyperclip.copy(text)
    except Exception:
        return

    time.sleep(0.05)

    # Simulate Ctrl+V
    keyboard_controller.press(Key.ctrl)
    keyboard_controller.press('v')
    keyboard_controller.release('v')
    keyboard_controller.release(Key.ctrl)

    time.sleep(0.05)
