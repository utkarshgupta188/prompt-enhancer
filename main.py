"""
Prompt Enhancer — Main Entry Point
Run without a CMD window: double-click run.pyw
"""
import sys
if sys.platform == "win32":
    import ctypes
    # Immediately hide the console window if it exists
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
import keyboard

from ui import EnhancerPopup
from tray import SystemTray
from settings_dialog import SettingsDialog
from clipboard_handler import capture_selected_text
from config import HOTKEY_COMBINATION, APP_NAME


class _Bridge(QObject):
    """Thread-safe bridge: keyboard thread → Qt main thread."""
    triggered = pyqtSignal()


class PromptEnhancerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setQuitOnLastWindowClosed(False)

        self._bridge = _Bridge()
        self._bridge.triggered.connect(self._on_hotkey)

        self.popup   = EnhancerPopup()
        self.tray    = SystemTray(self.app)
        self.settings_dlg = SettingsDialog()

        # wire signals
        self.tray.signals.show_popup.connect(lambda: self.popup.show_popup(""))
        self.tray.signals.show_settings.connect(self._show_settings)
        self.tray.signals.quit_app.connect(self._quit)
        self.popup.open_settings.connect(self._show_settings)
        self.settings_dlg.saved.connect(self.popup.refresh_badge)

        keyboard.add_hotkey(HOTKEY_COMBINATION, self._bridge.triggered.emit, suppress=True)

    def _on_hotkey(self):
        selected = capture_selected_text()
        self.popup.show_popup(text=selected)

    def _show_settings(self):
        self.settings_dlg.show_centered()

    def _quit(self):
        keyboard.unhook_all()
        self.app.quit()

    def run(self) -> int:
        self.tray.show()
        self.tray.show_message(
            "Prompt Enhancer",
            "Running. Press Ctrl+Shift+E to enhance text."
        )
        return self.app.exec_()


def main():
    app = PromptEnhancerApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
