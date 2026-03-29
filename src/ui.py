"""
Popup UI — Professional Native Desktop Aesthetic (Fluent/VSCode style).
"""
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QPushButton, QFrame, QButtonGroup, QDesktopWidget,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

from config import MODES
from enhancer import enhance_text
import pyperclip
from clipboard_handler import paste_text

W, H = 640, 560
OPACITY = 0.98

SS = """
QWidget#Popup {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 12px;
}
QLabel#title {
    color: #F8FAFC; font-size: 16px; font-weight: 600;
    font-family: 'Jost', 'Segoe UI', system-ui, sans-serif;
}
QLabel#hint {
    color: #94A3B8; font-size: 12px; font-family: 'Jost', 'Segoe UI', system-ui, sans-serif;
}
QLabel#err {
    color: #EF4444; font-size: 13px; font-family: 'Jost', 'Segoe UI', system-ui, sans-serif;
    padding: 4px 8px; background: rgba(239, 68, 68, 0.1); border-radius: 4px;
}

QTextEdit {
    background: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px;
    font-size: 14px;
    font-family: 'Jost', 'Segoe UI', system-ui, sans-serif;
    line-height: 1.5;
    selection-background-color: #3B82F6;
    selection-color: white;
}
QTextEdit:focus {
    border: 1px solid #3B82F6;
}

QPushButton#ico {
    background: transparent; color: #94A3B8; border: none;
    border-radius: 6px; font-size: 16px; padding: 6px;
}
QPushButton#ico:hover { background: #1E293B; color: #F8FAFC; }

QPushButton#mode {
    background: #1E293B; color: #94A3B8; border: 1px solid #334155;
    border-radius: 6px; padding: 6px 14px; font-size: 13px;
    font-family: 'Jost', 'Segoe UI', system-ui, sans-serif; font-weight: 500;
}
QPushButton#mode:hover { background: #334155; color: #F8FAFC; }
QPushButton#mode:checked { background: #3B82F6; color: #ffffff; border-color: #3B82F6; }

QPushButton#primary {
    background: #3B82F6; color: #ffffff; border: none;
    border-radius: 6px; padding: 8px 20px; font-size: 14px; font-weight: 600;
    font-family: 'Jost', 'Segoe UI', system-ui, sans-serif;
}
QPushButton#primary:hover { background: #2563EB; }
QPushButton#primary:disabled { background: #1E293B; color: #64748B; }

QPushButton#secondary {
    background: #334155; color: #F8FAFC; border: 1px solid #475569;
    border-radius: 6px; padding: 8px 20px; font-size: 14px; font-weight: 500;
    font-family: 'Jost', 'Segoe UI', system-ui, sans-serif;
}
QPushButton#secondary:hover { background: #475569; color: #ffffff; }
QPushButton#secondary:disabled { background: #1E293B; color: #64748B; border-color: #334155; }

QScrollBar:vertical { background: transparent; width: 8px; }
QScrollBar::handle:vertical { background: #475569; border-radius: 4px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #64748B; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


class Worker(QThread):
    done  = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self, text, mode):
        super().__init__(); self.text = text; self.mode = mode
    def run(self):
        try:    self.done.emit(enhance_text(self.text, self.mode))
        except Exception as e: self.error.emit(str(e))


class EnhancerPopup(QWidget):
    open_settings = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.worker: Worker | None = None
        self._drag = None
        self._build()
        self._shortcuts()

    def _build(self):
        self.setObjectName("Popup")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setFixedSize(W, H)
        self.setWindowOpacity(OPACITY)
        self.setStyleSheet(SS)

        lo = QVBoxLayout(self)
        lo.setContentsMargins(24, 24, 24, 24)
        lo.setSpacing(12)

        # ── Header ──
        hdr = QHBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 8)
        title = QLabel("✨ Prompt Enhancer"); title.setObjectName("title")
        hdr.addWidget(title); hdr.addStretch()

        self.err_lbl = QLabel(""); self.err_lbl.setObjectName("err"); self.err_lbl.hide()
        hdr.addWidget(self.err_lbl)

        set_btn = QPushButton("⚙"); set_btn.setObjectName("ico")
        set_btn.setCursor(Qt.PointingHandCursor)
        set_btn.clicked.connect(self.open_settings.emit)
        hdr.addWidget(set_btn)

        cls_btn = QPushButton("✕"); cls_btn.setObjectName("ico")
        cls_btn.setCursor(Qt.PointingHandCursor)
        cls_btn.clicked.connect(self.hide)
        hdr.addWidget(cls_btn)
        lo.addLayout(hdr)

        # ── Input Area ──
        self.inp = QTextEdit()
        self.inp.setPlaceholderText("Type your prompt here or select text to auto-enhance...")
        lo.addWidget(self.inp)

        # ── Modes / Middle Toolbar ──
        mid = QHBoxLayout()
        mid.setContentsMargins(0, 4, 0, 4)
        
        self.go_btn = QPushButton("⚡ Enhance"); self.go_btn.setObjectName("primary")
        self.go_btn.setCursor(Qt.PointingHandCursor)
        self.go_btn.clicked.connect(self._enhance)
        mid.addWidget(self.go_btn)

        mid.addStretch()

        # Mode Buttons
        self._pills = QButtonGroup(self); self._pills.setExclusive(True)
        pill_layout = QHBoxLayout(); pill_layout.setSpacing(6)
        for i, m in enumerate(MODES.keys()):
            b = QPushButton(m); b.setObjectName("mode")
            b.setCheckable(True); b.setCursor(Qt.PointingHandCursor)
            self._pills.addButton(b, i)
            pill_layout.addWidget(b)
        self._pills.button(0).setChecked(True)
        mid.addLayout(pill_layout)
        
        lo.addLayout(mid)

        # ── Output Area ──
        self.out = QTextEdit()
        self.out.setReadOnly(True)
        self.out.setPlaceholderText("Enhanced text will appear here. Press Replace or Copy when done.")
        lo.addWidget(self.out)

        # ── Footer ──
        ftr = QHBoxLayout()
        ftr.setContentsMargins(0, 8, 0, 0)
        self.sta = QLabel(""); self.sta.setObjectName("hint")
        ftr.addWidget(self.sta); ftr.addStretch()
        
        hint = QLabel("Ctrl+Enter to Replace  •  Ctrl+C to Copy")
        hint.setObjectName("hint"); ftr.addWidget(hint)
        ftr.addSpacing(16)
        
        self.copy_btn = QPushButton("📋 Copy"); self.copy_btn.setObjectName("secondary")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_out)
        self.copy_btn.setEnabled(False)
        ftr.addWidget(self.copy_btn)

        self.rep_btn = QPushButton("↵ Replace"); self.rep_btn.setObjectName("primary")
        self.rep_btn.setCursor(Qt.PointingHandCursor)
        self.rep_btn.clicked.connect(self._replace)
        self.rep_btn.setEnabled(False)
        ftr.addWidget(self.rep_btn)
        
        lo.addLayout(ftr)

    def _shortcuts(self):
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(
            lambda: self._enhance() if not self.inp.hasFocus() else None)
        # Add modifier shortcut so Enter in text field works
        QShortcut(QKeySequence("Shift+Return"), self).activated.connect(self._enhance)
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self._replace)
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.hide)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and self._drag:
            self.move(e.globalPos() - self._drag)
    def mouseReleaseEvent(self, e):
        self._drag = None

    def show_popup(self, text: str = ""):
        self.err_lbl.hide(); self.sta.setText("")
        self.out.clear()
        self.rep_btn.setEnabled(False); self.copy_btn.setEnabled(False)
        self.go_btn.setEnabled(True); self.go_btn.setText("⚡ Enhance")
        
        sc = QDesktopWidget().availableGeometry()
        self.move((sc.width() - W) // 2, (sc.height() - H) // 2)
        self.show(); self.activateWindow(); self.raise_()
        
        if text: 
            self.inp.setPlainText(text)
            self._enhance() # Auto-enhance!
        else: 
            self.inp.clear()
            self.inp.setFocus()

    def _mode(self) -> str:
        idx = self._pills.checkedId()
        return list(MODES.keys())[max(0, idx)]

    def _enhance(self):
        txt = self.inp.toPlainText().strip()
        if not txt:
            self.err_lbl.setText("Text is empty."); self.err_lbl.show(); return
        self.err_lbl.hide()
        self.sta.setText("Generating...")
        self.go_btn.setEnabled(False); self.go_btn.setText("⏳ Enhancing...")
        self.out.clear()
        self.rep_btn.setEnabled(False); self.copy_btn.setEnabled(False)
        self.worker = Worker(txt, self._mode())
        self.worker.done.connect(self._ok)
        self.worker.error.connect(self._err)
        self.worker.start()

    def _ok(self, res: str):
        self.out.setPlainText(res)
        self.go_btn.setEnabled(True); self.go_btn.setText("⚡ Enhance")
        self.sta.setText("✨ Ready")
        self.rep_btn.setEnabled(True); self.copy_btn.setEnabled(True)
        self.rep_btn.setFocus()

    def _err(self, msg: str):
        self.sta.setText(""); self.err_lbl.setText(msg); self.err_lbl.show()
        self.go_btn.setEnabled(True); self.go_btn.setText("⚡ Enhance")

    def _replace(self):
        txt = self.out.toPlainText().strip()
        if txt:
            self.hide() # hide first so window focus returns
            QTimer.singleShot(200, lambda: paste_text(txt))

    def _copy_out(self):
        txt = self.out.toPlainText().strip()
        if txt: 
            pyperclip.copy(txt)
            self.copy_btn.setText("✅ Copied")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("📋 Copy"))

    def refresh_badge(self):
        pass # Badge removed in minimalist UI
