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

# Load .env from the project root (one level up from src/)
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env", override=True)

# ── LLM provider ─────────────────────────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "demo").lower()

# ── IBM watsonx.ai credentials ───────────────────────────────
# Accept both the new short names (WATSONX_*) and the original IBM_WATSONX_*
# names so existing .env files are not broken.
IBM_WATSONX_API_KEY: str = (
    os.getenv("WATSONX_API_KEY") or os.getenv("IBM_WATSONX_API_KEY") or ""
)
IBM_WATSONX_PROJECT_ID: str = (
    os.getenv("WATSONX_PROJECT_ID") or os.getenv("IBM_WATSONX_PROJECT_ID") or ""
)
IBM_WATSONX_URL: str = (
    os.getenv("WATSONX_URL")
    or os.getenv("IBM_WATSONX_URL")
    or "https://us-south.ml.cloud.ibm.com"
)
IBM_GRANITE_MODEL_ID: str = (
    os.getenv("GRANITE_MODEL_ID")
    or os.getenv("IBM_GRANITE_MODEL_ID")
    or "ibm/granite-4-h-small"
)

# IAM token endpoint (overridable; default is the standard IBM Cloud IAM URL)
IBM_CLOUD_IAM_URL: str = (
    os.getenv("IBM_CLOUD_IAM_URL")
    or "https://iam.cloud.ibm.com/identity/token"
)

# ── Application settings ─────────────────────────────────────
APP_TITLE: str  = os.getenv("APP_NAME") or os.getenv("APP_TITLE") or "Smart Farming AI"
APP_ENV: str    = os.getenv("APP_ENV", "development").lower()
APP_PORT: int   = int(os.getenv("APP_PORT", "8501"))
APP_DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"

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
