"""
src/config.py
Application configuration loaded from environment variables via python-dotenv.

Credential loading rules
────────────────────────
- Credentials are NEVER hard-coded here.
- New canonical variable names (WATSONX_*) take priority; the older
  IBM_WATSONX_* names are accepted as fallbacks so existing .env files
  continue to work without any changes.
- Credentials are NEVER written to logs or printed to stdout.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Local .env values must never override platform-injected environment variables.
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env", override=False)


def _streamlit_secret(name: str) -> str:
    """Read one top-level Streamlit secret without failing outside Streamlit."""
    try:
        import streamlit as st

        value = st.secrets.get(name, "")
        if value:
            return str(value).strip()
    except Exception:
        # Streamlit raises when secrets.toml is absent or this runs outside an
        # app context. Missing secrets simply leave the provider unconfigured.
        return ""
    return ""


def _setting(*names: str, default: str = "") -> str:
    """Resolve environment variables first, then Streamlit Cloud secrets."""
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    for name in names:
        value = _streamlit_secret(name)
        if value:
            return value
    return default


def _resolve_provider(configured: str, api_key: str, project_id: str) -> str:
    """Use an explicit provider choice, otherwise enable Granite when configured."""
    if configured:
        return configured.lower()
    return "ibm_granite" if api_key and project_id else "demo"


# ── LLM provider ─────────────────────────────────────────────
_configured_provider = _setting("LLM_PROVIDER").lower()

# ── IBM watsonx.ai credentials ───────────────────────────────
# Streamlit Cloud users can provide these as top-level App secrets. The older
# IBM_WATSONX_* names remain supported for local environment compatibility.
IBM_WATSONX_API_KEY: str = _setting("WATSONX_API_KEY", "IBM_WATSONX_API_KEY")
IBM_WATSONX_PROJECT_ID: str = _setting("WATSONX_PROJECT_ID", "IBM_WATSONX_PROJECT_ID")
IBM_WATSONX_URL: str = _setting(
    "WATSONX_URL", "IBM_WATSONX_URL", default="https://us-south.ml.cloud.ibm.com"
)
IBM_GRANITE_MODEL_ID: str = _setting(
    "GRANITE_MODEL_ID", "IBM_GRANITE_MODEL_ID", default="ibm/granite-4-h-small"
)

# If credentials are present and no provider selector was supplied, use Granite.
# An explicit LLM_PROVIDER="demo" continues to select demo mode.
LLM_PROVIDER: str = _resolve_provider(
    _configured_provider, IBM_WATSONX_API_KEY, IBM_WATSONX_PROJECT_ID
)

# IAM token endpoint (overridable; default is the standard IBM Cloud IAM URL)
IBM_CLOUD_IAM_URL: str = _setting(
    "IBM_CLOUD_IAM_URL", default="https://iam.cloud.ibm.com/identity/token"
)

# ── Application settings ─────────────────────────────────────
APP_TITLE: str = _setting("APP_NAME", "APP_TITLE", default="Smart Farming AI")
APP_ENV: str = _setting("APP_ENV", default="development").lower()
APP_PORT: int = int(_setting("APP_PORT", default="8501"))
APP_DEBUG: bool = _setting("APP_DEBUG", default="false").lower() == "true"

# ── Data directory ────────────────────────────────────────────
DATA_DIR: Path = _project_root / "data"

# ── RAG settings ─────────────────────────────────────────────
RAG_TOP_K: int = 5            # number of chunks to retrieve
RAG_CHUNK_SIZE: int = 600     # approximate chars per chunk
RAG_MIN_SCORE: float = 0.05   # minimum cosine similarity to include

# ── Supported languages ───────────────────────────────────────
SUPPORTED_LANGUAGES: dict[str, str] = {
    "English": "en",
    "Tamil / தமிழ்": "ta",
    "Telugu / తెలుగు": "te",
    "Hindi / हिंदी": "hi",
}

# ── Safety hazard keywords (trigger safety card priority) ─────
SAFETY_KEYWORDS: list[str] = [
    "cyclone", "hurricane", "storm", "flood", "waterlog",
    "lightning", "thunder", "electric shock", "electrocute",
    "motor accident", "pump accident",
    "heatstroke", "heat stroke", "sunstroke",
    "pesticide poison", "chemical burn", "spray accident",
    "சூறாவளி", "வெள்ளம்", "மின்னல்", "வெப்ப அலை",
    "తుఫాను", "వరదలు", "పిడుగు", "వేడి",
    "चक्रवात", "बाढ़", "बिजली", "लू",
]
