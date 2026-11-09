#!/usr/bin/env python3
"""
scripts/test_ibm_connection.py
Standalone smoke-test for the IBM watsonx.ai integration.

Usage (from the smart-farming-ai/ project root):
    .\\venv\\Scripts\\python.exe scripts\\test_ibm_connection.py

What this script does
─────────────────────
1. Load credentials from the .env file in the project root.
2. Confirm all required variables are present (without printing their values).
3. Request an IAM Bearer token from IBM Cloud.
4. Send a minimal text-generation request to watsonx.ai (REST path).
5. If the ibm-watsonx-ai SDK is installed, run the same request via the SDK.
6. Run a RAG pipeline smoke-test with one sample farming question.
7. Print PASS / FAIL for each step.

Security rules
──────────────
- API keys, project IDs and tokens are NEVER printed or logged.
- Only non-sensitive metadata is shown (lengths, expiry time, HTTP status).
"""
from __future__ import annotations

import sys
import os
import time

# Ensure the project root is on sys.path so src/ imports resolve correctly
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

# ── Colour helpers (no extra deps) ───────────────────────────────────────────
def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"

def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"

def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"

def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"

PASS = _green("PASS")
FAIL = _red("FAIL")
SKIP = _yellow("SKIP")


# ── Helper ────────────────────────────────────────────────────────────────────

def _mask(value: str) -> str:
    """Show only the first 4 and last 3 characters; mask the rest."""
    if not value or len(value) < 10:
        return "(empty)"
    return f"{value[:4]}{'*' * (len(value) - 7)}{value[-3:]}"


def _check(label: str, ok: bool, detail: str = "") -> bool:
    icon = PASS if ok else FAIL
    line = f"  {icon}  {label}"
    if detail:
        line += f"  —  {detail}"
    print(line)
    return ok


# ── Step 1: Load config ───────────────────────────────────────────────────────

def step_load_config() -> bool:
    print(_bold("\n[1] Load configuration from .env"))
    try:
        from src.config import (
            IBM_WATSONX_API_KEY,
            IBM_WATSONX_PROJECT_ID,
            IBM_WATSONX_URL,
            IBM_GRANITE_MODEL_ID,
            IBM_CLOUD_IAM_URL,
            APP_TITLE,
            APP_ENV,
            APP_PORT,
            LLM_PROVIDER,
        )
    except Exception as exc:
        return _check("Import src.config", False, str(exc))

    all_ok = True
    all_ok &= _check("APP_TITLE loaded",    bool(APP_TITLE),   APP_TITLE)
    all_ok &= _check("APP_ENV loaded",      bool(APP_ENV),     APP_ENV)
    all_ok &= _check(f"APP_PORT = {APP_PORT}", APP_PORT == 8501, str(APP_PORT))
    all_ok &= _check("LLM_PROVIDER",        bool(LLM_PROVIDER), LLM_PROVIDER)
    all_ok &= _check("WATSONX_URL set",     bool(IBM_WATSONX_URL), IBM_WATSONX_URL)
    all_ok &= _check("GRANITE_MODEL_ID",    bool(IBM_GRANITE_MODEL_ID), IBM_GRANITE_MODEL_ID)
    all_ok &= _check("IBM_CLOUD_IAM_URL",   bool(IBM_CLOUD_IAM_URL), IBM_CLOUD_IAM_URL)

    # Show masked credential presence — never show actual values
    key_ok = bool(IBM_WATSONX_API_KEY) and IBM_WATSONX_API_KEY not in (
        "your_api_key_here", "YOUR_API_KEY_HERE", ""
    )
    proj_ok = bool(IBM_WATSONX_PROJECT_ID) and IBM_WATSONX_PROJECT_ID not in (
        "your_project_id_here", "YOUR_PROJECT_ID_HERE", ""
    )
    all_ok &= _check(
        "WATSONX_API_KEY present",
        key_ok,
        f"length={len(IBM_WATSONX_API_KEY)} starts={_mask(IBM_WATSONX_API_KEY)}" if key_ok else "NOT SET",
    )
    all_ok &= _check(
        "WATSONX_PROJECT_ID present",
        proj_ok,
        f"length={len(IBM_WATSONX_PROJECT_ID)} starts={_mask(IBM_WATSONX_PROJECT_ID)}" if proj_ok else "NOT SET",
    )
    return all_ok


