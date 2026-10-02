import os
import logging
from typing import Optional, Any

try:
    from app.config import settings
except ImportError:
    from ..config import settings

logger = logging.getLogger("fitbuddy.ai")


def get_gemini_client() -> Optional[Any]:
    """
    Initializes and returns a configured Google Gemini GenerativeModel instance.
    Returns None if GEMINI_API_KEY is not set, invalid format, or in test environment.
    """
    if os.getenv("TESTING", "").lower() in ("1", "true") or "pytest" in os.environ.get("_", "").lower():
        return None

    api_key = (getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")).strip()
    if not api_key or api_key in ("", "your_gemini_api_key_here") or len(api_key) < 15:
        logger.info("GEMINI_API_KEY is not configured or too short. Using intelligent rule engine.")
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)
        return model
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini client: {e}. Will use intelligent fallback.")
        return None
