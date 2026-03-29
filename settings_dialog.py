"""
Settings Dialog — Ultra-minimal design (Monochrome / Productivity style).
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QButtonGroup,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

import settings as S

OR_MODELS = [
    "openrouter/auto",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3-haiku",
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "google/gemini-flash-1.5",
    "meta-llama/llama-3.1-70b-instruct",
    "mistralai/mixtral-8x7b-instruct",
]
OA_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

_SS = """
QDialog {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 8px;
}
QLabel#h1 { color: #F8FAFC; font-size: 15px; font-weight: 600; font-family: 'Jost', 'Segoe UI', sans-serif; }
QLabel#sec { color: #94A3B8; font-size: 10px; font-weight: 600; font-family: 'Jost', 'Segoe UI', sans-serif; text-transform: uppercase; }
QLabel#hint { color: #64748B; font-size: 11px; font-family: 'Jost', 'Segoe UI', sans-serif; margin-bottom: 5px; }
QLabel#status { font-size: 12px; font-family: 'Jost', 'Segoe UI', sans-serif; }

QLineEdit {
    background: #1E293B; color: #F8FAFC; border: 1px solid #334155;
    border-radius: 5px; padding: 8px 12px; font-size: 12px; font-family: 'Jost', 'Segoe UI', monospace;
}
QLineEdit:focus { border-color: #3B82F6; background: #0F172A; }

QComboBox {
    background: #1E293B; color: #F8FAFC; border: 1px solid #334155;
    border-radius: 5px; padding: 8px 12px; font-size: 12px; font-family: 'Jost', 'Segoe UI', sans-serif;
}
QComboBox:hover { border-color: #3B82F6; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #94A3B8; margin-right: 8px; }
QComboBox QAbstractItemView {
    background: #0F172A; color: #F8FAFC; border: 1px solid #334155;
    selection-background-color: #3B82F6; outline: none; padding: 2px;
}

QPushButton#prov {
    background: transparent; color: #64748B; border: 1px solid transparent;
    border-radius: 5px; padding: 8px 0px; font-size: 12px; font-weight: 500; font-family: 'Jost', 'Segoe UI', sans-serif;
}
QPushButton#prov:checked {
    background: #1E293B; color: #F8FAFC; border: 1px solid #334155; font-weight: 600;
}
QPushButton#prov:hover:!checked { background: #1E293B; color: #94A3B8; }

QPushButton#save {
    background: #F8FAFC; color: #0F172A; border: none; border-radius: 5px; padding: 10px;
    font-size: 12px; font-weight: 600; font-family: 'Jost', 'Segoe UI', sans-serif;
}
QPushButton#save:hover { background: #ffffff; }

QPushButton#xbtn { background: transparent; color: #94A3B8; border: none; border-radius: 4px; font-size: 15px; min-width: 24px; min-height: 24px; }
QPushButton#xbtn:hover { background: #1E293B; color: #F8FAFC; }

QPushButton#eye { background: transparent; color: #94A3B8; border: none; border-radius: 4px; font-size: 14px; }
QPushButton#eye:hover { color: #F8FAFC; }