# ── Step 2: IAM token (REST) ──────────────────────────────────────────────────

def step_iam_token() -> bool:
    print(_bold("\n[2] Obtain IBM Cloud IAM token (REST)"))
    try:
        from src.config import IBM_WATSONX_API_KEY, IBM_CLOUD_IAM_URL
        from src.llm.ibm_granite_provider import _IAMTokenCache

        if not IBM_WATSONX_API_KEY or IBM_WATSONX_API_KEY == "your_api_key_here":
            return _check("IAM token request", False, "WATSONX_API_KEY not configured — skipping")

        cache = _IAMTokenCache()
        t0 = time.time()
        token = cache.get_token(IBM_WATSONX_API_KEY)
        elapsed = round(time.time() - t0, 2)

        ok = bool(token) and len(token) > 20
        return _check(
            "IAM token obtained",
            ok,
            f"token length={len(token)}, obtained in {elapsed}s" if ok else "empty token returned",
        )
    except RuntimeError as exc:
        return _check("IAM token request", False, str(exc))
    except Exception as exc:
        return _check("IAM token request", False, f"Unexpected error: {exc}")


# ── Step 3: watsonx.ai REST inference ────────────────────────────────────────

def step_rest_inference() -> bool:
    print(_bold("\n[3] watsonx.ai REST inference — minimal test prompt"))
    try:
        from src.config import IBM_WATSONX_API_KEY, IBM_WATSONX_PROJECT_ID

        if not IBM_WATSONX_API_KEY or IBM_WATSONX_API_KEY == "your_api_key_here":
            print(f"  {SKIP}  Credentials not configured — skipping inference test")
            return True  # not a failure — just not configured

        from src.llm.ibm_granite_provider import _call_watsonx_rest

        t0 = time.time()
        result = _call_watsonx_rest(
            "What is the best season to sow wheat in India? Answer in one sentence.",
            max_tokens=60,
        )
        elapsed = round(time.time() - t0, 2)

        ok = bool(result) and len(result) > 5
        _check(
            "REST inference successful",
            ok,
            f"response length={len(result)}, elapsed={elapsed}s",
        )
        if ok:
            print(f"  Preview: {result[:120].replace(chr(10), ' ')}")
        return ok

    except RuntimeError as exc:
        return _check("REST inference", False, str(exc))
    except Exception as exc:
        return _check("REST inference", False, f"Unexpected error: {exc}")


# ── Step 4: SDK inference (optional) ─────────────────────────────────────────

def step_sdk_inference() -> bool:
    print(_bold("\n[4] ibm-watsonx-ai SDK inference (optional)"))
    try:
        import importlib
        if importlib.util.find_spec("ibm_watsonx_ai") is None:
            print(f"  {SKIP}  ibm-watsonx-ai not installed — SDK path not tested")
            return True

        from src.config import IBM_WATSONX_API_KEY

        if not IBM_WATSONX_API_KEY or IBM_WATSONX_API_KEY == "your_api_key_here":
            print(f"  {SKIP}  Credentials not configured — skipping SDK test")
            return True

        from src.llm.ibm_granite_provider import IBMGraniteProvider

        provider = IBMGraniteProvider()
        if not provider._initialised:
            return _check("SDK provider init", False, provider._init_error)

        if not provider._use_sdk:
            print(f"  {SKIP}  SDK init fell back to REST — this is normal if SDK had an issue")
            return True

        t0 = time.time()
        result = provider._generate_sdk(
            "In one sentence, what is the most important step in preparing soil for wheat?",
            max_tokens=60,
        )
        elapsed = round(time.time() - t0, 2)
        ok = bool(result) and len(result) > 5
        _check(
            "SDK inference successful",
            ok,
            f"response length={len(result)}, elapsed={elapsed}s",
        )
        if ok:
            print(f"  Preview: {result[:120].replace(chr(10), ' ')}")
        return ok

    except Exception as exc:
        return _check("SDK inference", False, f"Unexpected error: {exc}")


