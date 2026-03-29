"""
Popup UI module.
Modern, frameless, dark-themed overlay window for text enhancement.
"""

import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QPushButton, QComboBox, QFrame,
    QScrollArea,
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QPoint, QTimer,
)
from PyQt5.QtGui import QFont, QColor, QKeySequence
from PyQt5.QtWidgets import QShortcut

from config import MODES, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_OPACITY, MAX_HISTORY_ITEMS
from enhancer import enhance_text, get_active_provider_label
from clipboard_handler import paste_text


# ──────────────────────────────────────────────────────
# Style Constants
# ──────────────────────────────────────────────────────
COLORS = {
    "bg": "#1a1b2e",
    "surface": "#242640",
    "surface_light": "#2d2f52",
    "border": "#3a3d6b",
    "text": "#e8e9f3",
    "text_dim": "#8b8da3",
    "accent": "#7c5cfc",
    "accent_hover": "#9178ff",
    "accent_glow": "rgba(124, 92, 252, 0.3)",
    "success": "#4ade80",
    "success_hover": "#22c55e",
    "error": "#f87171",
    "error_bg": "rgba(248, 113, 113, 0.1)",
}

STYLESHEET = f"""
    QWidget#EnhancerPopup {{
        background-color: {COLORS["bg"]};
        border: 1px solid rgba(124, 92, 252, 0.5);
        border-radius: 16px;
    }}

    QLabel#titleLabel {{
        color: {COLORS["text"]};
        font-size: 18px;
        font-weight: 700;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        padding: 0px;
    }}

    QLabel#subtitleLabel {{
        color: {COLORS["text_dim"]};
        font-size: 11px;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        padding: 0px;
    }}

    QLabel#providerLabel {{
        color: {COLORS["accent"]};
        font-size: 10px;
        font-weight: 600;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        background-color: rgba(124, 92, 252, 0.12);
        border: 1px solid rgba(124, 92, 252, 0.35);
        border-radius: 4px;
        padding: 1px 6px;
    }}

    QLabel#sectionLabel {{
        color: {COLORS["text_dim"]};
        font-size: 11px;
        font-weight: 600;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 0px;
    }}

    QLabel#statusLabel {{
        color: {COLORS["text_dim"]};
        font-size: 11px;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        padding: 2px 0px;
    }}

    QLabel#errorLabel {{
        color: {COLORS["error"]};
        font-size: 11px;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        background-color: {COLORS["error_bg"]};
        border-radius: 6px;
        padding: 6px 10px;
    }}

    QTextEdit {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 12px;
        font-size: 13px;
        font-family: 'Cascadia Code', 'Consolas', 'Segoe UI', monospace;
        selection-background-color: {COLORS["accent"]};
        selection-color: white;
    }}

    QTextEdit:focus {{
        border: 1px solid {COLORS["accent"]};
    }}

    QComboBox {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        min-width: 140px;
    }}

    QComboBox:hover {{
        border: 1px solid {COLORS["accent"]};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {COLORS["text_dim"]};
        margin-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {COLORS["surface"]};
        color: {COLORS["text"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 4px;
        selection-background-color: {COLORS["accent"]};
        selection-color: white;
        outline: none;
    }}

    QPushButton#enhanceBtn {{
        background-color: {COLORS["accent"]};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: 600;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }}

    QPushButton#enhanceBtn:hover {{
        background-color: {COLORS["accent_hover"]};
    }}

    QPushButton#enhanceBtn:pressed {{
        background-color: {COLORS["accent"]};
    }}

    QPushButton#enhanceBtn:disabled {{
        background-color: {COLORS["surface_light"]};
        color: {COLORS["text_dim"]};
    }}

    QPushButton#replaceBtn {{
        background-color: transparent;
        color: {COLORS["success"]};
        border: 1px solid {COLORS["success"]};
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: 600;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }}

    QPushButton#replaceBtn:hover {{
        background-color: rgba(74, 222, 128, 0.1);
        border-color: {COLORS["success_hover"]};
        color: {COLORS["success_hover"]};
    }}

    QPushButton#replaceBtn:disabled {{
        background-color: transparent;
        color: {COLORS["text_dim"]};
        border-color: {COLORS["surface_light"]};
    }}

    QPushButton#closeBtn {{
        background-color: transparent;
        color: {COLORS["text_dim"]};
        border: none;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 400;
        padding: 0px;
        min-width: 28px;
        max-width: 28px;
        min-height: 28px;
        max-height: 28px;
    }}

    QPushButton#closeBtn:hover {{
        background-color: {COLORS["surface_light"]};
        color: {COLORS["error"]};
    }}

    QPushButton#historyBtn {{
        background-color: transparent;
        color: {COLORS["text_dim"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 12px;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }}

    QPushButton#historyBtn:hover {{
        border-color: {COLORS["accent"]};
        color: {COLORS["accent"]};
    }}

    QPushButton#copyBtn {{
        background-color: transparent;
        color: {COLORS["text_dim"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 11px;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }}

    QPushButton#copyBtn:hover {{
        border-color: {COLORS["accent"]};
        color: {COLORS["accent"]};
    }}

    QFrame#divider {{
        background-color: {COLORS["border"]};
        max-height: 1px;
        min-height: 1px;
    }}

    QFrame#historyItem {{
        background-color: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 8px;
    }}

    QFrame#historyItem:hover {{
        border-color: {COLORS["accent"]};
    }}

    QScrollArea {{
        background: transparent;
        border: none;
    }}

    QScrollBar:vertical {{
        background: {COLORS["surface"]};
        width: 6px;
        border-radius: 3px;
    }}

    QScrollBar::handle:vertical {{
        background: {COLORS["border"]};
        border-radius: 3px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {COLORS["accent"]};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""


# ──────────────────────────────────────────────────────
# Worker Thread for AI Enhancement
# ──────────────────────────────────────────────────────
class EnhanceWorker(QThread):
    """Background thread that calls the AI enhancement API."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text: str, mode: str):
        super().__init__()
        self.text = text
        self.mode = mode

    def run(self):
        try:
            result = enhance_text(self.text, self.mode)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ──────────────────────────────────────────────────────
