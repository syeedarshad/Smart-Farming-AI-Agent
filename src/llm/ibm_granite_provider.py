"""
src/llm/ibm_granite_provider.py
IBM Granite provider via watsonx.ai.

Authentication
──────────────
IBM Cloud uses OAuth2 client-credentials flow.  We exchange the API key for a
short-lived Bearer token from the IAM endpoint, then include that token in every
watsonx.ai inference request.

Two integration paths are tried in order:
  1. ibm-watsonx-ai SDK  (preferred when the package is installed)
  2. Pure-requests REST  (fallback — works without the SDK)

Both paths read credentials exclusively from environment variables loaded by
src/config.py.  Credentials are NEVER written to logs, stdout or any file.

To activate:
  1. In .env set  LLM_PROVIDER=ibm_granite
  2. Set  WATSONX_API_KEY, WATSONX_PROJECT_ID
  3. Optionally set  WATSONX_URL, GRANITE_MODEL_ID, IBM_CLOUD_IAM_URL
  4. Run:  pip install ibm-watsonx-ai   (optional — REST path works without it)
  5. Restart the application.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Optional

import requests

from src.config import (
    IBM_CLOUD_IAM_URL,
    IBM_GRANITE_MODEL_ID,
    IBM_WATSONX_API_KEY,
    IBM_WATSONX_PROJECT_ID,
    IBM_WATSONX_URL,
)
from src.llm.base import LLMProvider

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
_IAM_GRANT_TYPE = "urn:ibm:params:oauth:grant-type:apikey"
_TOKEN_REFRESH_BUFFER_SECS = 60   # refresh token this many seconds before expiry
_CONNECT_TIMEOUT = 10             # seconds for TCP connect
_READ_TIMEOUT = 60                # seconds to wait for inference response


# ── IAM token cache (module-level, thread-safe) ───────────────────────────────

class _IAMTokenCache:
    """Thread-safe cache for a single IBM Cloud IAM Bearer token."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._token: str = ""
        self._expires_at: float = 0.0

    def get_token(self, api_key: str) -> str:
        """Return a valid token, refreshing if necessary."""
        with self._lock:
            if self._token and time.time() < self._expires_at:
                return self._token
            self._token, self._expires_at = self._fetch_token(api_key)
            return self._token

    @staticmethod
    def _fetch_token(api_key: str) -> tuple[str, float]:
        """
        Exchange the API key for a Bearer token via IBM Cloud IAM.
        Returns (token_string, unix_expiry_timestamp).
        Raises RuntimeError on any failure.
        """
        try:
            resp = requests.post(
                IBM_CLOUD_IAM_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"grant_type": _IAM_GRANT_TYPE, "apikey": api_key},
                timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT),
            )
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                f"Cannot reach IBM Cloud IAM ({IBM_CLOUD_IAM_URL}). "
                f"Check your network connection. Detail: {exc}"
            ) from exc
        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"IBM Cloud IAM request timed out after {_READ_TIMEOUT}s."
            )

        if resp.status_code == 400:
            raise RuntimeError(
                "IBM Cloud IAM returned HTTP 400 Bad Request. "
                "Your WATSONX_API_KEY may be invalid or malformed."
            )
        if resp.status_code == 401:
            raise RuntimeError(
                "IBM Cloud IAM returned HTTP 401 Unauthorised. "
                "Your WATSONX_API_KEY has been rejected — check it is current and active."
            )
        if resp.status_code == 429:
            raise RuntimeError(
                "IBM Cloud IAM rate-limited this request (HTTP 429). "
                "Please wait a moment and try again."
            )
        if not resp.ok:
            raise RuntimeError(
                f"IBM Cloud IAM returned HTTP {resp.status_code}. "
                f"Response: {resp.text[:200]}"
            )

        try:
            data = resp.json()
        except ValueError as exc:
            raise RuntimeError(
                f"IBM Cloud IAM returned non-JSON response: {resp.text[:200]}"
            ) from exc

        token: str = data.get("access_token", "")
        if not token:
            raise RuntimeError(
                "IBM Cloud IAM response did not contain an access_token. "
                f"Keys returned: {list(data.keys())}"
            )

        expires_in: int = int(data.get("expires_in", 3600))
        expiry = time.time() + expires_in - _TOKEN_REFRESH_BUFFER_SECS
        # Log only non-sensitive metadata
        logger.info(
            "IAM token obtained successfully. Expires in %ds.", expires_in
        )
        return token, expiry


_token_cache = _IAMTokenCache()


# ── REST inference helper ─────────────────────────────────────────────────────

