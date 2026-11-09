"""
src/farming_advisor.py
High-level query handler used by all Streamlit pages.
Initialises the retriever on first call (cached in Streamlit session state).
Provides convenience functions for each module.
"""
import logging
from typing import Optional

from src.data_loader import load_all_chunks
from src.retrieval import KnowledgeRetriever
from src.rag_pipeline import RAGResponse, run_rag

logger = logging.getLogger(__name__)

# ── Cached knowledge state ────────────────────────────────────────────────────
_chunks: Optional[list[dict]] = None
_retriever: Optional[KnowledgeRetriever] = None


def _get_retriever() -> KnowledgeRetriever:
    """
    Lazy-initialise the knowledge retriever.
    Loads and indexes all chunks exactly once per process lifetime.
    """
    global _chunks, _retriever
    if _retriever is None or not _retriever.is_ready:
        logger.info("Initialising knowledge retriever...")
        _chunks = load_all_chunks()
        _retriever = KnowledgeRetriever()
        _retriever.build_index(_chunks)
        logger.info("Retriever ready. Chunks: %d", _retriever.chunk_count)
    return _retriever


# ── Public API ────────────────────────────────────────────────────────────────

def ask(
    question: str,
    lang_code: str = "en",
    profile: Optional[dict] = None,
) -> RAGResponse:
    """
    Answer a general farming question using the RAG pipeline.

    Args:
        question: Farmer's question (any language).
        lang_code: Response language code.
        profile: Farmer profile dict (state, district, crop, soil_type, ...).

    Returns:
        RAGResponse with answer, sources and metadata.
    """
    retriever = _get_retriever()
    return run_rag(
        question=question,
        retriever=retriever,
        lang_code=lang_code,
        profile=profile,
    )


def get_crop_roadmap_answer(
    crop_id: str,
    stage_name: str,
    question: str,
    lang_code: str = "en",
    profile: Optional[dict] = None,
) -> RAGResponse:
    """
    Answer a question specific to a crop lifecycle stage.
    Boosts retrieval towards that crop's roadmap stage.
    """
    retriever = _get_retriever()
    enhanced_query = f"{crop_id} {stage_name} {question}"
    enhanced_profile = dict(profile or {})
    enhanced_profile["crop_id"] = crop_id
    return run_rag(
        question=enhanced_query,
        retriever=retriever,
        lang_code=lang_code,
        profile=enhanced_profile,
        top_k=6,
    )


def get_pest_advice(
    crop_name: str,
    symptoms: str,
    lang_code: str = "en",
    profile: Optional[dict] = None,
) -> RAGResponse:
    """
    Get pest and disease advice for a crop based on symptoms.
    Always includes IPM principles and safety guidance.
    """
    retriever = _get_retriever()
    query = f"{crop_name} pest disease symptoms: {symptoms}"
    enhanced_profile = dict(profile or {})
    enhanced_profile["crop_id"] = crop_name.lower().replace(" ", "_")
    return run_rag(
        question=query,
        retriever=retriever,
        lang_code=lang_code,
        profile=enhanced_profile,
        top_k=7,
    )


def get_safety_info(
    hazard_type: str,
    lang_code: str = "en",
) -> RAGResponse:
    """
    Retrieve safety information for a specific hazard.
    Forces safety topic in retrieval.
    """
    retriever = _get_retriever()
    return run_rag(
        question=f"safety guidance for {hazard_type}",
        retriever=retriever,
        lang_code=lang_code,
        force_safety=True,
    )


def get_natural_farming_info(
    practice: str,
    lang_code: str = "en",
) -> RAGResponse:
    """
    Retrieve natural farming practice information.
    """
    retriever = _get_retriever()
    return run_rag(
        question=f"natural farming {practice}",
        retriever=retriever,
        lang_code=lang_code,
        top_k=5,
    )


def get_crop_info(crop_name: str, lang_code: str = "en") -> RAGResponse:
    """
    Retrieve general crop information.
    """
    retriever = _get_retriever()
    return run_rag(
        question=f"crop information {crop_name}",
        retriever=retriever,
        lang_code=lang_code,
        profile={"crop_id": crop_name.lower().replace(" ", "_")},
        top_k=5,
    )


def get_knowledge_stats() -> dict:
    """Return stats about the loaded knowledge base."""
    retriever = _get_retriever()
    return {
        "total_chunks": retriever.chunk_count,
        "retriever_ready": retriever.is_ready,
    }


def get_all_crop_ids() -> list[str]:
    """Get all crop IDs from the loaded chunks."""
    retriever = _get_retriever()
    crop_ids = set()
    if _chunks:
        for chunk in _chunks:
            cid = chunk.get("crop_id")
            if cid and cid not in ("general", "unknown"):
                crop_ids.add(cid)
    return sorted(crop_ids)