# Main Popup Window
# ──────────────────────────────────────────────────────
class EnhancerPopup(QWidget):
    """
    Frameless, always-on-top popup window for text enhancement.
    """

    def __init__(self):
        super().__init__()
        self.history: list[dict] = []
        self.worker: EnhanceWorker | None = None
        self._drag_pos = None
        self._history_visible = False
        self._init_ui()
        self._setup_shortcuts()

    # ──────────────────────────────────────────────
    # UI Setup
    # ──────────────────────────────────────────────
    def _init_ui(self):
        self.setObjectName("EnhancerPopup")
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        # NOTE: WA_TranslucentBackground is intentionally NOT set.
        # It causes UpdateLayeredWindowIndirect failures on Windows
        # with certain DPI/multi-monitor configurations.
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowOpacity(WINDOW_OPACITY)
        self.setStyleSheet(STYLESHEET)

        # Main container (fills the whole window)
        container = QWidget(self)
        container.setObjectName("EnhancerPopup")
        container.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(12)

        # ─── Title Bar ───
        title_bar = QHBoxLayout()
        title_bar.setSpacing(0)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title_label = QLabel("⚡ Prompt Enhancer")
        title_label.setObjectName("titleLabel")
        title_col.addWidget(title_label)

        # Row: subtitle + provider badge
        sub_row = QHBoxLayout()
        sub_row.setSpacing(8)
        sub_row.setContentsMargins(0, 0, 0, 0)

        subtitle = QLabel("Select text → Enhance → Replace")
        subtitle.setObjectName("subtitleLabel")
        sub_row.addWidget(subtitle)

        self.provider_badge = QLabel(get_active_provider_label())
        self.provider_badge.setObjectName("providerLabel")
        sub_row.addWidget(self.provider_badge)
        sub_row.addStretch()

        title_col.addLayout(sub_row)

        title_bar.addLayout(title_col)
        title_bar.addStretch()

        # History button
        self.history_btn = QPushButton("📋 History")
        self.history_btn.setObjectName("historyBtn")
        self.history_btn.setCursor(Qt.PointingHandCursor)
        self.history_btn.clicked.connect(self._toggle_history)
        title_bar.addWidget(self.history_btn)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.hide)
        title_bar.addWidget(close_btn)

        main_layout.addLayout(title_bar)

        # ─── Divider ───
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.HLine)
        main_layout.addWidget(divider)

        # ─── Mode Selector + Input Section Label ───
        controls_row = QHBoxLayout()
        controls_row.setSpacing(12)

        input_label = QLabel("ORIGINAL TEXT")
        input_label.setObjectName("sectionLabel")
        controls_row.addWidget(input_label)

        controls_row.addStretch()

        mode_label = QLabel("MODE")
        mode_label.setObjectName("sectionLabel")
        controls_row.addWidget(mode_label)

        self.mode_combo = QComboBox()
        for mode_name in MODES.keys():
            self.mode_combo.addItem(mode_name)
        controls_row.addWidget(self.mode_combo)

        main_layout.addLayout(controls_row)

        # ─── Input Text Box ───
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Paste or type your text here...")
        self.input_text.setMinimumHeight(100)
        self.input_text.setMaximumHeight(140)
        main_layout.addWidget(self.input_text)

        # ─── Enhance Button ───
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.enhance_btn = QPushButton("⚡ Enhance")
        self.enhance_btn.setObjectName("enhanceBtn")
        self.enhance_btn.setCursor(Qt.PointingHandCursor)
        self.enhance_btn.clicked.connect(self._on_enhance)
        btn_row.addWidget(self.enhance_btn)

        btn_row.addStretch()

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        btn_row.addWidget(self.status_label)

        main_layout.addLayout(btn_row)

        # ─── Output Section ───
        output_header = QHBoxLayout()
        output_label = QLabel("ENHANCED TEXT")
        output_label.setObjectName("sectionLabel")
        output_header.addWidget(output_label)

        output_header.addStretch()

        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.setObjectName("copyBtn")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self._on_copy)
        self.copy_btn.setEnabled(False)
        output_header.addWidget(self.copy_btn)

        main_layout.addLayout(output_header)

        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Enhanced text will appear here...")
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(100)
        self.output_text.setMaximumHeight(140)
        main_layout.addWidget(self.output_text)

        # ─── Error label (hidden by default) ───
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)

        # ─── History Panel (hidden by default) ───
        self.history_panel = QScrollArea()
        self.history_panel.setWidgetResizable(True)
        self.history_panel.setMaximumHeight(150)
        self.history_panel.hide()

        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(6)
        self.history_panel.setWidget(self.history_container)
        main_layout.addWidget(self.history_panel)

        # ─── Bottom Buttons ───
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)

        shortcut_hint = QLabel("Enter = Enhance  •  Ctrl+Enter = Replace  •  Esc = Close")
        shortcut_hint.setObjectName("subtitleLabel")
        bottom_row.addWidget(shortcut_hint)

        bottom_row.addStretch()

        self.replace_btn = QPushButton("↵ Replace in App")
        self.replace_btn.setObjectName("replaceBtn")
        self.replace_btn.setCursor(Qt.PointingHandCursor)
        self.replace_btn.clicked.connect(self._on_replace)
        self.replace_btn.setEnabled(False)
        bottom_row.addWidget(self.replace_btn)

        main_layout.addLayout(bottom_row)

    # ──────────────────────────────────────────────
    # Keyboard Shortcuts
    # ──────────────────────────────────────────────
    def _setup_shortcuts(self):
        # Enter = Enhance (only when not in text edit)
        enhance_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        enhance_shortcut.activated.connect(self._shortcut_enhance)

        # Ctrl+Enter = Replace
        replace_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        replace_shortcut.activated.connect(self._on_replace)

        # Escape = Close
        esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        esc_shortcut.activated.connect(self.hide)

    def _shortcut_enhance(self):
        # Only trigger if input_text doesn't have focus (to allow Enter in text box)
        if not self.input_text.hasFocus():
            self._on_enhance()

    # ──────────────────────────────────────────────
    # Window Dragging
    # ──────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ──────────────────────────────────────────────
    # Show / Center
    # ──────────────────────────────────────────────
    def show_popup(self, initial_text: str = ""):
        """Shows the popup centered on screen with optional initial text."""
        self.error_label.hide()
        self.status_label.setText("")
        self.output_text.clear()
        self.replace_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)
        self.enhance_btn.setEnabled(True)
        self.enhance_btn.setText("⚡ Enhance")

        if initial_text:
            self.input_text.setPlainText(initial_text)
        else:
            self.input_text.clear()

        # Center on screen
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        self.show()
        self.activateWindow()
        self.raise_()
        self.input_text.setFocus()

    # ──────────────────────────────────────────────
    # Enhancement Logic
    # ──────────────────────────────────────────────
    def _on_enhance(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self._show_error("Please enter or select some text to enhance.")
            return

        self.error_label.hide()
        self.enhance_btn.setEnabled(False)
        self.enhance_btn.setText("⏳ Enhancing...")
        self.replace_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)
        self.output_text.clear()
        self.status_label.setText("Connecting to AI...")

        mode = self.mode_combo.currentText()

        # Start worker thread
        self.worker = EnhanceWorker(text, mode)
        self.worker.finished.connect(self._on_enhance_success)
        self.worker.error.connect(self._on_enhance_error)
        self.worker.start()

        # Animate loading dots
        self._loading_tick = 0
        self._loading_timer = QTimer(self)
        self._loading_timer.timeout.connect(self._update_loading)
        self._loading_timer.start(400)

    def _update_loading(self):
        self._loading_tick = (self._loading_tick + 1) % 4
        dots = "." * self._loading_tick
        self.status_label.setText(f"Enhancing{dots}")

    def _on_enhance_success(self, result: str):
        self._loading_timer.stop()
        self.output_text.setPlainText(result)
        self.enhance_btn.setEnabled(True)
        self.enhance_btn.setText("⚡ Enhance")
        self.replace_btn.setEnabled(True)
        self.copy_btn.setEnabled(True)
        self.status_label.setText("✅ Done!")

        # Clear status after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))

        # Add to history
        self._add_to_history(
            self.input_text.toPlainText().strip(),
            result,
            self.mode_combo.currentText()
        )

    def _on_enhance_error(self, error_msg: str):
        self._loading_timer.stop()
        self.enhance_btn.setEnabled(True)
        self.enhance_btn.setText("⚡ Enhance")
        self.status_label.setText("")
        self._show_error(error_msg)

    def _show_error(self, message: str):
        self.error_label.setText(f"⚠ {message}")
        self.error_label.show()

    # ──────────────────────────────────────────────
    # Replace / Copy
    # ──────────────────────────────────────────────
    def _on_replace(self):
        enhanced = self.output_text.toPlainText().strip()
        if not enhanced:
            return

        self.hide()
        # Small delay to let the popup hide and original app regain focus
        QTimer.singleShot(300, lambda: paste_text(enhanced))

    def _on_copy(self):
        enhanced = self.output_text.toPlainText().strip()
        if enhanced:
            import pyperclip
            pyperclip.copy(enhanced)
            self.copy_btn.setText("✅ Copied!")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("📋 Copy"))

    # ──────────────────────────────────────────────
    # History
    # ──────────────────────────────────────────────
    def _add_to_history(self, original: str, enhanced: str, mode: str):
        entry = {
            "original": original[:80] + ("..." if len(original) > 80 else ""),
            "enhanced": enhanced,
            "mode": mode,
            "time": datetime.datetime.now().strftime("%H:%M"),
        }
        self.history.insert(0, entry)
        if len(self.history) > MAX_HISTORY_ITEMS:
            self.history = self.history[:MAX_HISTORY_ITEMS]
        self._refresh_history_ui()

    def _refresh_history_ui(self):
        # Clear existing items
        while self.history_layout.count():
            child = self.history_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for entry in self.history:
            item = QFrame()
            item.setObjectName("historyItem")
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(10, 8, 10, 8)
            item_layout.setSpacing(4)

            header = QHBoxLayout()
            mode_lbl = QLabel(entry["mode"])
            mode_lbl.setStyleSheet(
                f"color: {COLORS['accent']}; font-size: 11px; font-weight: 600;"
            )
            header.addWidget(mode_lbl)
            header.addStretch()
            time_lbl = QLabel(entry["time"])
            time_lbl.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 10px;")
            header.addWidget(time_lbl)
            item_layout.addLayout(header)

            preview = QLabel(entry["original"])
            preview.setStyleSheet(
                f"color: {COLORS['text']}; font-size: 12px;"
            )
            preview.setWordWrap(True)
            item_layout.addWidget(preview)

            # Click to load
            item.setCursor(Qt.PointingHandCursor)
            enhanced_text = entry["enhanced"]
            original_full = entry.get("original", "")

            def make_click_handler(enh):
                def handler(event):
                    self.output_text.setPlainText(enh)
                    self.replace_btn.setEnabled(True)
                    self.copy_btn.setEnabled(True)
                return handler

            item.mousePressEvent = make_click_handler(enhanced_text)
            self.history_layout.addWidget(item)

        self.history_layout.addStretch()

    def _toggle_history(self):
        self._history_visible = not self._history_visible
        if self._history_visible:
            self._refresh_history_ui()
            self.history_panel.show()
            self.history_btn.setText("📋 Hide")
            self.setFixedHeight(WINDOW_HEIGHT + 160)
        else:
            self.history_panel.hide()
            self.history_btn.setText("📋 History")
            self.setFixedHeight(WINDOW_HEIGHT)

        # Re-center child container
        for child in self.children():
            if hasattr(child, 'setGeometry') and child.objectName() == "EnhancerPopup":
                child.setGeometry(0, 0, self.width(), self.height())
