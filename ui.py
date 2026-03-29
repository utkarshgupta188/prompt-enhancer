"""
Popup UI — premium dark theme, gradient accents, pill-mode selector,
built-in settings access, history panel.
"""
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QPushButton, QFrame, QScrollArea, QButtonGroup, QDesktopWidget,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

from config import MODES, MAX_HISTORY_ITEMS
from enhancer import enhance_text, get_provider_label
from clipboard_handler import paste_text
import pyperclip

W, H = 660, 710   # window dimensions
OPACITY = 0.97

# ─── Design tokens ────────────────────────────────────────────────────────────
C = {
    "bg":       "#0c0d1e",
    "surface":  "#141526",
    "s2":       "#1c1e38",
    "s3":       "#252848",
    "border":   "#2a2d55",
    "accent":   "#7c5cfc",
    "al":       "#a78bfa",
    "gs":       "#7c5cfc",
    "ge":       "#c471ed",
    "text":     "#f0f0ff",
    "t2":       "#9092b3",
    "t3":       "#5a5c7a",
    "ok":       "#34d399",
    "err":      "#f87171",
}

SS = f"""
QWidget#Popup {{
    background:{C["bg"]};
    border:1px solid rgba(124,92,252,0.45);
    border-radius:18px;
}}
/* ── labels ── */
QLabel#h1  {{ color:{C["text"]}; font-size:18px; font-weight:700; font-family:'Segoe UI','Inter',sans-serif; }}
QLabel#sub {{ color:{C["t2"]};  font-size:11px; font-family:'Segoe UI','Inter',sans-serif; }}
QLabel#sec {{ color:{C["t3"]};  font-size:10px; font-weight:600; font-family:'Segoe UI',sans-serif; letter-spacing:1.2px; }}
QLabel#cnt {{ color:{C["t3"]};  font-size:11px; font-family:'Segoe UI',sans-serif; }}
QLabel#sta {{ color:{C["t2"]};  font-size:11px; font-family:'Segoe UI',sans-serif; }}
QLabel#err {{
    color:{C["err"]}; font-size:12px; font-family:'Segoe UI',sans-serif;
    background:rgba(248,113,113,0.10); border-radius:8px; padding:8px 12px;
}}
QLabel#badge {{
    color:{C["al"]}; font-size:10px; font-weight:600; font-family:'Segoe UI',sans-serif;
    background:rgba(124,92,252,0.12); border:1px solid rgba(124,92,252,0.30);
    border-radius:5px; padding:1px 7px;
}}
/* ── textboxes ── */
QTextEdit {{
    background:{C["surface"]}; color:{C["text"]}; border:1px solid {C["border"]};
    border-radius:10px; padding:14px; font-size:13px;
    font-family:'Cascadia Code','Consolas','Segoe UI',monospace;
    selection-background-color:{C["accent"]}; selection-color:white;
}}
QTextEdit:focus {{ border-color:{C["accent"]}; }}
/* ── mode pills ── */
QPushButton#pill {{
    background:{C["surface"]}; color:{C["t2"]}; border:1px solid {C["border"]};
    border-radius:20px; padding:7px 0; font-size:12px; font-weight:500; font-family:'Segoe UI',sans-serif;
}}
QPushButton#pill:checked {{
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {C["gs"]},stop:1 {C["ge"]});
    color:white; border:none; font-weight:700;
}}
QPushButton#pill:hover:!checked {{ border-color:{C["accent"]}; color:{C["al"]}; }}
/* ── enhance button ── */
QPushButton#go {{
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {C["gs"]},stop:1 {C["ge"]});
    color:white; border:none; border-radius:10px; padding:13px 0;
    font-size:14px; font-weight:700; font-family:'Segoe UI',sans-serif; letter-spacing:0.5px;
}}
QPushButton#go:hover {{
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #9178ff,stop:1 #d68bff);
}}
QPushButton#go:disabled {{ background:{C["s2"]}; color:{C["t3"]}; }}
/* ── replace button ── */
QPushButton#rep {{
    background:transparent; color:{C["ok"]}; border:1px solid {C["ok"]};
    border-radius:8px; padding:9px 20px; font-size:13px; font-weight:600; font-family:'Segoe UI',sans-serif;
}}
QPushButton#rep:hover {{ background:rgba(52,211,153,0.10); }}
QPushButton#rep:disabled {{ color:{C["t3"]}; border-color:{C["border"]}; }}
/* ── icon buttons ── */
QPushButton#ico {{
    background:transparent; color:{C["t2"]}; border:none;
    border-radius:8px; font-size:15px; padding:4px 8px; min-width:32px; min-height:32px;
}}
QPushButton#ico:hover {{ background:{C["s2"]}; color:{C["al"]}; }}
QPushButton#xcl {{
    background:transparent; color:{C["t2"]}; border:none;
    border-radius:8px; font-size:15px; padding:4px 8px; min-width:32px; min-height:32px;
}}
QPushButton#xcl:hover {{ background:rgba(248,113,113,0.12); color:{C["err"]}; }}
/* ── copy button ── */
QPushButton#copy {{
    background:{C["surface"]}; color:{C["t2"]}; border:1px solid {C["border"]};
    border-radius:6px; padding:4px 10px; font-size:11px; font-family:'Segoe UI',sans-serif;
}}
QPushButton#copy:hover {{ border-color:{C["accent"]}; color:{C["al"]}; }}
/* ── misc ── */
QFrame#div  {{ background:{C["border"]}; max-height:1px; min-height:1px; }}
QScrollArea {{ background:transparent; border:none; }}
QScrollBar:vertical {{ background:{C["surface"]}; width:5px; border-radius:3px; }}
QScrollBar::handle:vertical {{ background:{C["border"]}; border-radius:3px; min-height:20px; }}
QScrollBar::handle:vertical:hover {{ background:{C["accent"]}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QFrame#hcard {{ background:{C["surface"]}; border:1px solid {C["border"]}; border-radius:8px; }}
"""


