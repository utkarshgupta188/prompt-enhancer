"""
Settings persistence — stores config in %APPDATA%/PromptEnhancer/settings.json
No environment variables required.
"""
import json, os
from pathlib import Path
from typing import Any

SETTINGS_DIR  = Path(os.getenv("APPDATA", str(Path.home()))) / "PromptEnhancer"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DEFAULTS: dict[str, Any] = {
    "provider":            "openrouter",
    "openrouter_api_key":  "",
    "openrouter_model":    "openrouter/auto",
    "openai_api_key":      "",
    "openai_model":        "gpt-4o-mini",
}

_cache: dict | None = None


def load() -> dict:
    global _cache
    if _cache is not None:
        return dict(_cache)
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                _cache = {**DEFAULTS, **json.load(f)}
            return dict(_cache)
    except Exception:
        pass
    _cache = dict(DEFAULTS)
    return dict(_cache)


def save(updates: dict) -> None:
    global _cache
    current = load()
    current.update(updates)
    _cache = current
    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
    except Exception as e:
        print(f"Settings save error: {e}")


def get(key: str, default: Any = None) -> Any:
    return load().get(key, default)


def invalidate() -> None:
    global _cache
    _cache = None
