# ⚡ Prompt Enhancer

A global AI-powered prompt enhancer for Windows. Select text in **any** application, press a hotkey, and get an AI-improved version instantly.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/UI-PyQt5-41CD52?logo=qt&logoColor=white)
![OpenAI](https://img.shields.io/badge/AI-OpenAI-412991?logo=openai&logoColor=white)
![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌐 **Global Hotkey** | `Ctrl+Shift+E` works from any application |
| 🎨 **Modern Dark UI** | Frameless, always-on-top popup with glassmorphism |
| 🤖 **AI Enhancement** | Powered by OpenAI GPT-4o-mini |
| 📋 **Smart Clipboard** | Auto-captures selected text, replaces it back |
| 🎯 **4 Modes** | Improve, Shorten, Formal, Casual |
| 📜 **History** | Last 5 enhancements saved and reusable |
| 🖥️ **System Tray** | Runs silently in background with tray icon |
| 🚀 **Auto-Start** | Toggle Windows startup from tray menu |
| ⌨️ **Keyboard Shortcuts** | Enter=Enhance, Ctrl+Enter=Replace, Esc=Close |
| 🧵 **Non-Blocking** | Threaded API calls — UI never freezes |

---

## 📁 Project Structure

```
prompt-enhancer/
├── src/
│   ├── main.py              # Entry point — wires everything together
│   ├── ui.py                # PyQt5 popup window (dark theme)
│   ├── enhancer.py          # OpenAI API communication
│   ├── clipboard_handler.py # Clipboard capture & paste simulation
│   ├── tray.py              # System tray icon & menu
│   ├── startup.py           # Windows auto-start management
│   ├── config.py            # All settings & mode prompts
│   ├── settings.py          # Settings persistence
│   └── settings_dialog.py   # Settings UI
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.10+** installed on Windows
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))

### 2. Install Dependencies

```bash
cd "d:\prompt enhancer app"
pip install -r requirements.txt
```

### 3. Set Your API Key

```bash
# Command Prompt
set OPENAI_API_KEY=sk-your-api-key-here

# PowerShell
$env:OPENAI_API_KEY = "sk-your-api-key-here"

# Permanent (System Environment Variable — recommended)
# Search "Environment Variables" in Windows Settings
# Add OPENAI_API_KEY with your key as the value
```

### 4. Run the App

```bash
# With console (for debugging)
python src/main.py

# Without console (silent background mode)
pythonw src/main.py
```

### 5. Use It!

1. **Select text** in any application (browser, VS Code, Notepad, etc.)
2. Press **`Ctrl+Shift+E`**
3. Choose an enhancement mode
4. Click **⚡ Enhance** (or press `Enter`)
5. Click **↵ Replace in App** (or press `Ctrl+Enter`)
6. The enhanced text replaces your selection!

---

## 📦 Build as .exe (Standalone)

### Install PyInstaller

```bash
pip install pyinstaller
```

### Build

```bash
pyinstaller --onefile --noconsole --name PromptEnhancer src/main.py
```

### With Custom Icon

```bash
# Place your icon.ico file in the project folder, then:
pyinstaller --onefile --noconsole --name PromptEnhancer --icon=icon.ico src/main.py
```

The `.exe` will be in the `dist/` folder.

### Run the .exe

```bash
# Set the environment variable first (or set it system-wide)
set OPENAI_API_KEY=sk-your-key
dist\PromptEnhancer.exe
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENAI_API_KEY` | `env var` | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | AI model to use |
| `HOTKEY_COMBINATION` | `ctrl+shift+e` | Global hotkey |
| `WINDOW_WIDTH` | `620` | Popup width |
| `WINDOW_HEIGHT` | `680` | Popup height |
| `MAX_HISTORY_ITEMS` | `5` | History entries to keep |

---

## 🎯 Enhancement Modes

| Mode | Effect |
|------|--------|
| ✨ Improve | Better clarity, grammar, and engagement |
| ✂️ Shorten | Concise version, no fluff |
| 🎩 Formal | Professional/academic tone |
| 😊 Casual | Friendly, conversational tone |

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+E` | Open enhancer (global) |
| `Enter` | Enhance text |
| `Ctrl+Enter` | Replace text in original app |
| `Esc` | Close popup |

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not set" | Set `OPENAI_API_KEY` environment variable |
| Hotkey not working | Run as Administrator |
| No text captured | Make sure text is selected before pressing hotkey |
| Popup doesn't appear | Check system tray — the app may be running |
| Replace not working | The original app must still be focused after popup closes |

---

## 📄 License

MIT License — Free for personal and commercial use.