QFrame#div { background: #1E293B; max-height: 1px; min-height: 1px; }
QFrame#provContainer { background: #0F172A; border: 1px solid #1E293B; border-radius: 6px; padding: 3px; }
"""


class SettingsDialog(QDialog):
    saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setFixedSize(420, 480)
        self.setStyleSheet(_SS)
        self._drag = None
        self._build()
        self._load()
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.hide)

    def _build(self):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(24, 20, 24, 24)
        lo.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 0)
        t = QLabel("Settings"); t.setObjectName("h1")
        hdr.addWidget(t); hdr.addStretch()
        x = QPushButton("✕"); x.setObjectName("xbtn"); x.setCursor(Qt.PointingHandCursor)
        x.clicked.connect(self.hide); hdr.addWidget(x)
        lo.addLayout(hdr)

        div = QFrame(); div.setObjectName("div"); div.setFrameShape(QFrame.HLine)
        lo.addWidget(div)
        lo.addSpacing(4)

        # Provider
        pl = QLabel("AI Provider"); pl.setObjectName("sec"); lo.addWidget(pl)
        
        pr_container = QFrame(); pr_container.setObjectName("provContainer")
        pr_layout = QHBoxLayout(pr_container); pr_layout.setContentsMargins(0, 0, 0, 0); pr_layout.setSpacing(4)
        
        self.or_btn = QPushButton("OpenRouter"); self.or_btn.setObjectName("prov")
        self.or_btn.setCheckable(True); self.or_btn.setCursor(Qt.PointingHandCursor)
        self.oa_btn = QPushButton("OpenAI"); self.oa_btn.setObjectName("prov")
        self.oa_btn.setCheckable(True); self.oa_btn.setCursor(Qt.PointingHandCursor)
        
        self._pg = QButtonGroup(self); self._pg.addButton(self.or_btn, 0)
        self._pg.addButton(self.oa_btn, 1); self._pg.setExclusive(True)
        self._pg.buttonClicked.connect(self._on_prov)
        
        pr_layout.addWidget(self.or_btn); pr_layout.addWidget(self.oa_btn)
        lo.addWidget(pr_container)

        self.hint = QLabel(); self.hint.setObjectName("hint"); self.hint.setWordWrap(True)
        lo.addWidget(self.hint)

        # API Key
        kl = QLabel("API Key"); kl.setObjectName("sec"); lo.addWidget(kl)
        kr = QHBoxLayout(); kr.setSpacing(6); kr.setContentsMargins(0, 0, 0, 0)
        self.key = QLineEdit(); self.key.setEchoMode(QLineEdit.Password)
        self.key.setPlaceholderText("Paste API key here...")
        self.eye = QPushButton("👁"); self.eye.setObjectName("eye")
        self.eye.setFixedWidth(30); self.eye.setCursor(Qt.PointingHandCursor)
        self.eye.clicked.connect(self._toggle_eye)
        kr.addWidget(self.key); kr.addWidget(self.eye); lo.addLayout(kr)

        # Model
        lo.addSpacing(4)
        ml = QLabel("Default Model"); ml.setObjectName("sec"); lo.addWidget(ml)
        self.model = QComboBox(); self.model.setEditable(True); lo.addWidget(self.model)

        lo.addStretch()

        self.status = QLabel(""); self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignCenter); lo.addWidget(self.status)

        sv = QPushButton("Save Config"); sv.setObjectName("save")
        sv.setCursor(Qt.PointingHandCursor); sv.clicked.connect(self._save)
        lo.addWidget(sv)

    def _load(self):
        cfg = S.load()
        prov = cfg.get("provider", "openrouter")
        (self.oa_btn if prov == "openai" else self.or_btn).setChecked(True)
        self._refresh_ui(prov)
        key = cfg.get("openrouter_api_key" if prov == "openrouter" else "openai_api_key", "")
        self.key.setText(key)

    def _on_prov(self):
        prov = "openai" if self.oa_btn.isChecked() else "openrouter"
        self._refresh_ui(prov)
        cfg = S.load()
        self.key.setText(cfg.get("openrouter_api_key" if prov == "openrouter" else "openai_api_key", ""))

    def _refresh_ui(self, prov):
        if prov == "openrouter":
            self.hint.setText("Get a free key at openrouter.ai/keys.")
            models, cur = OR_MODELS, S.get("openrouter_model", "openrouter/auto")
        else:
            self.hint.setText("Get a key at platform.openai.com/api-keys.")
            models, OA_MODELS, S.get("openai_model", "gpt-4o-mini")
        self.model.clear()
        for m in models: self.model.addItem(m)
        idx = self.model.findText(cur)
        self.model.setCurrentIndex(idx) if idx >= 0 else self.model.setCurrentText(cur)

    def _toggle_eye(self):
        is_password = self.key.echoMode() == QLineEdit.Password
        self.key.setEchoMode(QLineEdit.Normal if is_password else QLineEdit.Password)

    def _save(self):
        prov = "openai" if self.oa_btn.isChecked() else "openrouter"
        key = self.key.text().strip()
        model = self.model.currentText().strip()
        updates = {"provider": prov}
        if prov == "openrouter":
            updates["openrouter_api_key"] = key
            updates["openrouter_model"] = model or "openrouter/auto"
        else:
            updates["openai_api_key"] = key
            updates["openai_model"] = model or "gpt-4o-mini"
        S.save(updates); S.invalidate()
        self.status.setStyleSheet("color: #a3e635;")
        self.status.setText("Saved ✓")
        QTimer.singleShot(2000, lambda: self.status.setText(""))
        self.saved.emit()

    def show_centered(self):
        from PyQt5.QtWidgets import QDesktopWidget
        sc = QDesktopWidget().availableGeometry()
        self.move((sc.width() - self.width()) // 2, (sc.height() - self.height()) // 2)
        self.show(); self.activateWindow(); self.raise_()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and self._drag:
            self.move(e.globalPos() - self._drag)
    def mouseReleaseEvent(self, e):
        self._drag = None
