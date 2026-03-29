"""
AI Enhancement module.
Supports both OpenRouter (default, auto model) and OpenAI.

Provider resolution order:
  1. PROVIDER env var  →  "openrouter" | "openai"
  2. Falls back to OpenRouter if unset.

OpenRouter auto model (openrouter/auto) routes each request to the
best available model automatically, based on prompt size and content.
"""

from openai import OpenAI
from config import (
    PROVIDER,
    # OpenRouter
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL,
    OPENROUTER_MODEL, OPENROUTER_SITE_URL, OPENROUTER_SITE_NAME,
    # OpenAI
    OPENAI_API_KEY, OPENAI_MODEL,
    # Modes
    MODES,
)


def _make_client() -> tuple[OpenAI, str]:
    """
    Builds the correct OpenAI-compatible client and model name
    based on the configured PROVIDER.

    Returns:
        (client, model_name) tuple ready for chat completions.

    Raises:
        ValueError: If the required API key is missing.
    """
    if PROVIDER == "openrouter":
        if not OPENROUTER_API_KEY:
            raise ValueError(
                "OpenRouter API key not set.\n\n"
                "Get a free key at https://openrouter.ai/keys\n"
                "Then set it:\n"
                "  set OPENROUTER_API_KEY=sk-or-your-key-here\n\n"
                "Or switch to OpenAI:\n"
                "  set PROVIDER=openai\n"
                "  set OPENAI_API_KEY=sk-your-openai-key"
            )

        extra_headers = {}
        if OPENROUTER_SITE_URL:
            extra_headers["HTTP-Referer"] = OPENROUTER_SITE_URL
        if OPENROUTER_SITE_NAME:
            extra_headers["X-Title"] = OPENROUTER_SITE_NAME

        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            default_headers=extra_headers or None,
        )
        return client, OPENROUTER_MODEL

    else:  # openai
        if not OPENAI_API_KEY:
            raise ValueError(
                "OpenAI API key not set.\n\n"
                "Set the environment variable:\n"
                "  set OPENAI_API_KEY=sk-your-key-here\n\n"
                "Or use OpenRouter instead:\n"
                "  set PROVIDER=openrouter\n"
                "  set OPENROUTER_API_KEY=sk-or-your-key-here"
            )

        client = OpenAI(api_key=OPENAI_API_KEY)
        return client, OPENAI_MODEL


def enhance_text(text: str, mode: str) -> str:
    """
    Sends text to the configured AI provider for enhancement.

    Args:
        text: The original text to enhance.
        mode: The enhancement mode key (must exist in MODES dict).

    Returns:
        The enhanced text string.

    Raises:
        ValueError: If API key is not configured or inputs are invalid.
        Exception:  If the API call fails.
    """
    if not text or not text.strip():
        raise ValueError("No text provided for enhancement.")

    system_prompt = MODES.get(mode)
    if not system_prompt:
        raise ValueError(f"Unknown enhancement mode: {mode}")

    client, model = _make_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.7,
        max_tokens=2048,
    )

    result = response.choices[0].message.content
    return result.strip() if result else ""


def get_active_provider_label() -> str:
    """
    Returns a short human-readable label for the active provider + model.
    Used by the UI to show which backend is in use.
    """
    if PROVIDER == "openrouter":
        model = OPENROUTER_MODEL
        label = "auto" if model == "openrouter/auto" else model.split("/")[-1]
        return f"OpenRouter · {label}"
    else:
        return f"OpenAI · {OPENAI_MODEL}"
