"""
Settings Dialog — configure provider & API keys without touching env vars.
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
    background: #0c0d1e;
    border: 1px solid rgba(124,92,252,0.5);
    border-radius: 16px;
}
QLabel#h1 { color:#f0f0ff; font-size:17px; font-weight:700; font-family:'Segoe UI',sans-serif; }
QLabel#sec { color:#5a5c7a; font-size:10px; font-weight:600; font-family:'Segoe UI',sans-serif; letter-spacing:1.2px; }
QLabel#hint { color:#6e7099; font-size:11px; font-family:'Segoe UI',sans-serif; }
QLabel#status { font-size:12px; font-family:'Segoe UI',sans-serif; }
QLineEdit {
    background:#1c1e38; color:#f0f0ff; border:1px solid #2a2d55;
    border-radius:8px; padding:10px 14px; font-size:13px; font-family:'Segoe UI',monospace;
}
QLineEdit:focus { border-color:#7c5cfc; }
QComboBox {
    background:#1c1e38; color:#f0f0ff; border:1px solid #2a2d55;
    border-radius:8px; padding:10px 14px; font-size:13px; font-family:'Segoe UI',sans-serif;
}
QComboBox:hover { border-color:#7c5cfc; }
QComboBox::drop-down { border:none; width:28px; }
QComboBox::down-arrow { image:none; border-left:4px solid transparent; border-right:4px solid transparent; border-top:5px solid #9092b3; margin-right:10px; }
QComboBox QAbstractItemView { background:#141526; color:#f0f0ff; border:1px solid #2a2d55; selection-background-color:#7c5cfc; outline:none; padding:4px; }
QPushButton#prov {
    background:#1c1e38; color:#9092b3; border:1px solid #2a2d55;
    border-radius:20px; padding:10px 28px; font-size:13px; font-weight:500; font-family:'Segoe UI',sans-serif;
}
QPushButton#prov:checked {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7c5cfc,stop:1 #c471ed);
    color:white; border:none; font-weight:700;
}
QPushButton#save {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7c5cfc,stop:1 #c471ed);
    color:white; border:none; border-radius:10px; padding:13px; font-size:14px; font-weight:700; font-family:'Segoe UI',sans-serif;
}
QPushButton#save:hover {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #9178ff,stop:1 #d48bff);
}
QPushButton#xbtn { background:transparent; color:#9092b3; border:none; border-radius:8px; font-size:16px; padding:4px 8px; min-width:30px; min-height:30px; }
QPushButton#xbtn:hover { background:rgba(248,113,113,0.12); color:#f87171; }
QPushButton#eye { background:transparent; color:#9092b3; border:none; border-radius:6px; padding:4px 8px; font-size:14px; }
QPushButton#eye:hover { color:#a78bfa; }
QFrame#div { background:#2a2d55; max-height:1px; min-height:1px; }
"""


class SettingsDialog(QDialog):
    saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setFixedSize(460, 530)
        self.setStyleSheet(_SS)
        self._drag = None
        self._build()
        self._load()
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.hide)

    def _build(self):
        lo = QVBoxLayout(self)
        lo.setContentsMargins(28, 24, 28, 28)
        lo.setSpacing(14)

        # Header
        hdr = QHBoxLayout()
        t = QLabel("⚙  Settings"); t.setObjectName("h1")
        hdr.addWidget(t); hdr.addStretch()
        x = QPushButton("✕"); x.setObjectName("xbtn"); x.setCursor(Qt.PointingHandCursor)
        x.clicked.connect(self.hide); hdr.addWidget(x)
        lo.addLayout(hdr)

        div = QFrame(); div.setObjectName("div"); div.setFrameShape(QFrame.HLine)
        lo.addWidget(div)

        # Provider
        pl = QLabel("PROVIDER"); pl.setObjectName("sec"); lo.addWidget(pl)
        pr = QHBoxLayout(); pr.setSpacing(10)
        self.or_btn = QPushButton("🌐  OpenRouter"); self.or_btn.setObjectName("prov")
        self.or_btn.setCheckable(True); self.or_btn.setCursor(Qt.PointingHandCursor)
        self.oa_btn = QPushButton("🤖  OpenAI"); self.oa_btn.setObjectName("prov")
        self.oa_btn.setCheckable(True); self.oa_btn.setCursor(Qt.PointingHandCursor)
        self._pg = QButtonGroup(self); self._pg.addButton(self.or_btn, 0)
        self._pg.addButton(self.oa_btn, 1); self._pg.setExclusive(True)
        self._pg.buttonClicked.connect(self._on_prov)
        pr.addWidget(self.or_btn); pr.addWidget(self.oa_btn); lo.addLayout(pr)

        self.hint = QLabel(); self.hint.setObjectName("hint"); self.hint.setWordWrap(True)
        lo.addWidget(self.hint)

        # API Key
        kl = QLabel("API KEY"); kl.setObjectName("sec"); lo.addWidget(kl)
        kr = QHBoxLayout(); kr.setSpacing(6)
        self.key = QLineEdit(); self.key.setEchoMode(QLineEdit.Password)
        self.key.setPlaceholderText("Paste your API key here...")
        self.eye = QPushButton("👁"); self.eye.setObjectName("eye")
        self.eye.setFixedWidth(36); self.eye.setCursor(Qt.PointingHandCursor)
        self.eye.clicked.connect(self._toggle_eye)
        kr.addWidget(self.key); kr.addWidget(self.eye); lo.addLayout(kr)

        # Model
        ml = QLabel("MODEL"); ml.setObjectName("sec"); lo.addWidget(ml)
        self.model = QComboBox(); self.model.setEditable(True); lo.addWidget(self.model)

        lo.addStretch()

        self.status = QLabel(""); self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignCenter); lo.addWidget(self.status)

        sv = QPushButton("💾  Save Settings"); sv.setObjectName("save")
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
            self.hint.setText("Get a free key at openrouter.ai/keys — 200+ models including Claude, GPT-4, Gemini.")
            models, cur = OR_MODELS, S.get("openrouter_model", "openrouter/auto")
        else:
            self.hint.setText("Get a key at platform.openai.com/api-keys — direct GPT-4o access.")
            models, cur = OA_MODELS, S.get("openai_model", "gpt-4o-mini")
        self.model.clear()
        for m in models: self.model.addItem(m)
        idx = self.model.findText(cur)
        self.model.setCurrentIndex(idx) if idx >= 0 else self.model.setCurrentText(cur)

    def _toggle_eye(self):
        is_password = self.key.echoMode() == QLineEdit.Password
        self.key.setEchoMode(QLineEdit.Normal if is_password else QLineEdit.Password)
        self.eye.setText("🙈" if is_password else "👁")

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
        self.status.setStyleSheet("color:#34d399;")
        self.status.setText("✅  Saved!")
        QTimer.singleShot(2500, lambda: self.status.setText(""))
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
