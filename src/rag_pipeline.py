"""
src/rag_pipeline.py
Orchestrates the Retrieval-Augmented Generation workflow:
  1. Retrieve relevant knowledge chunks for the query.
  2. Build a grounded prompt from retrieved context.
  3. Call the configured LLM provider.
  4. Return structured response with sources and confidence.

The LLM is explicitly instructed to answer only from the retrieved context
and to clearly state when information is insufficient.
"""
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from src.config import LLM_PROVIDER, RAG_TOP_K
from src.language_service import get_label, get_language_instruction
from src.retrieval import KnowledgeRetriever

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """Structured response from the RAG pipeline."""
    answer: str
    sources: list[str] = field(default_factory=list)
    retrieved_chunks: list[dict] = field(default_factory=list)
    confidence: str = ""
    is_demo: bool = False
    provider_error: bool = False
    has_safety_content: bool = False
    language_code: str = "en"
    provider_diagnostic: str = ""


def _get_llm_provider():
    """
    Lazy-import and instantiate the configured LLM provider.
    Returns (provider_instance, is_demo).
    """
    provider_key = LLM_PROVIDER.lower()

    if provider_key == "ibm_granite":
        from src.llm.ibm_granite_provider import IBMGraniteProvider
        provider = IBMGraniteProvider()
        # Fall back to demo if IBM credentials not configured
        if not provider._initialised:
            logger.warning(
                "IBM Granite not initialised (%s). Falling back to demo provider.",
                provider._init_error,
            )
            from src.llm.demo_provider import DemoProvider
            return DemoProvider(diagnostic=provider._init_error), True
        return provider, False
    else:
        from src.llm.demo_provider import DemoProvider
        return DemoProvider(), True


def _build_prompt(
    question: str,
    context_chunks: list[dict],
    lang_code: str = "en",
    profile: Optional[dict] = None,
) -> str:
    """
    Assemble the RAG prompt from retrieved context chunks and the farmer's question.
    """
    # Build context string from retrieved chunks
    if context_chunks:
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk.get("source", "knowledge base")
            topic = chunk.get("topic", "")
            crop = chunk.get("crop_name", "")
            label = f"[{i}] Source: {source}"
            if crop:
                label += f" | Crop: {crop}"
            if topic:
                label += f" | Topic: {topic}"
            references = chunk.get("references", [])
            if references:
                citation_text = "; ".join(
                    f"{ref.get('title', 'Reference')} ({ref.get('url', '')})"
                    for ref in references
                )
                label += f" | References: {citation_text}"
            context_parts.append(f"{label}\n{chunk['text']}")
        context_text = "\n\n".join(context_parts)
    else:
        context_text = "No relevant information found in the knowledge base."

    # Build profile context string
    profile_text = ""
    if profile:
        parts = []
        if profile.get("state"):
            parts.append(f"State: {profile['state']}")
        if profile.get("district"):
            parts.append(f"District: {profile['district']}")
        if profile.get("crop"):
            parts.append(f"Crop: {profile['crop']}")
        if profile.get("soil_type"):
            parts.append(f"Soil type: {profile['soil_type']}")
        if profile.get("irrigation"):
            parts.append(f"Irrigation: {profile['irrigation']}")
        if parts:
            profile_text = f"Farmer context: {', '.join(parts)}\n"

    lang_instruction = get_language_instruction(lang_code)

    prompt = f"""You are a helpful and careful AI farming assistant for Indian farmers.

Your role is to provide accurate, safety-conscious agricultural guidance.

IMPORTANT RULES:
- Answer ONLY based on the retrieved knowledge provided below.
- Cite each factual recommendation using the numbered excerpt marker, such as [1] or [2]. Cite only excerpts that support the claim.
- If the retrieved knowledge does not contain enough information, say so clearly and suggest the farmer consult their local KVK or agricultural officer.
- Do NOT invent weather alerts, market prices, pesticide names/doses or crop statistics.
- Safety information always takes priority over productivity advice.
- If the question involves electrical hazards, pesticide exposure, flooding, lightning or heatstroke, include the relevant safety guidance prominently.
- Ask for clarification if the question is ambiguous and important details (crop, location, symptom) are missing.
- Do not guarantee yields, market prices or crop success.

{profile_text}
--- RETRIEVED KNOWLEDGE ---
{context_text}

--- FARMER'S QUESTION ---
{question}

--- LANGUAGE INSTRUCTION ---
{lang_instruction}

Please provide a helpful, grounded and safety-conscious answer:"""

    return prompt