def _call_watsonx_rest(prompt: str, max_tokens: int) -> str:
    """
    Call the watsonx.ai chat completions REST endpoint directly.
    Uses the current /ml/v1/text/chat API (the older /ml/v1/text/generation
    endpoint is deprecated and does not work with newer Granite models).
    Returns the generated text string.
    Raises RuntimeError on any failure.
    """
    bearer = _token_cache.get_token(IBM_WATSONX_API_KEY)

    base = IBM_WATSONX_URL.rstrip("/")
    url = f"{base}/ml/v1/text/chat?version=2023-05-29"

    payload = {
        "model_id": IBM_GRANITE_MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.3,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
        },
        "project_id": IBM_WATSONX_PROJECT_ID,
    }

    try:
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {bearer}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT),
        )
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Cannot reach watsonx.ai endpoint ({base}). "
            f"Check WATSONX_URL and your network. Detail: {exc}"
        ) from exc
    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"watsonx.ai inference request timed out after {_READ_TIMEOUT}s. "
            "The model may be busy — try again shortly."
        )

    if resp.status_code == 401:
        # Token may have just expired; invalidate cache and raise so caller can retry
        _token_cache._token = ""
        raise RuntimeError(
            "watsonx.ai returned HTTP 401. The IAM token may have expired. "
            "Retry the request — a new token will be obtained automatically."
        )
    if resp.status_code == 404:
        raise RuntimeError(
            f"watsonx.ai returned HTTP 404. "
            f"Model '{IBM_GRANITE_MODEL_ID}' was not found under project "
            f"'{IBM_WATSONX_PROJECT_ID}'. "
            "Verify GRANITE_MODEL_ID and WATSONX_PROJECT_ID in your .env file."
        )
    if resp.status_code == 429:
        raise RuntimeError(
            "watsonx.ai rate limit exceeded (HTTP 429). "
            "Wait a moment before retrying."
        )
    if not resp.ok:
        raise RuntimeError(
            f"watsonx.ai returned HTTP {resp.status_code}. "
            f"Response: {resp.text[:300]}"
        )

    try:
        data = resp.json()
    except ValueError as exc:
        raise RuntimeError(
            f"watsonx.ai returned non-JSON response: {resp.text[:200]}"
        ) from exc

    # Chat API response shape:
    #   {"choices": [{"message": {"role": "assistant", "content": "..."}}]}
    # Fall back to the old generation shape just in case:
    #   {"results": [{"generated_text": "..."}]}
    generated: str = ""

    choices = data.get("choices", [])
    if choices:
        msg = choices[0].get("message", {})
        generated = (msg.get("content") or "").strip()

    if not generated:
        # Try legacy shape
        results = data.get("results", [])
        if results:
            generated = (results[0].get("generated_text") or "").strip()

    if not generated:
        raise RuntimeError(
            "watsonx.ai returned an empty response. "
            f"Response keys: {list(data.keys())}. "
            "The model may not have produced output for this prompt."
        )

    return generated


# ── Provider class ────────────────────────────────────────────────────────────

