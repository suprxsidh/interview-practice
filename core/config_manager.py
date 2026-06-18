import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.json"

DEFAULTS = {
    "api_key": "",
    "interview_type": "behavioral",
    "session_length": 5,
    "job_role": "",
}


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
            return {**DEFAULTS, **data}
        except Exception:
            pass
    return dict(DEFAULTS)


def save_config(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, CONFIG_PATH)


def validate_api_key(key: str) -> tuple[bool, str]:
    if not key or len(key.strip()) < 10:
        return False, "API key is too short."
    try:
        import google.generativeai as genai
        genai.configure(api_key=key.strip())
        model = genai.GenerativeModel("gemini-1.5-flash")
        model.generate_content("Say OK")
        return True, "API key is valid."
    except Exception as e:
        msg = str(e)
        if "API_KEY_INVALID" in msg or "invalid" in msg.lower():
            return False, "Invalid API key. Please check and try again."
        if "quota" in msg.lower() or "429" in msg:
            return True, "Key valid (quota limit reached — try again later)."
        return False, f"Could not verify key: {msg[:120]}"


def get_api_key() -> str:
    return load_config().get("api_key", "")
