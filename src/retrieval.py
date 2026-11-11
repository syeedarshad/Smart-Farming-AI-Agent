"""
src/retrieval.py
TF-IDF + cosine similarity retrieval engine for the RAG pipeline.
No native binary dependencies required.
"""
import logging
import re
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import RAG_TOP_K, RAG_MIN_SCORE, SAFETY_KEYWORDS

logger = logging.getLogger(__name__)

# Small, explicit agriculture vocabulary bridges the four supported question
# languages to the English source corpus. The original text remains intact for
# Granite; only the local retrieval query is expanded.
_QUERY_CONCEPTS = (
    (("cotton", "cottons", "paruthi", "பருத்தி", "పత్తి", "कपास"), "cotton"),
    (("pest", "pests", "insect", "insects", "பூச்சி", "பூச்சிகள்", "చీడపీడ", "పురుగ", "कीट"), "pest insect bollworm whitefly"),
    (("organic", "natural", "இயற்கை", "செயற்கை இல்லா", "సేంద్రియ", "సేంద్రీయ", "జైవిక", "जैविक", "प्राकृतिक"), "organic natural biological IPM"),
    (("manage", "management", "control", "கட்டுப்படுத்து", "கட்டுப்பாடு", "నిర్వహ", "నియంత్ర", "నివార", "प्रबंधन", "नियंत्र", "काबू"), "management control"),
    (("rice", "paddy", "நெல்", "వరి", "धान"), "rice paddy"),
)

_LIFECYCLE_TERMS = (
    "lifecycle", "life cycle", "crop cycle", "growth stages", "growth stage",
    "crop stages", "stages of", "stage-wise", "stage wise",
)
_PEST_TERMS = (
    "pest", "pests", "insect", "insects", "bollworm", "whitefly", "aphid",
    "பூச்சி", "பூச்சிகள்", "சீமைப்பூச்சி", "చీడపీడ", "పురుగు", "कीट", "कीड़ों",
)
_NATURAL_FARMING_TERMS = (
    "natural farming", "organic farming", "natural practice", "natural practices",
    "compost", "vermicompost", "jeevamrutha", "soil health", "organic matter",
    "இயற்கை விவசாய", "இயற்கை உரம்", "సహజ వ్యవసాయ", "సేంద్రియ వ్యవసాయ", "प्राकृतिक खेती",
)


def _contains_term(query: str, term: str) -> bool:
    """Match whole Latin terms and native-script phrases without substring noise."""
    if term.isascii() and re.fullmatch(r"[a-z0-9 ]+", term, flags=re.IGNORECASE):
        return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", query, flags=re.IGNORECASE) is not None
    return term.casefold() in query.casefold()


def _infer_safety_id(query: str) -> Optional[str]:
    """Scope high-risk safety questions to the matching safety practice."""
    electrical_terms = (
        "electric", "electrical", "electrocution", "electrocute", "wiring",
        "earthing", "rccb", "water pump", "pump motor", "water motor",
        "irrigation pump", "மின்சார", "மின் பாதுகாப்பு", "విద్యుత్", "बिजली",
    )
    if any(_contains_term(query, term) for term in electrical_terms):
        return "electrical_safety"
    if any(_contains_term(query, term) for term in ("pesticide", "chemical exposure", "spray accident")):
        return "pesticide_safety"
    return None


def _expanded_retrieval_query(query: str) -> str:
    """Add English search terms for known Tamil, Telugu and Hindi farm terms."""
    folded = query.casefold()
    additions = []
    for aliases, expansion in _QUERY_CONCEPTS:
        if any(alias.casefold() in folded for alias in aliases):
            additions.extend(expansion.split())
    return f"{query} {' '.join(dict.fromkeys(additions))}".strip() if additions else query


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
        safety_id_filter: Optional[str] = None,
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

        # A topic hint narrows the candidate set before cosine ranking. This
        # prevents shared words such as "irrigation" or "organic" from pulling
        # in unrelated roadmaps when the question clearly names a domain.
        if topic_filter is None:
            topic_filter = self.infer_topic_filter(query)
        if topic_filter == "safety" and safety_id_filter is None:
            safety_id_filter = _infer_safety_id(query)

        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix)[0]
        expanded_query = _expanded_retrieval_query(query)
        if expanded_query != query:
            expanded_vec = self._vectorizer.transform([expanded_query])
            expanded_scores = cosine_similarity(expanded_vec, self._matrix)[0]
            # Preserve exact-language matches while allowing the mapped English
            # terms to rescue multilingual queries against the English corpus.
            scores = np.maximum(scores, expanded_scores)

        # Apply metadata pre-filters to narrow the candidate set.
        candidate_indices = list(range(len(self._chunks)))

        effective_crop_filter = crop_filter or self._infer_crop_filter(query)

        if effective_crop_filter:
            crop_filter_lower = effective_crop_filter.lower()
            candidate_indices = [
                i for i in candidate_indices
                if crop_filter_lower in self._chunks[i].get("crop_id", "").lower()
                or crop_filter_lower in self._chunks[i].get("crop_name", "").lower()
                or self._chunks[i].get("crop_id") == "general"
                or self._chunks[i].get("topic") in {"natural_farming", "safety"}
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

        if safety_id_filter:
            candidate_indices = [
                i for i in candidate_indices
                if self._chunks[i].get("safety_id") == safety_id_filter
            ]

        if not candidate_indices:
            return []

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

    def infer_topic_filter(self, query: str) -> Optional[str]:
        """Infer a narrow knowledge domain for clearly scoped farm questions."""
        if self.is_safety_query(query):
            return "safety"
        if any(_contains_term(query, term) for term in _LIFECYCLE_TERMS):
            return "crop_lifecycle"
        if any(_contains_term(query, term) for term in _PEST_TERMS):
            return "pest_disease"
        if any(_contains_term(query, term) for term in _NATURAL_FARMING_TERMS):
            return "natural_farming"
        return None

    def _infer_crop_filter(self, query: str) -> Optional[str]:
        """Detect crop names from indexed metadata when the farmer profile is blank."""
        matches: list[tuple[int, str]] = []
        seen: set[tuple[str, str]] = set()
        for chunk in self._chunks:
            crop_id = chunk.get("crop_id", "")
            if not crop_id or crop_id == "general":
                continue
            aliases = [
                crop_id.replace("_", " "),
                chunk.get("crop_name", ""),
                chunk.get("name_ta", ""),
                chunk.get("name_te", ""),
                chunk.get("name_hi", ""),
            ]
            for alias in aliases:
                alias = str(alias).strip()
                key = (crop_id, alias.casefold())
                if not alias or key in seen:
                    continue
                seen.add(key)
                if _contains_term(query, alias):
                    matches.append((len(alias), crop_id))
        return max(matches, default=(0, ""))[1] or None

    def search_safety(self, query: str) -> list[dict]:
        """
        Dedicated search scoped to safety topic only.
        Used when safety keywords are detected in the query.
        """
        safety_id = _infer_safety_id(query)
        return self.search(
            query,
            top_k=9,
            topic_filter="safety",
            safety_id_filter=safety_id,
            min_score=0.01,
        )[:3]

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