class IBMGraniteProvider(LLMProvider):
    """
    IBM Granite LLM provider using the watsonx.ai Inference API.

    Integration strategy
    ─────────────────────
    1. Try the ibm-watsonx-ai SDK (if installed) — it handles token rotation
       and retry internally.
    2. If the SDK is not installed, use the pure-requests REST path defined
       above — fully equivalent, no extra dependencies needed.

    In both cases authentication uses the API key set in WATSONX_API_KEY.
    """

    def __init__(self) -> None:
        self._sdk_model = None          # ibm_watsonx_ai ModelInference (if available)
        self._use_sdk: bool = False
        self._initialised: bool = False
        self._init_error: str = ""
        self._try_init()

    # ── Initialisation ────────────────────────────────────────────────────────

    def _try_init(self) -> None:
        """Validate credentials and attempt to initialise the chosen path."""
        if not IBM_WATSONX_API_KEY or IBM_WATSONX_API_KEY in (
            "your_api_key_here", "YOUR_API_KEY_HERE"
        ):
            self._init_error = (
                "WATSONX_API_KEY is not set. "
                "Add it to your .env file to use IBM Granite."
            )
            logger.warning("IBM Granite not configured: API key missing.")
            return

        if not IBM_WATSONX_PROJECT_ID or IBM_WATSONX_PROJECT_ID in (
            "your_project_id_here", "YOUR_PROJECT_ID_HERE"
        ):
            self._init_error = (
                "WATSONX_PROJECT_ID is not set. "
                "Add it to your .env file to use IBM Granite."
            )
            logger.warning("IBM Granite not configured: project ID missing.")
            return

        # Try SDK path first
        if self._try_init_sdk():
            return

        # Fall back to REST path — validate by getting a token
        try:
            _token_cache.get_token(IBM_WATSONX_API_KEY)
            self._use_sdk = False
            self._initialised = True
            logger.info(
                "IBM Granite REST path ready. model=%s project=%s url=%s",
                IBM_GRANITE_MODEL_ID,
                IBM_WATSONX_PROJECT_ID,
                IBM_WATSONX_URL,
            )
        except RuntimeError as exc:
            self._init_error = str(exc)
            logger.error("IBM Granite REST init failed: %s", exc)

    def _try_init_sdk(self) -> bool:
        """
        Attempt initialisation via the ibm-watsonx-ai SDK.
        Returns True if successful, False if the SDK is not installed.
        """
        try:
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

            credentials = Credentials(
                url=IBM_WATSONX_URL,
                api_key=IBM_WATSONX_API_KEY,
            )
            self._sdk_model = ModelInference(
                model_id=IBM_GRANITE_MODEL_ID,
                credentials=credentials,
                project_id=IBM_WATSONX_PROJECT_ID,
                params={
                    GenParams.MAX_NEW_TOKENS: 512,
                    GenParams.TEMPERATURE: 0.3,
                    GenParams.TOP_P: 0.9,
                    GenParams.REPETITION_PENALTY: 1.1,
                },
            )
            self._use_sdk = True
            self._initialised = True
            logger.info(
                "IBM Granite SDK path ready. model=%s project=%s",
                IBM_GRANITE_MODEL_ID,
                IBM_WATSONX_PROJECT_ID,
            )
            return True

        except ImportError:
            logger.info(
                "ibm-watsonx-ai SDK not installed; using direct REST path instead."
            )
            return False
        except Exception as exc:
            # SDK init error doesn't block REST fallback
            logger.warning("ibm-watsonx-ai SDK init failed (%s); trying REST.", exc)
            return False

    # ── LLMProvider interface ─────────────────────────────────────────────────

    @property
    def provider_name(self) -> str:
        path = "SDK" if self._use_sdk else "REST"
        return f"IBM Granite — {IBM_GRANITE_MODEL_ID} ({path})"

    @property
    def is_demo(self) -> bool:
        return False

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate a response via IBM Granite / watsonx.ai."""
        if not self._initialised:
            msg = self._init_error or "IBM Granite provider is not initialised."
            logger.error("generate() called but provider not ready: %s", msg)
            return (
                f"⚠️ IBM Granite is not available: {msg}\n\n"
                "Please check your .env configuration."
            )

        try:
            if self._use_sdk:
                return self._generate_sdk(prompt, max_tokens)
            return self._generate_rest(prompt, max_tokens)
        except RuntimeError as exc:
            logger.error("IBM Granite generation error: %s", exc)
            raise
        except Exception as exc:
            logger.error("Unexpected IBM Granite error: %s", exc)
            raise RuntimeError("Unexpected error while contacting IBM Granite.") from exc

    def _generate_sdk(self, prompt: str, max_tokens: int) -> str:
        """
        Use the SDK chat() method (works with newer Granite / chat models).
        Falls back to generate_text() if chat() is not available.
        """
        try:
            # Prefer the chat interface — works with ibm/granite-4-h-small and newer models
            response = self._sdk_model.chat(
                messages=[{"role": "user", "content": prompt}],
                params={"max_new_tokens": max_tokens},
            )
            # SDK chat response shape: {"choices": [{"message": {"content": "..."}}]}
            choices = response.get("choices", []) if isinstance(response, dict) else []
            if choices:
                content = (choices[0].get("message", {}).get("content") or "").strip()
                if content:
                    return content
        except AttributeError:
            pass  # SDK version doesn't have chat() — fall through to generate_text

        # Fallback: classic generate_text (works with older/base models)
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
        result = self._sdk_model.generate_text(
            prompt=prompt,
            params={GenParams.MAX_NEW_TOKENS: max_tokens},
        )
        if not result:
            raise RuntimeError("IBM Granite SDK returned an empty response.")
        return result.strip()

    def _generate_rest(self, prompt: str, max_tokens: int) -> str:
        return _call_watsonx_rest(prompt, max_tokens)

    def health_check(self) -> dict:
        """Run a minimal inference to verify the end-to-end pipeline works."""
        if not self._initialised:
            return {
                "ok": False,
                "message": self._init_error or "IBM Granite provider is not initialised.",
            }
        try:
            # Use a real farming question — short models respond better to
            # a concrete question than meta-instructions like "say OK"
            test_prompt = "What is the best season to sow wheat in India? Answer in one sentence."
            result = self.generate(test_prompt, max_tokens=40)
            ok = bool(result) and "⚠️" not in result
            return {
                "ok": ok,
                "message": (
                    f"IBM Granite is responding. "
                    f"Model: {IBM_GRANITE_MODEL_ID} | "
                    f"Path: {'SDK' if self._use_sdk else 'REST'}"
                ) if ok else f"IBM Granite health check returned unexpected result: {result[:100]}",
            }
        except Exception as exc:
            return {
                "ok": False,
                "message": f"IBM Granite health check failed: {exc}",
            }