# ── Step 5: RAG pipeline smoke-test ──────────────────────────────────────────

def step_rag_pipeline() -> bool:
    print(_bold("\n[5] RAG pipeline smoke-test (knowledge retrieval + LLM)"))
    try:
        from src.data_loader import load_all_chunks
        from src.retrieval import get_retriever
        from src.rag_pipeline import run_rag

        chunks = load_all_chunks()
        _check("Knowledge base loaded", len(chunks) > 0, f"{len(chunks)} chunks")

        retriever = get_retriever(chunks)
        _check("Retriever built", retriever.is_ready, "TF-IDF index ready")

        from src.config import LLM_PROVIDER
        question = "What are the best sowing practices for rice in Tamil Nadu?"
        t0 = time.time()
        response = run_rag(question, retriever, lang_code="en")
        elapsed = round(time.time() - t0, 2)

        answer_ok = bool(response.answer) and len(response.answer) > 20 and not response.provider_error
        _check(
            "RAG answer generated",
            answer_ok,
            f"provider={'IBM Granite' if not response.is_demo else 'Demo'}, "
            f"sources={len(response.sources)}, elapsed={elapsed}s",
        )
        _check(
            "Sources returned",
            len(response.sources) > 0,
            str(response.sources[:3]),
        )
        if response.provider_error:
            print("  Granite inference failed; no demo response was substituted.")
        elif response.is_demo:
            print(f"  Note: Demo mode active (LLM_PROVIDER={LLM_PROVIDER}). "
                  "Set LLM_PROVIDER=ibm_granite in .env to test real Granite responses.")
        else:
            print(f"  IBM Granite is providing RAG answers.")
        return answer_ok

    except Exception as exc:
        return _check("RAG pipeline", False, f"Unexpected error: {exc}")


# ── Step 6: Streamlit port check ─────────────────────────────────────────────

def step_port_check() -> bool:
    print(_bold("\n[6] Streamlit port configuration"))
    try:
        from src.config import APP_PORT
        ok = APP_PORT == 8501
        return _check(
            f"APP_PORT = {APP_PORT}",
            ok,
            "matches Streamlit default" if ok else "non-standard port — update your run command",
        )
    except Exception as exc:
        return _check("APP_PORT check", False, str(exc))


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(_bold("=" * 60))
    print(_bold("  Smart Farming AI — IBM watsonx.ai Connection Test"))
    print(_bold("=" * 60))

    results: list[bool] = []
    results.append(step_load_config())
    results.append(step_iam_token())
    results.append(step_rest_inference())
    results.append(step_sdk_inference())
    results.append(step_rag_pipeline())
    results.append(step_port_check())

    passed = sum(results)
    total = len(results)
    print(_bold("\n" + "=" * 60))
    colour = _green if passed == total else _red
    print(colour(f"  Result: {passed}/{total} steps passed"))
    print(_bold("=" * 60))

    if passed < total:
        print(
            "\nTo fix failures:\n"
            "  1. Copy .env.example to .env and fill in WATSONX_API_KEY and\n"
            "     WATSONX_PROJECT_ID with your real IBM Cloud credentials.\n"
            "  2. Set LLM_PROVIDER=ibm_granite in .env.\n"
            "  3. Install the SDK (optional):  pip install ibm-watsonx-ai\n"
            "  4. Re-run this script.\n"
        )
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
