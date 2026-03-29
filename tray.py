"""
System tray — icon, context menu, and signals.
"""
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from config import APP_NAME, APP_VERSION
from startup import is_auto_start_enabled, enable_auto_start, disable_auto_start


class _Signals(QObject):
    show_popup    = pyqtSignal()
    show_settings = pyqtSignal()
    quit_app      = pyqtSignal()


def _make_icon() -> QIcon:
    px = QPixmap(64, 64); px.fill(Qt.transparent)
    p = QPainter(px); p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QBrush(QColor("#7c5cfc"))); p.setPen(Qt.NoPen)
    p.drawEllipse(2, 2, 60, 60)
    p.setFont(QFont("Segoe UI", 28, QFont.Bold))
    p.setPen(QColor("white")); p.drawText(px.rect(), Qt.AlignCenter, "⚡")
    p.end(); return QIcon(px)


_MENU_SS = """
QMenu {
    background:#141526; color:#f0f0ff;
    border:1px solid #2a2d55; border-radius:10px;
    padding:6px; font-family:'Segoe UI',sans-serif; font-size:12px;
}
QMenu::item { padding:8px 24px 8px 12px; border-radius:5px; }
QMenu::item:selected { background:#7c5cfc; color:white; }
QMenu::separator { height:1px; background:#2a2d55; margin:4px 8px; }
"""


class SystemTray:
    def __init__(self, app: QApplication):
        self.app = app
        self.signals = _Signals()
        self._build()

    def _build(self):
        self.icon = QSystemTrayIcon(_make_icon(), self.app)
        self.icon.setToolTip(f"{APP_NAME} v{APP_VERSION}")

        menu = QMenu(); menu.setStyleSheet(_MENU_SS)

        a = QAction("⚡  Open Enhancer", self.app)
        a.triggered.connect(self.signals.show_popup.emit); menu.addAction(a)

        s = QAction("⚙  Settings", self.app)
        s.triggered.connect(self.signals.show_settings.emit); menu.addAction(s)

        menu.addSeparator()

        self._auto_act = QAction("", self.app)
        self._refresh_auto_label()
        self._auto_act.triggered.connect(self._toggle_auto)
        menu.addAction(self._auto_act)

        menu.addSeparator()

        info = QAction(f"  {APP_NAME} v{APP_VERSION}  •  Ctrl+Shift+E", self.app)
        info.setEnabled(False); menu.addAction(info)

        menu.addSeparator()

        q = QAction("❌  Quit", self.app)
        q.triggered.connect(self.signals.quit_app.emit); menu.addAction(q)

        self.icon.setContextMenu(menu)
        self.icon.activated.connect(self._activated)

    def _activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.signals.show_popup.emit()

    def _toggle_auto(self):
        (disable_auto_start if is_auto_start_enabled() else enable_auto_start)()
        self._refresh_auto_label()

    def _refresh_auto_label(self):
        on = is_auto_start_enabled()
        self._auto_act.setText("✅  Start with Windows" if on else "⬜  Start with Windows")

    def show(self): self.icon.show()

    def show_message(self, title: str, msg: str):
        self.icon.showMessage(title, msg, QSystemTrayIcon.Information, 3000)
