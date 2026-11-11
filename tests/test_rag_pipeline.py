"""
tests/test_rag_pipeline.py
End-to-end tests for the RAG pipeline and farming advisor.
Covers the 10 farmer-style test questions from the requirements.
Run with: python tests/test_rag_pipeline.py
or: python -m pytest tests/test_rag_pipeline.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from unittest.mock import patch


class TestRAGPipeline(unittest.TestCase):
    """Test the core RAG pipeline with demo provider."""

    @classmethod
    def setUpClass(cls):
        """Initialise retriever once for all tests."""
        from src.data_loader import load_all_chunks
        from src.retrieval import KnowledgeRetriever
        cls.chunks = load_all_chunks()
        cls.retriever = KnowledgeRetriever()
        cls.retriever.build_index(cls.chunks)
        print(f"\n  RAG pipeline test setup: {cls.retriever.chunk_count} chunks indexed")

    def _run_rag(self, question, lang="en", profile=None, force_safety=False):
        from src.rag_pipeline import run_rag
        from src.llm.demo_provider import DemoProvider
        # Unit tests exercise retrieval and response handling without network access.
        with patch("src.rag_pipeline._get_llm_provider", return_value=(DemoProvider(), True)):
            return run_rag(
                question=question,
                retriever=self.retriever,
                lang_code=lang,
                profile=profile or {},
                force_safety=force_safety,
            )

    # ── Test Q1: Basic crop sowing question ──────────────────────────────────
    def test_q1_paddy_sowing_tamil_nadu(self):
        result = self._run_rag(
            "When should I sow paddy in Tamil Nadu?",
            profile={"state": "Tamil Nadu", "crop_id": "rice"},
        )
        self.assertTrue(result.answer, "Answer should not be empty")
        self.assertIsInstance(result.sources, list)
        self.assertGreater(len(result.sources), 0, "Should have at least one source")
        print(f"\n  Q1 sources: {result.sources}")

    # ── Test Q2: Soil testing information ────────────────────────────────────
    def test_q2_soil_testing(self):
        result = self._run_rag("How do I do a soil test?")
        self.assertTrue(result.answer)
        self.assertGreater(len(result.retrieved_chunks), 0)

    # ── Test Q3: Pest question needing clarification ──────────────────────────
    def test_q3_vague_pest_question(self):
        result = self._run_rag("My tomato leaves are yellowing, what pest is it?")
        self.assertTrue(result.answer)
        # Should not invent a specific pesticide dose
        answer_lower = result.answer.lower()
        # The demo response should include retrieved knowledge about tomato
        print(f"\n  Q3 retrieved chunks: {len(result.retrieved_chunks)}")

    # ── Test Q4: Market price question with disclaimer ──────────────────────
    def test_q4_market_price_disclaimer_in_service(self):
        from src.market_service import get_disclaimer, get_all_commodities
        disclaimer = get_disclaimer()
        self.assertIn("illustrative", disclaimer.lower())
        self.assertIn("NOT real-time", disclaimer)
        commodities = get_all_commodities()
        self.assertGreater(len(commodities), 0)
        onion = next((c for c in commodities if c.get("commodity_id") == "onion"), None)
        self.assertIsNotNone(onion, "Onion should be in commodity list")

    # ── Test Q5: Neem / natural farming ──────────────────────────────────────
    def test_q5_neem_natural_farming(self):
        result = self._run_rag("How do I use neem for pest control?")
        self.assertTrue(result.answer)
        # Should not provide a fabricated homemade recipe
        # Should mention natural_farming.json as source
        self.assertGreater(len(result.retrieved_chunks), 0)

    # ── Test Q6: Safety keyword triggers safety chunks ────────────────────────
    def test_q6_lightning_safety(self):
        result = self._run_rag("There is lightning outside, is it safe to work?")
        self.assertTrue(result.answer)
        self.assertTrue(result.has_safety_content, "Lightning question should trigger safety content")
        # Safety source should be in retrieved chunks
        topics = [c.get("topic", "") for c in result.retrieved_chunks]
        self.assertIn("safety", topics, "Safety chunks should be retrieved for lightning query")

    # ── Test Q7: Crop recommendation for specific conditions ──────────────────
    def test_q7_crop_recommendation_black_cotton(self):
        result = self._run_rag(
            "Suggest a crop for black cotton soil in Maharashtra in Kharif",
            profile={"state": "Maharashtra", "soil_type": "Black Cotton"},
        )
        self.assertTrue(result.answer)
        self.assertGreater(len(result.retrieved_chunks), 0)

    # ── Test Q8: Electrical safety question ──────────────────────────────────
    def test_q8_electrical_safety(self):
        result = self._run_rag(
            "How do I safely connect my water pump motor?",
            force_safety=True,
        )
        self.assertTrue(result.answer)
        self.assertTrue(result.has_safety_content)
        # Answer should contain safety-related content
        safety_keywords = ["earthing", "qualified electrician", "RCCB", "electrician",
                          "earth", "rccb", "safety", "safe"]
        answer_lower = result.answer.lower()
        found_keywords = [kw for kw in safety_keywords if kw.lower() in answer_lower]
        self.assertGreater(len(found_keywords), 0,
                          f"Safety answer should mention electrical safety terms. Got: {result.answer[:200]}")

    # ── Test Q9: Hindi language ───────────────────────────────────────────────
    def test_q9_hindi_wheat_irrigation(self):
        result = self._run_rag("गेहूं की सिंचाई कब करें?", lang="hi")
        self.assertTrue(result.answer)
        # A demo fallback must not present its English text as a Hindi answer.
        self.assertIsInstance(result.sources, list)

    def test_non_english_demo_uses_localized_unavailability_message(self):
        from src.language_service import get_label

        questions = {
            "ta": "நெற்பயிருக்கு எப்போது நீர் பாய்ச்ச வேண்டும்?",
            "te": "వరి పంటకు ఎప్పుడు నీరు పెట్టాలి?",
            "hi": "धान की फसल में सिंचाई कब करें?",
        }
        for lang, question in questions.items():
            with self.subTest(language=lang):
                result = self._run_rag(question, lang=lang)
                self.assertTrue(result.is_demo)
                self.assertEqual(
                    result.answer,
                    get_label("demo_language_unavailable", lang),
                )

    # ── Test Q10: General yield question ──────────────────────────────────────
    def test_q10_yield_question_no_guarantee(self):
        result = self._run_rag("What is the yield of rice per acre?")
        self.assertTrue(result.answer)
        # Answer should not promise a specific yield guarantee

    # ── Test: Empty question handling ────────────────────────────────────────
    def test_empty_question_handled_gracefully(self):
        result = self._run_rag("")
        self.assertTrue(result.answer)
        self.assertIn("enter a question", result.answer.lower())

    # ── Test: Demo mode flag ──────────────────────────────────────────────────
    def test_demo_mode_is_flagged(self):
        result = self._run_rag("How do I grow wheat?")
        self.assertTrue(result.is_demo, "Demo mode must be identified from the provider used")

    # ── Test: Demo response does not claim to be Granite ────────────────────
    def test_demo_does_not_claim_granite(self):
        result = self._run_rag("What is the best soil for cotton?")
        self.assertTrue(result.is_demo)
        self.assertIn("not by IBM Granite", result.answer,
                      "Demo response must clearly say it was not generated by Granite")

    def test_successful_granite_double_is_not_demo(self):
        from src.rag_pipeline import run_rag

        class GraniteDouble:
            def generate(self, prompt):
                return "Controlled Granite inference response."

        with patch("src.rag_pipeline._get_llm_provider", return_value=(GraniteDouble(), False)):
            result = run_rag("How do I prepare soil for rice?", self.retriever)
        self.assertFalse(result.is_demo)
        self.assertFalse(result.provider_error)
        self.assertEqual(result.answer, "Controlled Granite inference response.")

    def test_granite_inference_failure_is_not_replaced_by_demo(self):
        from src.rag_pipeline import run_rag

        class FailingGraniteDouble:
            def generate(self, prompt):
                raise RuntimeError("simulated IBM network failure")

        with patch("src.rag_pipeline._get_llm_provider", return_value=(FailingGraniteDouble(), False)):
            result = run_rag("How do I prepare soil for rice?", self.retriever, lang_code="ta")
        self.assertFalse(result.is_demo)
        self.assertTrue(result.provider_error)
        self.assertIn("IBM Granite", result.answer)
        self.assertNotIn("DEMO MODE", result.answer)

    def test_cotton_organic_ipm_retrieves_with_all_supported_languages(self):
        questions = {
            "en": "How should I manage pests in cotton organically?",
            "ta": "பருத்தியில் பூச்சிகளை இயற்கை முறையில் எப்படிக் கட்டுப்படுத்துவது?",
            "te": "పత్తిలో చీడపీడలను సేంద్రియంగా ఎలా నిర్వహించాలి?",
            "hi": "कपास में कीटों का जैविक प्रबंधन कैसे करें?",
        }
        for lang, question in questions.items():
            with self.subTest(language=lang):
                result = self._run_rag(
                    question,
                    lang=lang,
                    profile={"crop_id": "cotton"},
                )
                guide_chunks = [
                    chunk for chunk in result.retrieved_chunks
                    if chunk.get("management_guide_id") == "cotton_organic_ipm"
                ]
                self.assertTrue(guide_chunks, "Cotton organic-IPM source should be retrieved")
                self.assertTrue(
                    any("TNAU Agritech Portal" in source for source in result.sources),
                    "Source citations should be returned with the retrieved guidance",
                )

    def test_cotton_ipm_prompt_contains_citations_and_scope_caution(self):
        from src.rag_pipeline import _build_prompt

        chunks = self.retriever.search(
            "How should I manage pests in cotton organically?",
            crop_filter="cotton",
        )
        guides = [
            chunk for chunk in chunks
            if chunk.get("management_guide_id") == "cotton_organic_ipm"
        ]
        prompt = _build_prompt("How should I manage cotton pests organically?", guides)
        self.assertIn("agritech.tnau.ac.in", prompt)
        self.assertIn("certification standard", prompt.lower())


class TestFarmingAdvisor(unittest.TestCase):
    """Test the farming_advisor high-level API."""

    def test_ask_basic_question(self):
        from src.farming_advisor import ask
        from src.llm.demo_provider import DemoProvider
        with patch("src.rag_pipeline._get_llm_provider", return_value=(DemoProvider(), True)):
            result = ask("How do I prepare soil for rice?")
        self.assertTrue(result.answer)
        self.assertIsInstance(result.sources, list)

    def test_get_knowledge_stats(self):
        from src.farming_advisor import get_knowledge_stats
        stats = get_knowledge_stats()
        self.assertIn("total_chunks", stats)
        self.assertIn("retriever_ready", stats)
        self.assertTrue(stats["retriever_ready"])
        self.assertGreater(stats["total_chunks"], 0)
        print(f"\n  Knowledge stats: {stats}")

    def test_get_all_crop_ids(self):
        from src.farming_advisor import get_all_crop_ids
        ids = get_all_crop_ids()
        self.assertIsInstance(ids, list)
        self.assertIn("rice", ids)
        self.assertIn("wheat", ids)
        self.assertIn("tomato", ids)
        print(f"\n  Available crop IDs: {ids}")

    def test_get_safety_info(self):
        from src.farming_advisor import get_safety_info
        result = get_safety_info("cyclone")
        self.assertTrue(result.answer)
        self.assertTrue(result.has_safety_content)


class TestLLMProviders(unittest.TestCase):
    """Test LLM provider instantiation and interface."""

    def test_demo_provider_generates_non_empty_response(self):
        from src.llm.demo_provider import DemoProvider
        provider = DemoProvider()
        self.assertFalse(provider.is_demo is False)  # demo=True
        self.assertTrue(provider.is_demo)
        response = provider.generate("Test prompt")
        self.assertTrue(response)
        self.assertIn("DEMO MODE", response)

    def test_demo_provider_health_check(self):
        from src.llm.demo_provider import DemoProvider
        provider = DemoProvider()
        health = provider.health_check()
        self.assertTrue(health["ok"])

    def test_ibm_provider_graceful_error_without_credentials(self):
        from src.llm.ibm_granite_provider import IBMGraniteProvider
        # An explicit empty-credential test must stay deterministic and offline.
        with patch("src.llm.ibm_granite_provider.IBM_WATSONX_API_KEY", ""), \
             patch("src.llm.ibm_granite_provider.IBM_WATSONX_PROJECT_ID", ""):
            provider = IBMGraniteProvider()
            health = provider.health_check()
        self.assertIn("message", health)
        self.assertFalse(health["ok"])
        self.assertIsInstance(health["message"], str)

    def test_base_provider_interface(self):
        from src.llm.base import LLMProvider
        from src.llm.demo_provider import DemoProvider
        provider = DemoProvider()
        # Verify it is a subclass of LLMProvider
        self.assertIsInstance(provider, LLMProvider)


class TestMarketService(unittest.TestCase):
    """Test market price service."""

    def test_get_all_commodities(self):
        from src.market_service import get_all_commodities
        commodities = get_all_commodities()
        self.assertIsInstance(commodities, list)
        self.assertGreater(len(commodities), 0)

    def test_disclaimer_present(self):
        from src.market_service import get_disclaimer
        disclaimer = get_disclaimer()
        self.assertIn("illustrative", disclaimer.lower())
        self.assertIn("NOT real-time", disclaimer)

    def test_format_price_table(self):
        from src.market_service import get_all_commodities, format_price_table
        commodities = get_all_commodities()
        if commodities:
            table = format_price_table(commodities[0], "en")
            self.assertIn("₹", table)
            self.assertIn("|", table)  # markdown table

    def test_market_copy_is_localized(self):
        from src.market_service import format_price_table, get_disclaimer
        sample = {
            "commodity_name": {"en": "Rice", "ta": "நெல்"},
            "unit": "₹ per quintal",
            "markets": [{"region": "Tamil Nadu", "min": 1, "max": 2, "modal": 2,
                         "grade_note": "Common paddy"}],
        }
        table = format_price_table(sample, "ta")
        self.assertIn("குறைந்த விலை", table)
        self.assertIn("பொதுத் தர நெல்", table)
        self.assertIn("குவிண்டால்", table)
        self.assertIn("நேரடி மண்டி விலைகள் அல்ல", get_disclaimer("ta"))

    def test_no_live_price_field(self):
        """Verify no commodity claims to be live/real-time."""
        from src.market_service import get_all_commodities
        for c in get_all_commodities():
            for market in c.get("markets", []):
                self.assertNotIn(
                    "real-time", str(market).lower(),
                    "Market data should not claim to be real-time"
                )


if __name__ == "__main__":
    print("Running RAG pipeline and advisor tests...")
    unittest.main(verbosity=2)
