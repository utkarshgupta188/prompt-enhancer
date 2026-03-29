"""
Prompt Enhancer — Main Entry Point
===================================
A global AI-powered prompt enhancer for Windows.

Hotkey: Ctrl+Shift+E — Captures selected text, enhances it, replaces it.

Usage:
    python main.py          (with console)
    pythonw main.py         (no console)
"""

import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

import keyboard  # global hotkey listener

from ui import EnhancerPopup
from tray import SystemTray
from clipboard_handler import capture_selected_text
from config import HOTKEY_COMBINATION, APP_NAME


class _HotkeyBridge(QObject):
    """
    Thread-safe signal bridge between the keyboard listener thread
    and the Qt main thread.

    Qt automatically uses a queued connection when a signal is emitted
    from a non-Qt thread to a slot running in the main thread, which
    makes this safe without any manual locking.
    """
    triggered = pyqtSignal()


class PromptEnhancerApp:
    """
    Main application controller.
    Wires together the UI popup, system tray, and global hotkey.
    """

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setQuitOnLastWindowClosed(False)  # Keep running in tray

        # ── Thread-safe bridge for hotkey → main thread ──
        self._hotkey_bridge = _HotkeyBridge()
        self._hotkey_bridge.triggered.connect(self._on_hotkey_triggered)

        # ── Components ──
        self.popup = EnhancerPopup()
        self.tray = SystemTray(self.app)

        # ── Signal Wiring ──
        self.tray.signals.show_popup.connect(self._show_popup_empty)
        self.tray.signals.quit_app.connect(self._quit)

        # ── Global Hotkey ──
        self._setup_hotkey()

    def _setup_hotkey(self):
        """
        Registers the global hotkey using the `keyboard` library.
        The listener runs in a daemon thread; we emit a Qt signal to
        safely cross back to the main thread.
        """
        bridge = self._hotkey_bridge

        def hotkey_handler():
            bridge.triggered.emit()

        keyboard.add_hotkey(HOTKEY_COMBINATION, hotkey_handler, suppress=True)

    def _on_hotkey_triggered(self):
        """Called on the Qt main thread when the global hotkey fires."""
        selected = capture_selected_text()
        self.popup.show_popup(initial_text=selected)

    def _show_popup_empty(self):
        """Opens the popup without pre-filled text (triggered from tray)."""
        self.popup.show_popup(initial_text="")

    def _quit(self):
        """Cleanly shuts down the application."""
        keyboard.unhook_all()
        self.app.quit()

    def run(self) -> int:
        """Starts the application event loop."""
        self.tray.show()
        self.tray.show_message(
            "Prompt Enhancer",
            "Running in background. Press Ctrl+Shift+E to enhance text."
        )
        return self.app.exec_()


def main():
    app = PromptEnhancerApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