def run_rag(
    question: str,
    retriever: KnowledgeRetriever,
    lang_code: str = "en",
    profile: Optional[dict] = None,
    top_k: int = RAG_TOP_K,
    force_safety: bool = False,
) -> RAGResponse:
    """
    Main RAG pipeline entry point.

    Args:
        question: The farmer's question.
        retriever: An initialised KnowledgeRetriever instance.
        lang_code: Target language code for the response.
        profile: Optional farmer profile dict (state, district, crop, soil_type, etc.).
        top_k: Number of chunks to retrieve.
        force_safety: If True, always prepend safety chunks.

    Returns:
        RAGResponse with answer, sources, retrieved_chunks and metadata.
    """
    if not question or not question.strip():
        return RAGResponse(
            answer="Please enter a question.",
            confidence="",
            language_code=lang_code,
        )

    # ── Step 1: Retrieve only the best-fit topic and crop context ─────────────
    is_safety = retriever.is_safety_query(question) or force_safety
    if is_safety:
        final_chunks = retriever.search_safety(question)[:top_k + 2]
        logger.info("Safety keywords detected. Retrieved %d safety excerpts.", len(final_chunks))
    else:
        crop_filter = profile.get("crop_id") if profile else None
        state_filter = profile.get("state") if profile else None
        topic_filter = retriever.infer_topic_filter(question)
        retrieval_limit = max(top_k + 2, 12) if topic_filter == "crop_lifecycle" else top_k + 2
        final_chunks = retriever.search(
            query=question,
            top_k=retrieval_limit,
            crop_filter=crop_filter,
            state_filter=state_filter,
            topic_filter=topic_filter,
        )

    # ── Step 3: Build prompt ──────────────────────────────────────────────────
    prompt = _build_prompt(question, final_chunks, lang_code, profile)

    # ── Step 4: Call LLM ──────────────────────────────────────────────────────
    provider, is_demo = _get_llm_provider()
    provider_diagnostic = getattr(provider, "diagnostic", "")

    provider_error = False
    try:
        raw_answer = provider.generate(prompt)
        if not raw_answer or not raw_answer.strip():
            raise RuntimeError("The configured language model returned an empty response.")
    except Exception as exc:
        logger.error("LLM generate() error: %s", exc)
        provider_error = True
        provider_diagnostic = str(exc)
        raw_answer = (
            get_label("granite_response_unavailable", lang_code)
            if not is_demo else
            "An error occurred while generating the response. Please try again or consult your local agricultural officer."
        )

    # ── Step 5: Keep demo answers honest about language availability ───────────
    # The local demo provider emits English knowledge text. Do not present it as
    # a selected-language answer when live Granite translation is unavailable.
    if is_demo and lang_code != "en":
        raw_answer = get_label("demo_language_unavailable", lang_code)

    # ── Step 6: Show only cited context sources ────────────────────────────────
    # DemoProvider includes every selected context excerpt in its response.
    # Granite responses must cite numbered excerpts, so unused context is not
    # presented as a source for the generated answer.
    if provider_error or (is_demo and lang_code != "en"):
        cited_chunks = []
    elif is_demo:
        cited_chunks = final_chunks
    else:
        citation_numbers = {
            int(number) for number in re.findall(r"\[(\d+)\]", raw_answer)
            if 1 <= int(number) <= len(final_chunks)
        }
        cited_chunks = [
            chunk for number, chunk in enumerate(final_chunks, 1)
            if number in citation_numbers
        ]

    source_items: dict[str, str] = {}
    for chunk in cited_chunks:
        references = chunk.get("references", [])
        if references:
            for reference in references:
                title = reference.get("title", "Agricultural source")
                url = reference.get("url", "")
                key = url or title
                source_items[key] = f"[{title}]({url})" if url else title
        elif chunk.get("source"):
            source_items[chunk["source"]] = chunk["source"]
    sources = sorted(source_items.values())

    # ── Step 7: Confidence note ───────────────────────────────────────────────
    if not final_chunks:
        confidence = get_label("confidence_no_match", lang_code)
    elif len(final_chunks) >= 3:
        confidence = get_label("confidence_based", lang_code).format(count=len(final_chunks))
    else:
        confidence = get_label("confidence_limited", lang_code)

    return RAGResponse(
        answer=raw_answer,
        sources=sources,
        retrieved_chunks=final_chunks,
        confidence=confidence,
        is_demo=is_demo,
        provider_error=provider_error,
        has_safety_content=is_safety,
        language_code=lang_code,
        provider_diagnostic=provider_diagnostic,
    )