# ─── Worker thread ─────────────────────────────────────────────────────────────
class Worker(QThread):
    done  = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self, text, mode):
        super().__init__(); self.text = text; self.mode = mode
    def run(self):
        try:    self.done.emit(enhance_text(self.text, self.mode))
        except Exception as e: self.error.emit(str(e))


# ─── Main popup ────────────────────────────────────────────────────────────────
class EnhancerPopup(QWidget):
    open_settings = pyqtSignal()   # consumed by main.py

    def __init__(self):
        super().__init__()
        self.history: list[dict] = []
        self.worker: Worker | None = None
        self._drag = None
        self._hist_open = False
        self._tick = 0
        self._build()
        self._shortcuts()

    # ── build ──────────────────────────────────────────────────────────────────
    def _build(self):
        self.setObjectName("Popup")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setFixedSize(W, H)
        self.setWindowOpacity(OPACITY)
        self.setStyleSheet(SS)

        container = QWidget(self)
        container.setObjectName("Popup")
        container.setGeometry(0, 0, W, H)

        lo = QVBoxLayout(container)
        lo.setContentsMargins(24, 20, 24, 22)
        lo.setSpacing(10)

        # ── Header bar ──────────────────────────────────────────────────────
        hdr = QHBoxLayout(); hdr.setSpacing(4)

        left = QVBoxLayout(); left.setSpacing(3)
        title = QLabel("⚡ Prompt Enhancer"); title.setObjectName("h1")
        left.addWidget(title)

        sub_row = QHBoxLayout(); sub_row.setSpacing(8); sub_row.setContentsMargins(0,0,0,0)
        sub = QLabel("Select text → Enhance → Replace"); sub.setObjectName("sub")
        sub_row.addWidget(sub)
        self.badge = QLabel(get_provider_label()); self.badge.setObjectName("badge")
        sub_row.addWidget(self.badge); sub_row.addStretch()
        left.addLayout(sub_row)

        hdr.addLayout(left); hdr.addStretch()

        # icon buttons: history, settings, close
        self.hist_btn = self._ico("🕐", "ico", self._toggle_hist)
        self.hist_btn.setToolTip("History")
        hdr.addWidget(self.hist_btn)

        set_btn = self._ico("⚙", "ico", self.open_settings.emit)
        set_btn.setToolTip("Settings")
        hdr.addWidget(set_btn)

        close_btn = self._ico("✕", "xcl", self.hide)
        hdr.addWidget(close_btn)

        lo.addLayout(hdr)

        # ── Divider ─────────────────────────────────────────────────────────
        lo.addWidget(self._div())

        # ── Mode pills ──────────────────────────────────────────────────────
        pill_row = QHBoxLayout(); pill_row.setSpacing(8)
        self._pill_group = QButtonGroup(self); self._pill_group.setExclusive(True)
        self._pills: list[QPushButton] = []
        for i, mode in enumerate(MODES.keys()):
            btn = QPushButton(mode); btn.setObjectName("pill")
            btn.setCheckable(True); btn.setCursor(Qt.PointingHandCursor)
            self._pill_group.addButton(btn, i)
            pill_row.addWidget(btn)
            self._pills.append(btn)
        self._pills[0].setChecked(True)
        lo.addLayout(pill_row)

        # ── Input ───────────────────────────────────────────────────────────
        in_hdr = QHBoxLayout()
        in_lbl = QLabel("YOUR TEXT"); in_lbl.setObjectName("sec")
        in_hdr.addWidget(in_lbl); in_hdr.addStretch()
        self.char_cnt = QLabel("0 chars"); self.char_cnt.setObjectName("cnt")
        in_hdr.addWidget(self.char_cnt)
        lo.addLayout(in_hdr)

        self.inp = QTextEdit()
        self.inp.setPlaceholderText("Paste or type text here, or select text anywhere and press Ctrl+Shift+E…")
        self.inp.setMinimumHeight(110); self.inp.setMaximumHeight(140)
        self.inp.textChanged.connect(self._update_count)
        lo.addWidget(self.inp)

        # ── Enhance button ───────────────────────────────────────────────────
        self.go_btn = QPushButton("⚡  Enhance"); self.go_btn.setObjectName("go")
        self.go_btn.setCursor(Qt.PointingHandCursor)
        self.go_btn.clicked.connect(self._enhance)
        lo.addWidget(self.go_btn)

        # ── Status ───────────────────────────────────────────────────────────
        self.sta = QLabel(""); self.sta.setObjectName("sta")
        self.sta.setAlignment(Qt.AlignCenter)
        lo.addWidget(self.sta)

        # ── Output ──────────────────────────────────────────────────────────
        out_hdr = QHBoxLayout()
        out_lbl = QLabel("ENHANCED TEXT"); out_lbl.setObjectName("sec")
        out_hdr.addWidget(out_lbl); out_hdr.addStretch()
        self.copy_btn = QPushButton("📋 Copy"); self.copy_btn.setObjectName("copy")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy)
        self.copy_btn.setEnabled(False)
        out_hdr.addWidget(self.copy_btn)
        lo.addLayout(out_hdr)

        self.out = QTextEdit()
        self.out.setReadOnly(True)
        self.out.setPlaceholderText("Enhanced text will appear here…")
        self.out.setMinimumHeight(110); self.out.setMaximumHeight(140)
        lo.addWidget(self.out)

        # ── Error label ──────────────────────────────────────────────────────
        self.err_lbl = QLabel(""); self.err_lbl.setObjectName("err")
        self.err_lbl.setWordWrap(True); self.err_lbl.hide()
        lo.addWidget(self.err_lbl)

        # ── History (hidden) ─────────────────────────────────────────────────
        self.hist_area = QScrollArea(); self.hist_area.setWidgetResizable(True)
        self.hist_area.setFixedHeight(140); self.hist_area.hide()
        self._hist_widget = QWidget()
        self._hist_lo = QVBoxLayout(self._hist_widget)
        self._hist_lo.setContentsMargins(0,0,0,0); self._hist_lo.setSpacing(6)
        self.hist_area.setWidget(self._hist_widget)
        lo.addWidget(self.hist_area)

        # ── Footer ──────────────────────────────────────────────────────────
        ftr = QHBoxLayout(); ftr.setSpacing(10)
        hint = QLabel("Enter = Enhance  •  Ctrl+Enter = Replace  •  Esc = Close")
        hint.setObjectName("sub"); ftr.addWidget(hint); ftr.addStretch()
        self.rep_btn = QPushButton("↵  Replace in App"); self.rep_btn.setObjectName("rep")
        self.rep_btn.setCursor(Qt.PointingHandCursor)
        self.rep_btn.clicked.connect(self._replace)
        self.rep_btn.setEnabled(False)
        ftr.addWidget(self.rep_btn)
        lo.addLayout(ftr)

    # ── helpers ────────────────────────────────────────────────────────────────
    def _ico(self, text, obj, slot) -> QPushButton:
        b = QPushButton(text); b.setObjectName(obj); b.setCursor(Qt.PointingHandCursor)
        b.clicked.connect(slot); return b

    def _div(self) -> QFrame:
        f = QFrame(); f.setObjectName("div"); f.setFrameShape(QFrame.HLine); return f

    def _update_count(self):
        n = len(self.inp.toPlainText())
        self.char_cnt.setText(f"{n} char{'s' if n != 1 else ''}")

    def _current_mode(self) -> str:
        idx = self._pill_group.checkedId()
        return list(MODES.keys())[idx] if idx >= 0 else list(MODES.keys())[0]

    # ── shortcuts ──────────────────────────────────────────────────────────────
    def _shortcuts(self):
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(
            lambda: self._enhance() if not self.inp.hasFocus() else None)
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self._replace)
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.hide)

    # ── drag ───────────────────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and self._drag:
            self.move(e.globalPos() - self._drag)
    def mouseReleaseEvent(self, e):
        self._drag = None

    # ── show ───────────────────────────────────────────────────────────────────
    def show_popup(self, initial_text: str = ""):
        self.err_lbl.hide(); self.sta.setText("")
        self.out.clear(); self.rep_btn.setEnabled(False); self.copy_btn.setEnabled(False)
        self.go_btn.setEnabled(True); self.go_btn.setText("⚡  Enhance")
        self.badge.setText(get_provider_label())
        if initial_text:
            self.inp.setPlainText(initial_text)
        else:
            self.inp.clear()
        sc = QDesktopWidget().availableGeometry()
        self.move((sc.width() - W) // 2, (sc.height() - H) // 2)
        self.show(); self.activateWindow(); self.raise_()
        self.inp.setFocus()

    # ── enhance ────────────────────────────────────────────────────────────────
    def _enhance(self):
        text = self.inp.toPlainText().strip()
        if not text:
            self._show_err("Please enter or select some text to enhance."); return
        self.err_lbl.hide()
        self.go_btn.setEnabled(False); self.go_btn.setText("⏳  Enhancing…")
        self.rep_btn.setEnabled(False); self.copy_btn.setEnabled(False)
        self.out.clear(); self.sta.setText("Connecting…")
        self._tick = 0
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick_loading)
        self._timer.start(400)
        self.worker = Worker(text, self._current_mode())
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_err)
        self.worker.start()

    def _tick_loading(self):
        self._tick = (self._tick + 1) % 4
        self.sta.setText("Enhancing" + "." * self._tick)

    def _on_done(self, result: str):
        self._timer.stop()
        self.out.setPlainText(result)
        self.go_btn.setEnabled(True); self.go_btn.setText("⚡  Enhance")
        self.rep_btn.setEnabled(True); self.copy_btn.setEnabled(True)
        self.sta.setStyleSheet(f"color:{C['ok']};"); self.sta.setText("✅  Done!")
        QTimer.singleShot(3000, lambda: (self.sta.setStyleSheet(""), self.sta.setText("")))
        self._add_history(self.inp.toPlainText().strip(), result, self._current_mode())

    def _on_err(self, msg: str):
        self._timer.stop()
        self.go_btn.setEnabled(True); self.go_btn.setText("⚡  Enhance")
        self.sta.setText(""); self._show_err(msg)

    def _show_err(self, msg: str):
        self.err_lbl.setText(f"⚠  {msg}"); self.err_lbl.show()

    # ── replace / copy ─────────────────────────────────────────────────────────
    def _replace(self):
        txt = self.out.toPlainText().strip()
        if txt:
            self.hide()
            QTimer.singleShot(300, lambda: paste_text(txt))

    def _copy(self):
        txt = self.out.toPlainText().strip()
        if txt:
            pyperclip.copy(txt)
            self.copy_btn.setText("✅ Copied!")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("📋 Copy"))

    # ── history ────────────────────────────────────────────────────────────────
    def _add_history(self, orig: str, enhanced: str, mode: str):
        self.history.insert(0, {
            "orig": orig[:80] + ("…" if len(orig) > 80 else ""),
            "enhanced": enhanced, "mode": mode,
            "time": datetime.datetime.now().strftime("%H:%M"),
        })
        self.history = self.history[:MAX_HISTORY_ITEMS]
        if self._hist_open:
            self._render_history()

    def _render_history(self):
        while self._hist_lo.count():
            c = self._hist_lo.takeAt(0)
            if c.widget(): c.widget().deleteLater()
        for entry in self.history:
            card = QFrame(); card.setObjectName("hcard")
            clo = QVBoxLayout(card); clo.setContentsMargins(10,8,10,8); clo.setSpacing(4)
            top = QHBoxLayout()
            ml = QLabel(entry["mode"])
            ml.setStyleSheet(f"color:{C['accent']};font-size:11px;font-weight:600;")
            top.addWidget(ml); top.addStretch()
            tl = QLabel(entry["time"])
            tl.setStyleSheet(f"color:{C['t3']};font-size:10px;")
            top.addWidget(tl); clo.addLayout(top)
            pl = QLabel(entry["orig"])
            pl.setStyleSheet(f"color:{C['text']};font-size:12px;")
            pl.setWordWrap(True); clo.addWidget(pl)
            card.setCursor(Qt.PointingHandCursor)
            enh = entry["enhanced"]
            card.mousePressEvent = (lambda e, t=enh: (
                self.out.setPlainText(t),
                self.rep_btn.setEnabled(True),
                self.copy_btn.setEnabled(True),
            ))
            self._hist_lo.addWidget(card)
        self._hist_lo.addStretch()

    def _toggle_hist(self):
        self._hist_open = not self._hist_open
        if self._hist_open:
            self._render_history()
            self.hist_area.show()
            self.hist_btn.setText("🕐")
            self.hist_btn.setStyleSheet(f"color:{C['accent']};")
            self.setFixedHeight(H + 150)
        else:
            self.hist_area.hide()
            self.hist_btn.setStyleSheet("")
            self.setFixedHeight(H)
        # resize container
        for c in self.children():
            if hasattr(c, "setGeometry") and c.objectName() == "Popup":
                c.setGeometry(0, 0, W, self.height())

    def refresh_badge(self):
        """Call after settings saved to update the provider badge."""
        self.badge.setText(get_provider_label())
