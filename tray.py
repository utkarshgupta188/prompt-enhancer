"""
System tray module.
Creates a system tray icon with context menu options.
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QFont, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from config import APP_NAME, APP_VERSION
from startup import is_auto_start_enabled, enable_auto_start, disable_auto_start


class TraySignals(QObject):
    """Signals emitted by the tray for inter-component communication."""
    show_popup = pyqtSignal()
    quit_app = pyqtSignal()


def _create_tray_icon() -> QIcon:
    """Creates a simple programmatic tray icon (purple lightning bolt)."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)

    # Background circle
    painter.setBrush(QBrush(QColor("#7c5cfc")))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 60, 60)

    # Lightning bolt symbol
    painter.setPen(QPen(QColor("white"), 2))
    painter.setBrush(QBrush(QColor("white")))
    font = QFont("Segoe UI", 28, QFont.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "⚡")

    painter.end()
    return QIcon(pixmap)


class SystemTray:
    """
    Manages the system tray icon and its context menu.
    """

    def __init__(self, app: QApplication):
        self.app = app
        self.signals = TraySignals()
        self._setup_tray()

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(_create_tray_icon(), self.app)
        self.tray_icon.setToolTip(f"{APP_NAME} v{APP_VERSION}")

        # Context menu
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1b2e;
                color: #e8e9f3;
                border: 1px solid #3a3d6b;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QMenu::item {
                padding: 8px 24px 8px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #7c5cfc;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3a3d6b;
                margin: 4px 8px;
            }
        """)

        # Show popup action
        show_action = QAction("⚡ Open Enhancer", self.app)
        show_action.triggered.connect(self.signals.show_popup.emit)
        menu.addAction(show_action)

        menu.addSeparator()

        # Auto-start toggle
        self.autostart_action = QAction("", self.app)
        self._update_autostart_label()
        self.autostart_action.triggered.connect(self._toggle_autostart)
        menu.addAction(self.autostart_action)

        menu.addSeparator()

        # About info (disabled, just for display)
        about_action = QAction(f"  {APP_NAME} v{APP_VERSION}", self.app)
        about_action.setEnabled(False)
        menu.addAction(about_action)

        hotkey_action = QAction("  Hotkey: Ctrl+Shift+E", self.app)
        hotkey_action.setEnabled(False)
        menu.addAction(hotkey_action)

        menu.addSeparator()

        # Quit action
        quit_action = QAction("❌ Quit", self.app)
        quit_action.triggered.connect(self.signals.quit_app.emit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

        # Double-click opens popup
        self.tray_icon.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.signals.show_popup.emit()

    def _toggle_autostart(self):
        if is_auto_start_enabled():
            disable_auto_start()
        else:
            enable_auto_start()
        self._update_autostart_label()

    def _update_autostart_label(self):
        if is_auto_start_enabled():
            self.autostart_action.setText("✅ Start with Windows (On)")
        else:
            self.autostart_action.setText("⬜ Start with Windows (Off)")

    def show(self):
        self.tray_icon.show()

    def show_message(self, title: str, message: str):
        self.tray_icon.showMessage(
            title, message,
            QSystemTrayIcon.Information,
            3000
        )
