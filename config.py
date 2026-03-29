"""
App constants — API keys & provider are now stored in settings.py (no env vars).
"""
import os

# ── App metadata ──────────────────────────────────────────────────────────────
APP_NAME    = "PromptEnhancer"
APP_VERSION = "1.1.0"

# ── Hotkey ────────────────────────────────────────────────────────────────────
HOTKEY_COMBINATION = "ctrl+shift+e"

# ── UI ────────────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 660
WINDOW_HEIGHT = 710
WINDOW_OPACITY = 0.97

# ── OpenRouter endpoint (used by enhancer.py) ─────────────────────────────────
OPENROUTER_BASE_URL  = "https://openrouter.ai/api/v1"
OPENROUTER_SITE_NAME = "PromptEnhancer"

# ── History ───────────────────────────────────────────────────────────────────
MAX_HISTORY_ITEMS = 5

# ── Enhancement mode prompts ──────────────────────────────────────────────────
MODES = {
    "✨ Improve": (
        "You are an expert writing assistant. Improve the following text to make it "
        "clearer, more professional, and more engaging. Fix grammar and spelling issues. "
        "Maintain the original meaning. Return ONLY the improved text, no explanations."
    ),
    "✂️ Shorten": (
        "You are an expert editor. Shorten the following text while preserving its core "
        "meaning. Make it concise and punchy. Return ONLY the shortened text, no explanations."
    ),
    "🎩 Formal": (
        "You are an expert in formal communication. Rewrite the following text in a "
        "formal, professional tone suitable for business or academic contexts. "
        "Return ONLY the formal version, no explanations."
    ),
    "😊 Casual": (
        "You are an expert in casual communication. Rewrite the following text in a "
        "friendly, casual, and conversational tone. "
        "Return ONLY the casual version, no explanations."
    ),
}
