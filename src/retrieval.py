"""
src/retrieval.py
TF-IDF + cosine similarity retrieval engine for the RAG pipeline.
No native binary dependencies required.
"""
import logging
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import RAG_TOP_K, RAG_MIN_SCORE, SAFETY_KEYWORDS

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """
    Builds a TF-IDF index over text chunks and retrieves
    the most relevant ones for a given query.
    """

    def __init__(self) -> None:
        self._chunks: list[dict] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._matrix = None  # sparse TF-IDF matrix
        self._is_ready = False

    def build_index(self, chunks: list[dict]) -> None:
        """
        Vectorise all chunks and build the TF-IDF index.
        Must be called before search().
        """
        if not chunks:
            logger.warning("No chunks provided to build_index.")
            return

        self._chunks = chunks
        texts = [c["text"] for c in chunks]

        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
            strip_accents="unicode",
        )
        self._matrix = self._vectorizer.fit_transform(texts)
        self._is_ready = True
        logger.info("TF-IDF index built: %d chunks, %d features",
                    len(chunks), self._matrix.shape[1])

    def search(
        self,
        query: str,
        top_k: int = RAG_TOP_K,
        min_score: float = RAG_MIN_SCORE,
        crop_filter: Optional[str] = None,
        state_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Retrieve top_k most relevant chunks for the given query.

        Returns a list of dicts, each with:
          - text: str
          - score: float (cosine similarity)
          - source, topic, and other metadata from the original chunk
        """
        if not self._is_ready:
            logger.warning("Retriever index not built. Call build_index() first.")
            return []

        if not query or not query.strip():
            return []

        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix)[0]

        # Apply metadata pre-filters to narrow the candidate set
        candidate_indices = list(range(len(self._chunks)))

        if crop_filter:
            crop_filter_lower = crop_filter.lower()
            candidate_indices = [
                i for i in candidate_indices
                if crop_filter_lower in self._chunks[i].get("crop_id", "").lower()
                or crop_filter_lower in self._chunks[i].get("crop_name", "").lower()
            ]

        if state_filter:
            state_filter_lower = state_filter.lower()
            state_candidates = [
                i for i in candidate_indices
                if state_filter_lower in self._chunks[i].get("state", "").lower()
            ]
            # If state filter yields results, use them; otherwise keep all candidates
            if state_candidates:
                candidate_indices = state_candidates

        if topic_filter:
            candidate_indices = [
                i for i in candidate_indices
                if self._chunks[i].get("topic", "") == topic_filter
            ]

        if not candidate_indices:
            candidate_indices = list(range(len(self._chunks)))

        # Score and rank candidates
        ranked = sorted(
            [(i, float(scores[i])) for i in candidate_indices],
            key=lambda x: x[1],
            reverse=True,
        )

        results = []
        for idx, score in ranked[:top_k]:
            if score < min_score:
                continue
            result = dict(self._chunks[idx])
            result["score"] = round(score, 4)
            results.append(result)

        return results

    def search_safety(self, query: str) -> list[dict]:
        """
        Dedicated search scoped to safety topic only.
        Used when safety keywords are detected in the query.
        """
        return self.search(query, top_k=3, topic_filter="safety", min_score=0.01)

    def is_safety_query(self, query: str) -> bool:
        """Check whether the query contains safety-critical keywords."""
        query_lower = query.lower()
        return any(kw.lower() in query_lower for kw in SAFETY_KEYWORDS)

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

    @property
    def is_ready(self) -> bool:
        return self._is_ready


# ── module-level singleton ────────────────────────────────────────────────────
# Created once; pages call get_retriever() which loads lazily via Streamlit cache.

_retriever_instance: Optional[KnowledgeRetriever] = None


def get_retriever(chunks: Optional[list[dict]] = None) -> KnowledgeRetriever:
    """
    Return the module-level retriever singleton.
    If chunks are provided and the retriever is not built yet, build the index.
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeRetriever()

    if chunks and not _retriever_instance.is_ready:
        _retriever_instance.build_index(chunks)

    return _retriever_instance
