"""
Configuration settings for the Prompt Enhancer application.
"""

import os

# ──────────────────────────────────────────────
# Provider Selection
# Set PROVIDER env var to "openai" to use OpenAI directly.
# Default is "openrouter" (recommended — free auto-routing).
# ──────────────────────────────────────────────
PROVIDER = os.getenv("PROVIDER", "openrouter").lower()  # "openrouter" | "openai"

# ──────────────────────────────────────────────
# OpenRouter Configuration
# Sign up free at https://openrouter.ai
# OPENROUTER_AUTO uses the best available model automatically.
# ──────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_AUTO_MODEL = "openrouter/auto"   # Auto-selects best model per request
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", OPENROUTER_AUTO_MODEL)
# Optional: site info sent in headers for OpenRouter leaderboard
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "")
OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", "PromptEnhancer")

# ──────────────────────────────────────────────
# OpenAI Configuration (fallback / alternative)
# ──────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ──────────────────────────────────────────────
# Global Hotkey
# ──────────────────────────────────────────────
HOTKEY_COMBINATION = "ctrl+shift+e"

# ──────────────────────────────────────────────
# Application Metadata
# ──────────────────────────────────────────────
APP_NAME = "PromptEnhancer"
APP_VERSION = "1.0.0"

# ──────────────────────────────────────────────
# UI Configuration
# ──────────────────────────────────────────────
WINDOW_WIDTH = 620
WINDOW_HEIGHT = 680
WINDOW_OPACITY = 0.97

# ──────────────────────────────────────────────
# Enhancement Modes & System Prompts
# ──────────────────────────────────────────────
MODES = {
    "✨ Improve": (
        "You are an expert writing assistant. Improve the following text to make it "
        "clearer, more professional, and more engaging. Fix any grammar or spelling "
        "issues. Maintain the original meaning and intent. Return ONLY the improved text, "
        "no explanations."
    ),
    "✂️ Shorten": (
        "You are an expert editor. Shorten the following text while preserving its core "
        "meaning. Make it concise and punchy. Remove unnecessary words and redundancy. "
        "Return ONLY the shortened text, no explanations."
    ),
    "🎩 Formal": (
        "You are an expert in formal communication. Rewrite the following text in a "
        "formal, professional tone suitable for business or academic contexts. "
        "Return ONLY the formal version, no explanations."
    ),
    "😊 Casual": (
        "You are an expert in casual communication. Rewrite the following text in a "
        "friendly, casual, and conversational tone. Make it feel natural and approachable. "
        "Return ONLY the casual version, no explanations."
    ),
}

# ──────────────────────────────────────────────
# History
# ──────────────────────────────────────────────
MAX_HISTORY_ITEMS = 5
