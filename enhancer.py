"""
AI Enhancement — reads provider/key/model from settings.py (no env vars needed).
"""
from openai import OpenAI
import settings as S
from config import MODES, OPENROUTER_BASE_URL, OPENROUTER_SITE_NAME


def _make_client() -> tuple[OpenAI, str]:
    cfg = S.load()
    prov = cfg.get("provider", "openrouter")

    if prov == "openrouter":
        key = cfg.get("openrouter_api_key", "").strip()
        if not key:
            raise ValueError(
                "OpenRouter API key not configured.\n\n"
                "Click ⚙ Settings to add your key.\n"
                "Get a free key at openrouter.ai/keys"
            )
        client = OpenAI(
            api_key=key,
            base_url=OPENROUTER_BASE_URL,
            default_headers={"X-Title": OPENROUTER_SITE_NAME},
        )
        return client, cfg.get("openrouter_model", "openrouter/auto")
    else:
        key = cfg.get("openai_api_key", "").strip()
        if not key:
            raise ValueError(
                "OpenAI API key not configured.\n\n"
                "Click ⚙ Settings to add your key."
            )
        return OpenAI(api_key=key), cfg.get("openai_model", "gpt-4o-mini")


def enhance_text(text: str, mode: str) -> str:
    if not text or not text.strip():
        raise ValueError("No text provided for enhancement.")
    prompt = MODES.get(mode)
    if not prompt:
        raise ValueError(f"Unknown mode: {mode}")
    client, model = _make_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
        temperature=0.7,
        max_tokens=2048,
    )
    result = resp.choices[0].message.content
    if result:
        result = result.strip()
        if (result.startswith('"') and result.endswith('"')) or (result.startswith("'") and result.endswith("'")):
            if len(result) >= 2:
                result = result[1:-1].strip()
    return result if result else ""


def get_provider_label() -> str:
    cfg = S.load()
    prov = cfg.get("provider", "openrouter")
    if prov == "openrouter":
        m = cfg.get("openrouter_model", "openrouter/auto")
        tag = "auto" if m == "openrouter/auto" else m.split("/")[-1]
        return f"OpenRouter · {tag}"
    return f"OpenAI · {cfg.get('openai_model', 'gpt-4o-mini')}"
